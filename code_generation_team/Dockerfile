# Dockerfile para Code Generation Team
FROM python:3.11-slim

# Metadatos
LABEL maintainer="MiniMax Agent"
LABEL description="HAAS+ Code Generation Team Service"
LABEL version="1.0.0"

# Configurar directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt si existe
COPY requirements.txt* ./

# Instalar dependencias Python
RUN if [ -f requirements.txt ]; then \
        pip install --no-cache-dir -r requirements.txt; \
    fi

# Instalar dependencias específicas para Code Generation Team
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    asyncpg==0.29.0 \
    redis==5.0.1 \
    httpx==0.25.2 \
    pydantic==2.5.0 \
    python-multipart==0.0.6 \
    python-jose[cryptography]==3.3.0 \
    passlib[bcrypt]==1.7.4 \
    networkx==3.2.1 \
    openai==1.3.7 \
    anthropic==0.7.7 \
    structlog==23.2.0 \
    prometheus-client==0.19.0 \
    black==23.11.0 \
    flake8==6.1.0 \
    mypy==1.7.1

# Crear directorio de logs
RUN mkdir -p /app/logs

# Copiar código de la aplicación
COPY . .

# Crear usuario no-root para seguridad
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando por defecto
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]