export type UserRole = 'admin' | 'estudiante';

export interface IUser {
  nombre: string;
  correo: string;
  password: string;
  rol: UserRole;
  apodo: string;
  puntos: number;
  estaActivo: boolean;
  sheerIdVerificationId?: string;
  otpCode?: string;
  isVerified: boolean;
  failedLoginAttempts: number;
  lockUntil?: Date | null;
}

export interface JwtPayload {
  userId: string;
  rol: UserRole;
}
