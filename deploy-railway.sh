#!/bin/bash

# 🚀 SCRIPT DE DESPLIEGUE RÁPIDO - RAILWAY/HEROKU
# Tiempo estimado: 30 minutos
# Costo: $20-50/mes

set -e

echo "🏗️  DESPLEGANDO FRAMEWORK MULTIAGENTE EN RAILWAY"
echo "=================================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[✅ SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[⚠️  WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[❌ ERROR]${NC} $1"
    exit 1
}

# Verificar dependencias
check_dependencies() {
    log "Verificando dependencias..."
    
    if ! command -v git &> /dev/null; then
        error "Git no está instalado"
    fi
    
    if ! command -v node &> /dev/null; then
        error "Node.js no está instalado"
    fi
    
    if ! command -v npm &> /dev/null; then
        error "npm no está instalado"
    fi
    
    success "Todas las dependencias están instaladas"
}

# Configurar variables de entorno
setup_environment() {
    log "Configurando variables de entorno..."
    
    # Crear archivo .env.production
    cat > .env.production << EOF
# BASE DE DATOS
DATABASE_URL=\${DATABASE_URL}
REDIS_URL=\${REDIS_URL}
NEO4J_URI=\${NEO4J_URI}
NEO4J_USER=neo4j
NEO4J_PASSWORD=\${NEO4J_PASSWORD}

# SEGURIDAD
JWT_SECRET_KEY=\${JWT_SECRET_KEY}
ENCRYPTION_KEY=\${ENCRYPTION_KEY}
ALLOWED_ORIGINS=\${ALLOWED_ORIGINS}

# APIs EXTERNAS (Configurar en Railway dashboard)
OPENAI_API_KEY=\${OPENAI_API_KEY}
GITHUB_TOKEN=\${GITHUB_TOKEN}
AWS_ACCESS_KEY_ID=\${AWS_ACCESS_KEY_ID}
AWS_SECRET_ACCESS_KEY=\${AWS_SECRET_ACCESS_KEY}
GOOGLE_SEARCH_API_KEY=\${GOOGLE_SEARCH_API_KEY}
SALESFORCE_CLIENT_ID=\${SALESFORCE_CLIENT_ID}
STRIPE_API_KEY=\${STRIPE_API_KEY}

# CONFIGURACIÓN
NODE_ENV=production
PORT=\${PORT:-8080}
API_VERSION=v1
EOF

    success "Archivo .env.production creado"
}

# Preparar package.json para Railway
setup_package_json() {
    log "Configurando package.json para Railway..."
    
    cat > package.json << 'EOF'
{
  "name": "multiagent-framework",
  "version": "1.0.0",
  "description": "Sistema Multiagente Framework - 25 servicios especializados",
  "main": "orchestrator/main.js",
  "scripts": {
    "start": "node orchestrator/main.js",
    "test": "bash master_test.sh",
    "dev": "nodemon orchestrator/main.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "helmet": "^7.0.0",
    "jsonwebtoken": "^9.0.2",
    "bcryptjs": "^2.4.3",
    "pg": "^8.11.0",
    "redis": "^4.6.5",
    "neo4j-driver": "^5.8.0",
    "amqplib": "^0.10.3",
    "axios": "^1.4.0",
    "dotenv": "^16.3.1",
    "morgan": "^1.10.0",
    "rate-limiter-flexible": "^3.0.0"
  },
  "devDependencies": {
    "nodemon": "^3.0.1",
    "jest": "^29.5.0"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
EOF

    success "package.json configurado"
}

# Crear Dockerfile optimizado para Railway
create_dockerfile() {
    log "Creando Dockerfile optimizado..."
    
    cat > Dockerfile.railway << 'EOF'
FROM node:18-alpine

# Instalar dependencias del sistema
RUN apk add --no-cache \
    postgresql-client \
    redis \
    curl

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./
RUN npm ci --only=production

# Copiar código fuente
COPY . .

# Crear usuario no-root
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nodejs -u 1001

# Cambiar propietario de archivos
RUN chown -R nodejs:nodejs /app
USER nodejs

# Exponer puerto
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Comando de inicio
CMD ["npm", "start"]
EOF

    success "Dockerfile.railway creado"
}

# Crear script de inicio para Railway
create_start_script() {
    log "Creando script de inicio..."
    
    cat > start.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Iniciando Framework Multiagente..."

# Verificar variables de entorno críticas
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL no está configurada"
    exit 1
fi

if [ -z "$JWT_SECRET_KEY" ]; then
    echo "❌ ERROR: JWT_SECRET_KEY no está configurada"
    exit 1
fi

# Ejecutar migraciones si es necesario
echo "📊 Verificando base de datos..."
npm run db:migrate || echo "No migrations to run"

# Iniciar servicios
echo "🏗️  Iniciando orquestador principal..."
exec node orchestrator/main.js
EOF

    chmod +x start.sh
    success "Script de inicio creado y configurado"
}

# Crear archivo de configuración de Railway
create_railway_config() {
    log "Creando configuración de Railway..."
    
    cat > railway.toml << 'EOF'
[build]
builder = "nixpacks"

[deploy]
startCommand = "npm start"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10

[environments.production.variables]
NODE_ENV = "production"
EOF

    success "railway.toml creado"
}

# Desplegar a GitHub
deploy_to_github() {
    log "Desplegando código a GitHub..."
    
    # Inicializar repositorio si no existe
    if [ ! -d ".git" ]; then
        git init
        git add .
        git commit -m "🚀 Sistema Multiagente Framework v1.0 - Despliegue inicial"
        
        echo "🔗 Para subir a GitHub, ejecuta:"
        echo "git remote add origin https://github.com/TU-USUARIO/multiagent-framework.git"
        echo "git branch -M main"
        echo "git push -u origin main"
    else
        git add .
        git commit -m "🚀 Actualización de despliegue - $(date)"
        echo "Git commit realizado. Push a GitHub con: git push"
    fi
    
    success "Código preparado para GitHub"
}

# Instrucciones para Railway
railway_instructions() {
    echo ""
    echo "🎯 INSTRUCCIONES PARA RAILWAY:"
    echo "=============================="
    echo ""
    echo "1. Instalar Railway CLI:"
    echo "   npm install -g @railway/cli"
    echo ""
    echo "2. Autenticar:"
    echo "   railway login"
    echo ""
    echo "3. Crear proyecto:"
    echo "   railway new"
    echo ""
    echo "4. Configurar variables de entorno en Railway dashboard:"
    echo "   - DATABASE_URL (PostgreSQL)"
    echo "   - REDIS_URL (Redis)"
    echo "   - JWT_SECRET_KEY (clave secreta)"
    echo "   - Todas las API keys necesarias"
    echo ""
    echo "5. Conectar repositorio de GitHub"
    echo ""
    echo "6. Desplegar:"
    echo "   railway up"
    echo ""
    echo "⏱️  Tiempo estimado: 5-10 minutos"
    echo "💰 Costo aproximado: $20-50/mes"
    echo ""
}

# Verificar que todo está listo
final_verification() {
    log "Verificación final..."
    
    # Verificar archivos necesarios
    files=("package.json" "orchestrator/main.js" "docker-compose.yml" ".env.production")
    
    for file in "${files[@]}"; do
        if [ ! -f "$file" ]; then
            warning "Archivo faltante: $file"
        fi
    done
    
    # Verificar directorios de equipos
    team_dirs=$(find . -maxdepth 1 -type d -name "*_team" | wc -l)
    if [ "$team_dirs" -lt 24 ]; then
        warning "Se esperan 24 directorios de equipos, encontrados: $team_dirs"
    else
        success "Directorios de equipos verificados"
    fi
    
    echo ""
    echo "✅ VERIFICACIÓN COMPLETADA"
    echo "=========================="
    echo "📁 Archivos preparados:"
    echo "   - package.json"
    echo "   - Dockerfile.railway"
    echo "   - start.sh"
    echo "   - railway.toml"
    echo "   - .env.production"
    echo ""
    echo "🚀 Sistema listo para desplegar en Railway!"
}

# Función principal
main() {
    echo ""
    echo "🏗️  SCRIPT DE DESPLIEGUE RÁPIDO - RAILWAY"
    echo "=========================================="
    echo "⏱️  Tiempo estimado: 30 minutos"
    echo "💰 Costo: $20-50/mes"
    echo "🚀 Escalabilidad: Media"
    echo ""
    
    check_dependencies
    setup_environment
    setup_package_json
    create_dockerfile
    create_start_script
    create_railway_config
    deploy_to_github
    final_verification
    railway_instructions
    
    echo ""
    success "🎉 ¡DESPLIEGUE PREPARADO EXITOSAMENTE!"
    echo "Sigue las instrucciones de Railway para completar el despliegue."
    echo ""
}

# Ejecutar función principal
main "$@"