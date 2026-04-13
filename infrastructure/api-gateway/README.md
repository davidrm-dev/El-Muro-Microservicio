# API Gateway

Este directorio deja preparada la configuracion de rutas para cuando el proyecto agregue el gateway como aplicacion ejecutable.

## Ruta registrada

- `/api/temas/**` -> `lb://temas-service`

La resolucion `lb://` asume que `temas-service` ya esta registrado en `eureka-server`.
