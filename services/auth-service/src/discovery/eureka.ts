import { env } from '../config/env';

const { Eureka } = require('eureka-js-client');

let client: {
  start: (cb: (error?: Error | null) => void) => void;
  stop: (cb: () => void) => void;
} | null = null;

const buildEurekaClient = () => {
  const baseUrl = `http://${env.EUREKA_INSTANCE_HOST}:${env.PORT}`;

  return new Eureka({
    instance: {
      app: env.EUREKA_SERVICE_NAME,
      hostName: env.EUREKA_INSTANCE_HOST,
      ipAddr: env.EUREKA_INSTANCE_HOST,
      port: {
        $: env.PORT,
        '@enabled': true,
      },
      statusPageUrl: `${baseUrl}/health`,
      healthCheckUrl: `${baseUrl}/health`,
      vipAddress: env.EUREKA_SERVICE_NAME,
      dataCenterInfo: {
        '@class': 'com.netflix.appinfo.InstanceInfo$DefaultDataCenterInfo',
        name: 'MyOwn',
      },
    },
    eureka: {
      host: env.EUREKA_HOST,
      port: env.EUREKA_PORT,
      servicePath: '/eureka/apps/',
    },
  });
};

export const startEurekaRegistration = async (): Promise<void> => {
  if (!env.EUREKA_ENABLED) {
    return;
  }

  if (client) {
    return;
  }

  client = buildEurekaClient();

  await new Promise<void>((resolve, reject) => {
    client?.start((error?: Error | null) => {
      if (error) {
        client = null;
        reject(error);
        return;
      }
      console.log(`auth-service registrado en Eureka (${env.EUREKA_HOST}:${env.EUREKA_PORT})`);
      resolve();
    });
  });
};

export const stopEurekaRegistration = async (): Promise<void> => {
  if (!client) {
    return;
  }

  await new Promise<void>((resolve) => {
    client?.stop(() => {
      console.log('auth-service removido de Eureka');
      resolve();
    });
  });

  client = null;
};
