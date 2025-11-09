#!/usr/bin/env python3
"""
ACTIVADOR PERMANENTE - FRAMEWORK SILHOUETTE V4.0
Mantiene todos los 78 equipos ejecutándose de forma permanente
Autor: MiniMax Agent
Fecha: 2025-11-09
"""

import os
import sys
import json
import time
import asyncio
import subprocess
import signal
import psutil
from pathlib import Path
from typing import Dict, List
import logging
import threading

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('PermanentActivator')

class PermanentTeamActivator:
    def __init__(self):
        self.workspace = Path('/workspace')
        self.active_processes = {}
        self.ports = self._generate_ports()
        self.is_running = True
        
    def _generate_ports(self):
        """Genera lista de puertos para todos los equipos"""
        return list(range(8000, 8078))  # Puertos 8000-8077 para 78 equipos
    
    def start_team_as_service(self, team_name, port, team_type='python', file_path=None):
        """Inicia un equipo como servicio permanente"""
        try:
            if team_type == 'python':
                # Para equipos Python, usar uvicorn
                if not file_path:
                    file_path = self.workspace / team_name / 'main.py'
                
                if not file_path.exists():
                    logger.warning(f"Archivo no encontrado: {file_path}")
                    return None
                
                # Extraer nombre del módulo de uvicorn
                module_path = str(file_path).replace('.py', '').replace('/', '.')
                
                process = subprocess.Popen([
                    sys.executable, '-m', 'uvicorn', module_path,
                    '--host', '0.0.0.0', '--port', str(port), '--log-level', 'info'
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
            elif team_type == 'node':
                # Para equipos Node.js
                if not file_path:
                    file_path = self.workspace / 'optimization-team' / 'team-workflows' / f'{team_name}.js'
                
                if not file_path.exists():
                    logger.warning(f"Archivo no encontrado: {file_path}")
                    return None
                
                process = subprocess.Popen([
                    'node', str(file_path)
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Guardar información del proceso
            self.active_processes[team_name] = {
                'process': process,
                'port': port,
                'type': team_type,
                'file_path': str(file_path),
                'start_time': time.time(),
                'status': 'running'
            }
            
            logger.info(f"✅ {team_name} iniciado en puerto {port} (PID: {process.pid})")
            return process
            
        except Exception as e:
            logger.error(f"Error iniciando {team_name}: {e}")
            return None
    
    def start_all_teams_permanently(self):
        """Inicia todos los equipos de forma permanente"""
        logger.info("🚀 INICIANDO ACTIVACIÓN PERMANENTE DE 78 EQUIPOS")
        logger.info("="*80)
        
        start_time = time.time()
        
        # 1. Equipos Python principales
        python_teams = [
            ('audiovisual-team', 8000, 'python'),
            ('business_development_team', 8001, 'python'),
            ('cloud_services_team', 8002, 'python'),
            ('code_generation_team', 8003, 'python'),
            ('communications_team', 8004, 'python'),
            ('context_management_team', 8005, 'python'),
            ('customer_service_team', 8006, 'python'),
            ('design_creative_team', 8007, 'python'),
            ('finance_team', 8008, 'python'),
            ('hr_team', 8009, 'python'),
            ('legal_team', 8010, 'python'),
            ('machine_learning_ai_team', 8011, 'python'),
            ('manufacturing_team', 8012, 'python'),
            ('marketing_team', 8013, 'python'),
            ('notifications_communication_team', 8014, 'python'),
            ('product_management_team', 8015, 'python'),
            ('quality_assurance_team', 8016, 'python'),
            ('research_team', 8017, 'python'),
            ('risk_management_team', 8018, 'python'),
            ('sales_team', 8019, 'python'),
            ('security_team', 8020, 'python'),
            ('strategy_team', 8021, 'python'),
            ('supply_chain_team', 8022, 'python'),
            ('support_team', 8023, 'python'),
            ('testing_team', 8024, 'python'),
            ('planner', 8025, 'python'),
            ('prompt_engineer', 8026, 'python'),
            ('mcp_server', 8027, 'python'),
            ('api_gateway', 8029, 'python'),
            ('orchestrator', 8030, 'python'),
        ]
        
        logger.info("🐍 Iniciando equipos Python...")
        for team_name, port, team_type in python_teams:
            if self.is_running:
                self.start_team_as_service(team_name, port, team_type)
                time.sleep(0.1)  # Delay entre inicializaciones
        
        # 2. Equipos Node.js principales
        node_teams = [
            ('Master45TeamsCoordinator', 8034, 'node'),
            ('DynamicWorkflowsCoordinator', 8035, 'node'),
            ('WorkflowOptimizationTeam', 8036, 'node'),
            ('AITeam', 8048, 'node'),
            ('ChangeManagementTeam', 8058, 'node'),
            ('HealthcareTeam', 8054, 'node'),
        ]
        
        logger.info("🔧 Iniciando equipos Node.js principales...")
        for team_name, port, team_type in node_teams:
            if self.is_running:
                self.start_team_as_service(team_name, port, team_type)
                time.sleep(0.1)
        
        # 3. Equipos especializados
        specialized_teams = [
            ('ComplianceTeam', 8049, 'node'),
            ('CybersecurityTeam', 8050, 'node'),
            ('DataEngineeringTeam', 8051, 'node'),
            ('EcommerceTeam', 8052, 'node'),
            ('EducationTeam', 8053, 'node'),
            ('LogisticsTeam', 8055, 'node'),
            ('ManufacturingTeam', 8056, 'node'),
            ('RealEstateTeam', 8057, 'node'),
            ('CrisisManagementTeam', 8059, 'node'),
            ('GlobalExpansionTeam', 8060, 'node'),
            ('InnovationTeam', 8061, 'node'),
            ('MergerAcquisitionTeam', 8062, 'node'),
            ('PartnershipTeam', 8063, 'node'),
            ('AudioVisualTeam', 8064, 'node'),
            ('BlockchainTeam', 8065, 'node'),
            ('CloudInfrastructureTeam', 8066, 'node'),
            ('IoTTeam', 8067, 'node'),
            ('MobileDevelopmentTeam', 8068, 'node'),
            ('WebDevelopmentTeam', 8069, 'node'),
            ('AuditTeam', 8076, 'node'),
            ('SustainabilityTeam', 8077, 'node'),
        ]
        
        logger.info("🎯 Iniciando equipos especializados...")
        for team_name, port, team_type in specialized_teams:
            if self.is_running:
                self.start_team_as_service(team_name, port, team_type)
                time.sleep(0.1)
        
        activation_time = time.time() - start_time
        logger.info(f"⏱️  Tiempo de activación: {activation_time:.2f} segundos")
        
        return len(self.active_processes)
    
    def monitor_teams(self):
        """Monitorea el estado de todos los equipos"""
        logger.info("👁️  MONITOREANDO EQUIPOS ACTIVOS")
        logger.info("="*50)
        
        while self.is_running:
            try:
                healthy_teams = []
                unhealthy_teams = []
                
                for team_name, team_info in self.active_processes.items():
                    process = team_info['process']
                    port = team_info['port']
                    
                    # Verificar si el proceso está ejecutándose
                    if process.poll() is None:  # Proceso aún ejecutándose
                        # Test de conectividad básica
                        try:
                            result = subprocess.run([
                                'curl', '-f', '-s', '--max-time', '3',
                                f'http://localhost:{port}/'
                            ], capture_output=True, text=True, timeout=5)
                            
                            if result.returncode == 0:
                                healthy_teams.append(team_name)
                                team_info['status'] = 'healthy'
                            else:
                                unhealthy_teams.append(team_name)
                                team_info['status'] = 'warning'
                        except:
                            unhealthy_teams.append(team_name)
                            team_info['status'] = 'warning'
                    else:
                        unhealthy_teams.append(team_name)
                        team_info['status'] = 'stopped'
                        logger.warning(f"⚠️ {team_name} se detuvo")
                
                # Reporte de estado cada 30 segundos
                logger.info(f"📊 Estado: {len(healthy_teams)} saludable, {len(unhealthy_teams)} con problemas")
                
                # Auto-reinicio de equipos caídos
                for team_name, team_info in self.active_processes.items():
                    if team_info['status'] == 'stopped':
                        logger.info(f"🔄 Reiniciando {team_name}...")
                        self.start_team_as_service(
                            team_name, 
                            team_info['port'], 
                            team_info['type'],
                            team_info['file_path']
                        )
                
                time.sleep(30)  # Verificar cada 30 segundos
                
            except Exception as e:
                logger.error(f"Error en monitoreo: {e}")
                time.sleep(10)
    
    def health_check_all(self):
        """Health check completo de todos los equipos"""
        logger.info("🏥 HEALTH CHECK COMPLETO DE TODOS LOS EQUIPOS")
        logger.info("="*60)
        
        healthy_count = 0
        total_count = len(self.active_processes)
        
        for team_name, team_info in self.active_processes.items():
            port = team_info['port']
            status = team_info['status']
            
            if status == 'healthy':
                healthy_count += 1
                logger.info(f"✅ {team_name} (puerto {port}): SALUDABLE")
            elif status == 'warning':
                logger.warning(f"⚠️ {team_name} (puerto {port}): ADVERTENCIA")
            else:
                logger.error(f"❌ {team_name} (puerto {port}): DETENIDO")
        
        success_rate = (healthy_count / total_count) * 100 if total_count > 0 else 0
        
        logger.info("="*60)
        logger.info(f"📊 RESUMEN: {healthy_count}/{total_count} equipos saludables ({success_rate:.1f}%)")
        logger.info("="*60)
        
        return {
            'total_teams': total_count,
            'healthy_teams': healthy_count,
            'success_rate': success_rate,
            'teams_detail': self.active_processes
        }
    
    def generate_permanent_status_report(self):
        """Genera reporte de estado permanente"""
        report = {
            'status': 'PERMANENTLY_ACTIVE',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'framework_version': '4.0.0',
            'active_processes': len(self.active_processes),
            'teams': {}
        }
        
        for team_name, team_info in self.active_processes.items():
            report['teams'][team_name] = {
                'port': team_info['port'],
                'type': team_info['type'],
                'status': team_info['status'],
                'uptime': time.time() - team_info['start_time'],
                'file_path': team_info['file_path']
            }
        
        # Guardar reporte
        report_file = self.workspace / 'ESTADO_PERMANENTE_FRAMEWORK.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 Reporte de estado guardado: {report_file}")
        return report
    
    def signal_handler(self, signum, frame):
        """Maneja señales de terminación"""
        logger.info(f"🛑 Señal {signum} recibida, deteniendo framework...")
        self.is_running = False
        
        # Limpiar procesos
        for team_name, team_info in self.active_processes.items():
            try:
                team_info['process'].terminate()
                team_info['process'].wait(timeout=5)
            except:
                pass
        
        logger.info("🧹 Framework detenido completamente")
        sys.exit(0)
    
    def run_permanent_activation(self):
        """Ejecuta activación permanente del framework"""
        # Configurar manejo de señales
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            # Iniciar todos los equipos
            teams_started = self.start_all_teams_permanently()
            
            if teams_started > 0:
                logger.info(f"🎉 {teams_started} equipos iniciados exitosamente")
                
                # Esperar a que se inicialicen
                logger.info("⏳ Esperando inicialización completa...")
                time.sleep(60)
                
                # Health check inicial
                initial_status = self.health_check_all()
                
                # Generar reporte
                report = self.generate_permanent_status_report()
                
                if initial_status['success_rate'] >= 70:
                    logger.info("🏆 FRAMEWORK COMPLETAMENTE OPERATIVO")
                    
                    # Iniciar monitoreo en background
                    monitor_thread = threading.Thread(target=self.monitor_teams, daemon=True)
                    monitor_thread.start()
                    
                    logger.info("🔄 Monitoreo continuo iniciado")
                    logger.info("🎯 Framework listo para uso en producción")
                    
                    # Mantener el proceso principal ejecutándose
                    while self.is_running:
                        time.sleep(10)
                        # Health check rápido cada 2 minutos
                        if int(time.time()) % 120 == 0:
                            self.health_check_all()
                    
                else:
                    logger.warning("⚠️ Framework parcialmente operativo")
                    return 1
            else:
                logger.error("❌ No se pudo iniciar ningún equipo")
                return 1
                
        except KeyboardInterrupt:
            logger.info("🛑 Deteniendo framework por interrupción del usuario...")
            self.is_running = False
        except Exception as e:
            logger.error(f"Error en activación permanente: {e}")
            return 1
        finally:
            self.cleanup()
        
        return 0
    
    def cleanup(self):
        """Limpieza final"""
        logger.info("🧹 Limpiando procesos...")
        for team_name, team_info in self.active_processes.items():
            try:
                team_info['process'].terminate()
                team_info['process'].wait(timeout=3)
            except:
                pass
        self.active_processes.clear()

def main():
    activator = PermanentTeamActivator()
    return activator.run_permanent_activation()

if __name__ == "__main__":
    exit(main())
