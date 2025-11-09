/**
 * Sistema de Recolección de Métricas
 * Framework Silhouette V4.0
 * 
 * @author MiniMax Agent
 * @version 4.0.0
 */

import { v4 as uuidv4 } from 'uuid';

class MetricsCollector {
    constructor(component = 'Framework') {
        this.component = component;
        this.metrics = new Map();
        this.counters = new Map();
        this.gauges = new Map();
        this.histograms = new Map();
        this.startTime = Date.now();
        
        // Configurar métricas por defecto
        this.initializeDefaultMetrics();
    }

    /**
     * Inicializar métricas por defecto
     */
    initializeDefaultMetrics() {
        this.setGauge('framework.start_time', this.startTime);
        this.setCounter('framework.reboots', 0);
        this.setGauge('framework.memory_usage', 0);
        this.setGauge('framework.cpu_usage', 0);
    }

    /**
     * Configurar contador
     */
    setCounter(name, value = 0) {
        this.counters.set(name, {
            name,
            value,
            type: 'counter',
            component: this.component,
            timestamp: Date.now()
        });
    }

    /**
     * Incrementar contador
     */
    incrementCounter(name, increment = 1) {
        const counter = this.counters.get(name);
        if (counter) {
            counter.value += increment;
            counter.lastUpdate = Date.now();
        } else {
            this.setCounter(name, increment);
        }
    }

    /**
     * Configurar gauge (medida actual)
     */
    setGauge(name, value) {
        this.gauges.set(name, {
            name,
            value,
            type: 'gauge',
            component: this.component,
            timestamp: Date.now()
        });
    }

    /**
     * Actualizar gauge
     */
    updateGauge(name, value) {
        this.setGauge(name, value);
    }

    /**
     * Registrar tiempo de una operación
     */
    recordTimer(name, duration) {
        const histogram = this.histograms.get(name);
        if (!histogram) {
            this.histograms.set(name, {
                name,
                values: [],
                type: 'histogram',
                component: this.component,
                timestamp: Date.now()
            });
        }
        
        this.histograms.get(name).values.push({
            duration,
            timestamp: Date.now()
        });
    }

    /**
     * Registrar evento de proyecto audiovisual
     */
    recordProjectCompletion(projectData) {
        const projectId = projectData.projectId || uuidv4();
        
        this.incrementCounter('audiovisual.projects.completed');
        this.incrementCounter('audiovisual.projects.total_duration', projectData.duration);
        this.recordTimer('audiovisual.project_duration', projectData.duration);
        
        // Calcular promedio de calidad
        this.updateGauge('audiovisual.average_quality', projectData.quality);
        
        // Métricas por fases
        if (projectData.phases) {
            this.updateGauge('audiovisual.phases.average_count', projectData.phases);
        }
        
        this.logger?.info('Proyecto audiovisual completado', {
            projectId,
            duration: projectData.duration,
            quality: projectData.quality
        });
    }

    /**
     * Registrar fallo de proyecto
     */
    recordProjectFailure(failureData) {
        this.incrementCounter('audiovisual.projects.failed');
        
        this.logger?.error('Proyecto audiovisual falló', {
            projectId: failureData.projectId,
            error: failureData.error,
            duration: failureData.duration
        });
    }

    /**
     * Registrar búsqueda de imágenes
     */
    recordImageSearch(searchData) {
        this.incrementCounter('audiovisual.images.searched', searchData.searched || 0);
        this.incrementCounter('audiovisual.images.found', searchData.found || 0);
        this.incrementCounter('audiovisual.images.downloaded', searchData.downloaded || 0);
        this.recordTimer('audiovisual.image_search_duration', searchData.duration || 0);
    }

    /**
     * Registrar QA
     */
    recordQAValidation(qaData) {
        this.updateGauge('audiovisual.qa.overall_score', qaData.score || 0);
        this.incrementCounter('audiovisual.qa.validations');
        
        if (qaData.passed) {
            this.incrementCounter('audiovisual.qa.passed');
        } else {
            this.incrementCounter('audiovisual.qa.failed');
        }
    }

    /**
     * Registrar actividad de framework
     */
    recordFrameworkActivity(activity) {
        this.incrementCounter('framework.activities.total');
        
        switch (activity.type) {
            case 'team_creation':
                this.incrementCounter('framework.teams.created');
                break;
            case 'task_assignment':
                this.incrementCounter('framework.tasks.assigned');
                break;
            case 'task_completion':
                this.incrementCounter('framework.tasks.completed');
                break;
            case 'error':
                this.incrementCounter('framework.errors');
                break;
        }
    }

    /**
     * Recolectar métricas del sistema
     */
    collectSystemMetrics() {
        // Uso de memoria
        const memUsage = process.memoryUsage();
        this.updateGauge('system.memory.heap_used', memUsage.heapUsed);
        this.updateGauge('system.memory.heap_total', memUsage.heapTotal);
        this.updateGauge('system.memory.external', memUsage.external);
        this.updateGauge('system.memory.rss', memUsage.rss);

        // CPU (aproximado)
        const cpuUsage = process.cpuUsage();
        this.updateGauge('system.cpu.user', cpuUsage.user);
        this.updateGauge('system.cpu.system', cpuUsage.system);

        // Uptime
        this.updateGauge('framework.uptime', Date.now() - this.startTime);

        // Estado de eventos de Node.js
        this.updateGauge('system.eventloop.lag', this.measureEventLoopLag());

        return this.getCurrentMetrics();
    }

    /**
     * Medir lag del event loop
     */
    measureEventLoopLag() {
        const start = process.hrtime.bigint();
        
        setImmediate(() => {
            const end = process.hrtime.bigint();
            return Number(end - start) / 1000000; // Convertir a milisegundos
        });
        
        return 0; // Placeholder
    }

    /**
     * Recolectar métricas específicas del framework
     */
    collectFrameworkMetrics(components) {
        Object.entries(components).forEach(([component, metrics]) => {
            if (metrics) {
                this.updateGauge(`framework.component.${component}.health`, 
                    metrics.isHealthy ? 1 : 0);
                
                if (metrics.activeTasks) {
                    this.updateGauge(`framework.component.${component}.active_tasks`, 
                        metrics.activeTasks);
                }
                
                if (metrics.utilization) {
                    this.updateGauge(`framework.component.${component}.utilization`, 
                        metrics.utilization);
                }
            }
        });
    }

    /**
     * Obtener métricas actuales
     */
    getCurrentMetrics() {
        return {
            component: this.component,
            timestamp: Date.now(),
            counters: Object.fromEntries(this.counters),
            gauges: Object.fromEntries(this.gauges),
            histograms: Object.fromEntries(
                Array.from(this.histograms.entries()).map(([name, data]) => [
                    name, 
                    {
                        ...data,
                        values: data.values.slice(-100) // Solo últimos 100 valores
                    }
                ])
            )
        };
    }

    /**
     * Obtener métricas de rendimiento
     */
    getPerformanceMetrics() {
        const uptime = Date.now() - this.startTime;
        const completed = this.counters.get('audiovisual.projects.completed')?.value || 0;
        const failed = this.counters.get('audiovisual.projects.failed')?.value || 0;
        const totalProjects = completed + failed;
        
        return {
            uptime,
            projects: {
                total: totalProjects,
                completed,
                failed,
                success_rate: totalProjects > 0 ? (completed / totalProjects) * 100 : 0
            },
            average_duration: this.calculateAverageDuration(),
            memory_usage: this.getMemoryUsage(),
            cpu_usage: this.getCPUUsage()
        };
    }

    /**
     * Calcular duración promedio de proyectos
     */
    calculateAverageDuration() {
        const histogram = this.histograms.get('audiovisual.project_duration');
        if (!histogram || histogram.values.length === 0) {
            return 0;
        }
        
        const total = histogram.values.reduce((sum, item) => sum + item.duration, 0);
        return total / histogram.values.length;
    }

    /**
     * Obtener uso de memoria
     */
    getMemoryUsage() {
        const memUsage = process.memoryUsage();
        return {
            heap_used: memUsage.heapUsed,
            heap_total: memUsage.heapTotal,
            external: memUsage.external,
            rss: memUsage.rss,
            percentage: (memUsage.heapUsed / memUsage.heapTotal) * 100
        };
    }

    /**
     * Obtener uso de CPU
     */
    getCPUUsage() {
        const cpuUsage = process.cpuUsage();
        return {
            user: cpuUsage.user,
            system: cpuUsage.system
        };
    }

    /**
     * Exportar métricas para Prometheus
     */
    exportPrometheusFormat() {
        const metrics = [];
        
        // Contadores
        for (const [name, data] of this.counters) {
            metrics.push(`${name}{component="${this.component}"} ${data.value}`);
        }
        
        // Gauges
        for (const [name, data] of this.gauges) {
            metrics.push(`${name}{component="${this.component}"} ${data.value}`);
        }
        
        return metrics.join('\n');
    }

    /**
     * Resetear métricas
     */
    reset() {
        this.counters.clear();
        this.gauges.clear();
        this.histograms.clear();
        this.startTime = Date.now();
        this.initializeDefaultMetrics();
    }

    /**
     * Verificar estado de salud del sistema de métricas
     */
    isHealthy() {
        return {
            status: 'healthy',
            component: this.component,
            startTime: this.startTime,
            metricsCount: this.counters.size + this.gauges.size + this.histograms.size
        };
    }
}

export { MetricsCollector };