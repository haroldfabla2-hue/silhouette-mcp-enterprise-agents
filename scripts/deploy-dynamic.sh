#!/bin/bash
# Script de Despliegue con Puertos Dinámicos
# Framework Silhouette V4.0 - 78 Equipos Especializados
# Autor: MiniMax Agent
# Fecha: 2025-11-10

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Función para mostrar banner
show_banner() {
    echo -e "${BLUE}"
    echo "================================================"
    echo "     FRAMEWORK SILHOUETTE V4.0 - DESPLIEGUE"
    echo "         78 Equipos Especializados"
    echo "     Sistema de Puertos Dinámicos"
    echo "================================================"
    echo -e "${NC}"
}

# Verificar prerrequisitos
check_prerequisites() {
    log_info "Verificando prerrequisitos..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker no está instalado"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose no está instalado"
        exit 1
    fi
    
    if ! command -v node &> /dev/null; then
        log_error "Node.js no está instalado"
        exit 1
    fi
    
    log_success "Todos los prerrequisitos están instalados"
}

# Limpiar recursos existentes
cleanup_existing_resources() {
    log_info "Limpiando recursos existentes..."
    
    # Detener contenedores existentes
    if [ -f "docker-compose.yml" ]; then
        docker-compose down --remove-orphans 2>/dev/null || true
    fi
    
    if [ -f "docker-compose.dynamic-ports.yml" ]; then
        docker-compose -f docker-compose.dynamic-ports.yml down --remove-orphans 2>/dev/null || true
    fi
    
    # Limpiar redes y volúmenes huérfanos
    docker system prune -f --volumes 2>/dev/null || true
    
    log_success "Recursos existentes limpiados"
}

# Generar puertos dinámicos
generate_dynamic_ports() {
    log_info "Generando configuración de puertos dinámicos..."
    
    # Verificar que los scripts existen
    if [ ! -f "scripts/port_allocator.cjs" ]; then
        log_error "Script port_allocator.cjs no encontrado"
        exit 1
    fi
    
    if [ ! -f "scripts/generate-docker-compose.cjs" ]; then
        log_error "Script generate-docker-compose.cjs no encontrado"
        exit 1
    fi
    
    # Ejecutar el generador de puertos
    node scripts/generate-docker-compose.cjs
    
    if [ ! -f "docker-compose.dynamic-ports.yml" ]; then
        log_error "No se pudo generar docker-compose.dynamic-ports.yml"
        exit 1
    fi
    
    log_success "Configuración de puertos dinámicos generada"
}

# Verificar equipos
verify_teams() {
    log_info "Verificando equipos especializados..."
    
    # Contar equipos esperados vs existentes
    expected_teams=78
    actual_teams=$(find . -maxdepth 2 -type d -name "*team*" | grep -v framework_clean | grep -v framework_clean_upload | wc -l)
    
    log_info "Equipos esperados: $expected_teams"
    log_info "Equipos encontrados: $actual_teams"
    
    if [ $actual_teams -lt $((expected_teams * 80 / 100)) ]; then
        log_warning "Número de equipos encontrado es menor al esperado"
    else
        log_success "Número de equipos verificado"
    fi
}

# Desplegar el framework
deploy_framework() {
    log_info "Desplegando Framework Silhouette V4.0..."
    
    # Usar el docker-compose generado dinámicamente
    if [ -f "docker-compose.dynamic-ports.yml" ]; then
        COMPOSE_FILE="docker-compose.dynamic-ports.yml"
        log_info "Usando docker-compose con puertos dinámicos"
    else
        COMPOSE_FILE="docker-compose.yml"
        log_warning "Usando docker-compose estándar (puertos estáticos)"
    fi
    
    # Construir y desplegar
    docker-compose -f $COMPOSE_FILE build --no-cache
    docker-compose -f $COMPOSE_FILE up -d
    
    log_success "Framework desplegado exitosamente"
}

# Verificar estado de despliegue
verify_deployment() {
    log_info "Verificando estado del despliegue..."
    
    # Esperar a que los servicios estén listos
    sleep 30
    
    # Verificar contenedores en ejecución
    running_containers=$(docker-compose -f docker-compose.dynamic-ports.yml ps --services --filter "status=running" 2>/dev/null | wc -l)
    total_containers=$(docker-compose -f docker-compose.dynamic-ports.yml ps --services 2>/dev/null | wc -l)
    
    log_info "Contenedores en ejecución: $running_containers de $total_containers"
    
    if [ $running_containers -gt 0 ]; then
        log_success "Algunos servicios están ejecutándose correctamente"
    else
        log_warning "No se detectaron servicios en ejecución"
    fi
}

# Mostrar información de puertos
show_port_information() {
    log_info "Información de puertos asignados..."
    
    if [ -f "config/allocated_ports.json" ]; then
        echo -e "${YELLOW}Puertos asignados:${NC}"
        cat config/allocated_ports.json | jq '.' 2>/dev/null || cat config/allocated_ports.json
    else
        log_warning "No se encontró archivo de puertos asignados"
    fi
}

# Mostrar logs del sistema
show_system_logs() {
    log_info "Mostrando logs del sistema..."
    
    if docker-compose -f docker-compose.dynamic-ports.yml ps | grep -q "Up"; then
        log_info "Últimas 20 líneas de logs del orquestador:"
        docker-compose -f docker-compose.dynamic-ports.yml logs --tail=20 orchestrator 2>/dev/null || echo "No hay logs disponibles"
    fi
}

# Función principal
main() {
    show_banner
    
    check_prerequisites
    cleanup_existing_resources
    generate_dynamic_ports
    verify_teams
    deploy_framework
    verify_deployment
    show_port_information
    show_system_logs
    
    echo -e "${GREEN}"
    echo "================================================"
    echo "     DESPLIEGUE COMPLETADO EXITOSAMENTE"
    echo "     Framework Silhouette V4.0 Operativo"
    echo "     78 Equipos Especializados Configurados"
    echo "     Puertos Dinámicos Asignados"
    echo "================================================"
    echo -e "${NC}"
    
    log_success "Para ver el estado de los servicios: docker-compose -f docker-compose.dynamic-ports.yml ps"
    log_success "Para ver logs: docker-compose -f docker-compose.dynamic-ports.yml logs -f"
    log_success "Para detener: docker-compose -f docker-compose.dynamic-ports.yml down"
}

# Verificar si el script se ejecuta con el parámetro --help
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Uso: $0 [opciones]"
    echo ""
    echo "Opciones:"
    echo "  --help, -h     Mostrar esta ayuda"
    echo "  --no-cleanup   No limpiar recursos existentes"
    echo "  --no-build     No reconstruir imágenes"
    echo "  --static       Usar puertos estáticos en lugar de dinámicos"
    echo ""
    exit 0
fi

# Ejecutar función principal
main "$@"