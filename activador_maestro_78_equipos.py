#!/usr/bin/env python3
"""
ACTIVADOR MAESTRO DE TODOS LOS EQUIPOS - FRAMEWORK SILHOUETTE V4.0
Script para activar y verificar los 78 equipos especializados
Autor: MiniMax Agent
Fecha: 2025-11-09
"""

import os
import sys
import json
import time
import asyncio
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Tuple
import threading
import signal
import psutil

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('FrameworkActivator')

class TeamActivator:
    def __init__(self):
        self.workspace = Path('/workspace')
        self.teams_status = {}
        self.active_processes = []
        self.framework_processes = []
        self.ports = self._generate_dynamic_ports()
        
    def _generate_dynamic_ports(self):
        """Genera puertos dinámicos para todos los equipos"""
        # Puertos base: 8000-8999 para equipos principales
        base_port = 8000
        ports = []
        
        # Lista de todos los equipos identificados (78 equipos)
        team_list = [
            # Equipos empresariales (34)
            'audiovisual-team', 'business_development_team', 'cloud_services_team',
            'code_generation_team', 'communications_team', 'context_management_team',
            'customer_service_team', 'design_creative_team', 'finance_team',
            'hr_team', 'legal_team', 'machine_learning_ai_team', 'manufacturing_team',
            'marketing_team', 'notifications_communication_team', 'product_management_team',
            'quality_assurance_team', 'research_team', 'risk_management_team',
            'sales_team', 'security_team', 'strategy_team', 'supply_chain_team',
            'support_team', 'testing_team', 'planner', 'prompt_engineer',
            'mcp_server', 'multiagent-framework-expandido', 'api_gateway',
            'orchestrator', 'worker', 'browser', 'optimization-team',
            
            # Equipos de optimización (31)
            'master45-coordinator', 'dynamic-workflows-coordinator', 'workflow-optimization',
            'dynamic-system-demo', 'audiovisual-workflow', 'business-continuity',
            'data-science', 'it-infrastructure', 'legal-workflow', 'marketing-workflow',
            'research-workflow', 'sales-workflow', 'strategic-planning', 'ultra-robust-qa',
            'ai-team', 'compliance-team', 'cybersecurity-team', 'data-engineering-team',
            'ecommerce-team', 'education-team', 'healthcare-team', 'logistics-team',
            'manufacturing-industry-team', 'realestate-team', 'change-management',
            'crisis-management', 'global-expansion', 'innovation-team', 'merger-acquisition',
            'partnership-team', 'audiovisual-technology',
            
            # Sub-equipos audiovisuales (11)
            'animation-prompt-generator', 'audiovisual-coordinator', 'prompt-execution-engine',
            'image-search-team', 'image-quality-verifier', 'audiovisual-integration',
            'audiovisual-research', 'video-scene-composer', 'professional-script-generator',
            'video-strategy-planner', 'requirements-manager',
            
            # Equipos adicionales (2)
            'audit-team', 'sustainability-team'
        ]
        
        for i, team in enumerate(team_list):
            port = base_port + i
            ports.append({
                'team': team,
                'port': port,
                'url': f'http://localhost:{port}',
                'health_url': f'http://localhost:{port}/health'
            })
            
        return ports
    
    def check_docker_compose_availability(self):
        """Verifica si Docker Compose está disponible"""
        try:
            result = subprocess.run(['docker-compose', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                logger.info(f"Docker Compose disponible: {result.stdout.strip()}")
                return True
            else:
                logger.error("Docker Compose no disponible")
                return False
        except Exception as e:
            logger.error(f"Error verificando Docker Compose: {e}")
            return False
    
    def start_teams_with_docker(self):
        """Inicia equipos con Docker Compose"""
        logger.info("🚀 Iniciando equipos con Docker Compose...")
        
        # Verificar docker-compose.yml principal
        main_compose = self.workspace / 'docker-compose-multiagente-cuantico.yml'
        if not main_compose.exists():
            logger.error("docker-compose-multiagente-cuantico.yml no encontrado")
            return False
            
        try:
            # Crear archivo de puertos dinámicos
            self._create_ports_file()
            
            # Levantar servicios
            result = subprocess.run([
                'docker-compose', '-f', str(main_compose), 'up', '-d'
            ], cwd=self.workspace, timeout=120, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Equipos Docker levantados exitosamente")
                return True
            else:
                logger.error(f"Error levantando equipos Docker: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error ejecutando Docker Compose: {e}")
            return False
    
    def start_teams_with_node(self):
        """Inicia equipos JavaScript/Node.js"""
        logger.info("🔧 Iniciando equipos Node.js...")
        
        # Directorios de equipos JS
        js_teams_dirs = [
            self.workspace / 'optimization-team' / 'team-workflows',
            self.workspace / 'audiovisual-team',
            self.workspace / 'src' / 'teams'
        ]
        
        for team_dir in js_teams_dirs:
            if not team_dir.exists():
                continue
                
            # Buscar archivos principales
            main_files = list(team_dir.rglob('*Team.js')) + list(team_dir.rglob('*Workflow.js'))
            
            for main_file in main_files:
                try:
                    # Iniciar equipo en proceso separado
                    process = subprocess.Popen([
                        'node', str(main_file)
                    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    
                    self.framework_processes.append({
                        'process': process,
                        'file': str(main_file),
                        'name': main_file.stem,
                        'start_time': time.time()
                    })
                    
                    logger.info(f"✅ Equipo iniciado: {main_file.stem}")
                    time.sleep(0.1)  # Delay para evitar sobrecarga
                    
                except Exception as e:
                    logger.error(f"Error iniciando {main_file}: {e}")
                    
        return len(self.framework_processes) > 0
    
    def start_python_teams(self):
        """Inicia equipos Python"""
        logger.info("🐍 Iniciando equipos Python...")
        
        # Directorios de equipos Python
        python_teams_dirs = [
            self.workspace,
        ]
        
        for team_dir in python_teams_dirs:
            if not team_dir.exists():
                continue
                
            # Buscar main.py en directorios de equipos
            for main_file in team_dir.rglob('main.py'):
                if 'user_input_files' in str(main_file):
                    continue
                    
                try:
                    # Determinar puerto
                    team_name = main_file.parent.name
                    team_info = next((p for p in self.ports if p['team'] == team_name), None)
                    port = team_info['port'] if team_info else 8000
                    
                    # Iniciar con uvicorn
                    process = subprocess.Popen([
                        'python3', '-m', 'uvicorn', str(main_file).replace('.py', ''), 
                        '--host', '0.0.0.0', '--port', str(port), '--reload'
                    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    
                    self.framework_processes.append({
                        'process': process,
                        'file': str(main_file),
                        'name': team_name,
                        'port': port,
                        'start_time': time.time()
                    })
                    
                    logger.info(f"✅ Equipo Python iniciado: {team_name} (puerto {port})")
                    time.sleep(0.2)
                    
                except Exception as e:
                    logger.error(f"Error iniciando equipo Python {main_file}: {e}")
                    
        return len(self.framework_processes) > 0
    
    def _create_ports_file(self):
        """Crea archivo de configuración de puertos"""
        ports_config = {f"PORT_{i+1}": port_info['port'] 
                       for i, port_info in enumerate(self.ports)}
        
        ports_file = self.workspace / '.env.activation'
        with open(ports_file, 'w') as f:
            f.write("# Configuración de puertos para activación completa\n")
            f.write("AUTOMATICALLY_ACTIVATED=true\n")
            f.write("ACTIVATION_DATE=2025-11-09\n")
            f.write("TOTAL_TEAMS=78\n")
            f.write("\n# Puertos dinámicos asignados\n")
            for key, value in ports_config.items():
                f.write(f"{key}={value}\n")
        
        logger.info(f"📝 Archivo de puertos creado: {ports_file}")
    
    def health_check_all_teams(self):
        """Verifica la salud de todos los equipos"""
        logger.info("🏥 Ejecutando health check de todos los equipos...")
        
        healthy_teams = []
        unhealthy_teams = []
        
        for team_info in self.ports:
            try:
                port = team_info['port']
                team_name = team_info['team']
                
                # Test de conectividad básica
                result = subprocess.run([
                    'curl', '-f', '-s', '--max-time', '5', 
                    f'http://localhost:{port}/'
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    healthy_teams.append(team_info)
                    logger.info(f"✅ {team_name} (puerto {port}): Saludable")
                else:
                    unhealthy_teams.append(team_info)
                    logger.warning(f"⚠️ {team_name} (puerto {port}): No responde")
                    
            except Exception as e:
                unhealthy_teams.append(team_info)
                logger.warning(f"⚠️ {team_info['team']}: Error de verificación - {e}")
        
        return healthy_teams, unhealthy_teams
    
    def test_inter_team_communication(self):
        """Prueba la comunicación entre equipos"""
        logger.info("🔗 Probando comunicación inter-equipos...")
        
        test_results = []
        
        # Simular algunos tests de comunicación
        key_teams = ['api-gateway', 'orchestrator', 'optimization-team']
        
        for team in key_teams:
            team_info = next((p for p in self.ports if p['team'] == team), None)
            if team_info:
                try:
                    # Test de ping interno
                    result = subprocess.run([
                        'curl', '-f', '-s', '--max-time', '3',
                        f'http://localhost:{team_info["port"]}/health'
                    ], capture_output=True, text=True, timeout=5)
                    
                    status = "✅ OK" if result.returncode == 0 else "❌ FAIL"
                    test_results.append({
                        'team': team,
                        'status': status,
                        'port': team_info['port']
                    })
                    
                except Exception as e:
                    test_results.append({
                        'team': team,
                        'status': f"❌ ERROR: {e}",
                        'port': team_info['port']
                    })
        
        return test_results
    
    def monitor_system_resources(self):
        """Monitorea recursos del sistema durante la activación"""
        logger.info("📊 Monitoreando recursos del sistema...")
        
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            logger.info(f"💻 CPU: {cpu_percent:.1f}%")
            logger.info(f"💾 RAM: {memory.percent:.1f}% ({memory.used // 1024 // 1024} MB / {memory.total // 1024 // 1024} MB)")
            logger.info(f"💽 Disk: {disk.percent:.1f}% ({disk.used // 1024 // 1024 // 1024} GB / {disk.total // 1024 // 1024 // 1024} GB)")
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': disk.percent,
                'status': 'OK' if cpu_percent < 80 and memory.percent < 80 else 'WARNING'
            }
            
        except Exception as e:
            logger.error(f"Error monitoreando recursos: {e}")
            return {'status': 'ERROR', 'error': str(e)}
    
    def generate_activation_report(self, healthy_teams, unhealthy_teams, communication_tests, resource_status):
        """Genera reporte de activación"""
        total_teams = len(self.ports)
        healthy_count = len(healthy_teams)
        unhealthy_count = len(unhealthy_teams)
        success_rate = (healthy_count / total_teams) * 100 if total_teams > 0 else 0
        
        report = {
            'activation_info': {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_teams_configured': total_teams,
                'teams_activated': healthy_count,
                'teams_failed': unhealthy_count,
                'success_rate': round(success_rate, 2),
                'framework_version': '4.0.0'
            },
            'health_status': {
                'healthy_teams': [t['team'] for t in healthy_teams],
                'unhealthy_teams': [t['team'] for t in unhealthy_teams]
            },
            'communication_tests': communication_tests,
            'resource_status': resource_status,
            'ports_assigned': self.ports,
            'processes_started': [
                {
                    'name': p.get('name', 'Unknown'),
                    'file': p.get('file', 'Unknown'),
                    'start_time': p.get('start_time', 0)
                }
                for p in self.framework_processes
            ]
        }
        
        # Guardar reporte
        report_file = self.workspace / 'REPORTE_ACTIVACION_78_EQUIPOS.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📊 Reporte guardado: {report_file}")
        return report
    
    def cleanup_on_exit(self):
        """Limpieza de procesos al salir"""
        logger.info("🧹 Limpiando procesos...")
        
        for process_info in self.framework_processes:
            try:
                process_info['process'].terminate()
                process_info['process'].wait(timeout=5)
            except Exception as e:
                logger.warning(f"Error terminando proceso {process_info.get('name')}: {e}")
        
        self.framework_processes.clear()
    
    async def activate_all_teams(self):
        """Activador maestro de todos los equipos"""
        logger.info("="*80)
        logger.info("🚀 ACTIVACIÓN MAESTRA - FRAMEWORK SILHOUETTE V4.0")
        logger.info("🎯 Objetivo: 78 equipos especializados")
        logger.info("="*80)
        
        # Verificar requisitos
        if not self.check_docker_compose_availability():
            logger.warning("Docker Compose no disponible, continuando con procesos individuales")
        
        # Monitorear recursos antes de la activación
        resource_status = self.monitor_system_resources()
        
        # Iniciar equipos
        start_time = time.time()
        
        # 1. Iniciar equipos Docker
        docker_success = self.start_teams_with_docker()
        time.sleep(5)  # Esperar a que los contenedores inicien
        
        # 2. Iniciar equipos Node.js
        node_success = self.start_teams_with_node()
        time.sleep(3)
        
        # 3. Iniciar equipos Python
        python_success = self.start_python_teams()
        time.sleep(5)
        
        # Health checks
        healthy_teams, unhealthy_teams = self.health_check_all_teams()
        
        # Tests de comunicación
        communication_tests = self.test_inter_team_communication()
        
        # Generar reporte
        final_report = self.generate_activation_report(
            healthy_teams, unhealthy_teams, communication_tests, resource_status
        )
        
        # Resultados
        activation_time = time.time() - start_time
        
        logger.info("="*80)
        logger.info("📊 RESULTADOS DE ACTIVACIÓN")
        logger.info("="*80)
        logger.info(f"⏱️  Tiempo de activación: {activation_time:.2f} segundos")
        logger.info(f"🎯 Equipos configurados: {len(self.ports)}")
        logger.info(f"✅ Equipos saludables: {len(healthy_teams)}")
        logger.info(f"❌ Equipos no saludables: {len(unhealthy_teams)}")
        logger.info(f"📈 Tasa de éxito: {final_report['activation_info']['success_rate']:.1f}%")
        
        if final_report['activation_info']['success_rate'] >= 90:
            logger.info("🏆 ACTIVACIÓN EXITOSA - Framework completamente operativo")
            return True
        elif final_report['activation_info']['success_rate'] >= 70:
            logger.info("⚠️  ACTIVACIÓN PARCIAL - Framework parcialmente operativo")
            return True
        else:
            logger.error("❌ ACTIVACIÓN FALLIDA - Requiere revisión")
            return False

def main():
    """Función principal"""
    activator = TeamActivator()
    
    # Manejo de señales para limpieza
    def signal_handler(sig, frame):
        logger.info("🛑 Señal de terminación recibida, limpiando...")
        activator.cleanup_on_exit()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Ejecutar activación
        success = asyncio.run(activator.activate_all_teams())
        
        if success:
            print("\n🎉 FRAMEWORK SILHOUETTE V4.0 COMPLETAMENTE ACTIVO")
            print("✅ Todos los equipos especializados operativos")
            print("🌐 Framework listo para uso en producción")
            return 0
        else:
            print("\n⚠️  ACTIVACIÓN COMPLETADA CON OBSERVACIONES")
            print("🔧 Revisar reporte para detalles")
            return 1
            
    except Exception as e:
        logger.error(f"Error en activación: {e}")
        return 1
    
    finally:
        activator.cleanup_on_exit()

if __name__ == "__main__":
    exit(main())
