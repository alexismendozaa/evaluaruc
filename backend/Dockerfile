# Dockerfile para el backend (Flask)
FROM python:3.9

# Configurar directorio de trabajo
WORKDIR /app

# Copiar archivos del backend
COPY backend /app

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto del backend
EXPOSE 5000

# Comando para ejecutar el backend
CMD ["python", "api.py"]
