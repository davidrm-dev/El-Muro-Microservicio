import axios from 'axios';
import jwt, { SignOptions } from 'jsonwebtoken';
import mongoose from 'mongoose';
import nodemailer from 'nodemailer';
import { env } from '../config/env';
import { IUserDocument, UserModel } from '../models/User.model';
import { JwtPayload, UserRole } from '../types/user.types';
import { HttpError } from '../utils/http-error';

interface RegisterInput {
  nombre: string;
  correo: string;
  password: string;
}

interface LoginInput {
  correo: string;
  password: string;
}

interface VerifyOtpInput {
  correo: string;
  otpCode: string;
}

interface AssignRoleInput {
  userId: string;
  rol: UserRole;
}

interface DeductPointsInput {
  userId: string;
  points: number;
  reason?: string;
}

const ADJECTIVES = ['agil', 'bravo', 'claro', 'firme', 'noble', 'audaz', 'sabio', 'tenaz', 'veloz', 'sereno'];
const ANIMALS = ['condor', 'jaguar', 'zorro', 'lince', 'halcon', 'puma', 'tigre', 'cebra', 'nutria', 'ibis'];
const UPTC_EMAIL_REGEX = /^[a-zA-Z0-9._%+-]+@uptc\.edu\.co$/;

class AuthService {
  private readonly transporter = nodemailer.createTransport({
    host: env.SMTP_HOST,
    port: env.SMTP_PORT,
    secure: env.SMTP_SECURE,
    auth: {
      user: env.SMTP_USER,
      pass: env.SMTP_PASS,
    },
  });

  private normalizeEmail(correo: string): string {
    return correo.trim().toLowerCase();
  }

  private validateInstitutionalEmail(correo: string): void {
    if (!UPTC_EMAIL_REGEX.test(correo)) {
      throw new HttpError(400, 'El correo debe ser institucional (@uptc.edu.co)');
    }
  }

  private generateOtpCode(): string {
    return Math.floor(100000 + Math.random() * 900000).toString();
  }

  private async callSheerIdSandbox(correo: string, nombre: string): Promise<string> {
    const requestBody = {
      firstName: nombre,
      email: correo,
      organizationId: 'uptc',
      verificationType: 'student',
      metadata: { source: 'auth-service' },
    };

    const response = await axios.post(`${env.SHEERID_BASE_URL}/verification`, requestBody, {
      headers: {
        Authorization: `Bearer ${env.SHEERID_API_TOKEN}`,
        'Content-Type': 'application/json',
      },
      timeout: 10000,
    });

    const verificationId = response.data?.verificationId || response.data?.id;
    if (!verificationId) {
      throw new HttpError(502, 'SheerID no retorno verificationId');
    }

    return verificationId as string;
  }

  private async sendOtpEmail(correo: string, otpCode: string): Promise<void> {
    await this.transporter.sendMail({
      from: env.SMTP_FROM,
      to: correo,
      subject: 'Verificacion de cuenta UPTC',
      text: `Tu codigo OTP es: ${otpCode}`,
      html: `<p>Tu codigo OTP es: <strong>${otpCode}</strong></p>`,
    });
  }

  private signToken(payload: JwtPayload): string {
    const signOptions: SignOptions = { expiresIn: `${env.JWT_EXPIRES_IN_HOURS}h` as SignOptions['expiresIn'] };
    return jwt.sign(payload, env.JWT_SECRET, signOptions);
  }

  private getLockUntilDate(): Date {
    const lockMs = env.LOGIN_LOCK_MINUTES * 60 * 1000;
    return new Date(Date.now() + lockMs);
  }

  private isAccountLocked(user: IUserDocument): boolean {
    return Boolean(user.lockUntil && user.lockUntil.getTime() > Date.now());
  }

  async generateUniqueNickname(): Promise<string> {
    let nickname = '';
    let exists = true;

    while (exists) {
      const adjective = ADJECTIVES[Math.floor(Math.random() * ADJECTIVES.length)];
      const animal = ANIMALS[Math.floor(Math.random() * ANIMALS.length)];
      const suffix = Math.floor(100 + Math.random() * 900).toString();
      nickname = `${adjective}_${animal}_${suffix}`;
      exists = Boolean(await UserModel.exists({ apodo: nickname }));
    }

    return nickname;
  }

  async register(input: RegisterInput): Promise<{ userId: string; correo: string; apodo: string }> {
    const correo = this.normalizeEmail(input.correo);
    this.validateInstitutionalEmail(correo);

    const existing = await UserModel.findOne({ correo });
    if (existing) {
      throw new HttpError(409, 'El correo ya esta registrado');
    }

    const sheerIdVerificationId = await this.callSheerIdSandbox(correo, input.nombre);
    const apodo = await this.generateUniqueNickname();
    const otpCode = this.generateOtpCode();

    const createdUser = await UserModel.create({
      nombre: input.nombre,
      correo,
      password: input.password,
      rol: 'estudiante',
      apodo,
      sheerIdVerificationId,
      otpCode,
      isVerified: false,
      estaActivo: true,
      failedLoginAttempts: 0,
      lockUntil: null,
    });

    await this.sendOtpEmail(createdUser.correo, otpCode);

    return {
      userId: createdUser._id.toString(),
      correo: createdUser.correo,
      apodo: createdUser.apodo,
    };
  }

  async verifyOtp(input: VerifyOtpInput): Promise<void> {
    const correo = this.normalizeEmail(input.correo);
    const user = await UserModel.findOne({ correo }).select('+otpCode');

    if (!user) {
      throw new HttpError(404, 'Usuario no encontrado');
    }

    if (!user.otpCode || user.otpCode !== input.otpCode) {
      throw new HttpError(401, 'OTP invalido');
    }

    user.isVerified = true;
    user.otpCode = undefined;
    await user.save();
  }

  async login(input: LoginInput): Promise<{ token: string; user: Partial<IUserDocument> }> {
    const correo = this.normalizeEmail(input.correo);
    const user = await UserModel.findOne({ correo }).select('+password');

    if (!user) {
      throw new HttpError(401, 'Credenciales invalidas');
    }

    if (this.isAccountLocked(user)) {
      throw new HttpError(429, 'Cuenta bloqueada temporalmente por multiples intentos fallidos');
    }

    const isPasswordValid = await user.comparePassword(input.password);
    if (!isPasswordValid) {
      user.failedLoginAttempts += 1;
      if (user.failedLoginAttempts >= env.MAX_LOGIN_ATTEMPTS) {
        user.lockUntil = this.getLockUntilDate();
        user.failedLoginAttempts = 0;
      }
      await user.save();
      throw new HttpError(401, 'Credenciales invalidas');
    }

    if (!user.isVerified) {
      throw new HttpError(401, 'Usuario no verificado');
    }

    if (!user.estaActivo) {
      throw new HttpError(403, 'Usuario deshabilitado');
    }

    user.failedLoginAttempts = 0;
    user.lockUntil = null;
    await user.save();

    const token = this.signToken({ userId: user._id.toString(), rol: user.rol });

    return {
      token,
      user: {
        _id: user._id,
        nombre: user.nombre,
        correo: user.correo,
        rol: user.rol,
        apodo: user.apodo,
        puntos: user.puntos,
        isVerified: user.isVerified,
        estaActivo: user.estaActivo,
      },
    };
  }

  async getStudentPoints(userId: string): Promise<{ userId: string; puntos: number }> {
    const user = await UserModel.findById(userId).select('puntos rol');
    if (!user) {
      throw new HttpError(404, 'Usuario no encontrado');
    }

    if (user.rol !== 'estudiante') {
      throw new HttpError(403, 'Solo aplica para estudiantes');
    }

    return { userId: user._id.toString(), puntos: user.puntos };
  }

  async disableUser(userId: string): Promise<void> {
    const updated = await UserModel.findByIdAndUpdate(userId, { estaActivo: false }, { new: true });
    if (!updated) {
      throw new HttpError(404, 'Usuario no encontrado');
    }
  }

  async assignRole(input: AssignRoleInput): Promise<{ userId: string; rol: UserRole }> {
    const updated = await UserModel.findByIdAndUpdate(
      input.userId,
      { rol: input.rol },
      { new: true, runValidators: true }
    );

    if (!updated) {
      throw new HttpError(404, 'Usuario no encontrado');
    }

    return { userId: updated._id.toString(), rol: updated.rol };
  }

  async deductPoints(input: DeductPointsInput): Promise<{ userId: string; puntos: number }> {
    if (!Number.isFinite(input.points) || input.points <= 0) {
      throw new HttpError(400, 'La cantidad de puntos a deducir debe ser mayor a cero');
    }

    const session = await mongoose.startSession();
    try {
      session.startTransaction();

      const user = await UserModel.findById(input.userId).session(session);
      if (!user) {
        throw new HttpError(404, 'Usuario no encontrado');
      }

      if (user.rol !== 'estudiante') {
        throw new HttpError(403, 'Solo aplica para estudiantes');
      }

      if (!user.estaActivo || !user.isVerified) {
        throw new HttpError(403, 'Usuario no habilitado para deduccion de puntos');
      }

      if (user.puntos < input.points) {
        throw new HttpError(409, 'Saldo de puntos insuficiente');
      }

      user.puntos -= input.points;
      await user.save({ session });
      await session.commitTransaction();

      return { userId: user._id.toString(), puntos: user.puntos };
    } catch (error) {
      await session.abortTransaction();
      throw error;
    } finally {
      session.endSession();
    }
  }
}

export const authService = new AuthService();
