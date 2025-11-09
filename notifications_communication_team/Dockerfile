FROM python:3.11-slim

# Instalar dependencias del sistema para comunicación
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root para seguridad
RUN groupadd -r notifications && useradd -r -g notifications notifications

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements primero para aprovechar cache de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Cambiar propietario de archivos
RUN chown -R notifications:notifications /app

# Cambiar a usuario no-root
USER notifications

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando por defecto
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]