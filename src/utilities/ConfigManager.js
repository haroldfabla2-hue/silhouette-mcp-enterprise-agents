/**
 * Sistema de Gestión de Configuración
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

class ConfigManager {
    constructor() {
        this.config = new Map();
        this.configFiles = new Map();
        this.isLoaded = false;
        
        // Rutas de configuración
        this.configDir = path.join(process.cwd(), 'config');
        this.configFile = path.join(this.configDir, 'framework.config.json');
        this.envFile = path.join(process.cwd(), '.env');
        
        // Cargar configuración
        this.loadConfiguration();
    }

    /**
     * Cargar toda la configuración
     */
    loadConfiguration() {
        try {
            // Cargar variables de entorno
            this.loadEnvironmentVariables();
            
            // Cargar archivos de configuración
            this.loadConfigFiles();
            
            // Cargar configuración de componentes
            this.loadComponentConfigs();
            
            this.isLoaded = true;
        } catch (error) {
            console.error('Error cargando configuración:', error);
            throw error;
        }
    }

    /**
     * Cargar variables de entorno
     */
    loadEnvironmentVariables() {
        // Configuración básica del framework
        this.set('NODE_ENV', process.env.NODE_ENV || 'development');
        this.set('PORT', parseInt(process.env.PORT) || 8080);
        this.set('LOG_LEVEL', process.env.LOG_LEVEL || 'info');
        this.set('MAX_LOG_ENTRIES', parseInt(process.env.MAX_LOG_ENTRIES) || 1000);
        
        // Configuración de base de datos
        this.set('DATABASE_URL', process.env.DATABASE_URL || 'sqlite:./data/framework.db');
        this.set('REDIS_URL', process.env.REDIS_URL || 'redis://localhost:6379');
        
        // Configuración de seguridad
        this.set('JWT_SECRET', process.env.JWT_SECRET || 'silhouette-super-secret-2025');
        this.set('API_KEY', process.env.API_KEY || 'silhouette-api-key-2025');
        
        // Configuración del sistema audiovisual
        this.set('UNSPLASH_ACCESS_KEY', process.env.UNSPLASH_ACCESS_KEY || '');
        this.set('VIDEO_AI_PROVIDER', process.env.VIDEO_AI_PROVIDER || 'runway');
        this.set('QUALITY_THRESHOLD', parseInt(process.env.QUALITY_THRESHOLD) || 90);
        
        // Configuración del framework
        this.set('MAX_CONCURRENT_TASKS', parseInt(process.env.MAX_CONCURRENT_TASKS) || 100);
        this.set('QA_STRICT_MODE', process.env.QA_STRICT_MODE === 'true');
        this.set('AUTO_OPTIMIZATION', process.env.AUTO_OPTIMIZATION === 'true');
        
        // URLs de servicios
        this.set('FRONTEND_URL', process.env.FRONTEND_URL || 'http://localhost:3000');
        this.set('MONITORING_URL', process.env.MONITORING_URL || 'http://localhost:3000');
    }

    /**
     * Cargar archivos de configuración
     */
    loadConfigFiles() {
        // Cargar configuración principal
        if (fs.existsSync(this.configFile)) {
            try {
                const configData = JSON.parse(fs.readFileSync(this.configFile, 'utf8'));
                this.mergeConfig('main', configData);
            } catch (error) {
                console.warn(`Error cargando archivo de configuración: ${error.message}`);
            }
        }
        
        // Cargar configuraciones específicas
        const configFiles = [
            'audiovisual.config.json',
            'teams.config.json',
            'framework.config.json',
            'database.config.json',
            'monitoring.config.json'
        ];
        
        for (const fileName of configFiles) {
            const filePath = path.join(this.configDir, fileName);
            if (fs.existsSync(filePath)) {
                try {
                    const configData = JSON.parse(fs.readFileSync(filePath, 'utf8'));
                    const configName = fileName.replace('.config.json', '');
                    this.mergeConfig(configName, configData);
                } catch (error) {
                    console.warn(`Error cargando ${fileName}: ${error.message}`);
                }
            }
        }
    }

    /**
     * Cargar configuraciones de componentes
     */
    loadComponentConfigs() {
        // Configuración del sistema audiovisual
        this.set('audiovisual', {
            enabled: true,
            providers: {
                unsplash: {
                    enabled: true,
                    rateLimit: 50,
                    quality: 'high'
                },
                runway: {
                    enabled: true,
                    apiKey: this.get('UNSPLASH_ACCESS_KEY'),
                    maxDuration: 30
                },
                pika: {
                    enabled: false,
                    apiKey: ''
                },
                luma: {
                    enabled: false,
                    apiKey: ''
                }
            },
            quality: {
                minScore: this.get('QUALITY_THRESHOLD'),
                verificationLevels: ['technical', 'content', 'brand', 'platform'],
                autoRetry: true,
                retryAttempts: 3
            }
        });
        
        // Configuración de equipos
        this.set('teams', {
            enabled: true,
            autoLoad: true,
            healthCheckInterval: 30000,
            maxTasks: this.get('MAX_CONCURRENT_TASKS'),
            defaultTimeout: 300000,
            retryAttempts: 3
        });
        
        // Configuración de QA
        this.set('qa', {
            strictMode: this.get('QA_STRICT_MODE'),
            autoOptimization: this.get('AUTO_OPTIMIZATION'),
            qualityThresholds: {
                excellent: 95,
                good: 85,
                acceptable: 75,
                poor: 60
            },
            validationLevels: ['technical', 'content', 'performance', 'legal']
        });
        
        // Configuración de workflow
        this.set('workflow', {
            dynamicOptimization: true,
            autoScaling: true,
            loadBalancing: true,
            fallbackStrategies: true,
            performanceMonitoring: true
        });
        
        // Configuración de monitoreo
        this.set('monitoring', {
            enabled: true,
            metricsInterval: 30000,
            alerts: {
                enabled: true,
                email: process.env.ALERT_EMAIL || '',
                slack: process.env.SLACK_WEBHOOK || ''
            },
            dashboards: {
                grafana: true,
                prometheus: true
            }
        });
    }

    /**
     * Fusionar configuración
     */
    mergeConfig(section, configData) {
        if (typeof configData === 'object' && configData !== null) {
            this.config.set(section, {
                ...this.config.get(section),
                ...configData
            });
        }
    }

    /**
     * Establecer valor de configuración
     */
    set(key, value) {
        this.config.set(key, value);
    }

    /**
     * Obtener valor de configuración
     */
    get(key, defaultValue = null) {
        return this.config.has(key) ? this.config.get(key) : defaultValue;
    }

    /**
     * Obtener configuración de sección
     */
    getSection(section) {
        return this.config.get(section) || {};
    }

    /**
     * Verificar si existe configuración
     */
    has(key) {
        return this.config.has(key);
    }

    /**
     * Eliminar configuración
     */
    delete(key) {
        return this.config.delete(key);
    }

    /**
     * Obtener todas las configuraciones
     */
    getAll() {
        return Object.fromEntries(this.config);
    }

    /**
     * Validar configuración
     */
    validate() {
        const errors = [];
        
        // Validaciones requeridas
        const required = [
            'NODE_ENV',
            'PORT',
            'DATABASE_URL',
            'JWT_SECRET'
        ];
        
        for (const key of required) {
            if (!this.has(key)) {
                errors.push(`Configuración requerida faltante: ${key}`);
            }
        }
        
        // Validaciones de tipos
        if (this.has('PORT') && typeof this.get('PORT') !== 'number') {
            errors.push('PORT debe ser un número');
        }
        
        if (this.has('MAX_CONCURRENT_TASKS') && typeof this.get('MAX_CONCURRENT_TASKS') !== 'number') {
            errors.push('MAX_CONCURRENT_TASKS debe ser un número');
        }
        
        if (this.has('QUALITY_THRESHOLD') && (this.get('QUALITY_THRESHOLD') < 0 || this.get('QUALITY_THRESHOLD') > 100)) {
            errors.push('QUALITY_THRESHOLD debe estar entre 0 y 100');
        }
        
        return {
            valid: errors.length === 0,
            errors
        };
    }

    /**
     * Guardar configuración
     */
    save(section = 'main') {
        if (!fs.existsSync(this.configDir)) {
            fs.mkdirSync(this.configDir, { recursive: true });
        }
        
        const configData = this.getSection(section);
        const filePath = path.join(this.configDir, `${section}.config.json`);
        
        try {
            fs.writeFileSync(filePath, JSON.stringify(configData, null, 2));
            return true;
        } catch (error) {
            console.error(`Error guardando configuración ${section}:`, error);
            return false;
        }
    }

    /**
     * Recargar configuración
     */
    reload() {
        this.config.clear();
        this.loadConfiguration();
    }

    /**
     * Obtener configuración para despliegue
     */
    getDeploymentConfig() {
        return {
            environment: this.get('NODE_ENV'),
            services: {
                framework: {
                    port: this.get('PORT'),
                    environment: this.get('NODE_ENV')
                },
                database: {
                    url: this.get('DATABASE_URL')
                },
                redis: {
                    url: this.get('REDIS_URL')
                },
                audiovisual: this.getSection('audiovisual'),
                teams: this.getSection('teams'),
                qa: this.getSection('qa')
            },
            security: {
                jwtSecret: this.get('JWT_SECRET'),
                apiKey: this.get('API_KEY')
            },
            monitoring: this.getSection('monitoring')
        };
    }

    /**
     * Verificar estado de salud del config manager
     */
    isHealthy() {
        return {
            status: this.isLoaded ? 'healthy' : 'unloaded',
            configKeys: this.config.size,
            validation: this.validate()
        };
    }
}

export { ConfigManager };