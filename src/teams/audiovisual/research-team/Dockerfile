# AudioVisual Research Team Service
# Framework Silhouette V4.0
# Autor: MiniMax Agent

FROM python:3.11-slim

LABEL maintainer="MiniMax Agent"
LABEL description="AudioVisual Research Team Service - Silhouette Framework V4.0"

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/cache/apt/*

# Configurar directorio de trabajo
WORKDIR /app

# Crear requirements.txt básico
RUN echo "fastapi==0.104.1\nuvicorn[standard]==0.24.0\nrequests==2.31.0" > requirements.txt

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponer puerto
EXPOSE 8050

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8050/health || exit 1

# Comando de inicio
CMD ["python", "-c", "import uvicorn; import fastapi; from fastapi import FastAPI; app = FastAPI(); @app.get('/health'); def health(): return {'status': 'ok'}; uvicorn.run(app, host='0.0.0.0', port=8050)"]