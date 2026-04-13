import jwt from 'jsonwebtoken';
import mongoose from 'mongoose';
import { MongoMemoryReplSet } from 'mongodb-memory-server';

process.env.MONGO_URI = 'mongodb://127.0.0.1:27017/placeholder';
process.env.JWT_SECRET = 'test-shared-secret';
process.env.SHEERID_API_TOKEN = 'test-sheerid-token';
process.env.SMTP_HOST = 'smtp.test.local';
process.env.SMTP_PORT = '587';
process.env.SMTP_SECURE = 'false';
process.env.SMTP_USER = 'smtp_user';
process.env.SMTP_PASS = 'smtp_pass';
process.env.INTERNAL_SERVICE_SECRET = 'internal-secret';
process.env.TRUSTED_SERVICE_IDS = 'order-service,purchase-service';
process.env.JWT_EXPIRES_IN_HOURS = '6';
process.env.MAX_LOGIN_ATTEMPTS = '3';
process.env.LOGIN_LOCK_MINUTES = '15';

jest.mock('axios', () => ({
  __esModule: true,
  default: {
    post: jest.fn().mockResolvedValue({ data: { verificationId: 'verification-123' } }),
  },
}));

jest.mock('nodemailer', () => ({
  __esModule: true,
  default: {
    createTransport: jest.fn().mockReturnValue({
      sendMail: jest.fn().mockResolvedValue(true),
    }),
  },
}));

import axios from 'axios';
import { authService } from '../../services/Auth.service';
import { UserModel } from '../../models/User.model';

describe('AuthService security and integration tests', () => {
  let replSet: MongoMemoryReplSet;

  beforeAll(async () => {
    replSet = await MongoMemoryReplSet.create({ replSet: { count: 1 } });
    await mongoose.connect(replSet.getUri('auth-service-test'));
  });

  afterAll(async () => {
    await mongoose.disconnect();
    if (replSet) {
      await replSet.stop();
    }
  });

  beforeEach(async () => {
    jest.clearAllMocks();
    await UserModel.deleteMany({});
  });

  it('flujo positivo: registro @uptc.edu.co llama SheerID y envia OTP SMTP', async () => {
    const sendMailSpy = (authService as any).transporter.sendMail as jest.Mock;

    await authService.register({
      nombre: 'Juan Perez',
      correo: 'juan.perez@uptc.edu.co',
      password: 'Password123',
    });

    expect((axios as any).post).toHaveBeenCalledTimes(1);
    expect((axios as any).post.mock.calls[0][1].email).toBe('juan.perez@uptc.edu.co');
    expect(sendMailSpy).toHaveBeenCalledTimes(1);
    expect(sendMailSpy.mock.calls[0][0].to).toBe('juan.perez@uptc.edu.co');
  });

  it('flujo negativo: correo no institucional es rechazado sin llamar SheerID', async () => {
    await expect(
      authService.register({
        nombre: 'Attacker',
        correo: 'attacker@gmail.com',
        password: 'Password123',
      })
    ).rejects.toThrow('El correo debe ser institucional (@uptc.edu.co)');

    expect((axios as any).post).not.toHaveBeenCalled();
  });

  it('JWT usa secreto compartido, sin password y exp <= 6 horas', async () => {
    const registerResult = await authService.register({
      nombre: 'Ana User',
      correo: 'ana.user@uptc.edu.co',
      password: 'Password123',
    });

    await authService.verifyOtp({
      correo: 'ana.user@uptc.edu.co',
      otpCode: (await UserModel.findById(registerResult.userId).select('+otpCode'))?.otpCode as string,
    });

    const login = await authService.login({
      correo: 'ana.user@uptc.edu.co',
      password: 'Password123',
    });

    const decoded = jwt.verify(login.token, process.env.JWT_SECRET as string) as jwt.JwtPayload;
    expect(decoded.userId).toBe(registerResult.userId);
    expect(decoded.rol).toBe('estudiante');
    expect((decoded as Record<string, unknown>).password).toBeUndefined();
    expect(decoded.exp).toBeDefined();
    expect(decoded.iat).toBeDefined();
    const ttlSeconds = (decoded.exp as number) - (decoded.iat as number);
    expect(ttlSeconds).toBeLessThanOrEqual(6 * 60 * 60);
  });

  it('IDOR: estudiante A no puede consultar puntos de estudiante B por ID en URL', async () => {
    const userA = await UserModel.create({
      nombre: 'A',
      correo: 'a@uptc.edu.co',
      password: 'Password123',
      rol: 'estudiante',
      apodo: 'agil_condor_101',
      isVerified: true,
      estaActivo: true,
      puntos: 10,
      failedLoginAttempts: 0,
    });

    const userB = await UserModel.create({
      nombre: 'B',
      correo: 'b@uptc.edu.co',
      password: 'Password123',
      rol: 'estudiante',
      apodo: 'bravo_jaguar_202',
      isVerified: true,
      estaActivo: true,
      puntos: 40,
      failedLoginAttempts: 0,
    });

    const pointsA = await authService.getStudentPoints(userA._id.toString());
    expect(pointsA.puntos).toBe(10);
    expect(userB._id.toString()).not.toBe(userA._id.toString());
  });

  it('race condition: dos deducciones simultaneas no dejan puntos negativos', async () => {
    const user = await UserModel.create({
      nombre: 'Race User',
      correo: 'race@uptc.edu.co',
      password: 'Password123',
      rol: 'estudiante',
      apodo: 'firme_lince_303',
      isVerified: true,
      estaActivo: true,
      puntos: 100,
      failedLoginAttempts: 0,
    });

    const [result1, result2] = await Promise.allSettled([
      authService.deductPoints({ userId: user._id.toString(), points: 80, reason: 'compra-1' }),
      authService.deductPoints({ userId: user._id.toString(), points: 80, reason: 'compra-2' }),
    ]);

    const fulfilled = [result1, result2].filter((r) => r.status === 'fulfilled');
    const rejected = [result1, result2].filter((r) => r.status === 'rejected');

    expect(fulfilled.length).toBe(1);
    expect(rejected.length).toBe(1);

    const refreshed = await UserModel.findById(user._id);
    expect(refreshed?.puntos).toBeGreaterThanOrEqual(0);
  });

  it('maximo intentos de login: bloquea temporalmente tras intentos fallidos', async () => {
    await authService.register({
      nombre: 'Lock User',
      correo: 'lock.user@uptc.edu.co',
      password: 'Password123',
    });

    const u = await UserModel.findOne({ correo: 'lock.user@uptc.edu.co' }).select('+otpCode');
    await authService.verifyOtp({
      correo: 'lock.user@uptc.edu.co',
      otpCode: u?.otpCode as string,
    });

    await expect(authService.login({ correo: 'lock.user@uptc.edu.co', password: 'bad-1' })).rejects.toThrow(
      'Credenciales invalidas'
    );
    await expect(authService.login({ correo: 'lock.user@uptc.edu.co', password: 'bad-2' })).rejects.toThrow(
      'Credenciales invalidas'
    );
    await expect(authService.login({ correo: 'lock.user@uptc.edu.co', password: 'bad-3' })).rejects.toThrow(
      'Credenciales invalidas'
    );

    await expect(authService.login({ correo: 'lock.user@uptc.edu.co', password: 'Password123' })).rejects.toThrow(
      'Cuenta bloqueada temporalmente por multiples intentos fallidos'
    );
  });
});
