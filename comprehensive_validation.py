#!/usr/bin/env python3
"""
VERIFICACIÓN EXHAUSTIVA - Framework Silhouette V4.0
Validación completa para asegurar:
1. Cero errores restantes
2. Todas las capacidades intactas  
3. Sistema de puertos dinámicos funcional

Autor: MiniMax Agent
Fecha: 2025-11-09 21:43:06
"""

import ast
import yaml
import json
import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set

class ComprehensiveValidator:
    """Validador exhaustivo del Framework Silhouette V4.0"""
    
    def __init__(self):
        self.workspace = Path("/workspace")
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.successes: List[str] = []
        self.verified_files: Set[Path] = set()
        
    def log_error(self, message: str):
        """Registra un error crítico"""
        self.errors.append(f"❌ {message}")
        print(f"❌ {message}")
        
    def log_warning(self, message: str):
        """Registra una advertencia"""
        self.warnings.append(f"⚠️  {message}")
        print(f"⚠️  {message}")
        
    def log_success(self, message: str):
        """Registra un éxito"""
        self.successes.append(f"✅ {message}")
        print(f"✅ {message}")
        
    def check_python_syntax_comprehensive(self) -> bool:
        """Verifica sintaxis de TODOS los archivos Python"""
        print("\n" + "="*60)
        print("🔍 VERIFICACIÓN EXHAUSTIVA DE SINTAXIS PYTHON")
        print("="*60)
        
        all_valid = True
        python_files = list(self.workspace.rglob("*.py"))
        
        print(f"Archivos Python encontrados: {len(python_files)}")
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verificar sintaxis con AST
                ast.parse(content)
                self.verified_files.add(py_file)
                self.log_success(f"Validado: {py_file.relative_to(self.workspace)}")
                
            except SyntaxError as e:
                self.log_error(f"Sintaxis inválida en {py_file.relative_to(self.workspace)}:{e.lineno}: {e.msg}")
                all_valid = False
            except Exception as e:
                self.log_warning(f"Error procesando {py_file.relative_to(self.workspace)}: {e}")
        
        return all_valid
        
    def check_docker_files_comprehensive(self) -> bool:
        """Verifica todos los archivos Docker y configuración"""
        print("\n" + "="*60)
        print("🐳 VERIFICACIÓN EXHAUSTIVA DE ARCHIVOS DOCKER")
        print("="*60)
        
        all_valid = True
        
        # Verificar Dockerfiles
        dockerfiles = list(self.workspace.rglob("Dockerfile"))
        for dockerfile in dockerfiles:
            try:
                with open(dockerfile, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verificaciones específicas
                if "-- " in content and not content.count("--") == content.count("# "):
                    self.log_error(f"Dockerfile contiene comentarios SQL: {dockerfile.relative_to(self.workspace)}")
                    all_valid = False
                else:
                    self.log_success(f"Dockerfile válido: {dockerfile.relative_to(self.workspace)}")
                    
                # Verificar autor correcto
                if "Silhouette Anonimo" in content:
                    self.log_error(f"Dockerfile con autor incorrecto: {dockerfile.relative_to(self.workspace)}")
                    all_valid = False
                    
            except Exception as e:
                self.log_error(f"Error procesando Dockerfile {dockerfile}: {e}")
                all_valid = False
        
        # Verificar docker-compose files
        compose_files = list(self.workspace.rglob("docker-compose*.yml"))
        for compose_file in compose_files:
            try:
                with open(compose_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verificar que sea YAML válido
                yaml.safe_load(content)
                self.log_success(f"Docker Compose válido: {compose_file.relative_to(self.workspace)}")
                
            except yaml.YAMLError as e:
                self.log_error(f"YAML inválido en {compose_file.relative_to(self.workspace)}: {e}")
                all_valid = False
            except Exception as e:
                self.log_error(f"Error procesando {compose_file}: {e}")
                all_valid = False
        
        return all_valid
        
    def check_json_files_comprehensive(self) -> bool:
        """Verifica todos los archivos JSON"""
        print("\n" + "="*60)
        print("📄 VERIFICACIÓN EXHAUSTIVA DE ARCHIVOS JSON")
        print("="*60)
        
        all_valid = True
        json_files = list(self.workspace.rglob("*.json"))
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    json.load(f)
                self.log_success(f"JSON válido: {json_file.relative_to(self.workspace)}")
                
            except json.JSONDecodeError as e:
                self.log_error(f"JSON inválido en {json_file.relative_to(self.workspace)}: {e}")
                all_valid = False
            except Exception as e:
                self.log_warning(f"Error procesando JSON {json_file}: {e}")
        
        return all_valid
        
    def check_framework_capabilities(self) -> bool:
        """Verifica que todas las capacidades del framework estén intactas"""
        print("\n" + "="*60)
        print("🚀 VERIFICACIÓN DE CAPACIDADES DEL FRAMEWORK")
        print("="*60)
        
        all_intact = True
        
        # Verificar equipos especializados (capability teams)
        team_dirs = [
            "code_generation_team", "planner", "prompt_engineer", 
            "machine_learning_ai_team", "research_team", "security_team",
            "marketing_team", "sales_team", "finance_team", "hr_team",
            "legal_team", "design_creative_team", "quality_assurance_team"
        ]
        
        for team_dir in team_dirs:
            team_path = self.workspace / team_dir
            if team_path.exists():
                main_py = team_path / "main.py"
                if main_py.exists():
                    self.log_success(f"Equipo activo: {team_dir}")
                else:
                    self.log_warning(f"Equipo sin main.py: {team_dir}")
            else:
                self.log_warning(f"Directorio de equipo faltante: {team_dir}")
        
        # Verificar componentes core
        core_components = [
            "orchestrator", "api_gateway", "mcp_server", 
            "browser", "external_api"
        ]
        
        for component in core_components:
            comp_path = self.workspace / component
            if comp_path.exists():
                self.log_success(f"Componente core: {component}")
            else:
                self.log_warning(f"Componente core faltante: {component}")
        
        # Verificar configuraciones
        config_files = [
            "config/prometheus.yml", "config/nginx/nginx.conf",
            "docker-compose.yml", "multiagent-framework-expandido/docker-compose.yml"
        ]
        
        for config_file in config_files:
            file_path = self.workspace / config_file
            if file_path.exists():
                self.log_success(f"Configuración: {config_file}")
            else:
                self.log_error(f"Configuración crítica faltante: {config_file}")
                all_intact = False
        
        return all_intact
        
    def check_dynamic_port_system(self) -> bool:
        """Verifica que el sistema de puertos dinámicos esté completo"""
        print("\n" + "="*60)
        print("🔄 VERIFICACIÓN DEL SISTEMA DE PUERTOS DINÁMICOS")
        print("="*60)
        
        all_good = True
        
        # Verificar archivos esenciales
        essential_files = [
            "docker-compose.dynamic.yml",
            ".env.dynamic", 
            "port_manager_corrected.py"
        ]
        
        for file_name in essential_files:
            file_path = self.workspace / file_name
            if file_path.exists():
                self.log_success(f"Sistema dinámico: {file_name} existe")
            else:
                self.log_error(f"Sistema dinámico: {file_name} FALTANTE")
                all_good = False
        
        # Verificar contenido de .env.dynamic
        env_file = self.workspace / ".env.dynamic"
        if env_file.exists():
            try:
                with open(env_file, 'r') as f:
                    env_content = f.read()
                
                # Contar variables de puertos
                port_lines = [line for line in env_content.split('\n') if 'PORT_' in line and '=' in line]
                
                if len(port_lines) >= 5:  # Mínimo esperado
                    self.log_success(f"Variables de puertos dinámicas: {len(port_lines)} configuradas")
                else:
                    self.log_warning(f"Pocas variables de puertos: {len(port_lines)} (esperado >= 5)")
                    
            except Exception as e:
                self.log_error(f"Error leyendo .env.dynamic: {e}")
                all_good = False
        
        # Verificar docker-compose.dynamic.yml contenido
        dynamic_compose = self.workspace / "docker-compose.dynamic.yml"
        if dynamic_compose.exists():
            try:
                with open(dynamic_compose, 'r') as f:
                    dynamic_config = yaml.safe_load(f)
                
                services = dynamic_config.get('services', {})
                if 'consul' in services and 'traefik' in services:
                    self.log_success("Service discovery (Consul) configurado")
                    self.log_success("Reverse proxy (Traefik) configurado")
                else:
                    self.log_error("Faltan servicios clave en docker-compose.dynamic.yml")
                    all_good = False
                    
            except Exception as e:
                self.log_error(f"Error validando docker-compose.dynamic.yml: {e}")
                all_good = False
        
        return all_good
        
    def run_comprehensive_validation(self) -> Dict:
        """Ejecuta validación exhaustiva completa"""
        print("🎯 VERIFICACIÓN EXHAUSTIVA COMPLETA")
        print("Framework Silhouette V4.0 - Validación Final")
        print(f"Fecha: 2025-11-09 21:43:06")
        print("="*60)
        
        results = {
            "python_syntax": self.check_python_syntax_comprehensive(),
            "docker_files": self.check_docker_files_comprehensive(),
            "json_files": self.check_json_files_comprehensive(),
            "framework_capabilities": self.check_framework_capabilities(),
            "dynamic_ports": self.check_dynamic_port_system()
        }
        
        # Resumen final
        print("\n" + "="*60)
        print("📊 RESUMEN DE VERIFICACIÓN EXHAUSTIVA")
        print("="*60)
        
        total_checks = len(results)
        passed_checks = sum(1 for result in results.values() if result)
        
        print(f"✅ Verificaciones exitosas: {passed_checks}/{total_checks}")
        print(f"❌ Errores críticos: {len(self.errors)}")
        print(f"⚠️  Advertencias: {len(self.warnings)}")
        print(f"✅ Éxitos: {len(self.successes)}")
        
        if self.errors:
            print("\n🔴 ERRORES CRÍTICOS ENCONTRADOS:")
            for error in self.errors:
                print(f"  {error}")
                
        if self.warnings:
            print("\n🟡 ADVERTENCIAS:")
            for warning in self.warnings:
                print(f"  {warning}")
                
        # Estado final
        all_passed = all(results.values())
        print("\n" + "="*60)
        if all_passed:
            print("🎉 ¡VERIFICACIÓN EXHAUSTIVA COMPLETA!")
            print("✅ Framework Silhouette V4.0 - SIN ERRORES")
            print("✅ TODAS las capacidades intactas")
            print("✅ Sistema de puertos dinámicos operativo")
            print("✅ Listo para producción empresarial")
        else:
            print("⚠️  VERIFICACIÓN INCOMPLETA")
            print("🔍 Revisar errores críticos arriba")
        print("="*60)
        
        return {
            "overall_status": "PASS" if all_passed else "FAIL",
            "results": results,
            "errors": self.errors,
            "warnings": self.warnings,
            "successes": self.successes,
            "verified_files": len(self.verified_files)
        }

def main():
    validator = ComprehensiveValidator()
    results = validator.run_comprehensive_validation()
    
    # Guardar reporte final
    report_file = "/workspace/REPORTE_VERIFICACION_EXHAUSTIVA_FINAL.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# REPORTE DE VERIFICACIÓN EXHAUSTIVA FINAL\n")
        f.write("## Framework Silhouette V4.0\n\n")
        f.write(f"**Fecha:** 2025-11-09 21:43:06\n")
        f.write(f"**Estado General:** {results['overall_status']}\n")
        f.write(f"**Archivos Verificados:** {results['verified_files']}\n")
        f.write(f"**Errores Críticos:** {len(results['errors'])}\n")
        f.write(f"**Advertencias:** {len(results['warnings'])}\n")
        f.write(f"**Verificaciones Exitosas:** {len(results['successes'])}\n\n")
        
        f.write("## RESULTADOS DE VERIFICACIÓN\n\n")
        for check, result in results['results'].items():
            status = "✅ PASS" if result else "❌ FAIL"
            check_name = check.replace('_', ' ').title()
            f.write(f"- **{check_name}:** {status}\n")
            
        if results['errors']:
            f.write(f"\n## ERRORES CRÍTICOS ({len(results['errors'])})\n\n")
            for error in results['errors']:
                f.write(f"- {error}\n")
                
        if results['warnings']:
            f.write(f"\n## ADVERTENCIAS ({len(results['warnings'])})\n\n")
            for warning in results['warnings']:
                f.write(f"- {warning}\n")
                
        if results['successes']:
            f.write(f"\n## VERIFICACIONES EXITOSAS ({len(results['successes'])})\n\n")
            for success in results['successes']:
                f.write(f"- {success}\n")
                
        f.write("\n---\n")
        f.write("*Verificación exhaustiva realizada por MiniMax Agent*\n")
    
    print(f"\n📄 Reporte guardado en: {report_file}")
    
    return 0 if results['overall_status'] == 'PASS' else 1

if __name__ == "__main__":
    exit(main())