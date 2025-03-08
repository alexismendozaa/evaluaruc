# Dockerfile para el frontend (Angular)
FROM node:18-alpine as build

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos del frontend
COPY frontend /app

# Instalar dependencias y construir Angular
RUN npm install && npm run build

# Usar un servidor web para servir la aplicación
FROM nginx:alpine

# Copiar archivos generados al servidor
COPY --from=build /app/dist/evalua-ruc-frontend /usr/share/nginx/html

# Exponer el puerto 80
EXPOSE 80

# Ejecutar Nginx
CMD ["nginx", "-g", "daemon off;"]
