/**
 * Port Allocator - Sistema de Asignación Dinámica de Puertos
 * Framework Silhouette V4.0 - 78 Equipos Especializados
 * Autor: MiniMax Agent
 * Fecha: 2025-11-10
 */

const fs = require('fs');
const net = require('net');
const path = require('path');

class PortAllocator {
    constructor() {
        this.startPort = 8000;
        this.endPort = 9000;
        this.configPath = path.join(__dirname, '../config/allocated_ports.json');
        this.allocatedPorts = this.loadAllocatedPorts();
    }

    loadAllocatedPorts() {
        try {
            if (fs.existsSync(this.configPath)) {
                return JSON.parse(fs.readFileSync(this.configPath, 'utf8'));
            }
        } catch (error) {
            console.error('Error loading allocated ports:', error);
        }
        return {};
    }

    saveAllocatedPorts() {
        try {
            const configDir = path.dirname(this.configPath);
            if (!fs.existsSync(configDir)) {
                fs.mkdirSync(configDir, { recursive: true });
            }
            fs.writeFileSync(this.configPath, JSON.stringify(this.allocatedPorts, null, 2));
        } catch (error) {
            console.error('Error saving allocated ports:', error);
        }
    }

    /**
     * Verifica si un puerto está disponible
     * @param {number} port - Puerto a verificar
     * @returns {Promise<boolean>} - true si el puerto está disponible
     */
    async isPortAvailable(port) {
        return new Promise((resolve) => {
            const server = net.createServer();
            server.listen(port, (err) => {
                if (err) {
                    resolve(false);
                } else {
                    server.once('close', () => resolve(true));
                    server.close();
                }
            });
            server.on('error', () => resolve(false));
        });
    }

    /**
     * Encuentra el próximo puerto disponible
     * @param {number} startPort - Puerto inicial para buscar
     * @param {number} maxTries - Máximo número de intentos
     * @returns {Promise<number|null>} - Puerto disponible o null si no encuentra
     */
    async findNextAvailablePort(startPort = this.startPort, maxTries = 100) {
        for (let i = 0; i < maxTries; i++) {
            const port = startPort + i;
            if (port <= this.endPort && await this.isPortAvailable(port)) {
                return port;
            }
        }
        return null;
    }

    /**
     * Asigna un puerto a un servicio
     * @param {string} serviceName - Nombre del servicio
     * @param {number} preferredPort - Puerto preferido (opcional)
     * @returns {Promise<number>} - Puerto asignado
     */
    async allocatePort(serviceName, preferredPort = null) {
        // Si el servicio ya tiene un puerto asignado, lo devuelve
        if (this.allocatedPorts[serviceName]) {
            return this.allocatedPorts[serviceName];
        }

        let assignedPort = null;

        // Si hay un puerto preferido y está disponible, usarlo
        if (preferredPort && await this.isPortAvailable(preferredPort)) {
            assignedPort = preferredPort;
        } else {
            // Buscar el próximo puerto disponible después del último usado
            const usedPorts = Object.values(this.allocatedPorts || {});
            let searchStart = this.startPort;
            
            if (usedPorts.length > 0) {
                const maxUsedPort = Math.max(...usedPorts);
                searchStart = maxUsedPort + 1;
            }
            
            assignedPort = await this.findNextAvailablePort(searchStart);
        }

        if (assignedPort) {
            this.allocatedPorts[serviceName] = assignedPort;
            this.saveAllocatedPorts();
            console.log(`✅ Puerto ${assignedPort} asignado a ${serviceName}`);
        } else {
            throw new Error(`No se pudo asignar un puerto a ${serviceName}`);
        }

        return assignedPort;
    }

    /**
     * Libera un puerto asignado
     * @param {string} serviceName - Nombre del servicio
     */
    freePort(serviceName) {
        if (this.allocatedPorts[serviceName]) {
            delete this.allocatedPorts[serviceName];
            this.saveAllocatedPorts();
            console.log(`🔄 Puerto liberado de ${serviceName}`);
        }
    }

    /**
     * Obtiene información de todos los puertos asignados
     * @returns {Object} - Objeto con todos los puertos asignados
     */
    getAllocatedPorts() {
        return { ...this.allocatedPorts };
    }

    /**
     * Verifica que todos los puertos asignados estén disponibles
     * @returns {Promise<Object>} - Estado de los puertos
     */
    async verifyAllocatedPorts() {
        const verificationResults = {};
        
        for (const [serviceName, port] of Object.entries(this.allocatedPorts || {})) {
            const isAvailable = await this.isPortAvailable(port);
            verificationResults[serviceName] = {
                port: port,
                available: isAvailable,
                status: isAvailable ? '✅ DISPONIBLE' : '❌ OCUPADO'
            };
        }
        
        return verificationResults;
    }

    /**
     * Reinicializa todas las asignaciones de puertos
     */
    resetAllocations() {
        this.allocatedPorts = {};
        this.saveAllocatedPorts();
        console.log('🔄 Todas las asignaciones de puertos han sido reinicializadas');
    }

    /**
     * Obtiene estadísticas de uso de puertos
     * @returns {Object} - Estadísticas de puertos
     */
    getPortStats() {
        const totalPorts = this.endPort - this.startPort + 1;
        const usedPorts = Object.keys(this.allocatedPorts || {}).length;
        const availablePorts = totalPorts - usedPorts;
        
        return {
            startPort: this.startPort,
            endPort: this.endPort,
            totalPorts: totalPorts,
            usedPorts: usedPorts,
            availablePorts: availablePorts,
            usagePercentage: ((usedPorts / totalPorts) * 100).toFixed(2) + '%'
        };
    }
}

module.exports = PortAllocator;

// Ejemplo de uso si se ejecuta directamente
if (require.main === module) {
    (async () => {
        const allocator = new PortAllocator();
        
        console.log('🚀 Verificando sistema de puertos dinámicos...');
        
        // Verificar puertos asignados existentes
        const allocatedPorts = allocator.getAllocatedPorts();
        console.log('📋 Puertos ya asignados:');
        Object.entries(allocatedPorts).forEach(([service, port]) => {
            console.log(`  - ${service}: ${port}`);
        });
        
        // Asignar puertos a nuevos servicios de ejemplo
        const testServices = [
            'nuevo_equipo_marketing',
            'nuevo_equipo_ventas',
            'nuevo_equipo_desarrollo'
        ];
        
        for (const service of testServices) {
            try {
                const port = await allocator.allocatePort(service);
                console.log(`✅ ${service} asignado al puerto ${port}`);
            } catch (error) {
                console.error(`❌ Error asignando puerto a ${service}:`, error.message);
            }
        }
        
        // Mostrar estadísticas finales
        const stats = allocator.getPortStats();
        console.log('\n📊 Estadísticas de puertos:');
        console.log(`  - Puertos totales disponibles: ${stats.totalPorts}`);
        console.log(`  - Puertos utilizados: ${stats.usedPorts}`);
        console.log(`  - Puertos disponibles: ${stats.availablePorts}`);
        console.log(`  - Porcentaje de uso: ${stats.usagePercentage}`);
        
        // Verificar estado de todos los puertos
        console.log('\n🔍 Verificando estado de puertos...');
        const verification = await allocator.verifyAllocatedPorts();
        Object.entries(verification).forEach(([service, info]) => {
            console.log(`  ${info.status} - ${service}:${info.port}`);
        });
    })();
}