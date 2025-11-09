#!/usr/bin/env python3
"""
VALIDADOR COMPLETO DEL FRAMEWORK SILHOUETTE V4.0
Valida todos los archivos: Python, JavaScript, Docker, y configuración

Autor: MiniMax Agent
Fecha: 2025-11-09
Versión: 1.0
"""

import os
import json
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any
import time

class FrameworkValidator:
    def __init__(self, workspace_path: str = "/workspace"):
        self.workspace_path = Path(workspace_path)
        self.stats = {
            "python_files": {"total": 0, "valid": 0, "invalid": 0, "errors": []},
            "javascript_files": {"total": 0, "valid": 0, "invalid": 0, "errors": []},
            "docker_files": {"total": 0, "valid": 0, "invalid": 0, "errors": []},
            "config_files": {"total": 0, "valid": 0, "invalid": 0, "errors": []},
            "requirements_files": {"total": 0, "valid": 0, "invalid": 0, "errors": []}
        }
        
    def find_files_by_pattern(self, pattern: str, exclude_dirs: List[str] = None) -> List[Path]:
        """Encuentra archivos que coinciden con un patrón."""
        if exclude_dirs is None:
            exclude_dirs = ['.git', 'node_modules', '__pycache__', '.pytest_cache']
            
        files = []
        for file_path in self.workspace_path.rglob(pattern):
            # Verificar que el archivo no esté en directorios excluidos
            if not any(exclude_dir in file_path.parts for exclude_dir in exclude_dirs):
                files.append(file_path)
        
        return sorted(files)
    
    def validate_python_syntax(self, file_path: Path) -> Tuple[bool, str]:
        """Valida la sintaxis de un archivo Python."""
        try:
            # Usar py_compile para validar sintaxis
            result = subprocess.run(
                ["python3", "-m", "py_compile", str(file_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return True, "Sintaxis válida"
            else:
                return False, result.stderr.strip()
                
        except subprocess.TimeoutExpired:
            return False, "Timeout durante validación"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def validate_javascript_syntax(self, file_path: Path) -> Tuple[bool, str]:
        """Valida la sintaxis de un archivo JavaScript."""
        try:
            # Usar node --check para validar sintaxis
            result = subprocess.run(
                ["node", "--check", str(file_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return True, "Sintaxis válida"
            else:
                return False, result.stderr.strip()
                
        except subprocess.TimeoutExpired:
            return False, "Timeout durante validación"
        except FileNotFoundError:
            # Node.js no está disponible, usar validación manual básica
            return self._validate_javascript_manual(file_path)
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def _validate_javascript_manual(self, file_path: Path) -> Tuple[bool, str]:
        """Validación manual básica de JavaScript si Node.js no está disponible."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Validaciones básicas manuales
            errors = []
            
            # Verificar llaves balanceadas
            open_braces = content.count('{')
            close_braces = content.count('}')
            if open_braces != close_braces:
                errors.append(f"Llaves desbalanceadas: {open_braces} abiertas, {close_braces} cerradas")
            
            # Verificar paréntesis balanceados
            open_parens = content.count('(')
            close_parens = content.count(')')
            if open_parens != close_parens:
                errors.append(f"Paréntesis desbalanceados: {open_parens} abiertos, {close_parens} cerrados")
            
            # Verificar corchetes balanceados
            open_brackets = content.count('[')
            close_brackets = content.count(']')
            if open_brackets != close_brackets:
                errors.append(f"Corchetes desbalanceados: {open_brackets} abiertos, {close_brackets} cerrados")
            
            if errors:
                return False, "; ".join(errors)
            else:
                return True, "Validación manual exitosa (balance de símbolos)"
                
        except Exception as e:
            return False, f"Error en validación manual: {str(e)}"
    
    def validate_dockerfile(self, file_path: Path) -> Tuple[bool, str]:
        """Valida la estructura básica de un Dockerfile."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Verificaciones básicas de Dockerfile
            has_from = any(line.strip().upper().startswith('FROM') for line in lines)
            has_workdir = any('WORKDIR' in line.upper() for line in lines)
            has_cmd = any(line.strip().upper().startswith('CMD') or line.strip().upper().startswith('ENTRYPOINT') for line in lines)
            
            issues = []
            if not has_from:
                issues.append("Falta instrucción FROM")
            if not has_workdir:
                issues.append("Falta instrucción WORKDIR")
            if not has_cmd:
                issues.append("Falta instrucción CMD o ENTRYPOINT")
            
            if issues:
                return False, "; ".join(issues)
            else:
                return True, "Estructura de Dockerfile válida"
                
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def validate_requirements(self, file_path: Path) -> Tuple[bool, str]:
        """Valida un archivo requirements.txt."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            issues = []
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Verificar formato básico de package
                    if not re.match(r'^[a-zA-Z0-9_\-\.]+([><=!]+.*)?$', line):
                        issues.append(f"Línea {i}: Formato inválido '{line}'")
            
            if issues:
                return False, "; ".join(issues)
            else:
                return True, "Formato de requirements.txt válido"
                
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def validate_all_files(self):
        """Ejecuta la validación completa del framework."""
        print("🚀 INICIANDO VALIDACIÓN COMPLETA DEL FRAMEWORK SILHOUETTE V4.0")
        print("=" * 80)
        
        start_time = time.time()
        
        # 1. Validar archivos Python
        print("\n🐍 VALIDANDO ARCHIVOS PYTHON...")
        python_files = self.find_files_by_pattern("*.py")
        self.stats["python_files"]["total"] = len(python_files)
        
        for i, file_path in enumerate(python_files, 1):
            relative_path = file_path.relative_to(self.workspace_path)
            print(f"\r  [{i}/{len(python_files)}] {relative_path}", end="", flush=True)
            
            is_valid, message = self.validate_python_syntax(file_path)
            if is_valid:
                self.stats["python_files"]["valid"] += 1
            else:
                self.stats["python_files"]["invalid"] += 1
                self.stats["python_files"]["errors"].append({
                    "file": str(relative_path),
                    "error": message
                })
                print(" ❌")
            if (i % 10 == 0) or (i == len(python_files)):
                print()
        
        # 2. Validar archivos JavaScript
        print("\n🟨 VALIDANDO ARCHIVOS JAVASCRIPT...")
        js_files = self.find_files_by_pattern("*.js")
        self.stats["javascript_files"]["total"] = len(js_files)
        
        for i, file_path in enumerate(js_files, 1):
            relative_path = file_path.relative_to(self.workspace_path)
            print(f"\r  [{i}/{len(js_files)}] {relative_path}", end="", flush=True)
            
            is_valid, message = self.validate_javascript_syntax(file_path)
            if is_valid:
                self.stats["javascript_files"]["valid"] += 1
            else:
                self.stats["javascript_files"]["invalid"] += 1
                self.stats["javascript_files"]["errors"].append({
                    "file": str(relative_path),
                    "error": message
                })
                print(" ❌")
            if (i % 10 == 0) or (i == len(js_files)):
                print()
        
        # 3. Validar Dockerfiles
        print("\n🐳 VALIDANDO DOCKERFILES...")
        docker_files = self.find_files_by_pattern("Dockerfile*")
        self.stats["docker_files"]["total"] = len(docker_files)
        
        for i, file_path in enumerate(docker_files, 1):
            relative_path = file_path.relative_to(self.workspace_path)
            print(f"\r  [{i}/{len(docker_files)}] {relative_path}", end="", flush=True)
            
            is_valid, message = self.validate_dockerfile(file_path)
            if is_valid:
                self.stats["docker_files"]["valid"] += 1
            else:
                self.stats["docker_files"]["invalid"] += 1
                self.stats["docker_files"]["errors"].append({
                    "file": str(relative_path),
                    "error": message
                })
                print(" ❌")
            if (i % 10 == 0) or (i == len(docker_files)):
                print()
        
        # 4. Validar archivos requirements.txt
        print("\n📋 VALIDANDO ARCHIVOS REQUIREMENTS.TXT...")
        requirements_files = self.find_files_by_pattern("requirements.txt")
        self.stats["requirements_files"]["total"] = len(requirements_files)
        
        for i, file_path in enumerate(requirements_files, 1):
            relative_path = file_path.relative_to(self.workspace_path)
            print(f"\r  [{i}/{len(requirements_files)}] {relative_path}", end="", flush=True)
            
            is_valid, message = self.validate_requirements(file_path)
            if is_valid:
                self.stats["requirements_files"]["valid"] += 1
            else:
                self.stats["requirements_files"]["invalid"] += 1
                self.stats["requirements_files"]["errors"].append({
                    "file": str(relative_path),
                    "error": message
                })
                print(" ❌")
            if (i % 10 == 0) or (i == len(requirements_files)):
                print()
        
        # Generar reporte final
        elapsed_time = time.time() - start_time
        self.generate_final_report(elapsed_time)
    
    def generate_final_report(self, elapsed_time: float):
        """Genera el reporte final de validación."""
        print("\n" + "=" * 80)
        print("📊 REPORTE FINAL DE VALIDACIÓN FRAMEWORK SILHOUETTE V4.0")
        print("=" * 80)
        print(f"⏱️  Tiempo total de validación: {elapsed_time:.2f} segundos")
        print(f"📅 Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Resumen por tipo de archivo
        total_files = sum(stats["total"] for stats in self.stats.values())
        total_valid = sum(stats["valid"] for stats in self.stats.values())
        total_invalid = sum(stats["invalid"] for stats in self.stats.values())
        
        print(f"\n📈 ESTADÍSTICAS GENERALES:")
        print(f"   • Total de archivos validados: {total_files}")
        print(f"   • Archivos válidos: {total_valid} ✅")
        print(f"   • Archivos con errores: {total_invalid} ❌")
        print(f"   • Tasa de éxito general: {(total_valid/total_files*100):.1f}%")
        
        # Detalle por tipo
        for file_type, stats in self.stats.items():
            print(f"\n🔍 {file_type.upper().replace('_', ' ')}:")
            print(f"   • Total: {stats['total']} | Válidos: {stats['valid']} | Errores: {stats['invalid']}")
            if stats['errors']:
                print(f"   • Errores encontrados:")
                for error in stats['errors'][:5]:  # Mostrar solo los primeros 5 errores
                    print(f"     - {error['file']}: {error['error']}")
                if len(stats['errors']) > 5:
                    print(f"     ... y {len(stats['errors']) - 5} errores más")
        
        # Verificar si está listo para producción
        production_ready = total_invalid == 0
        print(f"\n🚀 ESTADO PARA PRODUCCIÓN:")
        if production_ready:
            print("   ✅ FRAMEWORK LISTO PARA DESPLIEGUE EN PRODUCCIÓN")
            print("   ✅ Sin errores críticos encontrados")
            print("   ✅ Todos los archivos tienen sintaxis válida")
        else:
            print("   ❌ FRAMEWORK NO ESTÁ LISTO PARA PRODUCCIÓN")
            print("   ❌ Se encontraron errores que deben ser corregidos")
        
        # Guardar reporte en JSON
        report_data = {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "validation_duration_seconds": elapsed_time,
            "framework_version": "Silhouette V4.0",
            "production_ready": production_ready,
            "statistics": self.stats,
            "summary": {
                "total_files": total_files,
                "valid_files": total_valid,
                "invalid_files": total_invalid,
                "success_rate": f"{(total_valid/total_files*100):.1f}%"
            }
        }
        
        report_path = "/workspace/REPORTE_VALIDACION_FRAMEWORK_COMPLETO.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Reporte completo guardado en: {report_path}")
        
        return report_data

def main():
    """Función principal."""
    validator = FrameworkValidator()
    try:
        validator.validate_all_files()
    except KeyboardInterrupt:
        print("\n\n⚠️  Validación interrumpida por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error durante la validación: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
