#!/usr/bin/env node

/**
 * CONTEXT MANAGEMENT TEAM - Silhouette V4.0 Advanced
 * Sistema Avanzado de Gestión de Contexto para el Framework
 */

const express = require('express');
const cors = require('cors');
const compression = require('compression');
const { v4: uuidv4 } = require('uuid');

class AdvancedContextManager {
    constructor() {
        this.app = express();
        this.port = process.env.CONTEXT_MANAGER_PORT || 8070;
        this.sessions = new Map();
        this.compressionCache = new Map();
        this.vectorCache = new Map();
        this.teams = new Map();
        
        this.config = {
            maxTokensPerLevel: {
                raw: 4000,
                compressed: 8000, 
                summarized: 12000
            },
            compressionThresholds: {
                sentence: 128,
                paragraph: 512,
                document: 2048
            },
            semanticSettings: {
                embeddingDim: 384,
                similarityThreshold: 0.7,
                maxResults: 10
            }
        };
        
        this.setupMiddleware();
        this.setupRoutes();
    }

    setupMiddleware() {
        this.app.use(cors());
        this.app.use(compression());
        this.app.use(express.json({ limit: '10mb' }));
        
        // Logging middleware
        this.app.use((req, res, next) => {
            console.log(`[${new Date().toISOString()}] ${req.method} ${req.path}`);
            next();
        });
    }

    // Context Layer Management
    createContextLayer(type, content, teamId, importance = 0.5) {
        const layer = {
            id: uuidv4(),
            type, // 'raw', 'compressed', 'summarized', 'semantic'
            content,
            tokens: this.estimateTokens(content),
            importance,
            teamId,
            timestamp: new Date().toISOString(),
            metadata: {
                compressionRatio: null,
                similarity: null,
                topics: this.extractTopics(content),
                entities: this.extractEntities(content)
            }
        };

        // Calculate compression ratio
        if (type === 'compressed' || type === 'summarized') {
            const originalTokens = this.estimateTokens(content);
            layer.metadata.compressionRatio = layer.tokens / originalTokens;
        }

        return layer;
    }

    // Team Session Management
    async initializeTeamSession(teamId, teamType = 'enterprise') {
        const session = {
            sessionId: uuidv4(),
            teamId,
            teamType,
            layers: [],
            contextStats: {
                totalTokens: 0,
                compressionRatio: 0,
                activeLayers: 0,
                semanticVectors: 0,
                lastCompression: new Date().toISOString()
            },
            created: new Date().toISOString(),
            lastActivity: new Date().toISOString()
        };

        this.sessions.set(teamId, session);
        this.teams.set(teamId, {
            active: true,
            type: teamType,
            lastSeen: new Date().toISOString(),
            contextLayers: 0
        });

        return session;
    }

    // Add message to team context
    async addTeamMessage(teamId, message, importance = 0.8) {
        let session = this.sessions.get(teamId);
        if (!session) {
            session = await this.initializeTeamSession(teamId);
        }

        const layer = this.createContextLayer('raw', message, teamId, importance);
        session.layers.push(layer);
        
        // Auto-compression if needed
        if (session.layers.length > 10) {
            await this.compressTeamContext(teamId);
        }

        // Update stats
        this.updateContextStats(session);

        return {
            success: true,
            layerId: layer.id,
            stats: session.contextStats
        };
    }

    // Context compression for team
    async compressTeamContext(teamId) {
        const session = this.sessions.get(teamId);
        if (!session) return { success: false, error: 'Team session not found' };

        const rawLayers = session.layers.filter(l => l.type === 'raw');
        if (rawLayers.length < 3) return { success: false, error: 'Not enough data to compress' };

        // Compress by sentences
        const compressedContent = this.compressBySentences(rawLayers.map(l => l.content).join(' '));
        const compressedLayer = this.createContextLayer('compressed', compressedContent, teamId, 0.6);
        
        // Remove old raw layers and add compressed
        session.layers = session.layers.filter(l => l.type !== 'raw');
        session.layers.push(compressedLayer);

        this.updateContextStats(session);
        
        return {
            success: true,
            compressedTokens: compressedLayer.tokens,
            compressionRatio: compressedLayer.metadata.compressionRatio
        };
    }

    // Semantic search across all teams
    async searchSemantic(query, options = {}) {
        const {
            excludeTeams = [],
            includeTeams = null,
            similarityThreshold = 0.7,
            maxResults = 10
        } = options;

        const queryVector = this.generateSimpleEmbedding(query);
        const results = [];

        for (const [teamId, session] of this.sessions) {
            // Skip excluded teams
            if (excludeTeams.includes(teamId)) continue;
            
            // Filter by included teams if specified
            if (includeTeams && !includeTeams.includes(teamId)) continue;

            for (const layer of session.layers) {
                if (layer.type === 'semantic' && layer.metadata.vector) {
                    const similarity = this.cosineSimilarity(queryVector, layer.metadata.vector);
                    
                    if (similarity >= similarityThreshold) {
                        results.push({
                            teamId,
                            layerId: layer.id,
                            content: layer.content.substring(0, 200) + '...',
                            similarity: similarity,
                            type: layer.type,
                            timestamp: layer.timestamp,
                            topics: layer.metadata.topics
                        });
                    }
                }
            }
        }

        // Sort by similarity and return top results
        results.sort((a, b) => b.similarity - a.similarity);
        return results.slice(0, maxResults);
    }

    // Get optimized context for a team
    async getOptimizedContext(teamId, maxTokens = 6000) {
        const session = this.sessions.get(teamId);
        if (!session) return { content: '', stats: null };

        let totalTokens = 0;
        const optimizedContext = [];

        // Prioritize by importance and recency
        const sortedLayers = session.layers.sort((a, b) => {
            const scoreA = a.importance * this.getRecencyWeight(a.timestamp);
            const scoreB = b.importance * this.getRecencyWeight(b.timestamp);
            return scoreB - scoreA;
        });

        for (const layer of sortedLayers) {
            if (totalTokens + layer.tokens <= maxTokens) {
                optimizedContext.push(`[${layer.type.toUpperCase()}] ${layer.content}`);
                totalTokens += layer.tokens;
            }
        }

        return {
            content: optimizedContext.join('\n\n'),
            stats: session.contextStats,
            tokensUsed: totalTokens,
            tokensLimit: maxTokens
        };
    }

    // Generate vector embedding (simplified)
    generateSimpleEmbedding(text) {
        // Simplified embedding generation for demo
        const words = text.toLowerCase().split(' ');
        const vector = new Array(384).fill(0);
        
        words.forEach(word => {
            const hash = this.simpleHash(word) % 384;
            vector[hash] += 1;
        });
        
        // Normalize
        const magnitude = Math.sqrt(vector.reduce((sum, val) => sum + val * val, 0));
        return magnitude > 0 ? vector.map(val => val / magnitude) : vector;
    }

    // Compress by sentences (simplified)
    compressBySentences(content) {
        const sentences = content.split('.').filter(s => s.trim().length > 10);
        if (sentences.length <= 5) return content;
        
        // Keep first 3 and last 2 sentences
        const compressed = [
            ...sentences.slice(0, 3),
            '...',
            ...sentences.slice(-2)
        ].join('. ');
        
        return compressed;
    }

    // Helper methods
    estimateTokens(text) {
        return Math.ceil(text.length / 4); // Rough estimate
    }

    extractTopics(text) {
        // Simplified topic extraction
        const topics = [];
        const words = text.toLowerCase().split(' ');
        const topicKeywords = ['marketing', 'sales', 'research', 'strategy', 'development', 'analysis'];
        
        topicKeywords.forEach(keyword => {
            if (words.some(word => word.includes(keyword))) {
                topics.push(keyword);
            }
        });
        
        return topics;
    }

    extractEntities(text) {
        // Simplified entity extraction
        const entities = [];
        const words = text.split(' ');
        
        words.forEach(word => {
            if (word.match(/^[A-Z][a-z]+$/)) {
                entities.push(word);
            }
        });
        
        return entities;
    }

    simpleHash(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32-bit integer
        }
        return Math.abs(hash);
    }

    cosineSimilarity(vecA, vecB) {
        if (vecA.length !== vecB.length) return 0;
        
        let dotProduct = 0;
        let normA = 0;
        let normB = 0;
        
        for (let i = 0; i < vecA.length; i++) {
            dotProduct += vecA[i] * vecB[i];
            normA += vecA[i] * vecA[i];
            normB += vecB[i] * vecB[i];
        }
        
        const magnitude = Math.sqrt(normA) * Math.sqrt(normB);
        return magnitude > 0 ? dotProduct / magnitude : 0;
    }

    getRecencyWeight(timestamp) {
        const age = Date.now() - new Date(timestamp).getTime();
        const days = age / (1000 * 60 * 60 * 24);
        return Math.max(0.1, 1 - (days / 30)); // Decay over 30 days
    }

    updateContextStats(session) {
        const totalTokens = session.layers.reduce((sum, layer) => sum + layer.tokens, 0);
        const compressedLayers = session.layers.filter(l => l.type === 'compressed');
        const semanticVectors = session.layers.filter(l => l.type === 'semantic').length;
        
        const avgCompression = compressedLayers.length > 0 
            ? compressedLayers.reduce((sum, l) => sum + (l.metadata.compressionRatio || 0), 0) / compressedLayers.length
            : 0;

        session.contextStats = {
            totalTokens,
            compressionRatio: avgCompression,
            activeLayers: session.layers.length,
            semanticVectors,
            lastCompression: new Date().toISOString()
        };

        session.lastActivity = new Date().toISOString();
    }

    // API Routes
    setupRoutes() {
        // Health check
        this.app.get('/health', (req, res) => {
            res.json({
                status: 'healthy',
                timestamp: new Date().toISOString(),
                activeTeams: this.sessions.size,
                totalTeams: this.teams.size
            });
        });

        // Initialize team session
        this.app.post('/context/team/:teamId/init', async (req, res) => {
            try {
                const { teamId } = req.params;
                const { teamType = 'enterprise' } = req.body;
                
                const session = await this.initializeTeamSession(teamId, teamType);
                
                res.json({
                    success: true,
                    session
                });
            } catch (error) {
                res.status(500).json({
                    success: false,
                    error: error.message
                });
            }
        });

        // Add message to team
        this.app.post('/context/team/:teamId/message', async (req, res) => {
            try {
                const { teamId } = req.params;
                const { message, importance = 0.8 } = req.body;
                
                const result = await this.addTeamMessage(teamId, message, importance);
                
                res.json(result);
            } catch (error) {
                res.status(500).json({
                    success: false,
                    error: error.message
                });
            }
        });

        // Get optimized context
        this.app.get('/context/team/:teamId/optimized', async (req, res) => {
            try {
                const { teamId } = req.params;
                const { maxTokens = 6000 } = req.query;
                
                const context = await this.getOptimizedContext(teamId, parseInt(maxTokens));
                
                res.json({
                    success: true,
                    ...context
                });
            } catch (error) {
                res.status(500).json({
                    success: false,
                    error: error.message
                });
            }
        });

        // Semantic search
        this.app.post('/context/search/semantic', async (req, res) => {
            try {
                const { query, ...options } = req.body;
                
                const results = await this.searchSemantic(query, options);
                
                res.json({
                    success: true,
                    results,
                    query
                });
            } catch (error) {
                res.status(500).json({
                    success: false,
                    error: error.message
                });
            }
        });

        // Get team context stats
        this.app.get('/context/team/:teamId/stats', (req, res) => {
            try {
                const { teamId } = req.params;
                const session = this.sessions.get(teamId);
                
                if (!session) {
                    return res.status(404).json({
                        success: false,
                        error: 'Team session not found'
                    });
                }
                
                res.json({
                    success: true,
                    stats: session.contextStats,
                    layers: session.layers.map(l => ({
                        id: l.id,
                        type: l.type,
                        tokens: l.tokens,
                        importance: l.importance,
                        timestamp: l.timestamp
                    }))
                });
            } catch (error) {
                res.status(500).json({
                    success: false,
                    error: error.message
                });
            }
        });

        // Compress context
        this.app.post('/context/team/:teamId/compress', async (req, res) => {
            try {
                const { teamId } = req.params;
                
                const result = await this.compressTeamContext(teamId);
                
                res.json(result);
            } catch (error) {
                res.status(500).json({
                    success: false,
                    error: error.message
                });
            }
        });

        // System overview
        this.app.get('/context/overview', (req, res) => {
            try {
                const overview = {
                    totalTeams: this.teams.size,
                    activeTeams: Array.from(this.teams.values()).filter(t => t.active).length,
                    totalSessions: this.sessions.size,
                    totalLayers: Array.from(this.sessions.values()).reduce((sum, session) => sum + session.layers.length, 0),
                    totalTokens: Array.from(this.sessions.values()).reduce((sum, session) => sum + session.contextStats.totalTokens, 0),
                    avgCompressionRatio: this.calculateSystemCompressionRatio(),
                    systemHealth: 'operational'
                };
                
                res.json({
                    success: true,
                    overview
                });
            } catch (error) {
                res.status(500).json({
                    success: false,
                    error: error.message
                });
            }
        });
    }

    calculateSystemCompressionRatio() {
        const sessions = Array.from(this.sessions.values());
        const compressionRatios = sessions.map(s => s.contextStats.compressionRatio);
        const validRatios = compressionRatios.filter(r => r > 0);
        
        return validRatios.length > 0 
            ? validRatios.reduce((sum, r) => sum + r, 0) / validRatios.length
            : 0;
    }

    start() {
        this.app.listen(this.port, () => {
            console.log(`🧠 Context Management Team started on port ${this.port}`);
            console.log(`📊 Ready to manage context for ${this.teams.size} teams`);
        });
    }
}

// Start the server
if (require.main === module) {
    const contextManager = new AdvancedContextManager();
    contextManager.start();
}

module.exports = AdvancedContextManager;