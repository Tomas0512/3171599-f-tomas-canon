FROM python:3.12-slim

# Evita que Python genere archivos .pyc y permite ver logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instalamos las dependencias directamente
RUN pip install --no-cache-dir fastapi[standard]

# Copiamos el resto del código
COPY . .

EXPOSE 8000

# Comando para ejecutar la app
CMD ["fastapi", "dev", "src/main.py", "--host", "0.0.0.0"]
