import { Request, Response } from 'express';
import { authService } from '../services/Auth.service';
import { UserRole } from '../types/user.types';
import { HttpError } from '../utils/http-error';

type AuthenticatedRequest = Request & {
  user?: {
    userId: string;
    rol: UserRole;
  };
};

const handleError = (res: Response, error: unknown): void => {
  if (error instanceof HttpError) {
    res.status(error.statusCode).json({ message: error.message });
    return;
  }

  const message = error instanceof Error ? error.message : 'Error interno';
  res.status(500).json({ message });
};

export class AuthController {
  private static getPathParam(param: string | string[] | undefined): string {
    if (typeof param === 'string') {
      return param;
    }

    if (Array.isArray(param) && param.length > 0) {
      return param[0];
    }

    throw new HttpError(400, 'Parametro de ruta invalido');
  }

  static async register(req: Request, res: Response): Promise<void> {
    try {
      const result = await authService.register(req.body);
      res.status(201).json({
        message: 'Usuario registrado. Revisa tu correo institucional para OTP.',
        data: result,
      });
    } catch (error) {
      handleError(res, error);
    }
  }

  static async verifyOtp(req: Request, res: Response): Promise<void> {
    try {
      await authService.verifyOtp(req.body);
      res.status(200).json({ message: 'Cuenta verificada correctamente' });
    } catch (error) {
      handleError(res, error);
    }
  }

  static async login(req: Request, res: Response): Promise<void> {
    try {
      const result = await authService.login(req.body);
      res.status(200).json(result);
    } catch (error) {
      handleError(res, error);
    }
  }

  static async getMyPoints(req: Request, res: Response): Promise<void> {
    try {
      const userId = (req as AuthenticatedRequest).user?.userId;
      if (!userId) {
        throw new HttpError(401, 'No autenticado');
      }

      const result = await authService.getStudentPoints(userId);
      res.status(200).json(result);
    } catch (error) {
      handleError(res, error);
    }
  }

  static async disableUser(req: Request, res: Response): Promise<void> {
    try {
      const userId = AuthController.getPathParam(req.params.userId);
      await authService.disableUser(userId);
      res.status(200).json({ message: 'Usuario deshabilitado correctamente' });
    } catch (error) {
      handleError(res, error);
    }
  }

  static async assignRole(req: Request, res: Response): Promise<void> {
    try {
      const role = req.body.rol as UserRole;
      const userId = AuthController.getPathParam(req.params.userId);
      const result = await authService.assignRole({ userId, rol: role });

      res.status(200).json({
        message: 'Rol asignado correctamente',
        data: result,
      });
    } catch (error) {
      handleError(res, error);
    }
  }

  static async deductPoints(req: Request, res: Response): Promise<void> {
    try {
      const userId = AuthController.getPathParam(req.params.userId);
      const points = Number(req.body.points);
      const reason = typeof req.body.reason === 'string' ? req.body.reason : undefined;
      const result = await authService.deductPoints({ userId, points, reason });

      res.status(200).json({
        message: 'Deduccion de puntos aplicada',
        data: result,
      });
    } catch (error) {
      handleError(res, error);
    }
  }
}
