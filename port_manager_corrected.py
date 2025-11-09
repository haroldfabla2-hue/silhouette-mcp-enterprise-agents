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
from pathlib import Path
from typing import Dict, List, Optional

class SilhouettePortManager:
    """Gestor de Puertos Dinámicos para Framework Silhouette V4.0"""
    
    def __init__(self, compose_file: str = "docker-compose.dynamic.yml"):
        self.compose_file = compose_file
        self.services = {}
        self.assigned_ports = {}
        
    def load_compose_config(self) -> Dict:
        """Carga configuración de docker-compose"""
        try:
            with open(self.compose_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Error cargando {self.compose_file}: {e}")
            return {}
    
    def get_docker_port_info(self) -> Dict:
        """Obtiene información de puertos actualmente en uso"""
        try:
            result = subprocess.run([
                'docker', 'ps', '--format', 
                '{{.Names}}\t{{.Ports}}'
            ], capture_output=True, text=True)
            
            port_info = {}
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('\t', 1)
                    if len(parts) == 2:
                        name, ports = parts
                        port_info[name] = ports
            return port_info
        except Exception as e:
            print(f"❌ Error obteniendo info de puertos: {e}")
            return {}
    
    def find_available_port(self, preferred: Optional[int] = None) -> int:
        """Encuentra un puerto disponible"""
        used_ports = set()
        
        # Puertos de Docker actuales
        docker_info = self.get_docker_port_info()
        for ports in docker_info.values():
            # Extrae puertos externos (formato: 0.0.0.0:PORT->)
            import re
            matches = re.findall(r':(\d+)->', ports)
            for match in matches:
                used_ports.add(int(match))
        
        # Rango dinámico de Docker: 32768-65535
        start_port = 32768
        end_port = 65535
        
        # Intentar puerto preferido primero
        if preferred:
            if preferred not in used_ports and start_port <= preferred <= end_port:
                return preferred
        
        # Buscar puerto disponible
        for port in range(start_port, end_port):
            if port not in used_ports:
                return port
        
        raise RuntimeError("No hay puertos disponibles en el rango dinámico")
    
    def register_service_consul(self, service_name: str, port: int, health_check: str = None):
        """Registra servicio en Consul"""
        try:
            consul_data = {
                "ID": f"{service_name}-{port}",
                "Name": service_name,
                "Port": port,
                "Address": service_name,
                "Check": {
                    "HTTP": health_check or f"http://{service_name}:{port}/health",
                    "Interval": "30s",
                    "Timeout": "10s"
                } if health_check else None,
                "Tags": ["silhouette-v4", "enterprise", "auto-registered"]
            }
            
            # Registra en Consul
            subprocess.run([
                'curl', '-X', 'PUT',
                f'http://localhost:8500/v1/agent/service/register',
                '-H', 'Content-Type: application/json',
                '-d', json.dumps(consul_data)
            ], check=True)
            
            print(f"✅ Servicio {service_name} registrado en Consul con puerto {port}")
            
        except Exception as e:
            print(f"⚠️ Error registrando {service_name} en Consul: {e}")
    
    def setup_dynamic_environment(self):
        """Configura el entorno con puertos dinámicos"""
        print("🚀 Configurando Framework Silhouette V4.0 con Puertos Dinámicos...")
        
        # Cargar configuración
        config = self.load_compose_config()
        if not config:
            print("❌ No se pudo cargar la configuración")
            return
        
        # Generar archivo .env con puertos dinámicos
        env_vars = {}
        
        for service_name, service_config in config.get('services', {}).items():
            if 'ports' in service_config:
                for i, port_mapping in enumerate(service_config['ports']):
                    if isinstance(port_mapping, str) and not ':' in port_mapping:
                        # Solo puerto del contenedor, generar dinámico
                        try:
                            container_port = int(port_mapping)
                            host_port = self.find_available_port()
                            env_vars[f"{service_name.upper()}_PORT_{i}"] = str(host_port)
                            
                            # Registrar en Consul
                            health_check = f"http://{service_name}:{container_port}/health"
                            self.register_service_consul(service_name, host_port, health_check)
                            
                            print(f"📡 {service_name}:{container_port} → Host:{host_port}")
                        except Exception as e:
                            print(f"⚠️ Error procesando {service_name}:{port_mapping}: {e}")
        
        # Escribir archivo .env
        try:
            with open('.env.dynamic', 'w') as f:
                for key, value in env_vars.items():
                    f.write(f"{key}={value}\n")
            
            print(f"✅ Archivo .env.dynamic generado con {len(env_vars)} variables")
            print("🔧 Para usar: docker compose --env-file .env.dynamic up -d")
        except Exception as e:
            print(f"❌ Error escribiendo .env.dynamic: {e}")
    
    def health_check_all_services(self):
        """Verifica salud de todos los servicios"""
        print("🏥 Verificando salud de servicios...")
        
        services = [
            ("silhouette-consul", "http://localhost:8500/v1/status/leader"),
            ("silhouette-traefik", "http://localhost:8080/ping"),
            ("silhouette-prometheus", "http://localhost:9090/-/healthy")
        ]
        
        for service, health_url in services:
            try:
                result = subprocess.run([
                    'curl', '-f', '-s', health_url
                ], capture_output=True, timeout=10)
                
                if result.returncode == 0:
                    print(f"✅ {service}: Saludable")
                else:
                    print(f"⚠️ {service}: No responde")
                    
            except Exception as e:
                print(f"❌ {service}: Error - {e}")

def main():
    manager = SilhouettePortManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "setup":
            manager.setup_dynamic_environment()
        elif command == "health":
            manager.health_check_all_services()
        elif command == "ports":
            info = manager.get_docker_port_info()
            print("📊 Puertos en uso:")
            for service, ports in info.items():
                print(f"  {service}: {ports}")
        else:
            print("Comandos disponibles: setup, health, ports")
    else:
        print("Silhouette Port Manager V4.0")
        print("Uso: python3 port_manager_corrected.py [setup|health|ports]")

if __name__ == "__main__":
    main()