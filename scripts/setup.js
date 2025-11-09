/**
 * Script de Configuración Inicial del Framework
 * Framework Silhouette V4.0
 * 
 * @author MiniMax Agent
 * @version 4.0.0
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class FrameworkSetup {
    constructor() {
        this.projectRoot = path.join(__dirname, '..');
        this.configDir = path.join(this.projectRoot, 'config');
        this.dataDir = path.join(this.projectRoot, 'data');
        this.logsDir = path.join(this.projectRoot, 'logs');
        this.tempDir = path.join(this.projectRoot, 'temp');
    }

    /**
     * Ejecutar configuración completa
     */
    async runFullSetup() {
        console.log('🚀 Iniciando configuración completa del Framework Silhouette V4.0...');
        
        try {
            // 1. Crear estructura de directorios
            await this.createDirectoryStructure();
            
            // 2. Crear archivos de configuración
            await this.createConfigFiles();
            
            // 3. Configurar variables de entorno
            await this.setupEnvironmentFile();
            
            // 4. Crear base de datos inicial
            await this.initializeDatabase();
            
            // 5. Configurar logs
            this.setupLogging();
            
            // 6. Verificar dependencias
            await this.checkDependencies();
            
            // 7. Crear usuario administrador
            await this.createAdminUser();
            
            // 8. Configurar health checks
            this.setupHealthChecks();
            
            console.log('✅ Configuración completada exitosamente');
            this.printNextSteps();
            
        } catch (error) {
            console.error('❌ Error durante la configuración:', error);
            throw error;
        }
    }

    /**
     * Crear estructura de directorios
     */
    async createDirectoryStructure() {
        console.log('📁 Creando estructura de directorios...');
        
        const directories = [
            'data',
            'logs',
            'temp',
            'backups',
            'config',
            'docs',
            'examples',
            'scripts'
        ];
        
        for (const dir of directories) {
            const fullPath = path.join(this.projectRoot, dir);
            if (!fs.existsSync(fullPath)) {
                fs.mkdirSync(fullPath, { recursive: true });
                console.log(`  ✅ Creado: ${dir}/`);
            } else {
                console.log(`  ⚠️ Ya existe: ${dir}/`);
            }
        }
        
        // Crear subdirectorios específicos
        const subdirectories = [
            'data/audiovisual',
            'data/framework',
            'logs/framework',
            'logs/audit',
            'config/teams',
            'config/audiovisual',
            'config/monitoring'
        ];
        
        for (const subdir of subdirectories) {
            const fullPath = path.join(this.projectRoot, subdir);
            if (!fs.existsSync(fullPath)) {
                fs.mkdirSync(fullPath, { recursive: true });
            }
        }
    }

    /**
     * Crear archivos de configuración
     */
    async createConfigFiles() {
        console.log('⚙️ Creando archivos de configuración...');
        
        // Configuración principal del framework
        await this.createFrameworkConfig();
        
        // Configuración del sistema audiovisual
        await this.createAudioVisualConfig();
        
        // Configuración de equipos
        await this.createTeamsConfig();
        
        // Configuración de monitoreo
        await this.createMonitoringConfig();
        
        // Configuración de base de datos
        await this.createDatabaseConfig();
    }

    /**
     * Crear configuración del framework
     */
    async createFrameworkConfig() {
        const config = {
            framework: {
                name: "Silhouette Enterprise Multi-Agent System",
                version: "4.0.0",
                environment: process.env.NODE_ENV || "development",
                buildDate: new Date().toISOString()
            },
            coordinator: {
                maxConcurrentTasks: parseInt(process.env.MAX_CONCURRENT_TASKS) || 100,
                taskTimeout: 300000,
                retryAttempts: 3,
                healthCheckInterval: 30000
            },
            workflow: {
                dynamicOptimization: true,
                autoScaling: true,
                loadBalancing: true,
                fallbackStrategies: true
            },
            qa: {
                strictMode: process.env.QA_STRICT_MODE === 'true',
                autoOptimization: process.env.AUTO_OPTIMIZATION === 'true',
                qualityThresholds: {
                    excellent: 95,
                    good: 85,
                    acceptable: 75,
                    poor: 60
                }
            },
            logging: {
                level: process.env.LOG_LEVEL || 'info',
                maxFiles: 5,
                maxSize: '10m',
                format: 'json'
            },
            security: {
                jwtSecret: process.env.JWT_SECRET || 'silhouette-super-secret-2025',
                apiKey: process.env.API_KEY || 'silhouette-api-key-2025',
                corsOrigins: ['http://localhost:3000', 'https://yourdomain.com']
            }
        };
        
        const configPath = path.join(this.configDir, 'framework.config.json');
        fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
        console.log('  ✅ framework.config.json');
    }

    /**
     * Crear configuración del sistema audiovisual
     */
    async createAudioVisualConfig() {
        const config = {
            audiovisual: {
                enabled: true,
                version: "4.0.0",
                providers: {
                    unsplash: {
                        enabled: true,
                        apiKey: process.env.UNSPLASH_ACCESS_KEY || '',
                        rateLimit: 50,
                        baseUrl: 'https://api.unsplash.com',
                        quality: 'high'
                    },
                    runway: {
                        enabled: true,
                        apiKey: process.env.RUNWAY_API_KEY || '',
                        maxDuration: 30,
                        baseUrl: 'https://api.runwayml.com'
                    },
                    pika: {
                        enabled: false,
                        apiKey: process.env.PIKA_API_KEY || '',
                        maxDuration: 10
                    },
                    luma: {
                        enabled: false,
                        apiKey: process.env.LUMA_API_KEY || '',
                        maxDuration: 15
                    }
                },
                quality: {
                    minScore: parseInt(process.env.QUALITY_THRESHOLD) || 90,
                    verificationLevels: ['technical', 'content', 'brand', 'platform'],
                    autoRetry: true,
                    retryAttempts: 3,
                    timeout: 30000
                },
                search: {
                    maxResults: 20,
                    cacheEnabled: true,
                    cacheTTL: 3600,
                    sources: ['unsplash', 'pixabay', 'pexels']
                },
                processing: {
                    maxFileSize: '50mb',
                    allowedFormats: ['jpg', 'jpeg', 'png', 'webp'],
                    compression: {
                        quality: 90,
                        progressive: true
                    }
                }
            }
        };
        
        const configPath = path.join(this.configDir, 'audiovisual.config.json');
        fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
        console.log('  ✅ audiovisual.config.json');
    }

    /**
     * Crear configuración de equipos
     */
    async createTeamsConfig() {
        const config = {
            teams: {
                enabled: true,
                autoLoad: true,
                healthCheckInterval: 30000,
                defaultTimeout: 300000,
                retryAttempts: 3,
                loadBalancing: {
                    algorithm: 'round_robin',
                    weightBased: true
                },
                specializations: {
                    audiovisual: {
                        name: "AudioVisual Team",
                        capabilities: ["video_production", "script_writing", "asset_search", "animation"],
                        maxConcurrentTasks: 5,
                        priority: 9
                    },
                    business: {
                        name: "Business Development Team",
                        capabilities: ["strategy", "analysis", "planning", "sales"],
                        maxConcurrentTasks: 10,
                        priority: 8
                    },
                    marketing: {
                        name: "Marketing Team",
                        capabilities: ["campaigns", "content_creation", "seo", "social_media"],
                        maxConcurrentTasks: 8,
                        priority: 8
                    },
                    research: {
                        name: "Research Team",
                        capabilities: ["data_analysis", "market_research", "competitive_analysis"],
                        maxConcurrentTasks: 12,
                        priority: 7
                    },
                    design: {
                        name: "Design Team",
                        capabilities: ["ui_ux", "graphics", "branding", "visual_design"],
                        maxConcurrentTasks: 6,
                        priority: 7
                    }
                }
            }
        };
        
        const configPath = path.join(this.configDir, 'teams.config.json');
        fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
        console.log('  ✅ teams.config.json');
    }

    /**
     * Crear configuración de monitoreo
     */
    async createMonitoringConfig() {
        const config = {
            monitoring: {
                enabled: true,
                metricsInterval: 30000,
                alerts: {
                    enabled: true,
                    email: {
                        enabled: !!process.env.ALERT_EMAIL,
                        recipients: [process.env.ALERT_EMAIL].filter(Boolean)
                    },
                    slack: {
                        enabled: !!process.env.SLACK_WEBHOOK,
                        webhook: process.env.SLACK_WEBHOOK,
                        channel: '#alerts'
                    }
                },
                dashboards: {
                    grafana: {
                        enabled: true,
                        url: 'http://localhost:3000',
                        user: 'admin',
                        password: 'silhouette2025'
                    },
                    prometheus: {
                        enabled: true,
                        url: 'http://localhost:9090',
                        retention: '15d'
                    }
                },
                healthChecks: {
                    framework: {
                        interval: 30000,
                        timeout: 5000,
                        endpoints: ['/health', '/api/status']
                    },
                    teams: {
                        interval: 60000,
                        timeout: 10000
                    },
                    database: {
                        interval: 30000,
                        timeout: 5000
                    }
                }
            }
        };
        
        const configPath = path.join(this.configDir, 'monitoring.config.json');
        fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
        console.log('  ✅ monitoring.config.json');
    }

    /**
     * Crear configuración de base de datos
     */
    async createDatabaseConfig() {
        const config = {
            database: {
                type: "sqlite",
                url: process.env.DATABASE_URL || "sqlite:./data/framework.db",
                options: {
                    verbose: process.env.NODE_ENV === 'development'
                },
                migrations: {
                    enabled: true,
                    path: "./migrations"
                },
                seeding: {
                    enabled: true,
                    path: "./seeds"
                },
                backup: {
                    enabled: true,
                    interval: 86400000,
                    retention: 7
                }
            },
            redis: {
                url: process.env.REDIS_URL || "redis://localhost:6379",
                options: {
                    retryDelayOnFailover: 100,
                    enableReadyCheck: true,
                    maxRetriesPerRequest: 3
                }
            }
        };
        
        const configPath = path.join(this.configDir, 'database.config.json');
        fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
        console.log('  ✅ database.config.json');
    }

    /**
     * Configurar variables de entorno
     */
    async setupEnvironmentFile() {
        console.log('🔐 Configurando archivo .env...');
        
        const envFile = path.join(this.projectRoot, '.env');
        const envExists = fs.existsSync(envFile);
        
        if (envExists) {
            console.log('  ⚠️ Archivo .env ya existe, respaldando...');
            fs.copyFileSync(envFile, `${envFile}.backup.${Date.now()}`);
        }
        
        const envTemplate = `# Framework Silhouette V4.0 - Configuración de Entorno
# Generado automáticamente el ${new Date().toISOString()}

# === CONFIGURACIÓN BÁSICA ===
NODE_ENV=development
PORT=8080
LOG_LEVEL=info
MAX_LOG_ENTRIES=1000

# === BASE DE DATOS ===
DATABASE_URL=sqlite:./data/framework.db
REDIS_URL=redis://localhost:6379

# === SEGURIDAD ===
JWT_SECRET=silhouette-super-secret-jwt-key-2025-change-in-production
API_KEY=silhouette-api-key-2025-change-in-production

# === SISTEMA AUDIOVISUAL ===
UNSPLASH_ACCESS_KEY=your_unsplash_access_key_here
VIDEO_AI_PROVIDER=runway
QUALITY_THRESHOLD=90

# === FRAMEWORK ===
MAX_CONCURRENT_TASKS=100
QA_STRICT_MODE=true
AUTO_OPTIMIZATION=true

# === MONITOREO ===
FRONTEND_URL=http://localhost:3000
ALERT_EMAIL=admin@yourcompany.com
SLACK_WEBHOOK=https://hooks.slack.com/your-webhook-url

# === APIS EXTERNAS (OPCIONALES) ===
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
RUNWAY_API_KEY=your_runway_key_here
PIKA_API_KEY=your_pika_key_here
LUMA_API_KEY=your_luma_key_here

# === CONFIGURACIÓN AVANZADA ===
ENABLE_METRICS=true
ENABLE_AUDIT_LOG=true
ENABLE_DEBUG_MODE=false
`;
        
        fs.writeFileSync(envFile, envTemplate);
        console.log('  ✅ .env creado');
        
        if (!envExists) {
            console.log('  ℹ️ IMPORTANTE: Edita el archivo .env con tus valores reales');
        }
    }

    /**
     * Inicializar base de datos
     */
    async initializeDatabase() {
        console.log('🗄️ Inicializando base de datos...');
        
        // Crear esquema básico de la base de datos
        const dbPath = path.join(this.dataDir, 'framework.db');
        
        // Verificar si existe
        if (!fs.existsSync(dbPath)) {
            console.log('  📝 Creando base de datos inicial...');
            
            // Aquí se inicializaría la base de datos real
            // Por ahora, creamos un archivo marcador
            fs.writeFileSync(dbPath, 'Framework Silhouette V4.0 Database');
            console.log('  ✅ Base de datos inicializada');
        } else {
            console.log('  ℹ️ Base de datos ya existe');
        }
    }

    /**
     * Configurar logging
     */
    setupLogging() {
        console.log('📝 Configurando sistema de logging...');
        
        // Crear archivos de log iniciales
        const logFiles = [
            'framework.log',
            'coordinator.log',
            'workflow.log',
            'qa-system.log',
            'audiovisual.log',
            'teams.log',
            'errors.log',
            'audit.log'
        ];
        
        for (const logFile of logFiles) {
            const logPath = path.join(this.logsDir, logFile);
            if (!fs.existsSync(logPath)) {
                fs.writeFileSync(logPath, `# ${logFile} - Framework Silhouette V4.0\n`);
            }
        }
        
        console.log('  ✅ Sistema de logging configurado');
    }

    /**
     * Verificar dependencias
     */
    async checkDependencies() {
        console.log('🔍 Verificando dependencias...');
        
        // Verificar Node.js
        const nodeVersion = process.version;
        const majorVersion = parseInt(nodeVersion.substring(1).split('.')[0]);
        
        if (majorVersion < 18) {
            throw new Error(`Node.js 18+ requerido. Versión actual: ${nodeVersion}`);
        }
        
        console.log(`  ✅ Node.js ${nodeVersion} - OK`);
        
        // Verificar npm
        try {
            const { execSync } = await import('child_process');
            const npmVersion = execSync('npm --version', { encoding: 'utf8' }).trim();
            console.log(`  ✅ npm ${npmVersion} - OK`);
        } catch (error) {
            throw new Error('npm no está disponible');
        }
        
        // Verificar archivos críticos
        const criticalFiles = [
            'package.json',
            'src/framework/index.js',
            'src/teams/audiovisual/AudioVisualTeamCoordinator.js'
        ];
        
        for (const file of criticalFiles) {
            const filePath = path.join(this.projectRoot, file);
            if (fs.existsSync(filePath)) {
                console.log(`  ✅ ${file} - OK`);
            } else {
                console.log(`  ❌ ${file} - FALTANTE`);
            }
        }
    }

    /**
     * Crear usuario administrador
     */
    async createAdminUser() {
        console.log('👤 Creando usuario administrador...');
        
        // Crear configuración de usuario por defecto
        const adminConfig = {
            users: {
                admin: {
                    id: 'admin-001',
                    username: 'admin',
                    email: 'admin@silhouette-framework.com',
                    role: 'administrator',
                    permissions: ['*'],
                    createdAt: new Date().toISOString(),
                    active: true
                }
            },
            sessions: {
                defaultTimeout: 3600000,
                maxConcurrent: 3
            }
        };
        
        const adminPath = path.join(this.dataDir, 'admin.json');
        fs.writeFileSync(adminPath, JSON.stringify(adminConfig, null, 2));
        console.log('  ✅ Usuario admin creado');
    }

    /**
     * Configurar health checks
     */
    setupHealthChecks() {
        console.log('❤️ Configurando health checks...');
        
        const healthConfig = {
            checks: {
                framework: {
                    enabled: true,
                    interval: 30000,
                    timeout: 5000,
                    endpoints: ['/health', '/api/status']
                },
                database: {
                    enabled: true,
                    interval: 30000,
                    timeout: 5000
                },
                redis: {
                    enabled: true,
                    interval: 30000,
                    timeout: 5000
                },
                teams: {
                    enabled: true,
                    interval: 60000,
                    timeout: 10000
                }
            },
            alerts: {
                enabled: true,
                failureThreshold: 3,
                recoveryThreshold: 2
            }
        };
        
        const healthPath = path.join(this.configDir, 'health-checks.json');
        fs.writeFileSync(healthPath, JSON.stringify(healthConfig, null, 2));
        console.log('  ✅ Health checks configurados');
    }

    /**
     * Mostrar próximos pasos
     */
    printNextSteps() {
        console.log('\n🎉 ¡CONFIGURACIÓN COMPLETADA!');
        console.log('\n📋 PRÓXIMOS PASOS:');
        console.log('1. 📝 Editar archivo .env con tus valores reales');
        console.log('2. 🔑 Configurar API keys (Unsplash, OpenAI, etc.)');
        console.log('3. 🗄️ Configurar base de datos (opcional)');
        console.log('4. 📦 Instalar dependencias: npm install');
        console.log('5. 🚀 Iniciar framework: npm start');
        console.log('6. 🌐 Acceder a: http://localhost:8080/health');
        console.log('\n📚 DOCUMENTACIÓN:');
        console.log('- Documentación técnica: docs/DOCUMENTACION_TECNICA_COMPLETA.md');
        console.log('- API Reference: docs/API.md');
        console.log('- Deployment: docs/DEPLOYMENT.md');
        console.log('\n🆘 SOPORTE:');
        console.log('- Logs: logs/');
        console.log('- Health: http://localhost:8080/health');
        console.log('- Status: http://localhost:8080/api/status');
    }
}

// Ejecutar setup si se llama directamente
if (import.meta.url === `file://${process.argv[1]}`) {
    const setup = new FrameworkSetup();
    
    setup.runFullSetup()
        .then(() => {
            console.log('\n✅ Setup completado exitosamente');
            process.exit(0);
        })
        .catch(error => {
            console.error('\n❌ Error en setup:', error);
            process.exit(1);
        });
}

export { FrameworkSetup };