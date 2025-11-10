#!/usr/bin/env node

/**
 * EJEMPLO DE INTEGRACIÓN: Context Management Team
 * Muestra cómo los equipos existentes pueden usar el sistema de contexto avanzado
 * Framework Silhouette V4.0
 */

const axios = require('axios');

class ContextIntegrationExample {
    constructor() {
        this.contextAPI = 'http://localhost:8070';
        this.teamExamples = [
            'marketing_team',
            'sales_team', 
            'research_team',
            'strategy_team',
            'finance_team'
        ];
    }

    /**
     * Simula cómo un equipo de Marketing añadiría contexto
     */
    async simulateMarketingContext() {
        console.log('🏢 Simulando contexto de Marketing Team...\n');

        // Añadir contexto de campaña
        await this.addContextToTeam('marketing_team', 
            'Q3 Campaign Results: ROI improved 25% through targeted email marketing. Conversion rate: 4.2%',
            0.9
        );

        // Añadir insights de audiencia
        await this.addContextToTeam('marketing_team',
            'Audience Analysis: 65% mobile users, peak engagement 7-9 PM, preferred content: video tutorials',
            0.8
        );

        // Añadir estrategia de contenido
        await this.addContextToTeam('marketing_team',
            'Content Strategy 2025: Focus on video content, influencer partnerships, interactive campaigns',
            0.85
        );

        console.log('✅ Contexto de Marketing añadido exitosamente\n');
    }

    /**
     * Simula cómo el equipo de Sales accedería a contexto de Marketing
     */
    async simulateSalesCrossTeamIntelligence() {
        console.log('💼 Simulando inteligencia cruzada de Sales...\n');

        // Sales busca insights de marketing
        console.log('🔍 Sales buscando insights de Marketing...');
        const marketingInsights = await this.searchContext('campaign performance conversion', {
            includeTeams: ['marketing_team'],
            similarityThreshold: 0.6
        });

        console.log('📊 Insights encontrados:');
        marketingInsights.results.forEach((result, index) => {
            console.log(`  ${index + 1}. [${result.teamId}] ${Math.round(result.similarity * 100)}% similar`);
            console.log(`     ${result.content.substring(0, 100)}...`);
        });

        // Sales añade su propio contexto
        await this.addContextToTeam('sales_team',
            'Using marketing insights: 4.2% conversion rate helps qualify leads. Mobile optimization critical.',
            0.9
        );

        console.log('\n✅ Inteligencia cruzada completada\n');
    }

    /**
     * Simula cómo Strategy combina contexto de múltiples equipos
     */
    async simulateStrategyCrossFunctionalAnalysis() {
        console.log('🎯 Simulando análisis estratégico cruzado...\n');

        // Añadir contexto estratégico
        await this.addContextToTeam('strategy_team',
            'Strategic Priority Q4: Digital transformation, customer experience focus, operational efficiency',
            0.95
        );

        await this.addContextToTeam('strategy_team',
            'Market Analysis: Competitor advantage in mobile experience. Need to accelerate digital initiatives.',
            0.9
        );

        // Buscar insights de todos los equipos
        console.log('🔍 Buscando insights estratégicos en todos los equipos...');
        const strategicInsights = await this.searchContext('digital transformation customer experience', {
            excludeTeams: ['strategy_team'], // Excluir propias búsquedas
            similarityThreshold: 0.5
        });

        console.log('📈 Insights estratégicos encontrados:');
        strategicInsights.results.forEach((result, index) => {
            console.log(`  ${index + 1}. [${result.teamId}] ${Math.round(result.similarity * 100)}% similar`);
            console.log(`     ${result.content.substring(0, 80)}...`);
            console.log('');
        });

        console.log('✅ Análisis estratégico completado\n');
    }

    /**
     * Simula optimización de contexto en tiempo real
     */
    async simulateContextOptimization() {
        console.log('⚡ Simulando optimización de contexto...\n');

        for (const team of this.teamExamples) {
            // Comprimir contexto del equipo
            const compressionResult = await this.compressTeamContext(team);
            if (compressionResult.success) {
                console.log(`📊 ${team}: ${compressionResult.compressionRatio.toFixed(2)} ratio - ${compressionResult.compressedTokens} tokens`);
            }
        }

        console.log('\n✅ Optimización de contexto completada\n');
    }

    /**
     * Muestra el estado general del sistema
     */
    async showSystemOverview() {
        console.log('📊 ESTADO GENERAL DEL SISTEMA DE CONTEXTO\n');
        console.log('═'.repeat(50));

        // Estado general
        const overview = await this.getSystemOverview();
        console.log(`🏢 Equipos totales: ${overview.totalTeams}`);
        console.log(`🔄 Equipos activos: ${overview.activeTeams}`);
        console.log(`💾 Total tokens: ${overview.totalTokens.toLocaleString()}`);
        console.log(`📈 Compresión promedio: ${(overview.avgCompressionRatio * 100).toFixed(1)}%`);
        console.log(`💚 Salud del sistema: ${overview.systemHealth}`);

        console.log('\n📋 DETALLE POR EQUIPOS:\n');

        // Estado por equipo
        for (const team of this.teamExamples) {
            const teamStats = await this.getTeamStats(team);
            if (teamStats) {
                console.log(`🏷️  ${team}:`);
                console.log(`   Tokens: ${teamStats.totalTokens.toLocaleString()}`);
                console.log(`   Compresión: ${(teamStats.compressionRatio * 100).toFixed(1)}%`);
                console.log(`   Capas activas: ${teamStats.activeLayers}`);
                console.log('');
            }
        }

        console.log('═'.repeat(50));
    }

    // Métodos de API helper
    async addContextToTeam(teamId, message, importance = 0.8) {
        try {
            const response = await axios.post(`${this.contextAPI}/context/team/${teamId}/message`, {
                message,
                importance
            });
            return response.data;
        } catch (error) {
            console.error(`Error adding context to ${teamId}:`, error.message);
            return null;
        }
    }

    async searchContext(query, options = {}) {
        try {
            const response = await axios.post(`${this.contextAPI}/context/search/semantic`, {
                query,
                ...options
            });
            return response.data;
        } catch (error) {
            console.error('Error searching context:', error.message);
            return { results: [] };
        }
    }

    async compressTeamContext(teamId) {
        try {
            const response = await axios.post(`${this.contextAPI}/context/team/${teamId}/compress`);
            return response.data;
        } catch (error) {
            console.error(`Error compressing ${teamId}:`, error.message);
            return { success: false };
        }
    }

    async getTeamStats(teamId) {
        try {
            const response = await axios.get(`${this.contextAPI}/context/team/${teamId}/stats`);
            return response.data.stats;
        } catch (error) {
            return null;
        }
    }

    async getSystemOverview() {
        try {
            const response = await axios.get(`${this.contextAPI}/context/overview`);
            return response.data.overview;
        } catch (error) {
            console.error('Error getting system overview:', error.message);
            return {};
        }
    }

    /**
     * Ejecuta el demo completo
     */
    async runDemo() {
        console.log('🧠 DEMO: INTEGRACIÓN AVANZADA DE CONTEXTO');
        console.log('Framework Silhouette V4.0 - Sistema de Gestión Inteligente\n');

        try {
            // Verificar que el servicio esté corriendo
            await axios.get(`${this.contextAPI}/health`);
            console.log('✅ Context Management Team está activo\n');

            // Ejecutar simulaciones
            await this.simulateMarketingContext();
            await this.simulateSalesCrossTeamIntelligence();
            await this.simulateStrategyCrossFunctionalAnalysis();
            await this.simulateContextOptimization();
            await this.showSystemOverview();

            console.log('🎉 DEMO COMPLETADO EXITOSAMENTE');
            console.log('\n💡 Próximos pasos:');
            console.log('1. Acceder al dashboard: http://localhost:8070/dashboard/');
            console.log('2. Integrar APIs con equipos existentes');
            console.log('3. Configurar webhooks para sincronización');
            console.log('4. Monitorear métricas de rendimiento');

        } catch (error) {
            console.error('❌ Error ejecutando demo:', error.message);
            console.log('\n🔧 Asegúrate de que el Context Management Team esté corriendo:');
            console.log('   node /workspace/context_management_team/main.js');
        }
    }
}

// Ejecutar demo
if (require.main === module) {
    const demo = new ContextIntegrationExample();
    demo.runDemo();
}

module.exports = ContextIntegrationExample;