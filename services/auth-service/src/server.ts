import express from 'express';
import cors from 'cors';
import { env } from './config/env';
import { connectMongo } from './database/mongoose';
import { authRouter } from './routes/auth.routes';

// Inicialización de la aplicación Express
const app = express();
const PORT = env.PORT;

// Middleware
app.use(cors());
app.use(express.json());

app.get('/health', (_req, res) => {
  res.status(200).json({ message: 'auth-service online' });
});

app.use('/api/auth', authRouter);

const bootstrap = async (): Promise<void> => {
  await connectMongo();
  app.listen(PORT, () => {
    console.log(`Servidor corriendo en http://localhost:${PORT}`);
  });
};

bootstrap().catch((error: unknown) => {
  console.error('Error al iniciar auth-service:', error);
  process.exit(1);
});
