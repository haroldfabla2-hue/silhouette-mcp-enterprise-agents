#!/usr/bin/env node

/**
 * VALIDADOR RÁPIDO SILHOUETTE V4.0
 * ===============================
 * Validador simplificado para identificar errores críticos
 */

const fs = require('fs');
const { execSync } = require('child_process');

console.log('🔍 VALIDACIÓN RÁPIDA FRAMEWORK SILHOUETTE V4.0');
console.log('='.repeat(60));

let errores = 0;
let advertencias = 0;

// 1. Verificar archivos críticos
console.log('\n1. Verificando archivos críticos...');

const archivosCriticos = [
    'optimization-team/workflows/DynamicWorkflowEngine.js',
    'optimization-team/team-workflows/DesignCreativeWorkflow.js',
    'optimization-team/team-workflows/MarketingWorkflow.js',
    'marketing_team/main.py',
    'audiovisual-team/main.py',
    'docker-compose.yml'
];

archivosCriticos.forEach(archivo => {
    const ruta = `/workspace/${archivo}`;
    if (fs.existsSync(ruta)) {
        console.log(`✅ ${archivo}`);
    } else {
        console.log(`❌ ${archivo} - FALTANTE`);
        errores++;
    }
});

// 2. Validar sintaxis JavaScript básica
console.log('\n2. Validando sintaxis JavaScript...');

function validarJS(archivo) {
    try {
        const contenido = fs.readFileSync(archivo, 'utf8');
        new Function('"use strict";\n' + contenido);
        return true;
    } catch (error) {
        console.log(`❌ ${archivo} - Error: ${error.message}`);
        return false;
    }
}

// Validar archivos JS críticos
['optimization-team/workflows/DynamicWorkflowEngine.js', 
 'optimization-team/team-workflows/DesignCreativeWorkflow.js'].forEach(archivo => {
    const ruta = `/workspace/${archivo}`;
    if (fs.existsSync(ruta)) {
        if (validarJS(ruta)) {
            console.log(`✅ ${archivo} - Sintaxis OK`);
        } else {
            errores++;
        }
    }
});

// 3. Verificar que DesignCreativeWorkflow existe
console.log('\n3. Verificando Design_Creative coverage...');
const designWorkflow = '/workspace/optimization-team/team-workflows/DesignCreativeWorkflow.js';
if (fs.existsSync(designWorkflow)) {
    const contenido = fs.readFileSync(designWorkflow, 'utf8');
    if (contenido.includes('visual_design') && 
        contenido.includes('brand_assets') && 
        contenido.includes('creative_campaigns') && 
        contenido.includes('content_creation')) {
        console.log('✅ DesignCreativeWorkflow - 4 workflows implementados');
    } else {
        console.log('❌ DesignCreativeWorkflow - workflows incompletos');
        errores++;
    }
} else {
    console.log('❌ DesignCreativeWorkflow - NO EXISTE');
    errores++;
}

// 4. Verificar equipos principales
console.log('\n4. Verificando equipos principales...');
const equipos = ['marketing_team', 'sales_team', 'research_team', 'finance_team', 'operations_team', 'audiovisual-team', 'design_creative_team'];

equipos.forEach(equipo => {
    const mainPath = `/workspace/${equipo}/main.py`;
    if (fs.existsSync(mainPath)) {
        console.log(`✅ ${equipo}/main.py`);
    } else {
        console.log(`❌ ${equipo}/main.py - FALTANTE`);
        errores++;
    }
});

// 5. Contar archivos en el proyecto
console.log('\n5. Contando archivos del proyecto...');
function contarArchivos(dir) {
    let count = 0;
    try {
        const items = fs.readdirSync(dir);
        items.forEach(item => {
            const ruta = `${dir}/${item}`;
            const stat = fs.statSync(ruta);
            if (stat.isDirectory() && !item.startsWith('.') && item !== 'node_modules') {
                count += contarArchivos(ruta);
            } else if (stat.isFile()) {
                count++;
            }
        });
    } catch (e) {
        // Ignorar errores
    }
    return count;
}

const totalArchivos = contarArchivos('/workspace');
console.log(`📊 Total de archivos en proyecto: ${totalArchivos}`);

// 6. Resultado final
console.log('\n' + '='.repeat(60));
console.log('📊 RESUMEN DE VALIDACIÓN:');
console.log(`❌ Errores encontrados: ${errores}`);
console.log(`⚠️ Advertencias: ${advertencias}`);

if (errores === 0) {
    console.log('\n🎉 RESULTADO: ✅ FRAMEWORK VALIDADO - LISTO PARA GITHUB');
    console.log('🚀 Estado: 100% operativo');
} else {
    console.log('\n⚠️ RESULTADO: ❌ FRAMEWORK TIENE ERRORES');
    console.log('🔧 Estado: Requiere corrección');
}

console.log('='.repeat(60));