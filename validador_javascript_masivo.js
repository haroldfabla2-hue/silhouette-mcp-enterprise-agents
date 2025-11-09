/**
 * VALIDADOR MASIVO DE ARCHIVOS JAVASCRIPT - FRAMEWORK SILHOUETTE V4.0
 * Valida sintaxis de todos los archivos .js del framework
 * 
 * Autor: MiniMax Agent
 * Fecha: 2025-11-09
 * Versión: 1.0
 */

const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const { promisify } = require('util');

const execAsync = promisify(exec);

class JavaScriptValidator {
    constructor() {
        this.stats = {
            totalFiles: 0,
            validFiles: 0,
            invalidFiles: 0,
            errors: [],
            warnings: []
        };
    }

    /**
     * Encuentra todos los archivos JavaScript en el directorio dado
     */
    findJavaScriptFiles(dir, fileList = []) {
        if (!fs.existsSync(dir)) {
            return fileList;
        }

        const files = fs.readdirSync(dir);
        
        files.forEach(file => {
            const filePath = path.join(dir, file);
            const stat = fs.statSync(filePath);
            
            if (stat.isDirectory()) {
                // Excluir directorios de node_modules y similares
                if (!file.startsWith('.') && file !== 'node_modules') {
                    this.findJavaScriptFiles(filePath, fileList);
                }
            } else if (file.endsWith('.js') || file.endsWith('.mjs')) {
                fileList.push(filePath);
            }
        });
        
        return fileList;
    }

    /**
     * Valida la sintaxis de un archivo JavaScript usando Node.js
     */
    async validateJavaScriptFile(filePath) {
        try {
            // Verificar que el archivo existe
            if (!fs.existsSync(filePath)) {
                throw new Error(`File not found: ${filePath}`);
            }

            // Leer el contenido del archivo
            const content = fs.readFileSync(filePath, 'utf8');
            
            // Crear archivo temporal para validación
            const tempFile = `/tmp/validate_${Date.now()}_${path.basename(filePath)}`;
            fs.writeFileSync(tempFile, content);
            
            // Validar sintaxis usando Node.js --check
            try {
                await execAsync(`node --check "${tempFile}"`);
                fs.unlinkSync(tempFile);
                return { valid: true, error: null, file: filePath };
            } catch (syntaxError) {
                fs.unlinkSync(tempFile);
                return { valid: false, error: syntaxError.message, file: filePath };
            }
            
        } catch (error) {
            return { valid: false, error: error.message, file: filePath };
        }
    }

    /**
     * Valida todos los archivos JavaScript encontrados
     */
    async validateAllJavaScriptFiles(directories) {
        console.log('🔍 INICIANDO VALIDACIÓN MASIVA DE JAVASCRIPT');
        console.log('=' * 60);
        
        let allFiles = [];
        
        // Buscar archivos en todos los directorios especificados
        directories.forEach(dir => {
            console.log(`📂 Buscando archivos en: ${dir}`);
            const files = this.findJavaScriptFiles(dir);
            allFiles = allFiles.concat(files);
            console.log(`   ✅ Encontrados ${files.length} archivos .js`);
        });
        
        // Eliminar duplicados
        allFiles = [...new Set(allFiles)];
        
        this.stats.totalFiles = allFiles.length;
        console.log(`\n📊 TOTAL DE ARCHIVOS A VALIDAR: ${allFiles.length}`);
        console.log('=' * 60);
        
        // Validar cada archivo
        for (let i = 0; i < allFiles.length; i++) {
            const filePath = allFiles[i];
            const relativePath = path.relative('/workspace', filePath);
            
            process.stdout.write(`\r🔄 Validando archivo ${i + 1}/${allFiles.length}: ${path.basename(filePath)}`);
            
            const result = await this.validateJavaScriptFile(filePath);
            
            if (result.valid) {
                this.stats.validFiles++;
                process.stdout.write(' ✅');
            } else {
                this.stats.invalidFiles++;
                this.stats.errors.push({
                    file: relativePath,
                    error: result.error
                });
                process.stdout.write(' ❌');
            }
            
            // Mostrar progreso cada 10 archivos
            if ((i + 1) % 10 === 0) {
                console.log();
            }
        }
        
        console.log('\n');
        return this.generateReport();
    }

    /**
     * Genera el reporte final de validación
     */
    generateReport() {
        console.log('\n' + '=' * 60);
        console.log('📋 REPORTE DE VALIDACIÓN JAVASCRIPT');
        console.log('=' * 60);
        
        console.log(`📊 ESTADÍSTICAS GENERALES:`);
        console.log(`   • Total de archivos: ${this.stats.totalFiles}`);
        console.log(`   • Archivos válidos: ${this.stats.validFiles} ✅`);
        console.log(`   • Archivos con errores: ${this.stats.invalidFiles} ❌`);
        console.log(`   • Tasa de éxito: ${((this.stats.validFiles / this.stats.totalFiles) * 100).toFixed(1)}%`);
        
        if (this.stats.errors.length > 0) {
            console.log(`\n❌ ERRORES ENCONTRADOS (${this.stats.errors.length}):`);
            this.stats.errors.forEach((error, index) => {
                console.log(`\n   ${index + 1}. ${error.file}`);
                console.log(`      Error: ${error.error}`);
            });
        } else {
            console.log('\n✅ NO SE ENCONTRARON ERRORES - TODOS LOS ARCHIVOS SON VÁLIDOS');
        }
        
        return this.stats;
    }
}

// Ejecutar validación
async function main() {
    const validator = new JavaScriptValidator();
    
    // Directorios a validar
    const directories = [
        '/workspace/optimization-team',
        '/workspace/orchestrator',
        '/workspace/api_gateway',
        '/workspace/mcp_server',
        '/workspace/planner'
    ];
    
    try {
        const stats = await validator.validateAllJavaScriptFiles(directories);
        
        // Guardar reporte en archivo
        const reportPath = '/workspace/REPORTE_VALIDACION_JAVASCRIPT.json';
        const reportData = {
            timestamp: new Date().toISOString(),
            validation_type: 'javascript_syntax_validation',
            statistics: stats,
            summary: {
                total_files: stats.totalFiles,
                valid_files: stats.validFiles,
                invalid_files: stats.invalidFiles,
                success_rate: (stats.validFiles / stats.totalFiles * 100).toFixed(1) + '%',
                all_valid: stats.invalidFiles === 0
            }
        };
        
        fs.writeFileSync(reportPath, JSON.stringify(reportData, null, 2));
        console.log(`\n💾 Reporte guardado en: ${reportPath}`);
        
    } catch (error) {
        console.error('❌ Error durante la validación:', error);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

module.exports = JavaScriptValidator;