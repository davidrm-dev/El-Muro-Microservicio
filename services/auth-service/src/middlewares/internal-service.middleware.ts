import crypto from 'crypto';
import { NextFunction, Request, Response } from 'express';
import { env } from '../config/env';

const getHeaderValue = (headerValue: string | string[] | undefined): string => {
  if (typeof headerValue === 'string') {
    return headerValue;
  }

  if (Array.isArray(headerValue) && headerValue.length > 0) {
    return headerValue[0];
  }

  return '';
};

const buildExpectedSignature = (serviceId: string, timestamp: string, method: string, path: string): string => {
  const payload = `${serviceId}:${timestamp}:${method.toUpperCase()}:${path}`;
  return crypto.createHmac('sha256', env.INTERNAL_SERVICE_SECRET).update(payload).digest('hex');
};

const safeCompare = (a: string, b: string): boolean => {
  if (a.length !== b.length) {
    return false;
  }

  return crypto.timingSafeEqual(Buffer.from(a), Buffer.from(b));
};

export const validateInternalService = (req: Request, res: Response, next: NextFunction): void => {
  const serviceId = getHeaderValue(req.headers['x-service-id']);
  const signature = getHeaderValue(req.headers['x-service-signature']);
  const timestamp = getHeaderValue(req.headers['x-service-timestamp']);

  if (!serviceId || !signature || !timestamp) {
    res.status(401).json({ message: 'Headers internos incompletos' });
    return;
  }

  if (!env.TRUSTED_SERVICE_IDS.includes(serviceId)) {
    res.status(403).json({ message: 'Servicio no autorizado' });
    return;
  }

  const timestampMs = Number(timestamp);
  if (!Number.isFinite(timestampMs)) {
    res.status(401).json({ message: 'Timestamp invalido' });
    return;
  }

  const maxSkewMs = 5 * 60 * 1000;
  if (Math.abs(Date.now() - timestampMs) > maxSkewMs) {
    res.status(401).json({ message: 'Timestamp fuera de ventana permitida' });
    return;
  }

  const expectedSignature = buildExpectedSignature(serviceId, timestamp, req.method, req.path);
  if (!safeCompare(signature, expectedSignature)) {
    res.status(401).json({ message: 'Firma interna invalida' });
    return;
  }

  next();
};
