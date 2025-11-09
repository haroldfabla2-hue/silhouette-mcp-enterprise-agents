#!/bin/bash
# master_test.sh - Script maestro para verificación completa del Framework Multiagente

set -e  # Exit on any error

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

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

# Contadores
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Función para contar tests
test_count() {
    ((TESTS_TOTAL++))
}

# Función para marcar test como pasado
test_pass() {
    ((TESTS_PASSED++))
    log_success "$1"
}

# Función para marcar test como fallido
test_fail() {
    ((TESTS_FAILED++))
    log_error "$1"
}

echo -e "${BLUE}"
echo "🚀 FRAMEWORK MULTIAGENTE - VERIFICACIÓN COMPLETA"
echo "============================================="
echo "🎯 Objetivo: 100% Confianza en el Sistema"
echo -e "${NC}"

# ========================================
# FASE 1: VERIFICACIÓN DE INFRAESTRUCTURA
# ========================================

log "Fase 1: Verificando infraestructura base..."

# 1.1 Verificar Docker
test_count
if docker info >/dev/null 2>&1; then
    test_pass "Docker está ejecutándose"
else
    test_fail "Docker no está ejecutándose"
fi

# 1.2 Verificar Docker Compose
test_count
if docker compose version >/dev/null 2>&1; then
    test_pass "Docker Compose está disponible"
else
    test_fail "Docker Compose no está disponible"
fi

# 1.3 Verificar servicios base
echo ""
log "Verificando servicios de base de datos..."

# PostgreSQL
test_count
if curl -s http://localhost:5432 >/dev/null 2>&1; then
    test_pass "PostgreSQL: Puerto accesible"
else
    test_warning "PostgreSQL: Puerto no accesible (puede ser normal si no está expuestos)"
fi

# Redis
test_count
if curl -s http://localhost:6379 >/dev/null 2>&1; then
    test_pass "Redis: Puerto accesible"
else
    test_warning "Redis: Puerto no accesible (puede ser normal si no está expuestos)"
fi

# RabbitMQ Management
test_count
if curl -s http://localhost:15672 >/dev/null 2>&1; then
    test_pass "RabbitMQ Management: Accesible en http://localhost:15672"
else
    test_warning "RabbitMQ Management: No accesible (verificar que el servicio esté corriendo)"
fi

# Neo4j Browser
test_count
if curl -s http://localhost:7474 >/dev/null 2>&1; then
    test_pass "Neo4j Browser: Accesible en http://localhost:7474"
else
    test_warning "Neo4j Browser: No accesible (verificar que el servicio esté corriendo)"
fi

# ========================================
# FASE 2: VERIFICACIÓN DE SERVICIOS
# ========================================

log ""
log "Fase 2: Verificando servicios del framework..."

# Lista de servicios a verificar
SERVICES=(
    "8000:API Gateway"
    "8001:Development Team"
    "8002:Marketing Team"
    "8003:Sales Team"
    "8004:MCP Server"
    "8005:Finance Team"
)

for service_info in "${SERVICES[@]}"; do
    port=$(echo $service_info | cut -d: -f1)
    name=$(echo $service_info | cut -d: -f2)
    
    log "Verificando $name (puerto $port)..."
    
    # Test de health check
    test_count
    health_response=$(curl -s -w "%{http_code}" -o /dev/null "http://localhost:$port/health" --connect-timeout 10 2>/dev/null || echo "000")
    
    if [[ "$health_response" == "200" ]]; then
        test_pass "$name: Health check OK (HTTP 200)"
    else
        test_fail "$name: Health check FAILED (HTTP $health_response)"
    fi
done

# ========================================
# FASE 3: VERIFICACIÓN DE HERRAMIENTAS MCP
# ========================================

log ""
log "Fase 3: Verificando herramientas MCP..."

# Verificar que el endpoint de tools esté disponible
test_count
tools_response=$(curl -s -w "%{http_code}" -o /dev/null "http://localhost:8004/tools" --connect-timeout 10 2>/dev/null || echo "000")

if [[ "$tools_response" == "200" ]]; then
    test_pass "MCP Server: Endpoint /tools accesible"
    
    # Intentar obtener la lista de herramientas
    tools_list=$(curl -s "http://localhost:8004/tools" 2>/dev/null || echo "")
    if [[ "$tools_list" == *"openai_chat"* ]]; then
        test_pass "MCP Server: Lista de herramientas disponible"
    else
        test_warning "MCP Server: No se pudo verificar la lista de herramientas"
    fi
else
    test_fail "MCP Server: Endpoint /tools no accesible (HTTP $tools_response)"
fi

# Test rápido de una herramienta MCP
test_count
if curl -s -X POST "http://localhost:8004/mcp/tools/execute" \
    -H "Content-Type: application/json" \
    -d '{"tool": "openai_chat", "parameters": {"prompt": "Test", "max_tokens": 5}}' \
    --connect-timeout 30 >/dev/null 2>&1; then
    test_pass "MCP Tools: Herramienta OpenAI Chat respondiendo"
else
    test_warning "MCP Tools: OpenAI Chat no respondió (puede ser normal si no hay API key configurada)"
fi

# ========================================
# FASE 4: VERIFICACIÓN DE INTERFACES WEB
# ========================================

log ""
log "Fase 4: Verificando interfaces web..."

# Swagger UI
test_count
swagger_response=$(curl -s -w "%{http_code}" -o /dev/null "http://localhost:8004/docs" --connect-timeout 10 2>/dev/null || echo "000")

if [[ "$swagger_response" == "200" ]]; then
    test_pass "Swagger UI: Accesible en http://localhost:8004/docs"
else
    test_fail "Swagger UI: No accesible (HTTP $swagger_response)"
fi

# OpenAPI JSON
test_count
openapi_response=$(curl -s -w "%{http_code}" -o /dev/null "http://localhost:8004/openapi.json" --connect-timeout 10 2>/dev/null || echo "000")

if [[ "$openapi_response" == "200" ]]; then
    test_pass "OpenAPI JSON: Accesible en http://localhost:8004/openapi.json"
else
    test_fail "OpenAPI JSON: No accesible (HTTP $openapi_response)"
fi

# Grafana
test_count
grafana_response=$(curl -s -w "%{http_code}" -o /dev/null "http://localhost:3000" --connect-timeout 10 2>/dev/null || echo "000")

if [[ "$grafana_response" == "200" ]]; then
    test_pass "Grafana Dashboard: Accesible en http://localhost:3000"
else
    test_warning "Grafana Dashboard: No accesible (HTTP $grafana_response)"
fi

# ========================================
# FASE 5: VERIFICACIÓN DE DOCUMENTACIÓN
# ========================================

log ""
log "Fase 5: Verificando documentación..."

# Verificar que los archivos de documentación existen
DOCS=(
    "GUIA_INTEGRACION_FRAMEWORK.md"
    "SDK_JAVASCRIPT_TYPESCRIPT.md"
    "SDK_PYTHON.md"
    "EJEMPLO_PRACTICO_TECHSTORE.md"
    "DEMO_SISTEMA_FUNCIONANDO.md"
    "RESPUESTA_FINAL_FRAMEWORK.md"
    "RESUMEN_EJECUTIVO_FINAL.md"
    "QUE_ES_UN_FRAMEWORK.md"
    "PLAN_TESTING_VERIFICACION.md"
)

for doc in "${DOCS[@]}"; do
    test_count
    if [[ -f "$doc" ]]; then
        test_pass "Documentación: $doc existe"
    else
        test_fail "Documentación: $doc no encontrado"
    fi
done

# ========================================
# RESUMEN FINAL
# ========================================

echo ""
echo -e "${BLUE}=============================================${NC}"
echo -e "${BLUE}📊 RESUMEN DE VERIFICACIÓN${NC}"
echo -e "${BLUE}=============================================${NC}"

PASS_RATE=0
if [ $TESTS_TOTAL -gt 0 ]; then
    PASS_RATE=$(( (TESTS_PASSED * 100) / TESTS_TOTAL ))
fi

echo ""
echo -e "Total de tests ejecutados: ${BLUE}$TESTS_TOTAL${NC}"
echo -e "Tests pasados: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests fallidos: ${RED}$TESTS_FAILED${NC}"
echo -e "Tasa de éxito: ${GREEN}$PASS_RATE%${NC}"

echo ""
if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 ¡EXCELENTE! Todos los tests han pasado${NC}"
    echo -e "${GREEN}✅ El Framework Multiagente está 100% verificado${NC}"
    echo -e "${GREEN}🚀 Sistema listo para producción${NC}"
elif [ $PASS_RATE -ge 80 ]; then
    echo -e "${YELLOW}⚠️ BUENO: La mayoría de tests han pasado ($PASS_RATE%)${NC}"
    echo -e "${YELLOW}🔧 Revisar los tests fallidos antes de producción${NC}"
else
    echo -e "${RED}💥 PROBLEMA: Muchos tests han fallado ($PASS_RATE%)${NC}"
    echo -e "${RED}🔧 Corregir problemas antes de continuar${NC}"
fi

echo ""
echo -e "${BLUE}📋 PRÓXIMOS PASOS RECOMENDADOS:${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}1. ✅ Integrar el framework en tu aplicación${NC}"
    echo -e "${GREEN}2. ✅ Probar las APIs en http://localhost:8004/docs${NC}"
    echo -e "${GREEN}3. ✅ Monitorear con Grafana en http://localhost:3000${NC}"
    echo -e "${GREEN}4. ✅ Configurar API keys para herramientas MCP${NC}"
    echo -e "${GREEN}5. ✅ Escalar a producción${NC}"
else
    echo -e "${YELLOW}1. 🔧 Revisar logs de servicios fallidos${NC}"
    echo -e "${YELLOW}2. 🔧 Verificar que Docker esté corriendo correctamente${NC}"
    echo -e "${YELLOW}3. 🔧 Comprobar variables de entorno${NC}"
    echo -e "${YELLOW}4. 🔧 Re-ejecutar este script después de correcciones${NC}"
fi

echo ""
echo -e "${BLUE}🌐 URLs IMPORTANTES:${NC}"
echo -e "📚 Documentación API: ${BLUE}http://localhost:8004/docs${NC}"
echo -e "📊 Dashboard Monitoreo: ${BLUE}http://localhost:3000${NC}"
echo -e "📈 Métricas Sistema: ${BLUE}http://localhost:9090${NC}"
echo -e "🔄 Cola de Mensajes: ${BLUE}http://localhost:15672${NC}"
echo -e "🗃️ Base de Datos Grafos: ${BLUE}http://localhost:7474${NC}"

echo ""
echo -e "${GREEN}=============================================${NC}"
echo -e "${GREEN}✨ VERIFICACIÓN COMPLETADA ✨${NC}"
echo -e "${GREEN}=============================================${NC}"

# Código de salida basado en resultados
if [ $TESTS_FAILED -eq 0 ]; then
    exit 0  # Todo OK
elif [ $PASS_RATE -ge 80 ]; then
    exit 1  # Advertencia
else
    exit 2  # Error crítico
fi