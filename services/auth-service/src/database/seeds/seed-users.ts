import dotenv from 'dotenv';
import mongoose from 'mongoose';
import { UserModel } from '../../models/User.model';

dotenv.config();

type SeedUser = {
  nombre: string;
  correo: string;
  password: string;
  rol: 'admin' | 'estudiante';
  apodo: string;
  puntos: number;
  estaActivo: boolean;
  isVerified: boolean;
};

const seedUsers: SeedUser[] = [
  {
    nombre: 'Admin Principal',
    correo: 'admin.principal@uptc.edu.co',
    password: 'Admin12345',
    rol: 'admin',
    apodo: 'noble_condor_001',
    puntos: 0,
    estaActivo: true,
    isVerified: true,
  },
  {
    nombre: 'Estudiante Uno',
    correo: 'estudiante.uno@uptc.edu.co',
    password: 'Estudiante123',
    rol: 'estudiante',
    apodo: 'agil_lince_101',
    puntos: 120,
    estaActivo: true,
    isVerified: true,
  },
  {
    nombre: 'Estudiante Dos',
    correo: 'estudiante.dos@uptc.edu.co',
    password: 'Estudiante123',
    rol: 'estudiante',
    apodo: 'firme_jaguar_202',
    puntos: 40,
    estaActivo: false,
    isVerified: true,
  },
];

const getMongoUri = (): string => {
  const mongoUri = process.env.MONGO_URI;
  if (!mongoUri) {
    throw new Error('MONGO_URI no esta definida en variables de entorno');
  }
  return mongoUri;
};

const upsertUser = async (entry: SeedUser): Promise<void> => {
  const existing = await UserModel.findOne({ correo: entry.correo }).select('+password');

  if (!existing) {
    await UserModel.create({
      ...entry,
      failedLoginAttempts: 0,
      lockUntil: null,
      sheerIdVerificationId: null,
      otpCode: null,
    });
    return;
  }

  existing.nombre = entry.nombre;
  existing.password = entry.password;
  existing.rol = entry.rol;
  existing.apodo = entry.apodo;
  existing.puntos = entry.puntos;
  existing.estaActivo = entry.estaActivo;
  existing.isVerified = entry.isVerified;
  existing.failedLoginAttempts = 0;
  existing.lockUntil = null;
  existing.sheerIdVerificationId = undefined;
  existing.otpCode = undefined;

  await existing.save();
};

const seed = async (): Promise<void> => {
  const mongoUri = getMongoUri();
  await mongoose.connect(mongoUri);

  try {
    for (const user of seedUsers) {
      await upsertUser(user);
    }

    console.log(`Seed completado: ${seedUsers.length} usuarios procesados`);
  } finally {
    await mongoose.disconnect();
  }
};

seed().catch((error: unknown) => {
  console.error('Error ejecutando seed de usuarios:', error);
  process.exit(1);
});
