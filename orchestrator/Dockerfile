# Orchestrator Team - Framework Silhouette V4.0
# Servicio principal de coordinación y orquestación
FROM python:3.11-slim

# Metadatos
LABEL maintainer="MiniMax Agent"
LABEL description="Orchestrator Team - Framework Silhouette V4.0"
LABEL version="4.0.0"

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Configurar directorio de trabajo
WORKDIR /app

# Copiar requirements y instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear directorios necesarios
RUN mkdir -p /app/data /app/logs

# Usuario no-root
RUN useradd -m -u 1001 orchestrator && \
    chown -R orchestrator:orchestrator /app
USER orchestrator

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando de inicio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]