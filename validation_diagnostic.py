#!/usr/bin/env python3
"""
Diagnóstico de Validación Post-Corrección - Framework Silhouette V4.0
Verifica que todos los errores han sido corregidos

Autor: MiniMax Agent
Fecha: 2025-11-09
"""

import os
import ast
import yaml
import json
import re
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple

class ValidationDiagnostic:
    """Diagnóstico de validación post-corrección"""
    
    def __init__(self):
        self.workspace = Path("/workspace")
        self.errors_found = []
        self.warnings = []
        self.success_count = 0
        
    def log_error(self, message: str):
        """Registra un error encontrado"""
        self.errors_found.append(f"❌ {message}")
        print(f"❌ {message}")
        
    def log_warning(self, message: str):
        """Registra una advertencia"""
        self.warnings.append(f"⚠️  {message}")
        print(f"⚠️  {message}")
        
    def log_success(self, message: str):
        """Registra un éxito"""
        self.success_count += 1
        print(f"✅ {message}")
        
    def validate_python_syntax(self) -> bool:
        """Valida sintaxis de archivos Python"""
        print("\n🔍 VALIDANDO SINTAXIS DE ARCHIVOS PYTHON...")
        
        python_files = list(self.workspace.rglob("*.py"))
        all_valid = True
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Intentar parsear el AST
                ast.parse(content)
                self.log_success(f"{py_file.relative_to(self.workspace)}: Sintaxis válida")
                
            except SyntaxError as e:
                self.log_error(f"{py_file.relative_to(self.workspace)}: Error de sintaxis en línea {e.lineno}: {e.msg}")
                all_valid = False
                
            except Exception as e:
                self.log_warning(f"{py_file.relative_to(self.workspace)}: No se pudo validar: {e}")
                
        return all_valid
        
    def check_specific_errors(self) -> bool:
        """Verifica errores específicos identificados anteriormente"""
        print("\n🔍 VERIFICANDO ERRORES ESPECÍFICOS CORREGIDOS...")
        
        all_fixed = True
        
        # Verificar que no hay código Rust en archivos Python
        rust_patterns = [
            r'tracing::info!',
            r'println!',
            r'println!',
            r'let\s+\w+',
            r'pub\s+(struct|enum|fn)',
        ]
        
        for py_file in self.workspace.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern in rust_patterns:
                    matches = re.findall(pattern, content, re.MULTILINE)
                    if matches:
                        self.log_error(f"{py_file.relative_to(self.workspace)}: Contiene código que parece Rust")
                        all_fixed = False
                        
            except Exception:
                continue
                
        # Verificar comentarios SQL
        sql_comments = ['-- GESTOR DE EVENTOS', '-- ANALIZADOR DE PROMPTS']
        
        for py_file in self.workspace.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for comment in sql_comments:
                    if comment in content:
                        self.log_error(f"{py_file.relative_to(self.workspace)}: Contiene comentario SQL no corregido")
                        all_fixed = False
                        
            except Exception:
                continue
                
        # Verificar Dockerfile con autor correcto
        dockerfile_path = self.workspace / "multiagent-framework-expandido" / "Dockerfile"
        if dockerfile_path.exists():
            try:
                with open(dockerfile_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if "Silhouette Anonimo" in content:
                    self.log_error("Dockerfile: Aún contiene autor incorrecto 'Silhouette Anonimo'")
                    all_fixed = False
                else:
                    self.log_success("Dockerfile: Autor corregido correctamente")
                    
            except Exception as e:
                self.log_error(f"Dockerfile: No se pudo leer: {e}")
                all_fixed = False
                
        return all_fixed
        
    def validate_docker_compose_files(self) -> bool:
        """Valida archivos docker-compose"""
        print("\n🔍 VALIDANDO ARCHIVOS DOCKER COMPOSE...")
        
        compose_files = list(self.workspace.glob("**/docker-compose*.yml"))
        all_valid = True
        
        for compose_file in compose_files:
            try:
                with open(compose_file, 'r', encoding='utf-8') as f:
                    yaml.safe_load(f)
                self.log_success(f"{compose_file.relative_to(self.workspace)}: YAML válido")
                
            except yaml.YAMLError as e:
                self.log_error(f"{compose_file.relative_to(self.workspace)}: Error YAML: {e}")
                all_valid = False
                
            except Exception as e:
                self.log_error(f"{compose_file.relative_to(self.workspace)}: No se pudo validar: {e}")
                all_valid = False
                
        return all_valid
        
    def validate_json_files(self) -> bool:
        """Valida archivos JSON"""
        print("\n🔍 VALIDANDO ARCHIVOS JSON...")
        
        json_files = list(self.workspace.rglob("*.json"))
        all_valid = True
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    json.load(f)
                self.log_success(f"{json_file.relative_to(self.workspace)}: JSON válido")
                
            except json.JSONDecodeError as e:
                self.log_error(f"{json_file.relative_to(self.workspace)}: Error JSON: {e}")
                all_valid = False
                
            except Exception as e:
                self.log_warning(f"{json_file.relative_to(self.workspace)}: No se pudo validar: {e}")
                
        return all_valid
        
    def check_dynamic_port_configuration(self) -> bool:
        """Verifica configuración de puertos dinámicos"""
        print("\n🔍 VERIFICANDO CONFIGURACIÓN DE PUERTOS DINÁMICOS...")
        
        # Verificar que existe docker-compose.dynamic.yml
        dynamic_compose = self.workspace / "docker-compose.dynamic.yml"
        if dynamic_compose.exists():
            self.log_success("docker-compose.dynamic.yml: Archivo existe")
        else:
            self.log_error("docker-compose.dynamic.yml: Archivo no encontrado")
            return False
            
        # Verificar que existe .env.dynamic
        env_dynamic = self.workspace / ".env.dynamic"
        if env_dynamic.exists():
            self.log_success(".env.dynamic: Archivo de variables de entorno existe")
            
            try:
                with open(env_dynamic, 'r') as f:
                    env_content = f.read()
                    
                port_vars = [line for line in env_content.split('\n') if 'PORT_' in line and '=' in line]
                self.log_success(f".env.dynamic: Contiene {len(port_vars)} variables de puertos dinámicos")
                
            except Exception as e:
                self.log_error(f".env.dynamic: No se pudo leer: {e}")
                return False
        else:
            self.log_error(".env.dynamic: Archivo no encontrado")
            return False
            
        # Verificar port_manager
        port_manager = self.workspace / "port_manager_corrected.py"
        if port_manager.exists():
            self.log_success("port_manager_corrected.py: Script de gestión de puertos existe")
        else:
            self.log_error("port_manager_corrected.py: Script no encontrado")
            return False
            
        return True
        
    def check_framework_structure(self) -> bool:
        """Verifica estructura del framework"""
        print("\n🔍 VERIFICANDO ESTRUCTURA DEL FRAMEWORK...")
        
        # Verificar directorios clave
        key_dirs = [
            "config",
            "multiagent-framework-expandido", 
            "code_generation_team",
            "planner",
            "prompt_engineer"
        ]
        
        all_exist = True
        for dir_name in key_dirs:
            dir_path = self.workspace / dir_name
            if dir_path.exists():
                self.log_success(f"Directorio: {dir_name}")
            else:
                self.log_error(f"Directorio faltante: {dir_name}")
                all_exist = False
                
        # Verificar archivos de configuración clave
        config_files = [
            "config/prometheus.yml",
            "config/nginx/nginx.conf"
        ]
        
        for config_file in config_files:
            file_path = self.workspace / config_file
            if file_path.exists():
                self.log_success(f"Config: {config_file}")
            else:
                self.log_warning(f"Config opcional faltante: {config_file}")
                
        return all_exist
        
    def run_comprehensive_check(self) -> Dict:
        """Ejecuta verificación completa"""
        print("🏥 DIAGNÓSTICO DE VALIDACIÓN POST-CORRECCIÓN")
        print("=" * 60)
        print("Verificando que todos los errores han sido corregidos...")
        
        results = {
            "python_syntax": self.validate_python_syntax(),
            "specific_errors": self.check_specific_errors(),
            "docker_compose": self.validate_docker_compose_files(),
            "json_files": self.validate_json_files(),
            "dynamic_ports": self.check_dynamic_port_configuration(),
            "framework_structure": self.check_framework_structure()
        }
        
        # Resumen final
        print("\n" + "=" * 60)
        print("📊 RESUMEN DEL DIAGNÓSTICO DE VALIDACIÓN")
        print("=" * 60)
        
        total_checks = len(results)
        passed_checks = sum(1 for result in results.values() if result)
        
        print(f"✅ Verificaciones exitosas: {passed_checks}/{total_checks}")
        print(f"❌ Errores encontrados: {len(self.errors_found)}")
        print(f"⚠️  Advertencias: {len(self.warnings)}")
        
        if self.errors_found:
            print("\n🔴 ERRORES DETECTADOS:")
            for error in self.errors_found:
                print(f"  {error}")
                
        if self.warnings:
            print("\n🟡 ADVERTENCIAS:")
            for warning in self.warnings:
                print(f"  {warning}")
                
        # Estado general
        all_passed = all(results.values())
        if all_passed:
            print("\n🎉 ¡DIAGNÓSTICO COMPLETO! Todos los errores han sido corregidos.")
            print("✅ Framework Silhouette V4.0 está listo para producción")
        else:
            print("\n⚠️  DIAGNÓSTICO INCOMPLETO. Aún hay errores por resolver.")
            
        return {
            "overall_status": "PASS" if all_passed else "FAIL",
            "results": results,
            "errors": self.errors_found,
            "warnings": self.warnings,
            "success_count": self.success_count
        }

def main():
    diagnostic = ValidationDiagnostic()
    results = diagnostic.run_comprehensive_check()
    
    # Guardar reporte
    report_file = "/workspace/REPORTE_VALIDACION_POST_CORRECCION.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# REPORTE DE VALIDACIÓN POST-CORRECCIÓN\n")
        f.write("## Framework Silhouette V4.0\n\n")
        f.write(f"**Fecha:** 2025-11-09 21:36:05\n")
        f.write(f"**Estado General:** {results['overall_status']}\n")
        f.write(f"**Verificaciones Exitosas:** {results['success_count']}\n\n")
        
        f.write("## RESUMEN DE VERIFICACIONES\n\n")
        for check, result in results['results'].items():
            status = "✅ PASS" if result else "❌ FAIL"
            f.write(f"- **{check.replace('_', ' ').title()}:** {status}\n")
            
        if results['errors']:
            f.write(f"\n## ERRORES DETECTADOS ({len(results['errors'])})\n\n")
            for error in results['errors']:
                f.write(f"- {error}\n")
                
        if results['warnings']:
            f.write(f"\n## ADVERTENCIAS ({len(results['warnings'])})\n\n")
            for warning in results['warnings']:
                f.write(f"- {warning}\n")
                
        f.write("\n---\n*Reporte generado automáticamente por MiniMax Agent*\n")
    
    print(f"\n📄 Reporte guardado en: {report_file}")
    
    return 0 if results['overall_status'] == 'PASS' else 1

if __name__ == "__main__":
    exit(main())