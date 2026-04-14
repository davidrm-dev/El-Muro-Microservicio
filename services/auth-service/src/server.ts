import express from 'express';
import cors from 'cors';
import { Server } from 'http';
import { env } from './config/env';
import { connectMongo } from './database/mongoose';
import { startEurekaRegistration, stopEurekaRegistration } from './discovery/eureka';
import { authRouter } from './routes/auth.routes';

// Inicialización de la aplicación Express
const app = express();
const PORT = env.PORT;
let server: Server | null = null;
let isShuttingDown = false;

// Middleware
app.use(cors());
app.use(express.json());

app.get('/health', (_req, res) => {
  res.status(200).json({ message: 'auth-service online' });
});

app.use('/api/auth', authRouter);

const bootstrap = async (): Promise<void> => {
  await connectMongo();
  server = app.listen(PORT, () => {
    console.log(`Servidor corriendo en http://localhost:${PORT}`);
  });

  await startEurekaRegistration();
};

const shutdown = async (signal: NodeJS.Signals): Promise<void> => {
  if (isShuttingDown) {
    return;
  }

  isShuttingDown = true;
  console.log(`Señal ${signal} recibida. Cerrando auth-service...`);

  try {
    await stopEurekaRegistration();

    if (server) {
      await new Promise<void>((resolve, reject) => {
        server?.close((error?: Error) => {
          if (error) {
            reject(error);
            return;
          }
          resolve();
        });
      });
    }

    process.exit(0);
  } catch (error) {
    console.error('Error durante el apagado de auth-service:', error);
    process.exit(1);
  }
};

process.on('SIGINT', () => {
  shutdown('SIGINT').catch((error) => {
    console.error('Error al procesar SIGINT:', error);
  });
});

process.on('SIGTERM', () => {
  shutdown('SIGTERM').catch((error) => {
    console.error('Error al procesar SIGTERM:', error);
  });
});

bootstrap().catch((error: unknown) => {
  console.error('Error al iniciar auth-service:', error);
  process.exit(1);
});
