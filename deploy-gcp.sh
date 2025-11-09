#!/bin/bash

# ☁️ SCRIPT DE DESPLIEGUE ENTERPRISE - GOOGLE CLOUD RUN
# Tiempo estimado: 2-3 horas
# Costo: $50-200/mes
# Escalabilidad: Máxima

set -e

echo "🏗️  DESPLEGANDO FRAMEWORK MULTIAGENTE EN GOOGLE CLOUD RUN"
echo "=========================================================="

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
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

info() {
    echo -e "${PURPLE}[ℹ️  INFO]${NC} $1"
}

# Verificar dependencias
check_dependencies() {
    log "Verificando dependencias..."
    
    if ! command -v gcloud &> /dev/null; then
        error "Google Cloud SDK no está instalado. Instalar con: curl https://sdk.cloud.google.com | bash"
    fi
    
    if ! command -v git &> /dev/null; then
        error "Git no está instalado"
    fi
    
    if ! command -v docker &> /dev/null; then
        error "Docker no está instalado"
    fi
    
    success "Todas las dependencias están instaladas"
}

# Configurar Google Cloud
setup_gcp() {
    log "Configurando Google Cloud Platform..."
    
    # Solicitar project ID
    read -p "🔑 Ingresa tu PROJECT_ID de Google Cloud: " PROJECT_ID
    
    if [ -z "$PROJECT_ID" ]; then
        error "PROJECT_ID es requerido"
    fi
    
    # Configurar proyecto
    gcloud config set project $PROJECT_ID
    
    # Solicitar región
    read -p "🌍 Ingresa tu REGIÓN (ej: us-central1): " REGION
    
    if [ -z "$REGION" ]; then
        REGION="us-central1"
    fi
    
    # Autenticar si es necesario
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        log "Solicitando autenticación..."
        gcloud auth login
    fi
    
    # Habilitar APIs necesarias
    log "Habilitando APIs de Google Cloud..."
    
    APIs=(
        "run.googleapis.com"
        "cloudbuild.googleapis.com"
        "containerregistry.googleapis.com"
        "sql.googleapis.com"
        "redis.googleapis.com"
        "compute.googleapis.com"
        "monitoring.googleapis.com"
        "logging.googleapis.com"
    )
    
    for api in "${APIs[@]}"; do
        log "Habilitando $api..."
        gcloud services enable $api --quiet
    done
    
    success "Google Cloud Platform configurado"
    info "PROJECT_ID: $PROJECT_ID"
    info "REGION: $REGION"
}

# Crear bucket para Artifact Registry
create_artifact_registry() {
    log "Creando Artifact Registry..."
    
    REPOSITORY_NAME="multiagent-framework"
    
    gcloud artifacts repositories create $REPOSITORY_NAME \
        --repository-format=docker \
        --location=$REGION \
        --description="Multiagent Framework Container Registry"
    
    gcloud auth configure-docker $REGION-docker.pkg.dev
    
    success "Artifact Registry creado: $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME"
}

# Crear base de datos Cloud SQL
setup_database() {
    log "Configurando base de datos Cloud SQL..."
    
    # Instalar SQL proxy si no está disponible
    if ! command -v cloud_sql_proxy &> /dev/null; then
        log "Descargando Cloud SQL Proxy..."
        curl -L https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -o cloud_sql_proxy
        chmod +x cloud_sql_proxy
    fi
    
    # Crear instancia de PostgreSQL
    log "Creando instancia de PostgreSQL..."
    gcloud sql instances create multiagent-db \
        --database-version=POSTGRES_13 \
        --cpu=2 \
        --memory=7680MiB \
        --region=$REGION \
        --storage-type=SSD \
        --storage-size=100GB
    
    # Crear base de datos
    log "Creando base de datos..."
    gcloud sql databases create haasdb --instance=multiagent-db
    
    # Crear usuario
    log "Creando usuario de base de datos..."
    gcloud sql users create haas \
        --instance=multiagent-db \
        --password=haaspass123
    
    # Obtener connection string
    DB_CONNECTION_NAME=$(gcloud sql instances describe multiagent-db --format="value(connectionName)")
    
    success "Base de datos configurada"
    info "Connection Name: $DB_CONNECTION_NAME"
}

# Crear Redis
setup_redis() {
    log "Configurando Redis..."
    
    gcloud redis instances create multiagent-redis \
        --size=1 \
        --region=$REGION \
        --redis-version=redis_6_x
    
    REDIS_HOST=$(gcloud redis instances describe multiagent-redis --region=$REGION --format="value(host)")
    REDIS_PORT=$(gcloud redis instances describe multiagent-redis --region=$REGION --format="value(port)")
    
    success "Redis configurado"
    info "Host: $REDIS_HOST"
    info "Port: $REDIS_PORT"
}

# Crear variables de entorno para producción
create_production_env() {
    log "Creando variables de entorno de producción..."
    
    # Obtener connection strings
    DB_CONNECTION_NAME=$(gcloud sql instances describe multiagent-db --format="value(connectionName)")
    
    cat > .env.production << EOF
# GOOGLE CLOUD CONFIGURATION
GOOGLE_CLOUD_PROJECT=$PROJECT_ID
GOOGLE_CLOUD_REGION=$REGION

# BASE DE DATOS
DATABASE_URL=postgresql://haas:haaspass123@/$DB_NAME?host=/cloudsql/$DB_CONNECTION_NAME
DB_CONNECTION_NAME=$DB_CONNECTION_NAME
DB_NAME=haasdb

# REDIS
REDIS_URL=redis://$REDIS_HOST:$REDIS_PORT

# NEO4J (usar servicio gestionado o self-hosted)
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4jpass123

# SEGURIDAD
JWT_SECRET_KEY=$(openssl rand -base64 32)
ENCRYPTION_KEY=$(openssl rand -base64 32)
ALLOWED_ORIGINS=https://yourapp.com,https://api.yourapp.com

# CONFIGURACIÓN
NODE_ENV=production
API_VERSION=v1
MAX_CONCURRENT_REQUESTS=100
REQUEST_TIMEOUT=30000

# MONITOREO
GRAFANA_ADMIN_PASSWORD=secureadminpass123
PROMETHEUS_RETENTION=30d
LOG_LEVEL=info
EOF

    success "Variables de entorno creadas"
}

# Crear Dockerfile optimizado para Cloud Run
create_cloud_run_dockerfile() {
    log "Creando Dockerfile optimizado para Cloud Run..."
    
    cat > Dockerfile.cloudrun << 'EOF'
# Usar imagen optimizada
FROM node:18-bullseye-slim

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias primero (para cachear)
COPY package*.json ./
RUN npm ci --only=production --silent

# Copiar código fuente
COPY . .

# Crear usuario no-root
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nodejs
RUN chown -R nodejs:nodejs /app
USER nodejs

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8080}/health || exit 1

# Variables de entorno optimizadas
ENV NODE_OPTIONS="--max-old-space-size=512"
ENV PORT=8080

# Exponer puerto
EXPOSE 8080

# Comando de inicio
CMD ["npm", "start"]
EOF

    success "Dockerfile.cloudrun creado"
}

# Crear script de despliegue
create_deploy_script() {
    log "Creando script de despliegue..."
    
    cat > deploy-to-gcp.sh << 'EOF'
#!/bin/bash
set -e

PROJECT_ID=$1
REGION=$2
SERVICE_NAME=$3
SOURCE_DIR=$4

if [ -z "$PROJECT_ID" ] || [ -z "$REGION" ] || [ -z "$SERVICE_NAME" ]; then
    echo "Uso: $0 <PROJECT_ID> <REGION> <SERVICE_NAME> [SOURCE_DIR]"
    echo "Ejemplo: $0 my-project us-central1 api-gateway ./api-gateway"
    exit 1
fi

SOURCE_DIR=${SOURCE_DIR:-./}

echo "🚀 Desplegando $SERVICE_NAME en $REGION..."

# Construir y desplegar
gcloud run deploy $SERVICE_NAME \
    --source $SOURCE_DIR \
    --project $PROJECT_ID \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --port 8080 \
    --memory 1Gi \
    --cpu 1 \
    --concurrency 80 \
    --max-instances 10 \
    --set-env-vars "NODE_ENV=production" \
    --quiet

echo "✅ $SERVICE_NAME desplegado exitosamente"
EOF

    chmod +x deploy-to-gcp.sh
    success "Script de despliegue creado"
}

# Desplegar servicios
deploy_services() {
    log "Desplegando servicios en Google Cloud Run..."
    
    # API Gateway
    log "Desplegando API Gateway..."
    ./deploy-to-gcp.sh $PROJECT_ID $REGION api-gateway ./api-gateway
    
    # MCP Server
    log "Desplegando MCP Server..."
    ./deploy-to-gcp.sh $PROJECT_ID $REGION mcp-server ./mcp_server
    
    # Equipos especializados (en lotes para evitar rate limits)
    teams=(
        "marketing-team:./marketing_team"
        "sales-team:./sales_team"
        "finance-team:./finance_team"
        "hr-team:./hr_team"
        "legal-team:./legal_team"
        "product-team:./product_management_team"
        "customer-service-team:./customer_service_team"
        "support-team:./support_team"
        "communications-team:./communications_team"
        "research-team:./research_team"
        "design-team:./design_creative_team"
        "manufacturing-team:./manufacturing_team"
        "supply-chain-team:./supply_chain_team"
        "cloud-services-team:./cloud_services_team"
        "code-generation-team:./code_generation_team"
        "ml-ai-team:./machine_learning_ai_team"
        "qa-team:./quality_assurance_team"
        "security-team:./security_team"
        "risk-management-team:./risk_management_team"
        "strategy-team:./strategy_team"
        "business-development-team:./business_development_team"
    )
    
    for i in "${!teams[@]}"; do
        team_info=${teams[i]}
        service_name=${team_info%%:*}
        source_dir=${team_info##*:}
        
        log "Desplegando $service_name ($(($i + 1))/$((${#teams[@]})))..."
        ./deploy-to-gcp.sh $PROJECT_ID $REGION $service_name $source_dir
        
        # Rate limiting
        if [ $(($(date +%s) % 3)) -eq 0 ]; then
            sleep 5
        fi
    done
    
    success "Todos los servicios desplegados"
}

# Configurar monitoreo
setup_monitoring() {
    log "Configurando monitoreo..."
    
    # Crear topic de Pub/Sub para logs
    gcloud pubsub topics create multiagent-logs
    
    # Crear workspace de monitoring
    gcloud monitoring workspaces create --display-name="Multiagent Framework"
    
    # Configurar alerting
    cat > monitoring-alerts.json << 'EOF'
{
  "displayName": "Multiagent Framework Alerts",
  "enabled": true,
  "conditions": [
    {
      "displayName": "High Error Rate",
      "conditionThreshold": {
        "filter": "resource.type=\"cloud_run_revision\"",
        "comparison": "COMPARISON_GREATER_THAN",
        "thresholdValue": 0.05,
        "duration": "300s"
      }
    }
  ]
}
EOF
    
    gcloud alpha monitoring policies create --policy-from-file=monitoring-alerts.json
    
    success "Monitoreo configurado"
}

# Crear archivo de configuración de Cloud Run
create_cloudrun_config() {
    log "Creando configuración de Cloud Run..."
    
    cat > cloudrun.yaml << 'EOF'
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: multiagent-framework
  annotations:
    run.googleapis.com/ingress: all
    run.googleapis.com/cpu-throttling: "false"
spec:
  template:
    metadata:
      annotations:
        run.googleapis.com/cpu-throttling: "false"
        run.googleapis.com/memory: 1Gi
        run.googleapis.com/cpu: 1
    spec:
      containerConcurrency: 80
      timeoutSeconds: 300
      containers:
      - image: gcr.io/PROJECT_ID/multiagent-framework
        ports:
        - name: http1
          containerPort: 8080
        env:
        - name: NODE_ENV
          value: production
        - name: PORT
          value: "8080"
        resources:
          limits:
            cpu: 1
            memory: 1Gi
EOF

    success "cloudrun.yaml creado"
}

# Crear script de actualización
create_update_script() {
    log "Creando script de actualización..."
    
    cat > update-framework.sh << 'EOF'
#!/bin/bash
set -e

PROJECT_ID=$1
REGION=$2

if [ -z "$PROJECT_ID" ] || [ -z "$REGION" ]; then
    echo "Uso: $0 <PROJECT_ID> <REGION>"
    exit 1
fi

echo "🔄 Actualizando Framework Multiagente..."

# Actualizar todos los servicios
services=(
    "api-gateway"
    "mcp-server"
    "marketing-team"
    "sales-team"
    "finance-team"
    "hr-team"
    "legal-team"
    "product-team"
    "customer-service-team"
    "support-team"
    "communications-team"
    "research-team"
    "design-team"
    "manufacturing-team"
    "supply-chain-team"
    "cloud-services-team"
    "code-generation-team"
    "ml-ai-team"
    "qa-team"
    "security-team"
    "risk-management-team"
    "strategy-team"
    "business-development-team"
)

for service in "${services[@]}"; do
    echo "Actualizando $service..."
    gcloud run deploy $service \
        --source ./${service//-/_}_team \
        --project $PROJECT_ID \
        --region $REGION \
        --platform managed \
        --allow-unauthenticated \
        --quiet
done

echo "✅ Framework actualizado exitosamente"
EOF

    chmod +x update-framework.sh
    success "Script de actualización creado"
}

# Instrucciones finales
final_instructions() {
    echo ""
    echo "🎯 CONFIGURACIÓN FINAL:"
    echo "======================"
    echo ""
    echo "1. Configurar variables de entorno en Cloud Run:"
    echo "   gcloud run services update api-gateway"
    echo "   --set-env-vars DATABASE_URL=...,JWT_SECRET_KEY=..."
    echo ""
    echo "2. Configurar dominio personalizado:"
    echo "   gcloud run domain-mappings create"
    echo "   --service api-gateway"
    echo "   --domain api.your-framework.com"
    echo ""
    echo "3. Configurar SSL (automático):"
    echo "   gcloud run domain-mappings create"
    echo "   --service api-gateway"
    echo "   --domain api.your-framework.com"
    echo ""
    echo "4. Verificar despliegue:"
    echo "   gcloud run services list"
    echo "   gcloud run services describe api-gateway"
    echo ""
    echo "🔗 URLs de servicios:"
    echo "   API Gateway: https://api-gateway-xxxxxxxx-uc.a.run.app"
    echo "   MCP Server: https://mcp-server-xxxxxxxx-uc.a.run.app"
    echo ""
    echo "💰 COSTOS ESTIMADOS:"
    echo "   Cloud Run: $50-200/mes"
    echo "   Cloud SQL: $50-150/mes"
    echo "   Redis: $30-100/mes"
    echo "   Total: $130-450/mes"
    echo ""
}

# Función principal
main() {
    echo ""
    echo "☁️  SCRIPT DE DESPLIEGUE ENTERPRISE - GOOGLE CLOUD RUN"
    echo "======================================================"
    echo "⏱️  Tiempo estimado: 2-3 horas"
    echo "💰 Costo: $130-450/mes"
    echo "🚀 Escalabilidad: Máxima"
    echo "🏢 Recomendado para: Producción, Enterprise, Alto tráfico"
    echo ""
    
    check_dependencies
    setup_gcp
    create_artifact_registry
    setup_database
    setup_redis
    create_production_env
    create_cloud_run_dockerfile
    create_deploy_script
    create_cloudrun_config
    create_update_script
    
    # Preguntar si desplegar ahora
    echo ""
    read -p "¿Deseas desplegar los servicios ahora? (y/n): " deploy_now
    
    if [ "$deploy_now" = "y" ] || [ "$deploy_now" = "Y" ]; then
        deploy_services
        setup_monitoring
        echo ""
        success "🎉 ¡DESPLIEGUE COMPLETADO!"
    else
        echo ""
        success "🎉 ¡CONFIGURACIÓN COMPLETADA!"
        echo "Para desplegar manualmente, ejecuta: ./deploy-to-gcp.sh $PROJECT_ID $REGION <servicio>"
    fi
    
    final_instructions
}

# Ejecutar función principal
main "$@"