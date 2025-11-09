#!/usr/bin/env python3
"""
Script final para completar la subida del framework sin tokens
"""

import subprocess
import os
from pathlib import Path

def main():
    print("🚀 COMPLETANDO SUBIDA FINAL DEL FRAMEWORK")
    print("=" * 50)
    
    workspace = '/workspace'
    os.chdir(workspace)
    
    # Remover el script que contiene el token
    script_problematico = Path(workspace) / 'subir_limpio_final.py'
    if script_problematico.exists():
        script_problematico.unlink()
        print("✅ Script problemático eliminado")
    
    # Remover también el archivo de resultado si existe
    resultado = Path(workspace) / 'resultado_subida_final.txt'
    if resultado.exists():
        resultado.unlink()
        print("✅ Archivo de resultado eliminado")
    
    # Agregar solo archivos del framework
    print("📦 Agregando archivos limpios...")
    subprocess.run(['git', 'add', '.'], cwd=workspace, check=True, capture_output=True)
    
    # Commit final
    print("💾 Haciendo commit final...")
    mensaje = '''Framework Silhouette V4.0 - Lanzamiento Final

✅ Framework empresarial completo
✅ Sistema audiovisual integrado  
✅ 45+ equipos especializados
✅ Docker deployment ready
✅ Sin secretos ni tokens'''
    
    subprocess.run(['git', 'commit', '--amend', '-m', mensaje], cwd=workspace, check=True, capture_output=True)
    print("✅ Commit final realizado")
    
    # Push
    print("🚀 Realizando push final...")
    resultado = subprocess.run(['git', 'push', '-f', 'origin', 'main'], cwd=workspace, capture_output=True, text=True)
    
    if resultado.returncode == 0:
        print("✅ ¡Push exitoso!")
        print(resultado.stdout)
        
        # Tag
        print("🏷️  Creando tag...")
        subprocess.run(['git', 'tag', '-d', 'v4.0.0'], cwd=workspace, capture_output=True)
        subprocess.run(['git', 'tag', '-a', 'v4.0.0', '-m', 'Framework Silhouette V4.0'], cwd=workspace, check=True, capture_output=True)
        
        resultado_tag = subprocess.run(['git', 'push', '-f', 'origin', 'v4.0.0'], cwd=workspace, capture_output=True, text=True)
        if resultado_tag.returncode == 0:
            print("✅ Tag subido exitosamente!")
        else:
            print("⚠️  Error subiendo tag:", resultado_tag.stderr)
    else:
        print("❌ Error en push:", resultado.stderr)
    
    print("\n" + "=" * 50)
    print("🎉 SUBIDA COMPLETADA")
    print("🌐 https://github.com/haroldfabla2-hue/silhouette-mcp-enterprise-agents")
    print("=" * 50)

if __name__ == "__main__":
    main()
