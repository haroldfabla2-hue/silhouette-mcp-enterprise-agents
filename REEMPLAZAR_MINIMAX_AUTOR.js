#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

/**
 * Script para reemplazar todas las referencias a "Silhouette Anónimo" por "Silhouette Anónimo"
 * en todos los archivos del workspace
 */

const fileTypes = ['.md', '.js', '.py', '.txt', '.json', '.yml', '.yaml', '.ts'];

function shouldProcessFile(filePath) {
    const ext = path.extname(filePath);
    return fileTypes.includes(ext);
}

function replaceMinimaxReferences(content) {
    return content
        .replace(/Silhouette Anónimo/gi, 'Silhouette Anónimo')
        .replace(/minimax\/multiagent-framework/gi, 'silhouette/multiagent-framework')
        .replace(/@minimax\/multiagent-framework/gi, '@silhouette/multiagent-framework');
}

function processDirectory(dir) {
    const items = fs.readdirSync(dir);
    let modifiedFiles = 0;
    let totalChanges = 0;

    for (const item of items) {
        const fullPath = path.join(dir, item);
        const stat = fs.statSync(fullPath);

        if (stat.isDirectory()) {
            // Skip certain directories
            if (item === 'node_modules' || item === '.git' || item === 'user_input_files') {
                continue;
            }
            const subResults = processDirectory(fullPath);
            modifiedFiles += subResults.modifiedFiles;
            totalChanges += subResults.totalChanges;
        } else if (shouldProcessFile(fullPath)) {
            try {
                const content = fs.readFileSync(fullPath, 'utf8');
                const newContent = replaceMinimaxReferences(content);
                
                if (content !== newContent) {
                    fs.writeFileSync(fullPath, newContent, 'utf8');
                    
                    // Count changes
                    const minimaxMatches = content.match(/Silhouette Anónimo/gi) || [];
                    const totalMatches = minimaxMatches.length;
                    
                    modifiedFiles++;
                    totalChanges += totalMatches;
                    
                    console.log(`✅ ${path.relative('.', fullPath)}: ${totalMatches} cambios realizados`);
                }
            } catch (error) {
                console.log(`⚠️  Error procesando ${fullPath}: ${error.message}`);
            }
        }
    }

    return { modifiedFiles, totalChanges };
}

console.log('🔄 Iniciando reemplazo de referencias Silhouette Anónimo → Silhouette Anónimo...\n');

const results = processDirectory('.');

console.log(`\n🎉 Proceso completado:`);
console.log(`   📁 Archivos modificados: ${results.modifiedFiles}`);
console.log(`   🔄 Cambios totales: ${results.totalChanges}`);
console.log(`   ✅ Listo para subir a GitHub sin referencias a MiniMax`);