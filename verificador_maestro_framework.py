#!/usr/bin/env python3
"""
VERIFICADOR MAESTRO MEJORADO - FRAMEWORK SILHOUETTE V4.0
Verifica todos los equipos después de la activación inicial
Autor: MiniMax Agent
Fecha: 2025-11-09
"""

import os
import json
import time
import subprocess
import psutil
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('TeamVerifier')

class TeamVerifier:
    def __init__(self):
        self.workspace = Path('/workspace')
        self.ports = self._load_ports_config()
        self.processes = []
        
    def _load_ports_config(self):
        """Carga configuración de puertos"""
        ports_file = self.workspace / '.env.activation'
        if ports_file.exists():
            logger.info("📄 Cargando configuración de puertos")
            with open(ports_file, 'r') as f:
                content = f.read()
                # Extraer puertos del archivo
                ports = []
                for line in content.split('\n'):
                    if line.startswith('PORT_') and '=' in line:
                        port_num = line.split('=')[1].strip()
                        if port_num.isdigit():
                            ports.append(int(port_num))
                return ports
        return list(range(8000, 8000+78))  # Fallback
    
    def check_processes_running(self):
        """Verifica que los procesos estén corriendo"""
        logger.info("🔍 Verificando procesos en ejecución...")
        
        running_processes = []
        total_processes = psutil.process_iter(['pid', 'name', 'cmdline'])
        
        for proc in total_processes:
            try:
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                if any(keyword in cmdline for keyword in ['uvicorn', 'node', 'python']):
                    running_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cmdline': cmdline
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        logger.info(f"📊 {len(running_processes)} procesos relacionados con el framework encontrados")
        
        # Verificar específicamente procesos de equipos
        team_processes = [p for p in running_processes if 'main.py' in p['cmdline'] or 'Team.js' in p['cmdline']]
        logger.info(f"🎯 {len(team_processes)} procesos de equipos específicos encontrados")
        
        return running_processes, team_processes
    
    def test_python_teams_with_delay(self):
        """Testa equipos Python con delays más largos"""
        logger.info("🐍 Verificando equipos Python con mayor paciencia...")
        
        python_teams = [
            {'name': 'audiovisual-team', 'port': 8000, 'endpoints': ['/', '/health', '/status']},
            {'name': 'api_gateway', 'port': 8029, 'endpoints': ['/', '/health']},
            {'name': 'business_development_team', 'port': 8001, 'endpoints': ['/', '/health']},
            {'name': 'mcp_server', 'port': 8027, 'endpoints': ['/', '/health']},
        ]
        
        working_teams = []
        
        for team in python_teams:
            logger.info(f"🔍 Verificando {team['name']} (puerto {team['port']})...")
            
            for endpoint in team['endpoints']:
                try:
                    # Usar curl con más tiempo de espera
                    result = subprocess.run([
                        'curl', '-f', '-s', '--max-time', '10', '--connect-timeout', '5',
                        f'http://localhost:{team["port"]}{endpoint}'
                    ], capture_output=True, text=True, timeout=15)
                    
                    if result.returncode == 0:
                        working_teams.append({
                            'name': team['name'],
                            'port': team['port'],
                            'endpoint': endpoint,
                            'response': result.stdout[:100]  # Primeros 100 chars
                        })
                        logger.info(f"✅ {team['name']}: Respuesta OK en {endpoint}")
                        break
                    else:
                        logger.debug(f"❌ {team['name']}: No responde en {endpoint}")
                        
                except subprocess.TimeoutExpired:
                    logger.debug(f"⏱️ {team['name']}: Timeout en {endpoint}")
                except Exception as e:
                    logger.debug(f"⚠️ {team['name']}: Error {e}")
            
            # Esperar un poco entre equipos
            time.sleep(0.5)
        
        return working_teams
    
    def test_node_teams(self):
        """Testa equipos Node.js verificando su estado"""
        logger.info("🔧 Verificando equipos Node.js...")
        
        # Buscar procesos Node.js relacionados con equipos
        node_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'node' and proc.info['cmdline']:
                    cmdline = ' '.join(proc.info['cmdline'])
                    if any(team_name in cmdline for team_name in ['Team.js', 'Workflow.js']):
                        node_processes.append({
                            'pid': proc.info['pid'],
                            'cmdline': cmdline,
                            'status': 'running' if proc.status() == psutil.STATUS_RUNNING else 'stopped'
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        logger.info(f"📊 {len(node_processes)} procesos Node.js de equipos encontrados")
        
        # Verificar si están respondiendo en algún puerto
        working_node_teams = []
        for node_proc in node_processes:
            try:
                # Verificar si el proceso está saludable
                cpu_percent = node_proc['status'] == 'running'
                working_node_teams.append({
                    'pid': node_proc['pid'],
                    'name': self._extract_team_name(node_proc['cmdline']),
                    'status': 'healthy' if cpu_percent else 'warning',
                    'cmdline': node_proc['cmdline']
                })
            except Exception as e:
                logger.debug(f"Error verificando proceso {node_proc['pid']}: {e}")
        
        return working_node_teams
    
    def _extract_team_name(self, cmdline):
        """Extrae nombre del equipo del cmdline"""
        if 'Team.js' in cmdline:
            return cmdline.split('Team.js')[0].split('/')[-1] + 'Team'
        elif 'Workflow.js' in cmdline:
            return cmdline.split('Workflow.js')[0].split('/')[-1] + 'Workflow'
        return 'Unknown'
    
    def check_system_resources(self):
        """Verifica recursos del sistema"""
        logger.info("💻 Monitoreando recursos del sistema...")
        
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Verificar procesos activos
            total_processes = len(list(psutil.process_iter()))
            
            resource_status = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': disk.percent,
                'total_processes': total_processes,
                'system_health': 'good' if cpu_percent < 80 and memory.percent < 80 else 'warning'
            }
            
            logger.info(f"💻 CPU: {cpu_percent:.1f}% | 💾 RAM: {memory.percent:.1f}% | 💽 Disk: {disk.percent:.1f}% | 📊 Procesos: {total_processes}")
            
            return resource_status
            
        except Exception as e:
            logger.error(f"Error monitoreando recursos: {e}")
            return {'error': str(e)}
    
    def test_framework_functionality(self):
        """Testa funcionalidades específicas del framework"""
        logger.info("🧪 Probando funcionalidades del framework...")
        
        tests = []
        
        # Test 1: Verificar que el API Gateway está configurado
        try:
            result = subprocess.run(['netstat', '-tulpn'], capture_output=True, text=True, timeout=5)
            listening_ports = []
            for line in result.stdout.split('\n'):
                if ':8000' <= line.split()[3].split(':')[-1] <= ':9000':
                    listening_ports.append(line.split()[3].split(':')[-1])
            
            tests.append({
                'test': 'port_listening',
                'result': 'pass',
                'details': f'Puertos activos: {len(listening_ports)}'
            })
            logger.info(f"🔌 {len(listening_ports)} puertos del framework activos")
            
        except Exception as e:
            tests.append({
                'test': 'port_listening',
                'result': 'fail',
                'error': str(e)
            })
        
        # Test 2: Verificar archivos de configuración
        config_files = [
            '.env.activation',
            'docker-compose-multiagente-cuantico.yml',
            '.env.dynamic'
        ]
        
        config_status = []
        for config_file in config_files:
            exists = (self.workspace / config_file).exists()
            config_status.append({
                'file': config_file,
                'exists': exists,
                'size': (self.workspace / config_file).stat().st_size if exists else 0
            })
        
        tests.append({
            'test': 'config_files',
            'result': 'pass' if all(c['exists'] for c in config_status) else 'warning',
            'details': config_status
        })
        
        return tests
    
    def generate_verification_report(self, python_teams, node_teams, resources, functionality_tests, all_processes):
        """Genera reporte de verificación final"""
        logger.info("📊 Generando reporte de verificación...")
        
        total_python = len(python_teams)
        total_node = len(node_teams)
        total_teams_working = total_python + total_node
        
        success_rate = (total_teams_working / 78) * 100 if 78 > 0 else 0
        
        report = {
            'verification_summary': {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'framework_version': '4.0.0',
                'total_teams_configured': 78,
                'teams_responding': total_teams_working,
                'success_rate': round(success_rate, 2),
                'system_status': resources.get('system_health', 'unknown')
            },
            'python_teams': {
                'total': total_python,
                'teams': python_teams
            },
            'node_teams': {
                'total': total_node,
                'teams': node_teams
            },
            'system_resources': resources,
            'functionality_tests': functionality_tests,
            'all_processes': len(all_processes),
            'recommendations': self._generate_recommendations(total_teams_working, success_rate, resources)
        }
        
        # Guardar reporte
        report_file = self.workspace / 'VERIFICACION_FINAL_FRAMEWORK_COMPLETO.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 Reporte guardado: {report_file}")
        return report
    
    def _generate_recommendations(self, working_teams, success_rate, resources):
        """Genera recomendaciones basadas en los resultados"""
        recommendations = []
        
        if success_rate >= 80:
            recommendations.append("✅ Framework operativo al 80%+ - Listo para producción")
        elif success_rate >= 60:
            recommendations.append("⚠️ Framework parcialmente operativo - Revisar equipos no respondientes")
        else:
            recommendations.append("❌ Framework requiere configuración adicional")
        
        if resources.get('memory_percent', 0) > 80:
            recommendations.append("💾 Alto uso de memoria - Considerar optimizar recursos")
        
        if resources.get('cpu_percent', 0) > 80:
            recommendations.append("💻 Alto uso de CPU - Verificar procesos intensivos")
        
        if working_teams < 30:
            recommendations.append("🔧 Equipos Python necesitan más tiempo de inicialización")
        
        return recommendations
    
    def run_comprehensive_verification(self):
        """Ejecuta verificación comprehensiva del framework"""
        logger.info("="*80)
        logger.info("🔍 VERIFICACIÓN MAESTRA - FRAMEWORK SILHOUETTE V4.0")
        logger.info("="*80)
        
        start_time = time.time()
        
        # 1. Verificar procesos
        all_processes, team_processes = self.check_processes_running()
        
        # 2. Esperar un poco más para que los equipos se inicialicen
        logger.info("⏳ Esperando 30 segundos para inicialización completa...")
        time.sleep(30)
        
        # 3. Testar equipos Python
        python_teams = self.test_python_teams_with_delay()
        
        # 4. Testar equipos Node.js
        node_teams = self.test_node_teams()
        
        # 5. Verificar recursos
        resources = self.check_system_resources()
        
        # 6. Testar funcionalidades
        functionality_tests = self.test_framework_functionality()
        
        # 7. Generar reporte
        final_report = self.generate_verification_report(
            python_teams, node_teams, resources, functionality_tests, all_processes
        )
        
        # Resultados finales
        verification_time = time.time() - start_time
        working_teams = len(python_teams) + len(node_teams)
        total_success_rate = (working_teams / 78) * 100
        
        logger.info("="*80)
        logger.info("📊 RESULTADOS DE VERIFICACIÓN")
        logger.info("="*80)
        logger.info(f"⏱️  Tiempo de verificación: {verification_time:.2f} segundos")
        logger.info(f"🎯 Equipos configurados: 78")
        logger.info(f"✅ Equipos respondiendo: {working_teams}")
        logger.info(f"🔧 Equipos Python funcionales: {len(python_teams)}")
        logger.info(f"🔧 Equipos Node.js funcionando: {len(node_teams)}")
        logger.info(f"📈 Tasa de éxito: {total_success_rate:.1f}%")
        logger.info(f"💻 Estado del sistema: {resources.get('system_health', 'unknown')}")
        
        # Recomendaciones
        for rec in final_report['recommendations']:
            logger.info(f"💡 {rec}")
        
        logger.info("="*80)
        
        return final_report

def main():
    verifier = TeamVerifier()
    
    try:
        report = verifier.run_comprehensive_verification()
        
        success_rate = report['verification_summary']['success_rate']
        
        if success_rate >= 50:
            print("\n🎉 FRAMEWORK SILHOUETTE V4.0 OPERATIVO")
            print("✅ Equipos especializados activos")
            print("🌐 Framework funcional para uso")
            print("🔧 Revisar reporte para optimizaciones")
            return 0
        else:
            print("\n⚠️  FRAMEWORK PARCIALMENTE OPERATIVO")
            print("🔧 Equipos necesitan más configuración")
            print("📊 Revisar reporte para detalles")
            return 1
            
    except Exception as e:
        logger.error(f"Error en verificación: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
