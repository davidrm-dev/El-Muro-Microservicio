import dotenv from 'dotenv';

dotenv.config();

const requireEnv = (key: string): string => {
  const value = process.env[key];
  if (!value) {
    throw new Error(`Missing environment variable: ${key}`);
  }
  return value;
};

const parsePositiveInt = (value: string | undefined, fallback: number): number => {
  const parsed = Number(value);
  if (!Number.isFinite(parsed) || parsed <= 0) {
    return fallback;
  }
  return Math.floor(parsed);
};

const parseJwtHours = (value: string | undefined): number => {
  const parsed = parsePositiveInt(value, 6);
  return Math.min(parsed, 6);
};

export const env = {
  PORT: parsePositiveInt(process.env.PORT, 3000),
  MONGO_URI: requireEnv('MONGO_URI'),
  JWT_SECRET: requireEnv('JWT_SECRET'),
  JWT_EXPIRES_IN_HOURS: parseJwtHours(process.env.JWT_EXPIRES_IN_HOURS),
  SHEERID_BASE_URL: process.env.SHEERID_BASE_URL ?? 'https://services-sandbox.sheerid.com/rest/v2',
  SHEERID_API_TOKEN: requireEnv('SHEERID_API_TOKEN'),
  SMTP_HOST: requireEnv('SMTP_HOST'),
  SMTP_PORT: parsePositiveInt(process.env.SMTP_PORT, 587),
  SMTP_SECURE: process.env.SMTP_SECURE === 'true',
  SMTP_USER: requireEnv('SMTP_USER'),
  SMTP_PASS: requireEnv('SMTP_PASS'),
  SMTP_FROM: process.env.SMTP_FROM ?? 'no-reply@uptc.edu.co',
  INTERNAL_SERVICE_SECRET: requireEnv('INTERNAL_SERVICE_SECRET'),
  TRUSTED_SERVICE_IDS: (process.env.TRUSTED_SERVICE_IDS ?? '').split(',').map((id) => id.trim()).filter(Boolean),
  MAX_LOGIN_ATTEMPTS: parsePositiveInt(process.env.MAX_LOGIN_ATTEMPTS, 5),
  LOGIN_LOCK_MINUTES: parsePositiveInt(process.env.LOGIN_LOCK_MINUTES, 15),
};
