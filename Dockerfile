# Framework Silhouette Enterprise Multi-Agent System V4.0
# Dockerfile Principal

FROM node:18-alpine

# Información del proyecto
LABEL maintainer="MiniMax Agent"
LABEL description="Framework Silhouette Enterprise Multi-Agent System V4.0"
LABEL version="4.0.0"

# Instalar dependencias del sistema
RUN apk add --no-cache \
    ffmpeg \
    python3 \
    make \
    g++ \
    curl \
    && rm -rf /var/cache/apk/*

# Configurar directorio de trabajo
WORKDIR /app

# Copiar archivos de configuración
COPY package*.json ./
COPY src/ ./src/
COPY config/ ./config/ 2>/dev/null || true

# Instalar dependencias
RUN npm ci --only=production && npm cache clean --force

# Crear directorios necesarios
RUN mkdir -p /app/data /app/logs /app/temp /app/backups

# Configurar usuario no-root
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

# Cambiar permisos
RUN chown -R nodejs:nodejs /app

# Cambiar a usuario no-root
USER nodejs

# Exponer puerto
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Comando de inicio
CMD ["node", "src/framework/index.js"]