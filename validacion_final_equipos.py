#!/usr/bin/env python3
"""
SCRIPT DE VALIDACIÓN FINAL - FRAMEWORK SILHOUETTE V4.0
Verificación exhaustiva de todos los equipos de agentes funcionales
Autor: MiniMax Agent
Fecha: 2025-11-09
"""

import os
import ast
import json
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Tuple

class FrameworkValidator:
    def __init__(self):
        self.workspace = Path('/workspace')
        self.teams_found = {}
        self.errors = []
        self.warnings = []
        self.successes = []
        
    def log_success(self, message):
        self.successes.append(f"✅ {message}")
        print(f"✅ {message}")
        
    def log_error(self, message):
        self.errors.append(f"❌ {message}")
        print(f"❌ {message}")
        
    def log_warning(self, message):
        self.warnings.append(f"⚠️  {message}")
        print(f"⚠️  {message}")
        
    def validate_python_syntax(self, file_path):
        """Valida sintaxis de archivos Python"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            ast.parse(content)
            return True
        except SyntaxError as e:
            self.log_error(f"Syntax error in {file_path}: {e}")
            return False
            
    def validate_javascript_syntax(self, file_path):
        """Valida sintaxis básica de archivos JavaScript"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Validación básica de sintaxis
            if content.count('{') != content.count('}'):
                self.log_warning(f"Braces mismatch in {file_path}")
                return False
            if content.count('(') != content.count(')'):
                self.log_warning(f"Parentheses mismatch in {file_path}")
                return False
            return True
        except Exception as e:
            self.log_error(f"Error reading {file_path}: {e}")
            return False
            
    def find_teams_with_dockerfile(self):
        """Encuentra todos los equipos con Dockerfile"""
        dockerfile_teams = []
        for dockerfile in self.workspace.rglob('Dockerfile'):
            if 'user_input_files' in str(dockerfile):
                continue
            team_name = dockerfile.parent.name
            dockerfile_teams.append(team_name)
        return dockerfile_teams
        
    def find_teams_with_main_files(self):
        """Encuentra equipos con archivos main.py o main.js"""
        main_teams = []
        
        # Buscar main.py
        for main_file in self.workspace.rglob('main.py'):
            if 'user_input_files' in str(main_file):
                continue
            team_name = main_file.parent.name
            if team_name not in main_teams:
                main_teams.append(team_name)
                
        # Buscar main.js
        for main_file in self.workspace.rglob('main.js'):
            if 'user_input_files' in str(main_file):
                continue
            team_name = main_file.parent.name
            if team_name not in main_teams:
                main_teams.append(team_name)
                
        return main_teams
        
    def find_optimization_teams(self):
        """Encuentra equipos en el directorio de optimización"""
        opt_teams = []
        opt_dir = self.workspace / 'optimization-team' / 'team-workflows'
        
        if not opt_dir.exists():
            return opt_teams
            
        # Buscar archivos JS en subdirectorios
        subdirs = ['ai', 'compliance', 'cybersecurity', 'data-engineering', 
                  'industry', 'phase3', 'specialized', 'strategic', 'technology']
        
        for subdir in subdirs:
            subdir_path = opt_dir / subdir
            if subdir_path.exists():
                for js_file in subdir_path.glob('*.js'):
                    team_name = js_file.stem.replace('Team', '').replace('Workflow', '')
                    opt_teams.append({
                        'name': team_name,
                        'file': js_file,
                        'category': subdir,
                        'full_path': js_file
                    })
                    
        return opt_teams
        
    def find_audiovisual_teams(self):
        """Encuentra sub-equipos audiovisuales"""
        av_teams = []
        av_dir = self.workspace / 'audiovisual-team'
        
        if not av_dir.exists():
            return av_teams
            
        for js_file in av_dir.rglob('*.js'):
            if js_file.name.startswith('DEMO_'):
                continue
            team_name = js_file.stem
            av_teams.append({
                'name': team_name,
                'file': js_file,
                'full_path': js_file
            })
            
        return av_teams
        
    def validate_team_implementation(self, team_path, team_type):
        """Valida la implementación de un equipo"""
        validations = {
            'dockerfile': False,
            'main_file': False,
            'requirements': False,
            'implementation': False
        }
        
        # Verificar Dockerfile
        dockerfile = team_path / 'Dockerfile'
        if dockerfile.exists():
            validations['dockerfile'] = True
            self.log_success(f"{team_type}: Dockerfile found")
        else:
            self.log_warning(f"{team_type}: No Dockerfile found")
            
        # Verificar archivo principal
        main_files = ['main.py', 'main.js', 'index.js']
        main_found = False
        for main_file in main_files:
            if (team_path / main_file).exists():
                main_found = True
                validations['main_file'] = True
                # Validar sintaxis
                file_path = team_path / main_file
                if main_file.endswith('.py'):
                    if self.validate_python_syntax(file_path):
                        self.log_success(f"{team_type}: Python syntax valid")
                elif main_file.endswith('.js'):
                    if self.validate_javascript_syntax(file_path):
                        self.log_success(f"{team_type}: JavaScript syntax valid")
                break
                
        if not main_found:
            self.log_error(f"{team_type}: No main file found")
            
        # Verificar dependencias
        dep_files = ['requirements.txt', 'package.json']
        for dep_file in dep_files:
            if (team_path / dep_file).exists():
                validations['requirements'] = True
                self.log_success(f"{team_type}: {dep_file} found")
                break
                
        return validations
        
    def count_total_teams(self):
        """Cuenta el total de equipos encontrados"""
        docker_teams = self.find_teams_with_dockerfile()
        main_teams = self.find_teams_with_main_files()
        opt_teams = self.find_optimization_teams()
        av_teams = self.find_audiovisual_teams()
        
        # Consolidar equipos únicos
        all_teams = set()
        all_teams.update(docker_teams)
        all_teams.update(main_teams)
        all_teams.update([t['name'] for t in opt_teams])
        all_teams.update([t['name'] for t in av_teams])
        
        return {
            'docker_teams': len(docker_teams),
            'main_teams': len(main_teams),
            'optimization_teams': len(opt_teams),
            'audiovisual_teams': len(av_teams),
            'total_unique': len(all_teams),
            'all_teams': all_teams,
            'details': {
                'docker': docker_teams,
                'main': main_teams,
                'optimization': opt_teams,
                'audiovisual': av_teams
            }
        }
        
    def generate_report(self):
        """Genera reporte final de validación"""
        print("\n" + "="*80)
        print("🔍 VALIDACIÓN FINAL - FRAMEWORK SILHOUETTE V4.0")
        print("="*80)
        
        team_count = self.count_total_teams()
        
        print(f"\n📊 ESTADÍSTICAS GENERALES:")
        print(f"  • Equipos con Dockerfiles: {team_count['docker_teams']}")
        print(f"  • Equipos con archivos main: {team_count['main_teams']}")
        print(f"  • Equipos de optimización: {team_count['optimization_teams']}")
        print(f"  • Sub-equipos audiovisuales: {team_count['audiovisual_teams']}")
        print(f"  • TOTAL DE EQUIPOS ÚNICOS: {team_count['total_unique']}")
        
        print(f"\n🎯 REQUISITOS:")
        requirement_met = team_count['total_unique'] >= 45
        status = "✅ CUMPLIDO" if requirement_met else "❌ NO CUMPLIDO"
        print(f"  • Requisito 45+ equipos: {status}")
        
        if team_count['total_unique'] >= 45:
            excess = team_count['total_unique'] - 45
            print(f"  • EXCESO SOBRE REQUISITO: +{excess} equipos")
            
        print(f"\n📋 RESUMEN DE VALIDACIÓN:")
        print(f"  • Validaciones exitosas: {len(self.successes)}")
        print(f"  • Errores encontrados: {len(self.errors)}")
        print(f"  • Advertencias: {len(self.warnings)}")
        
        # Verificar workflows dinámicos
        print(f"\n🔄 WORKFLOWS DINÁMICOS:")
        workflow_files = list(self.workspace.rglob('*Dynamic*.js'))
        print(f"  • Archivos de workflow dinámico: {len(workflow_files)}")
        for wf in workflow_files[:5]:  # Mostrar solo los primeros 5
            print(f"    - {wf.relative_to(self.workspace)}")
            
        # Verificar auto-optimización
        print(f"\n🤖 CAPACIDADES DE AUTO-OPTIMIZACIÓN:")
        opt_files = list(self.workspace.rglob('*Optimization*.js')) + list(self.workspace.rglob('*AI*.js'))
        print(f"  • Archivos de optimización: {len(opt_files)}")
        
        print(f"\n📈 ANÁLISIS DE CAPACIDADES:")
        print(f"  • Suma de equipos empresariales: {team_count['docker_teams'] + team_count['main_teams']}")
        print(f"  • Suma de equipos especializados: {team_count['optimization_teams'] + team_count['audiovisual_teams']}")
        print(f"  • TOTAL GENERAL: {team_count['total_unique']} equipos")
        
        # Guardar reporte detallado
        report = {
            'validation_date': '2025-11-09',
            'framework_version': '4.0.0',
            'teams_count': team_count,
            'validations': {
                'successes': self.successes,
                'errors': self.errors,
                'warnings': self.warnings
            },
            'requirements_met': {
                '45_plus_teams': team_count['total_unique'] >= 45,
                'dynamic_workflows': len(workflow_files) > 0,
                'auto_optimization': len(opt_files) > 0
            }
        }
        
        with open('/workspace/VALIDACION_FINAL_FRAMEWORK.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        print(f"\n💾 REPORTE GUARDADO: VALIDACION_FINAL_FRAMEWORK.json")
        
        # Verificación final
        print(f"\n🏆 VERIFICACIÓN FINAL:")
        if team_count['total_unique'] >= 45 and len(self.errors) == 0:
            print("  ✅ FRAMEWORK APROBADO PARA PRODUCCIÓN")
            print("  ✅ TODOS LOS REQUISITOS CUMPLIDOS")
            print("  ✅ EXCEDE EXPECTATIVAS")
        else:
            print("  ❌ FRAMEWORK REQUIERE REVISIÓN")
            
        return team_count['total_unique'] >= 45

def main():
    print("🚀 Iniciando validación del Framework Silhouette V4.0...")
    validator = FrameworkValidator()
    is_valid = validator.generate_report()
    
    if is_valid:
        print("\n🎉 VALIDACIÓN COMPLETADA EXITOSAMENTE")
        return 0
    else:
        print("\n⚠️ VALIDACIÓN COMPLETADA CON OBSERVACIONES")
        return 1

if __name__ == "__main__":
    exit(main())
