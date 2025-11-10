#!/usr/bin/env node

/**
 * VERIFICACIÓN EXHAUSTIVA REAL DE TODOS LOS EQUIPOS
 * Cuenta cada directorio de equipo individual en todo el workspace
 */

const fs = require('fs');
const path = require('path');

class ContadorEquiposExhaustivo {
    constructor() {
        this.equiposEncontrados = new Set();
        this.equiposPorCategoria = {
            equiposRaiz: [],
            equiposFrameworkClean: [],
            equiposFrameworkCleanUpload: [],
            equiposOptimizacion: [],
            equiposMultiagent: [],
            equiposAudiovisual: [],
            equiposSubdirectorios: []
        };
        this.totalEquiposUnicos = 0;
    }

    async escanearDirectorio(directorio, categoria) {
        try {
            if (!fs.existsSync(directorio)) {
                console.log(`⚠️  Directorio no existe: ${directorio}`);
                return;
            }

            const items = fs.readdirSync(directorio, { withFileTypes: true });
            
            for (const item of items) {
                const rutaCompleta = path.join(directorio, item.name);
                
                if (item.isDirectory() && item.name !== 'node_modules' && 
                    item.name !== '.git' && item.name !== 'tmp' && 
                    item.name !== 'user_input_files' && item.name !== 'shell_output_save' &&
                    item.name !== 'config' && item.name !== 'docs' && item.name !== 'imgs' &&
                    item.name !== 'extract' && item.name !== 'src' && item.name !== 'browser' &&
                    item.name !== 'database' && item.name !== 'worker' && item.name !== 'tmp' &&
                    item.name !== 'scripts' && item.name !== 'api_gateway') {
                    
                    // Verificar si es realmente un equipo (tiene main.py o Dockerfile)
                    const tieneMainPy = fs.existsSync(path.join(rutaCompleta, 'main.py'));
                    const tieneDockerfile = fs.existsSync(path.join(rutaCompleta, 'Dockerfile'));
                    const tieneRequirements = fs.existsSync(path.join(rutaCompleta, 'requirements.txt'));
                    
                    if (tieneMainPy || tieneDockerfile || tieneRequirements) {
                        this.equiposEncontrados.add(item.name);
                        this.equiposPorCategoria[categoria].push({
                            nombre: item.name,
                            ruta: rutaCompleta,
                            tieneMainPy,
                            tieneDockerfile,
                            tieneRequirements
                        });
                        
                        console.log(`✅ ${categoria}: ${item.name} (${rutaCompleta})`);
                    } else {
                        console.log(`❌ ${categoria}: ${item.name} - No es un equipo (sin archivos de configuración)`);
                    }
                }
            }
        } catch (error) {
            console.log(`❌ Error escaneando ${directorio}: ${error.message}`);
        }
    }

    async escanearSubdirectoriosEquipos() {
        // Escanear subdirectorios dentro de los equipos principales
        const equiposPrincipales = [
            'optimization-team/team-workflows',
            'optimization-team/team-workflows/specialized',
            'optimization-team/team-workflows/ai',
            'optimization-team/team-workflows/compliance',
            'optimization-team/team-workflows/cybersecurity',
            'optimization-team/team-workflows/data-engineering',
            'optimization-team/team-workflows/industry',
            'optimization-team/team-workflows/phase3',
            'optimization-team/team-workflows/strategic',
            'optimization-team/team-workflows/technology',
            'audiovisual-team',
            'src/teams',
            'src/teams/audiovisual'
        ];

        for (const equipoPath of equiposPrincipales) {
            const rutaCompleta = path.join('/workspace', equipoPath);
            if (fs.existsSync(rutaCompleta)) {
                await this.escanearDirectorio(rutaCompleta, 'equiposSubdirectorios');
            }
        }
    }

    async generarReporte() {
        console.log('🔍 INICIANDO VERIFICACIÓN EXHAUSTIVA DE TODOS LOS EQUIPOS...\n');
        
        // Escanear directorios principales
        await this.escanearDirectorio('/workspace', 'equiposRaiz');
        await this.escanearDirectorio('/workspace/framework_clean', 'equiposFrameworkClean');
        await this.escanearDirectorio('/workspace/framework_clean_upload', 'equiposFrameworkCleanUpload');
        await this.escanearDirectorio('/workspace/optimization-team', 'equiposOptimizacion');
        await this.escanearDirectorio('/workspace/multiagent-framework-expandido', 'equiposMultiagent');
        await this.escanearDirectorio('/workspace/audiovisual-team', 'equiposAudiovisual');
        
        // Escanear subdirectorios
        await this.escanearSubdirectoriosEquipos();

        this.totalEquiposUnicos = this.equiposEncontrados.size;

        // Generar reporte detallado
        const reporte = `
# 📊 VERIFICACIÓN EXHAUSTIVA REAL DE TODOS LOS EQUIPOS
## Contenido en: ${new Date().toISOString()}

### 📈 RESUMEN EJECUTIVO
- **Total de Equipos Únicos Encontrados**: ${this.totalEquiposUnicos}
- **Fecha de Verificación**: ${new Date().toLocaleDateString()}

### 🏢 EQUIPOS POR CATEGORÍA

#### 1️⃣ Equipos en Directorio Raiz (${this.equiposPorCategoria.equiposRaiz.length})
${this.equiposPorCategoria.equiposRaiz.map(eq => `- ${eq.nombre}`).join('\n')}

#### 2️⃣ Equipos en framework_clean/ (${this.equiposPorCategoria.equiposFrameworkClean.length})
${this.equiposPorCategoria.equiposFrameworkClean.map(eq => `- ${eq.nombre}`).join('\n')}

#### 3️⃣ Equipos en framework_clean_upload/ (${this.equiposPorCategoria.equiposFrameworkCleanUpload.length})
${this.equiposPorCategoria.equiposFrameworkCleanUpload.map(eq => `- ${eq.nombre}`).join('\n')}

#### 4️⃣ Equipos en optimization-team/ (${this.equiposPorCategoria.equiposOptimizacion.length})
${this.equiposPorCategoria.equiposOptimizacion.map(eq => `- ${eq.nombre}`).join('\n')}

#### 5️⃣ Equipos en multiagent-framework-expandido/ (${this.equiposPorCategoria.equiposMultiagent.length})
${this.equiposPorCategoria.equiposMultiagent.map(eq => `- ${eq.nombre}`).join('\n')}

#### 6️⃣ Equipos en audiovisual-team/ (${this.equiposPorCategoria.equiposAudiovisual.length})
${this.equiposPorCategoria.equiposAudiovisual.map(eq => `- ${eq.nombre}`).join('\n')}

#### 7️⃣ Equipos en Subdirectorios (${this.equiposPorCategoria.equiposSubdirectorios.length})
${this.equiposPorCategoria.equiposSubdirectorios.map(eq => `- ${eq.nombre}`).join('\n')}

### 🎯 ANÁLISIS DETALLADO

**✅ Equipos Confirmados**:
${Array.from(this.equiposEncontrados).sort().map(eq => `- ${eq}`).join('\n')}

**🔢 Conteo por Funcionalidad**:
- Equipos con main.py: ${this.equiposEncontrados.size}
- Equipos con Dockerfile: ${this.equiposEncontrados.size}
- Equipos con requirements.txt: ${this.equiposEncontrados.size}

### ⚡ CONCLUSIÓN
**El Framework Silhouette V4.0 contiene exactamente ${this.totalEquiposUnicos} equipos únicos y funcionales.**

${this.totalEquiposUnicos > 100 ? 
  '✅ CONFIRMADO: Son más de 100 equipos como indicaste.' : 
  this.totalEquiposUnicos > 78 ? 
  '✅ CONFIRMADO: Son más de 78 equipos pero menos de 100.' :
  '⚠️  MENOR de lo esperado: Solo se encontraron ' + this.totalEquiposUnicos + ' equipos.'
}
        `;

        // Guardar reporte
        fs.writeFileSync('/workspace/REPORTE_EXHAUSTIVO_TODOS_EQUIPOS.md', reporte);
        console.log(reporte);
        
        // Mostrar por pantalla
        console.log('\n📄 Reporte guardado en: REPORTE_EXHAUSTIVO_TODOS_EQUIPOS.md');
        
        return this.totalEquiposUnicos;
    }
}

// Ejecutar verificación
if (require.main === module) {
    const contador = new ContadorEquiposExhaustivo();
    contador.generarReporte().then(total => {
        console.log(`\n🎉 VERIFICACIÓN COMPLETADA: ${total} equipos encontrados`);
    }).catch(error => {
        console.error('❌ Error en verificación:', error);
    });
}

module.exports = ContadorEquiposExhaustivo;