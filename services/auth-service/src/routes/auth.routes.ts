import { Router } from 'express';
import { AuthController } from '../controllers/Auth.controller';
import { validateInternalService } from '../middlewares/internal-service.middleware';
import { authenticateToken, authorizeRoles } from '../middlewares/role.middleware';

const authRouter = Router();

authRouter.post('/register', AuthController.register);
authRouter.post('/verify-otp', AuthController.verifyOtp);
authRouter.post('/login', AuthController.login);

authRouter.get('/me/puntos', authenticateToken, authorizeRoles('estudiante'), AuthController.getMyPoints);

authRouter.patch(
  '/admin/users/:userId/disable',
  authenticateToken,
  authorizeRoles('admin'),
  AuthController.disableUser
);

authRouter.patch(
  '/admin/users/:userId/role',
  authenticateToken,
  authorizeRoles('admin'),
  AuthController.assignRole
);

authRouter.patch('/internal/users/:userId/deduct-points', validateInternalService, AuthController.deductPoints);
authRouter.patch('/internal/users/:userId/add-points', validateInternalService, AuthController.addPoints);

export { authRouter };
