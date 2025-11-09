#!/bin/bash

echo "🚀 Iniciando push a GitHub..."
echo "📁 Cambiando al directorio del framework..."
cd /workspace/multiagent-framework-expandido

echo "🔧 Verificando estado de git..."
git status

echo "🌐 Verificando remoto..."
git remote -v

echo "📤 Ejecutando push a GitHub..."
git push -u origin main

echo "✅ ¡Push completado exitosamente!"