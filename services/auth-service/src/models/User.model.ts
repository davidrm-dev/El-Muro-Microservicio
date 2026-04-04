import bcrypt from 'bcryptjs';
import { Document, Model, Schema, model } from 'mongoose';
import { IUser } from '../types/user.types';

const UPTC_EMAIL_REGEX = /^[a-zA-Z0-9._%+-]+@uptc\.edu\.co$/;

export interface IUserDocument extends IUser, Document {
  comparePassword(candidatePassword: string): Promise<boolean>;
}

interface IUserModel extends Model<IUserDocument> {}

const userSchema = new Schema<IUserDocument>(
  {
    nombre: {
      type: String,
      required: true,
      trim: true,
    },
    correo: {
      type: String,
      required: true,
      unique: true,
      lowercase: true,
      trim: true,
      match: [UPTC_EMAIL_REGEX, 'El correo debe ser institucional (@uptc.edu.co)'],
    },
    password: {
      type: String,
      required: true,
      minlength: 8,
      select: false,
    },
    rol: {
      type: String,
      enum: ['admin', 'estudiante'],
      required: true,
      default: 'estudiante',
    },
    apodo: {
      type: String,
      required: true,
      unique: true,
      trim: true,
    },
    puntos: {
      type: Number,
      default: 0,
      required: true,
      min: 0,
    },
    estaActivo: {
      type: Boolean,
      default: true,
      required: true,
    },
    sheerIdVerificationId: {
      type: String,
      default: null,
      trim: true,
    },
    otpCode: {
      type: String,
      default: null,
      select: false,
    },
    isVerified: {
      type: Boolean,
      default: false,
      required: true,
    },
    failedLoginAttempts: {
      type: Number,
      default: 0,
      required: true,
      min: 0,
    },
    lockUntil: {
      type: Date,
      default: null,
    },
  },
  {
    timestamps: true,
    versionKey: false,
  }
);

userSchema.pre('save', async function preSave(next) {
  if (!this.isModified('password')) {
    return next();
  }

  const saltRounds = 10;
  this.password = await bcrypt.hash(this.password, saltRounds);
  next();
});

userSchema.methods.comparePassword = async function comparePassword(candidatePassword: string): Promise<boolean> {
  return bcrypt.compare(candidatePassword, this.password);
};

export const UserModel = model<IUserDocument, IUserModel>('User', userSchema);
