# AudioVisual Team Service
# Framework Silhouette V4.0
# Autor: MiniMax Agent

FROM python:3.11-slim

LABEL maintainer="MiniMax Agent"
LABEL description="AudioVisual Team Service - Silhouette Framework V4.0"

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    && rm -rf /var/cache/apt/*

# Configurar directorio de trabajo
WORKDIR /app

# Copiar archivos de configuración
COPY requirements.txt .
COPY main.py .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Crear directorios necesarios
RUN mkdir -p /app/data /app/logs /app/temp

# Exponer puerto
EXPOSE 8048

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8048/health', timeout=5)"

# Comando de inicio
CMD ["python", "main.py"]