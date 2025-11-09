#!/usr/bin/env python3
"""
Script de Automatización para Asignación Dinámica de Puertos
Framework Silhouette V4.0 - Implementación Práctica

Autor: MiniMax Agent
Fecha: 2025-11-09
"""

import os
import sys
import yaml
import json
import subprocess
import time
import re
import socket
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class PortInfo:
    """Información de puerto asignado"""
    service_name: str
    container_port: int
    host_port: int
    protocol: str = "tcp"

class SilhouetteDynamicPortManager:
    """
    Gestor de puertos dinámicos para Framework Silhouette V4.0
    Implementa service discovery y asignación automática
    """
    
    def __init__(self, compose_file: str = "docker-compose.yml"):
        self.compose_file = compose_file
        self.docker_network = "silhouette-network"
        self.assigned_ports = {}
        self.used_host_ports = set()
        
    def get_running_containers(self) -> Dict[str, str]:
        """Obtiene contenedores en ejecución y sus puertos"""
        try:
            result = subprocess.run([
                'docker', 'ps', '--format', 
                '{{.Name}}\t{{.Ports}}\t{{.Status}}'
            ], capture_output=True, text=True)
            
            containers = {}
            for line in result.stdout.strip().split('\n'):
                if line and '\t' in line:
                    parts = line.split('\t')
                    if len(parts) >= 3:
                        name, ports, status = parts[0], parts[1], parts[2]
                        if 'Up' in status:
                            containers[name] = ports
            return containers
        except Exception as e:
            print(f"Error obteniendo contenedores: {e}")
            return {}
    
    def get_host_system_ports(self) -> set:
        """Obtiene puertos ya usados en el sistema host"""
        used_ports = set()
        
        # Puertos de Docker
        docker_containers = self.get_running_containers()
        for ports in docker_containers.values():
            # Extrae puertos externos (formato: 0.0.0.0:PORT->)
            matches = re.findall(r':(\d+)->', ports)
            for match in matches:
                used_ports.add(int(match))
        
        # Puertos del sistema (bind excluding ephemeral)
        try:
            result = subprocess.run([
                'ss', '-tuln'
            ], capture_output=True, text=True)
            
            for line in result.stdout.split('\n'):
                if 'LISTEN' in line:
                    # Extrae puertos de líneas LISTEN
                    match = re.search(r':(\d+)\s', line)
                    if match:
                        port = int(match.group(1))
                        # Solo puertos >= 1024 (no privileged)
                        if port >= 1024:
                            used_ports.add(port)
        except:
            pass  # ss no disponible, continuar con Docker
            
        return used_ports
    
    def check_port_available(self, port: int) -> bool:
        """Verifica si un puerto está disponible"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                return result != 0
        except:
            return True  # Asumir disponible si no se puede verificar
    
    def find_available_port(self, preferred: Optional[int] = None) -> int:
        """
        Encuentra un puerto disponible en el sistema
        
        Args:
            preferred: Puerto preferido a intentar primero
            
        Returns:
            int: Puerto disponible encontrado
        """
        used_ports = self.get_host_system_ports()
        
        # Intentar puerto preferido primero
        if preferred and preferred not in used_ports and self.check_port_available(preferred):
            return preferred
        
        # Rango dinámico: 32768-65535 (rango de Docker ephemeral)
        start_port = 32768
        end_port = 65535
        
        # Puerto alterno para puertos conocidos del framework
        alternate_ports = [8000, 8001, 8080, 3000, 5000, 9000, 5432, 6379, 9090, 8500]
        
        # Intentar puertos conocidos primero (si están disponibles)
        for port in alternate_ports:
            if port not in used_ports and self.check_port_available(port):
                return port
        
        # Buscar en rango dinámico
        for port in range(start_port, end_port):
            if port not in used_ports and self.check_port_available(port):
                return port
        
        raise RuntimeError(f"No hay puertos disponibles en el rango {start_port}-{end_port}")
    
    def parse_compose_ports(self, port_config: List) -> List[PortInfo]:
        """Parsea configuración de puertos de docker-compose"""
        port_infos = []
        
        for port_mapping in port_config:
            if isinstance(port_mapping, str):
                # Formato: "host:container" o "container"
                if ':' in port_mapping:
                    host_port, container_port = port_mapping.split(':', 1)
                    if host_port == container_port:
                        # Puerto dinámico para ambos
                        container_port = int(container_port)
                        host_port = self.find_available_port(container_port)
                    else:
                        # Puerto fijo específico
                        host_port = int(host_port)
                        container_port = int(container_port)
                else:
                    # Solo puerto del contenedor - generar dinámico
                    container_port = int(port_mapping)
                    host_port = self.find_available_port(container_port)
                
                port_infos.append(PortInfo(
                    service_name="unknown",
                    container_port=container_port,
                    host_port=host_port
                ))
            elif isinstance(port_mapping, dict):
                # Formato con target/published
                target = port_mapping.get('target', port_mapping.get('container_port'))
                published = port_mapping.get('published', port_mapping.get('host_port'))
                
                if published and target:
                    port_infos.append(PortInfo(
                        service_name="unknown",
                        container_port=int(target),
                        host_port=int(published)
                    ))
                elif target:
                    port_infos.append(PortInfo(
                        service_name="unknown",
                        container_port=int(target),
                        host_port=self.find_available_port(int(target))
                    ))
        
        return port_infos
    
    def create_dynamic_compose_file(self) -> str:
        """Crea versión dinámica del docker-compose.yml"""
        try:
            with open(self.compose_file, 'r') as f:
                config = yaml.safe_load(f)
        except Exception as e:
            print(f"Error cargando {self.compose_file}: {e}")
            return None
        
        dynamic_config = config.copy()
        dynamic_ports = {}
        
        for service_name, service_config in config.get('services', {}).items():
            if 'ports' in service_config and service_config['ports']:
                port_infos = self.parse_compose_ports(service_config['ports'])
                
                if port_infos:
                    new_ports = []
                    for port_info in port_infos:
                        # Asignar puerto dinámico
                        available_port = self.find_available_port(port_info.container_port)
                        new_ports.append(f"{available_port}:{port_info.container_port}")
                        dynamic_ports[service_name] = available_port
                        
                        print(f"🔗 {service_name}:{port_info.container_port} → Host:{available_port}")
                    
                    dynamic_config['services'][service_name]['ports'] = new_ports
        
        # Agregar labels para Traefik auto-discovery
        if 'services' in dynamic_config:
            for service_name in dynamic_ports.keys():
                if 'labels' not in dynamic_config['services'][service_name]:
                    dynamic_config['services'][service_name]['labels'] = []
                elif isinstance(dynamic_config['services'][service_name]['labels'], list):
                    dynamic_config['services'][service_name]['labels'].extend([
                        "traefik.enable=true",
                        f"traefik.http.routers.{service_name}.rule=Host(`{service_name}.localhost`)",
                        f"traefik.http.services.{service_name}.loadbalancer.server.port=8080"
                    ])
        
        # Guardar archivo dinámico
        dynamic_filename = self.compose_file.replace('.yml', '.dynamic.yml')
        with open(dynamic_filename, 'w') as f:
            yaml.dump(dynamic_config, f, default_flow_style=False, sort_keys=False)
        
        return dynamic_filename, dynamic_ports
    
    def create_traefik_config(self) -> str:
        """Crea configuración de Traefik para reverse proxy dinámico"""
        traefik_config = """
# Traefik Configuration for Silhouette V4.0 Dynamic Ports
api:
  dashboard: true
  insecure: true

entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entrypoint:
          to: websecure
          scheme: https
  websecure:
    address: ":443"

providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false
    network: silhouette-network
  file:
    filename: /etc/traefik/dynamic.yml
    watch: true

log:
  level: INFO

accessLog: {}

metrics:
  prometheus:
    addEntryPointsLabels: true
    addServicesLabels: true

# Middleware para headers de seguridad
http:
  middlewares:
    security-headers:
      headers:
        accessControlAllowMethods:
          - GET
          - POST
          - PUT
          - DELETE
        accessControlMaxAge: 100
        hostsProxyHeaders:
          - "X-Forwarded-Host"
        referrerPolicy: "same-origin"
        stsSeconds: 63072000
        stsIncludeSubdomains: true
        stsPreload: true
    redirect-to-https:
      redirectScheme:
        scheme: https
        permanent: true
        port: "443"

# Rutas dinámicas para servicios
tcp:
  routers:
    silhouette-tcp:
      rule: "HostSNI(`*`)"
      service: "silhouette-service"
  services:
    silhouette-service:
      loadbalancer:
        servers:
          - address: "silhouette-framework:8080"
"""
        
        with open('traefik.yml', 'w') as f:
            f.write(traefik_config)
        
        return 'traefik.yml'
    
    def create_consul_config(self) -> str:
        """Crea configuración de Consul para service discovery"""
        consul_config = """
{
  "datacenter": "silhouette-v4",
  "data_dir": "/consul/data",
  "log_level": "INFO",
  "server": true,
  "bootstrap_expect": 1,
  "bind_addr": "0.0.0.0",
  "client_addr": "0.0.0.0",
  "ui_config": {
    "enabled": true
  },
  "ports": {
    "dns": 8600,
    "http": 8500,
    "serf_lan": 8301,
    "serf_wan": 8302,
    "server": 8300
  },
  "connect": {
    "enabled": true
  },
  "telemetry": {
    "prometheus_retention_time": "30s"
  }
}
"""
        
        os.makedirs('consul', exist_ok=True)
        with open('consul/config.json', 'w') as f:
            f.write(consul_config)
        
        return 'consul/config.json'
    
    def generate_health_check_script(self) -> str:
        """Genera script de health check para todos los servicios"""
        script_content = """#!/bin/bash
# Health Check Script for Silhouette V4.0 Dynamic Services

echo "🏥 Silhouette V4.0 - Health Check Report"
echo "======================================"
echo "Timestamp: $(date)"
echo ""

# Function to check HTTP service
check_http_service() {
    local service_name=$1
    local url=$2
    local expected_status=${3:-200}
    
    echo -n "Checking $service_name... "
    
    if curl -f -s -o /dev/null -w "%{http_code}" "$url" | grep -q "$expected_status"; then
        echo "✅ HEALTHY"
        return 0
    else
        echo "❌ UNHEALTHY"
        return 1
    fi
}

# Function to check TCP service
check_tcp_service() {
    local service_name=$1
    local host=$2
    local port=$3
    
    echo -n "Checking $service_name... "
    
    if timeout 5 bash -c "</dev/tcp/$host/$port" 2>/dev/null; then
        echo "✅ HEALTHY"
        return 0
    else
        echo "❌ UNHEALTHY"
        return 1
    fi
}

# Check Docker containers
echo "📦 Container Status:"
docker ps --format "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}" | grep -E "(Name|silhouette)"

echo ""
echo "🌐 Service Health Checks:"

# Check Core Services
check_http_service "Consul UI" "http://localhost:8500"
check_tcp_service "Traefik Dashboard" "localhost" "8080"
check_http_service "Prometheus" "http://localhost:9090/-/healthy"

# Check Silhouette Framework (dynamic port)
SILHOUETTE_PORT=$(docker port silhouette-framework 8080 2>/dev/null | cut -d: -f2)
if [ ! -z "$SILHOUETTE_PORT" ]; then
    check_http_service "Silhouette Framework" "http://localhost:$SILHOUETTE_PORT/health"
else
    echo "❌ Silhouette Framework: Port not found"
fi

# Check Database Services
REDIS_PORT=$(docker port silhouette-redis 6379 2>/dev/null | cut -d: -f2)
if [ ! -z "$REDIS_PORT" ]; then
    check_tcp_service "Redis" "localhost" "$REDIS_PORT"
else
    echo "❌ Redis: Port not found"
fi

POSTGRES_PORT=$(docker port silhouette-postgres 5432 2>/dev/null | cut -d: -f2)
if [ ! -z "$POSTGRES_PORT" ]; then
    check_tcp_service "PostgreSQL" "localhost" "$POSTGRES_PORT"
else
    echo "❌ PostgreSQL: Port not found"
fi

echo ""
echo "📊 Port Mapping Summary:"
docker ps --format "table {{.Names}}\\t{{.Ports}}" | grep silhouette

echo ""
echo "🔍 Consul Service Registry:"
curl -s "http://localhost:8500/v1/catalog/services" | jq -r 'to_entries[] | "\(.key): \(.value | join(", "))"' 2>/dev/null || echo "Consul not accessible"

echo ""
echo "✅ Health check completed"
"""
        
        with open('health_check.sh', 'w') as f:
            f.write(script_content)
        
        os.chmod('health_check.sh', 0o755)
        return 'health_check.sh'
    
    def create_deployment_script(self) -> str:
        """Crea script principal de deployment dinámico"""
        script_content = """#!/bin/bash
# Silhouette V4.0 Dynamic Port Deployment Script
# Autor: MiniMax Agent

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="docker-compose.yml"
DYNAMIC_COMPOSE_FILE="docker-compose.dynamic.yml"
ENV_FILE=".env.dynamic"

echo "🚀 Silhouette V4.0 - Dynamic Port Deployment"
echo "=============================================="

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
BLUE='\\033[0;34m'
NC='\\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    if ! command -v curl &> /dev/null; then
        print_error "curl is not installed"
        exit 1
    fi
    
    print_success "All prerequisites satisfied"
}

# Create necessary directories
setup_directories() {
    print_status "Setting up directories..."
    
    mkdir -p data/{postgres,redis,prometheus,grafana,consul}
    mkdir -p logs
    mkdir -p backups
    
    print_success "Directories created"
}

# Generate dynamic configuration
generate_dynamic_config() {
    print_status "Generating dynamic port configuration..."
    
    if [ -f "port_manager.py" ]; then
        python3 port_manager.py setup
    else
        print_error "port_manager.py not found"
        exit 1
    fi
    
    if [ -f "$DYNAMIC_COMPOSE_FILE" ]; then
        print_success "Dynamic compose file created: $DYNAMIC_COMPOSE_FILE"
    else
        print_error "Failed to create dynamic compose file"
        exit 1
    fi
}

# Start services
start_services() {
    print_status "Starting Silhouette V4.0 services..."
    
    # Stop any existing services
    docker compose -f "$DYNAMIC_COMPOSE_FILE" --env-file "$ENV_FILE" down 2>/dev/null || true
    
    # Start with new configuration
    docker compose -f "$DYNAMIC_COMPOSE_FILE" --env-file "$ENV_FILE" up -d
    
    print_success "Services started with dynamic ports"
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        print_status "Attempt $attempt/$max_attempts"
        
        if curl -f -s http://localhost:8500/v1/status/leader > /dev/null 2>&1; then
            print_success "Consul is ready"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            print_error "Services failed to start within timeout"
            docker compose -f "$DYNAMIC_COMPOSE_FILE" logs
            exit 1
        fi
        
        sleep 5
        ((attempt++))
    done
}

# Display service information
show_service_info() {
    print_status "Service Information:"
    echo ""
    
    # Show running containers
    echo "📦 Running Containers:"
    docker ps --format "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}" | grep silhouette
    echo ""
    
    # Show port mappings
    echo "🔗 Port Mappings:"
    docker ps --format "table {{.Names}}\\t{{.Ports}}" | grep silhouette
    echo ""
    
    # Show service discovery info
    echo "🔍 Service Discovery (Consul):"
    curl -s "http://localhost:8500/v1/catalog/services" | jq -r 'to_entries[] | "  - \(.key): http://localhost:\(.value[0].ServicePort // "N/A")"' 2>/dev/null || echo "  Consul not accessible"
    echo ""
    
    # Show Traefik dashboard
    TRAEFIK_PORT=$(docker port silhouette-traefik 8080 2>/dev/null | cut -d: -f2 || echo "N/A")
    echo "🌐 Access Points:"
    echo "  - Traefik Dashboard: http://localhost:$TRAEFIK_PORT"
    echo "  - Consul UI: http://localhost:8500"
    echo "  - Framework: http://silhouette.localhost"
}

# Health check
run_health_check() {
    print_status "Running health checks..."
    
    if [ -f "health_check.sh" ]; then
        ./health_check.sh
    else
        print_warning "health_check.sh not found"
    fi
}

# Main execution
main() {
    echo "Starting deployment at $(date)"
    
    check_prerequisites
    setup_directories
    generate_dynamic_config
    start_services
    wait_for_services
    show_service_info
    run_health_check
    
    print_success "🚀 Silhouette V4.0 deployed successfully with dynamic ports!"
    echo ""
    echo "To stop services: docker compose -f $DYNAMIC_COMPOSE_FILE down"
    echo "To view logs: docker compose -f $DYNAMIC_COMPOSE_FILE logs -f"
    echo "To check status: ./health_check.sh"
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "stop")
        print_status "Stopping services..."
        docker compose -f "$DYNAMIC_COMPOSE_FILE" down
        print_success "Services stopped"
        ;;
    "restart")
        print_status "Restarting services..."
        docker compose -f "$DYNAMIC_COMPOSE_FILE" restart
        print_success "Services restarted"
        ;;
    "logs")
        docker compose -f "$DYNAMIC_COMPOSE_FILE" logs -f "${2:-}"
        ;;
    "status")
        show_service_info
        ;;
    "health")
        run_health_check
        ;;
    *)
        echo "Usage: $0 {deploy|stop|restart|logs|status|health}"
        echo ""
        echo "Commands:"
        echo "  deploy  - Deploy with dynamic ports (default)"
        echo "  stop    - Stop all services"
        echo "  restart - Restart all services"
        echo "  logs    - Show logs (optional service name)"
        echo "  status  - Show service status and port mappings"
        echo "  health  - Run health checks"
        exit 1
        ;;
esac
"""
        
        with open('deploy_dynamic.sh', 'w') as f:
            f.write(script_content)
        
        os.chmod('deploy_dynamic.sh', 0o755)
        return 'deploy_dynamic.sh'
    
    def setup_complete_environment(self):
        """Configura el entorno completo con todos los archivos necesarios"""
        print("🏗️  Configurando entorno completo de puertos dinámicos...")
        
        # 1. Crear docker-compose dinámico
        compose_file, ports = self.create_dynamic_compose_file()
        if not compose_file:
            return False
        
        # 2. Crear configuraciones adicionales
        traefik_config = self.create_traefik_config()
        consul_config = self.create_consul_config()
        health_script = self.generate_health_check_script()
        deploy_script = self.create_deployment_script()
        
        # 3. Crear archivo de entorno
        env_content = f"""# Silhouette V4.0 Dynamic Environment Configuration
# Generated automatically on {time.strftime('%Y-%m-%d %H:%M:%S')}

# Framework Configuration
FRAMEWORK_ENV=production
FRAMEWORK_VERSION=4.0.0
DYNAMIC_PORTS=true

# Service Discovery
CONSUL_URL=http://consul:8500
CONSUL_DC=silhouette-v4

# Traefik Configuration
TRAEFIK_LOG_LEVEL=INFO
TRAEFIK_API_INSECURE=true

# Database Configuration
POSTGRES_DB=silhouette
POSTGRES_USER=silhouette
POSTGRES_PASSWORD=silhouette_secure_2025
REDIS_PASSWORD=silhouette_redis_2025

# Monitoring
PROMETHEUS_RETENTION=200h
GRAFANA_ADMIN_PASSWORD=silhouette_admin_2025

# Network Configuration
DOCKER_NETWORK=silhouette-network

# Assigned Dynamic Ports
"""
        
        for service, port in ports.items():
            env_content += f"{service.upper()}_PORT={port}\n"
        
        with open('.env.dynamic', 'w') as f:
            f.write(env_content)
        
        # 4. Mostrar resumen
        print("\\n" + "="*60)
        print("✅ ENTORNO DINÁMICO CONFIGURADO EXITOSAMENTE")
        print("="*60)
        print(f"📁 Archivos creados:")
        print(f"   - {compose_file}")
        print(f"   - {traefik_config}")
        print(f"   - {consul_config}")
        print(f"   - {health_script}")
        print(f"   - {deploy_script}")
        print(f"   - .env.dynamic")
        print()
        print(f"🔗 Puertos dinámicos asignados:")
        for service, port in ports.items():
            print(f"   - {service}:{8080 if 'silhouette' in service else 'dynamic'} → Host:{port}")
        print()
        print("🚀 Para iniciar el entorno:")
        print("   ./deploy_dynamic.sh deploy")
        print()
        print("📋 Comandos disponibles:")
        print("   ./deploy_dynamic.sh deploy  - Desplegar con puertos dinámicos")
        print("   ./deploy_dynamic.sh status  - Ver estado de servicios")
        print("   ./deploy_dynamic.sh health  - Verificar salud")
        print("   ./deploy_dynamic.sh stop    - Detener servicios")
        print("="*60)
        
        return True

def main():
    """Función principal del script"""
    if len(sys.argv) < 2:
        print("""
🏗️  Silhouette V4.0 - Dynamic Port Manager

Uso: python3 port_manager.py <comando>

Comandos disponibles:
  setup    - Configurar entorno completo con puertos dinámicos
  ports    - Mostrar puertos actualmente en uso
  health   - Verificar salud de servicios
  info     - Información del sistema
  help     - Mostrar esta ayuda

Ejemplos:
  python3 port_manager.py setup    # Configurar entorno dinámico
  python3 port_manager.py ports    # Ver puertos en uso
  python3 port_manager.py health   # Verificar servicios
        """)
        return
    
    manager = SilhouetteDynamicPortManager()
    command = sys.argv[1]
    
    if command == "setup":
        success = manager.setup_complete_environment()
        if success:
            print("🎉 Configuración completada. Usa './deploy_dynamic.sh deploy' para iniciar.")
        else:
            print("❌ Error en la configuración.")
            sys.exit(1)
            
    elif command == "ports":
        containers = manager.get_running_containers()
        print("📊 Puertos actualmente en uso por Docker:")
        for name, ports in containers.items():
            print(f"  {name}: {ports}")
            
    elif command == "health":
        script = manager.generate_health_check_script()
        subprocess.run(['bash', script])
        
    elif command == "info":
        print("🔍 Información del sistema:")
        used_ports = manager.get_host_system_ports()
        print(f"  Puertos en uso: {len(used_ports)}")
        print(f"  Red Docker: {manager.docker_network}")
        print(f"  Archivo compose: {manager.compose_file}")
        
    elif command == "help":
        main()  # Mostrar ayuda
        
    else:
        print(f"❌ Comando desconocido: {command}")
        print("Usa 'python3 port_manager.py help' para ver comandos disponibles.")
        sys.exit(1)

if __name__ == "__main__":
    main()