/**
 * Generate Docker Compose - Generador de Docker Compose con Puertos Dinámicos
 * Framework Silhouette V4.0 - 78 Equipos Especializados
 * Autor: MiniMax Agent
 * Fecha: 2025-11-10
 */

const PortAllocator = require('./port_allocator.cjs');
const fs = require('fs');
const path = require('path');

class DockerComposeGenerator {
    constructor() {
        this.portAllocator = new PortAllocator();
        this.outputPath = path.join(__dirname, '../docker-compose.dynamic-ports.yml');
        this.services = [];
    }

    /**
     * Configuración de servicios base (infraestructura)
     */
    getBaseServices() {
        return [
            {
                name: 'postgres',
                image: 'postgres:15-alpine',
                environment: {
                    POSTGRES_USER: '${POSTGRES_USER:-silhouette}',
                    POSTGRES_PASSWORD: '${POSTGRES_PASSWORD:-silhouette2024}',
                    POSTGRES_DB: '${POSTGRES_DB:-silhouette_db}'
                },
                volumes: [
                    'postgres_data:/var/lib/postgresql/data'
                ],
                networks: ['silhouette_network'],
                restart: 'unless-stopped',
                healthcheck: {
                    test: ['CMD-SHELL', 'pg_isready -U ${POSTGRES_USER:-silhouette}'],
                    interval: '10s',
                    timeout: '5s',
                    retries: 5
                }
            },
            {
                name: 'redis',
                image: 'redis:7-alpine',
                environment: {
                    REDIS_PASSWORD: '${REDIS_PASSWORD:-silhouette2024}'
                },
                command: 'redis-server --requirepass ${REDIS_PASSWORD:-silhouette2024} --appendonly yes --maxmemory 1gb --maxmemory-policy allkeys-lru',
                networks: ['silhouette_network'],
                restart: 'unless-stopped'
            }
        ];
    }

    /**
     * Configuración de equipos empresariales
     */
    getEnterpriseTeams() {
        return [
            { name: 'business_development_team', type: 'team' },
            { name: 'cloud_services_team', type: 'team' },
            { name: 'communications_team', type: 'team' },
            { name: 'context_management_team', type: 'team' },
            { name: 'customer_service_team', type: 'team' },
            { name: 'design_creative_team', type: 'team' },
            { name: 'finance_team', type: 'team' },
            { name: 'hr_team', type: 'team' },
            { name: 'legal_team', type: 'team' },
            { name: 'machine_learning_ai_team', type: 'team' },
            { name: 'manufacturing_team', type: 'team' },
            { name: 'marketing_team', type: 'team' },
            { name: 'notifications_communication_team', type: 'team' },
            { name: 'product_management_team', type: 'team' },
            { name: 'quality_assurance_team', type: 'team' },
            { name: 'research_team', type: 'team' },
            { name: 'risk_management_team', type: 'team' },
            { name: 'sales_team', type: 'team' },
            { name: 'security_team', type: 'team' },
            { name: 'strategy_team', type: 'team' },
            { name: 'supply_chain_team', type: 'team' },
            { name: 'support_team', type: 'team' },
            { name: 'testing_team', type: 'team' },
            { name: 'audiovisual-team', type: 'team' }
        ];
    }

    /**
     * Configuración de equipos de optimización y workflows
     */
    getOptimizationTeams() {
        return [
            { name: 'orchestrator', type: 'service', port: 8000 },
            { name: 'api_gateway', type: 'service', port: 8080 },
            { name: 'master45-coordinator', type: 'workflow' },
            { name: 'dynamic-workflows-coordinator', type: 'workflow' },
            { name: 'workflow-optimization', type: 'workflow' },
            { name: 'dynamic-system-demo', type: 'workflow' },
            { name: 'audiovisual-workflow', type: 'workflow' },
            { name: 'business-continuity', type: 'workflow' },
            { name: 'data-science', type: 'workflow' },
            { name: 'it-infrastructure', type: 'workflow' },
            { name: 'legal-workflow', type: 'workflow' },
            { name: 'marketing-workflow', type: 'workflow' },
            { name: 'research-workflow', type: 'workflow' },
            { name: 'sales-workflow', type: 'workflow' },
            { name: 'strategic-planning', type: 'workflow' },
            { name: 'ultra-robust-qa', type: 'workflow' },
            { name: 'ai-team', type: 'specialized' },
            { name: 'compliance-team', type: 'specialized' },
            { name: 'cybersecurity-team', type: 'specialized' },
            { name: 'data-engineering-team', type: 'specialized' },
            { name: 'ecommerce-team', type: 'specialized' },
            { name: 'education-team', type: 'specialized' },
            { name: 'healthcare-team', type: 'specialized' },
            { name: 'logistics-team', type: 'specialized' },
            { name: 'manufacturing-industry-team', type: 'specialized' },
            { name: 'realestate-team', type: 'specialized' },
            { name: 'change-management', type: 'strategic' },
            { name: 'crisis-management', type: 'strategic' },
            { name: 'global-expansion', type: 'strategic' },
            { name: 'innovation-team', type: 'strategic' },
            { name: 'merger-acquisition', type: 'strategic' },
            { name: 'partnership-team', type: 'strategic' },
            { name: 'audiovisual-technology', type: 'tech' },
            { name: 'animation-prompt-generator', type: 'tech' },
            { name: 'audiovisual-coordinator', type: 'tech' },
            { name: 'prompt-execution-engine', type: 'tech' },
            { name: 'image-search-team', type: 'media' },
            { name: 'image-quality-verifier', type: 'media' },
            { name: 'audiovisual-integration', type: 'media' },
            { name: 'audiovisual-research', type: 'media' },
            { name: 'video-scene-composer', type: 'media' },
            { name: 'professional-script-generator', type: 'media' },
            { name: 'video-strategy-planner', type: 'media' },
            { name: 'requirements-manager', type: 'specialized' },
            { name: 'audit-team', type: 'specialized' },
            { name: 'sustainability-team', type: 'specialized' }
        ];
    }

    /**
     * Genera la configuración de un servicio
     */
    async generateServiceConfig(serviceConfig) {
        const { name, type, port } = serviceConfig;
        
        // Asignar puerto dinámicamente
        const assignedPort = port || await this.portAllocator.allocatePort(name);
        
        const service = {
            container_name: `silhouette_${name}`,
            ports: [`${assignedPort}:8000`],
            networks: ['silhouette_network'],
            restart: 'unless-stopped',
            environment: {
                SERVICE_NAME: name,
                SERVICE_TYPE: type,
                PORT: assignedPort
            },
            depends_on: ['postgres', 'redis']
        };

        // Configuración específica por tipo
        switch (type) {
            case 'team':
                service.build = {
                    context: `../${name}`,
                    dockerfile: 'Dockerfile'
                };
                service.volumes = [
                    `../${name}:/app`
                ];
                service.working_dir = '/app';
                service.command = 'npm start';
                break;
                
            case 'workflow':
            case 'specialized':
            case 'strategic':
            case 'tech':
            case 'media':
                service.build = {
                    context: `../optimization-team/team-workflows`,
                    dockerfile: 'Dockerfile'
                };
                service.working_dir = '/app';
                service.volumes = [
                    `../optimization-team/team-workflows:/app`
                ];
                service.command = `node ${name}.js`;
                break;
                
            case 'service':
                if (name === 'orchestrator') {
                    service.build = {
                        context: `../orchestrator`,
                        dockerfile: 'Dockerfile'
                    };
                    service.volumes = [`../orchestrator:/app`];
                    service.working_dir = '/app';
                    service.command = 'npm start';
                } else if (name === 'api_gateway') {
                    service.build = {
                        context: `../api_gateway`,
                        dockerfile: 'Dockerfile'
                    };
                    service.volumes = [`../api_gateway:/app`];
                    service.working_dir = '/app';
                    service.command = 'npm start';
                }
                break;
        }

        return { ...service, name, assignedPort };
    }

    /**
     * Genera el archivo docker-compose completo
     */
    async generateDockerCompose() {
        console.log('🚀 Generando docker-compose con puertos dinámicos...');

        // Obtener todos los servicios
        const baseServices = this.getBaseServices();
        const enterpriseTeams = this.getEnterpriseTeams();
        const optimizationTeams = this.getOptimizationTeams();

        // Generar servicios base
        for (const baseService of baseServices) {
            const port = await this.portAllocator.allocatePort(baseService.name);
            const service = {
                ...baseService,
                name: baseService.name,
                assignedPort: port,
                ports: baseService.ports || [`${port}:8000`]
            };
            this.services.push(service);
        }

        // Generar equipos empresariales
        for (const team of enterpriseTeams) {
            const service = await this.generateServiceConfig(team);
            this.services.push(service);
        }

        // Generar equipos de optimización
        for (const team of optimizationTeams) {
            const service = await this.generateServiceConfig(team);
            this.services.push(service);
        }

        // Crear el contenido del docker-compose
        const dockerComposeContent = this.createDockerComposeContent();
        
        // Escribir el archivo
        fs.writeFileSync(this.outputPath, dockerComposeContent);
        console.log(`✅ Docker compose generado: ${this.outputPath}`);

        return this.outputPath;
    }

    /**
     * Crea el contenido del archivo docker-compose
     */
    createDockerComposeContent() {
        let content = `# Framework Silhouette V4.0 - Docker Compose con Puertos Dinámicos
# 78 Equipos Especializados - Sistema de Asignación Automática de Puertos
# Autor: MiniMax Agent
# Fecha: 2025-11-10
# Generado automáticamente por PortAllocator

version: '3.8'

services:
`;

        // Agregar servicios base
        content += `  # ===== INFRAESTRUCTURA BASE =====
`;
        for (const service of this.services.filter(s => ['postgres', 'redis'].includes(s.name))) {
            content += this.formatService(service);
        }

        // Agregar servicios principales
        content += `\n  # ===== SERVICIOS PRINCIPALES =====
`;
        for (const service of this.services.filter(s => s.name === 'orchestrator' || s.name === 'api_gateway')) {
            content += this.formatService(service);
        }

        // Agregar equipos empresariales
        content += `\n  # ===== EQUIPOS EMPRESARIALES =====
`;
        for (const service of this.services.filter(s => s.type === 'team')) {
            content += this.formatService(service);
        }

        // Agregar equipos de optimización
        content += `\n  # ===== EQUIPOS DE OPTIMIZACIÓN Y WORKFLOWS =====
`;
        for (const service of this.services.filter(s => s.type && s.type !== 'team')) {
            content += this.formatService(service);
        }

        // Agregar networks y volumes
        content += `
networks:
  silhouette_network:
    driver: bridge

volumes:
  postgres_data:
    driver: local
`;

        return content;
    }

    /**
     * Formatea un servicio para el docker-compose
     */
    formatService(service) {
        let content = `  ${service.name}:
`;

        if (service.image) {
            content += `    image: ${service.image}\n`;
        }

        if (service.build) {
            content += `    build:\n`;
            content += `      context: ${service.build.context}\n`;
            content += `      dockerfile: ${service.build.dockerfile}\n`;
        }

        if (service.container_name) {
            content += `    container_name: ${service.container_name}\n`;
        }

        if (service.ports) {
            service.ports.forEach(port => {
                content += `    ports:\n      - "${port}"\n`;
            });
        }

        if (service.environment) {
            content += `    environment:\n`;
            Object.entries(service.environment).forEach(([key, value]) => {
                content += `      ${key}: ${value}\n`;
            });
        }

        if (service.volumes) {
            content += `    volumes:\n`;
            service.volumes.forEach(volume => {
                content += `      - "${volume}"\n`;
            });
        }

        if (service.networks) {
            content += `    networks:\n`;
            service.networks.forEach(network => {
                content += `      - ${network}\n`;
            });
        }

        if (service.restart) {
            content += `    restart: ${service.restart}\n`;
        }

        if (service.working_dir) {
            content += `    working_dir: ${service.working_dir}\n`;
        }

        if (service.command) {
            content += `    command: ${service.command}\n`;
        }

        if (service.depends_on) {
            content += `    depends_on:\n`;
            service.depends_on.forEach(dep => {
                content += `      - ${dep}\n`;
            });
        }

        if (service.healthcheck) {
            content += `    healthcheck:\n`;
            Object.entries(service.healthcheck).forEach(([key, value]) => {
                content += `      ${key}: ${value}\n`;
            });
        }

        return content + '\n';
    }

    /**
     * Obtiene estadísticas de la generación
     */
    getGenerationStats() {
        return {
            totalServices: this.services.length,
            teams: this.services.filter(s => s.type === 'team').length,
            workflows: this.services.filter(s => s.type === 'workflow').length,
            specialized: this.services.filter(s => s.type === 'specialized').length,
            strategic: this.services.filter(s => s.type === 'strategic').length,
            tech: this.services.filter(s => s.type === 'tech').length,
            media: this.services.filter(s => s.type === 'media').length,
            services: this.services.filter(s => s.type === 'service').length,
            infrastructure: this.services.filter(s => ['postgres', 'redis'].includes(s.name)).length,
            portRange: this.portAllocator.getPortStats()
        };
    }
}

module.exports = DockerComposeGenerator;

// Ejemplo de uso si se ejecuta directamente
if (require.main === module) {
    (async () => {
        const generator = new DockerComposeGenerator();
        
        try {
            const outputFile = await generator.generateDockerCompose();
            const stats = generator.getGenerationStats();
            
            console.log('\n📊 Estadísticas de generación:');
            console.log(`  - Total de servicios: ${stats.totalServices}`);
            console.log(`  - Equipos empresariales: ${stats.teams}`);
            console.log(`  - Workflows: ${stats.workflows}`);
            console.log(`  - Equipos especializados: ${stats.specialized}`);
            console.log(`  - Equipos estratégicos: ${stats.strategic}`);
            console.log(`  - Equipos tecnológicos: ${stats.tech}`);
            console.log(`  - Equipos multimedia: ${stats.media}`);
            console.log(`  - Servicios principales: ${stats.services}`);
            console.log(`  - Infraestructura: ${stats.infrastructure}`);
            console.log(`  - Rango de puertos: ${stats.portRange.startPort}-${stats.portRange.endPort}`);
            
            console.log(`\n✅ Docker compose generado exitosamente: ${outputFile}`);
        } catch (error) {
            console.error('❌ Error generando docker compose:', error);
            process.exit(1);
        }
    })();
}