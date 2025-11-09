/**
 * Sistema de Logging Avanzado
 * Framework Silhouette V4.0
 * 
 * @author MiniMax Agent
 * @version 4.0.0
 */

import winston from 'winston';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class Logger {
    constructor(component = 'Framework') {
        this.component = component;
        this.logs = [];
        
        // Crear directorio de logs si no existe
        this.logDir = path.join(process.cwd(), 'logs');
        
        // Configurar logger de Winston
        this.logger = winston.createLogger({
            level: process.env.LOG_LEVEL || 'info',
            format: winston.format.combine(
                winston.format.timestamp({
                    format: 'YYYY-MM-DD HH:mm:ss'
                }),
                winston.format.errors({ stack: true }),
                winston.format.json()
            ),
            defaultMeta: { component: this.component },
            transports: [
                // Log a todos los archivos
                new winston.transports.File({ 
                    filename: path.join(this.logDir, 'error.log'), 
                    level: 'error',
                    maxsize: 5242880, // 5MB
                    maxFiles: 5
                }),
                new winston.transports.File({ 
                    filename: path.join(this.logDir, 'combined.log'),
                    maxsize: 5242880, // 5MB
                    maxFiles: 5
                })
            ]
        });

        // También log a consola en desarrollo
        if (process.env.NODE_ENV !== 'production') {
            this.logger.add(new winston.transports.Console({
                format: winston.format.combine(
                    winston.format.colorize(),
                    winston.format.simple()
                )
            }));
        }
    }

    /**
     * Log de información
     */
    info(message, meta = {}) {
        this.logger.info(message, meta);
        this.logs.push({ level: 'info', message, meta, timestamp: new Date() });
        this.trimLogs();
    }

    /**
     * Log de advertencia
     */
    warn(message, meta = {}) {
        this.logger.warn(message, meta);
        this.logs.push({ level: 'warn', message, meta, timestamp: new Date() });
        this.trimLogs();
    }

    /**
     * Log de error
     */
    error(message, error = null, meta = {}) {
        const errorMeta = {
            ...meta,
            error: error?.message || error,
            stack: error?.stack
        };
        
        this.logger.error(message, errorMeta);
        this.logs.push({ 
            level: 'error', 
            message, 
            meta: errorMeta, 
            timestamp: new Date() 
        });
        this.trimLogs();
    }

    /**
     * Log de debug
     */
    debug(message, meta = {}) {
        this.logger.debug(message, meta);
        this.logs.push({ level: 'debug', message, meta, timestamp: new Date() });
        this.trimLogs();
    }

    /**
     * Log de auditoría para acciones críticas
     */
    audit(action, user, meta = {}) {
        const auditLog = {
            action,
            user,
            timestamp: new Date().toISOString(),
            ...meta
        };
        
        this.logger.info(`AUDIT: ${action}`, auditLog);
        this.logs.push({ 
            level: 'audit', 
            message: `AUDIT: ${action}`, 
            meta: auditLog, 
            timestamp: new Date() 
        });
        this.trimLogs();
    }

    /**
     * Crear logger hijo para componentes específicos
     */
    child(component) {
        return new LoggerChild(this.logger, component);
    }

    /**
     * Obtener logs recientes
     */
    getRecentLogs(count = 100) {
        return this.logs.slice(-count);
    }

    /**
     * Obtener logs por nivel
     */
    getLogsByLevel(level) {
        return this.logs.filter(log => log.level === level);
    }

    /**
     * Limpiar logs antiguos
     */
    trimLogs() {
        const maxLogs = parseInt(process.env.MAX_LOG_ENTRIES) || 1000;
        if (this.logs.length > maxLogs) {
            this.logs = this.logs.slice(-maxLogs);
        }
    }

    /**
     * Exportar logs para análisis
     */
    exportLogs(format = 'json') {
        if (format === 'json') {
            return JSON.stringify(this.logs, null, 2);
        }
        return this.logs;
    }

    /**
     * Verificar si el sistema de logging está funcionando
     */
    isHealthy() {
        return this.logger ? true : false;
    }
}

/**
 * Logger hijo para componentes específicos
 */
class LoggerChild {
    constructor(parentLogger, component) {
        this.parent = parentLogger;
        this.component = component;
    }

    info(message, meta = {}) {
        this.parent.info(message, { ...meta, component: this.component });
    }

    warn(message, meta = {}) {
        this.parent.warn(message, { ...meta, component: this.component });
    }

    error(message, error = null, meta = {}) {
        this.parent.error(message, error, { ...meta, component: this.component });
    }

    debug(message, meta = {}) {
        this.parent.debug(message, { ...meta, component: this.component });
    }

    audit(action, user, meta = {}) {
        this.parent.audit(action, user, { ...meta, component: this.component });
    }
}

export { Logger };