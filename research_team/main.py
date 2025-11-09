"""
Research Team - HAAS+ Multi-Agent System
========================================

Servicio especializado en investigación y análisis de datos con capacidades de:
- Data Research: Investigación de datos e información
- Web Scraping: Extracción de información web
- Information Analysis: Análisis de información y generación de insights
- Data Mining: Minería de datos y patrones
- Academic Research: Investigación académica y papers

Puerto: 8013
"""

import os
import json
import uuid
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import asyncpg
import redis.asyncio as redis
import httpx
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import structlog
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Configuración de logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Configuración
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://haas:haaspass@localhost:5432/haasdb")
REDIS_URL = os.getenv("REDIS_URL", "redis://:haaspass@localhost:6379")

app = FastAPI(
    title="Research Team",
    description="Investigación y análisis de datos para el sistema HAAS+",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Métricas Prometheus
RESEARCH_REQUESTS = Counter('research_requests_total', 'Total research requests')
RESEARCH_DURATION = Histogram('research_duration_seconds', 'Research duration')
RESEARCH_ERRORS = Counter('research_errors_total', 'Total research errors')
WEB_SCRAPES = Counter('web_scrapes_total', 'Total web scraping operations')
DATA_ANALYSIS = Counter('data_analysis_operations_total', 'Total data analysis operations')
INSIGHTS_GENERATED = Gauge('insights_generated_total', 'Total insights generated')

# Modelos de datos
class ResearchType(str, Enum):
    DATA_MINING = "data_mining"
    WEB_RESEARCH = "web_research"
    ACADEMIC_RESEARCH = "academic_research"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    MARKET_RESEARCH = "market_research"
    TECHNICAL_RESEARCH = "technical_research"
    TREND_ANALYSIS = "trend_analysis"

class ResearchPriority(str, Enum):
    CRITICAL = "P0"
    HIGH = "P1"
    MEDIUM = "P2"
    LOW = "P3"

class ResearchStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ResearchRequest(BaseModel):
    research_type: ResearchType
    query: str = Field(..., description="Consulta de investigación")
    sources: List[str] = Field(default_factory=list, description="URLs o fuentes a investigar")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parámetros de investigación")
    tenant_id: str = Field(..., description="ID del tenant")
    project_id: Optional[str] = Field(None, description="ID del proyecto")
    priority: ResearchPriority = ResearchPriority.MEDIUM
    timeout_seconds: int = Field(300, description="Timeout en segundos")

class ResearchResponse(BaseModel):
    research_id: str
    status: ResearchStatus
    results: Optional[Dict[str, Any]] = None
    insights: Optional[List[Dict[str, Any]]] = None
    summary: str
    execution_time: Optional[float] = None
    sources_analyzed: Optional[int] = None
    data_points_collected: Optional[int] = None

class WebScrapingRequest(BaseModel):
    urls: List[str] = Field(..., description="URLs a scrapear")
    selectors: Dict[str, str] = Field(..., description="Selectors CSS/XPath para extraer datos")
    output_format: str = Field("json", description="Formato de salida: json, csv, xml")
    rate_limit: int = Field(1, description="Delay entre requests en segundos")
    user_agent: Optional[str] = Field(None, description="User agent personalizado")

class DataAnalysisRequest(BaseModel):
    data_sources: List[str] = Field(..., description="Fuentes de datos a analizar")
    analysis_type: str = Field(..., description="Tipo de análisis: statistical, trend, correlation, pattern")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parámetros del análisis")
    output_format: str = Field("json", description="Formato de salida")

class InsightGenerationRequest(BaseModel):
    research_results: List[Dict[str, Any]] = Field(..., description="Resultados de investigación")
    insight_type: str = Field(..., description="Tipo de insight: business, technical, strategic")
    target_audience: str = Field(..., description="Audiencia objetivo: executives, developers, analysts")

class ServiceState:
    def __init__(self):
        self.db_pool: Optional[asyncpg.Pool] = None
        self.redis_client: Optional[redis.Redis] = None
        self.http_client: Optional[httpx.AsyncClient] = None

# Instancia global del estado del servicio
service_state = ServiceState()

class ResearchService:
    """Servicio principal de investigación"""
    
    def __init__(self):
        self.logger = logger.bind(service="Research")
    
    async def initialize(self):
        """Inicializar conexiones a base de datos y servicios"""
        try:
            # Conexión a PostgreSQL
            self.db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=5, max_size=20)
            
            # Cliente Redis
            self.redis_client = redis.from_url(REDIS_URL, decode_responses=True)
            
            # Cliente HTTP con configuración para scraping
            self.http_client = httpx.AsyncClient(
                timeout=30.0,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
            )
            
            # Crear tablas necesarias
            await self._create_tables()
            
            self.logger.info("Research service initialized successfully")
            
        except Exception as e:
            self.logger.error("Failed to initialize Research service", error=str(e))
            raise
    
    async def _create_tables(self):
        """Crear tablas para investigación"""
        async with self.db_pool.acquire() as conn:
            # Tabla de investigaciones
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS research_jobs (
                    research_id UUID PRIMARY KEY,
                    research_type TEXT NOT NULL,
                    query TEXT NOT NULL,
                    sources TEXT[] DEFAULT '{}',
                    parameters JSONB DEFAULT '{}',
                    tenant_id TEXT NOT NULL,
                    project_id TEXT,
                    priority TEXT DEFAULT 'P2',
                    status TEXT DEFAULT 'pending',
                    results JSONB DEFAULT '{}',
                    insights JSONB DEFAULT '[]',
                    summary TEXT DEFAULT '',
                    execution_time FLOAT,
                    sources_analyzed INTEGER DEFAULT 0,
                    data_points_collected INTEGER DEFAULT 0,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    completed_at TIMESTAMPTZ,
                    agent_id TEXT NOT NULL DEFAULT 'research_team'
                );
            """)
            
            # Tabla de web scraping
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS web_scraping_jobs (
                    job_id UUID PRIMARY KEY,
                    urls TEXT[] NOT NULL,
                    selectors JSONB NOT NULL,
                    output_format TEXT DEFAULT 'json',
                    rate_limit INTEGER DEFAULT 1,
                    user_agent TEXT,
                    results JSONB DEFAULT '{}',
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    completed_at TIMESTAMPTZ
                );
            """)
            
            # Tabla de análisis de datos
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS data_analysis_jobs (
                    analysis_id UUID PRIMARY KEY,
                    data_sources TEXT[] NOT NULL,
                    analysis_type TEXT NOT NULL,
                    parameters JSONB DEFAULT '{}',
                    output_format TEXT DEFAULT 'json',
                    results JSONB DEFAULT '{}',
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    completed_at TIMESTAMPTZ
                );
            """)
            
            # Tabla de insights
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS generated_insights (
                    insight_id UUID PRIMARY KEY,
                    research_ids TEXT[] NOT NULL,
                    insight_type TEXT NOT NULL,
                    target_audience TEXT NOT NULL,
                    content JSONB NOT NULL,
                    confidence_score FLOAT,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)
            
            # Índices para optimización
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_research_jobs_tenant ON research_jobs(tenant_id);
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_research_jobs_type ON research_jobs(research_type);
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_research_jobs_status ON research_jobs(status);
            """)
            
            self.logger.info("Database tables created successfully")
    
    async def conduct_research(self, request: ResearchRequest) -> ResearchResponse:
        """Realizar investigación según tipo y parámetros"""
        try:
            RESEARCH_REQUESTS.inc()
            start_time = datetime.now()
            
            research_id = str(uuid.uuid4())
            
            # Insertar job en la base de datos
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO research_jobs (
                        research_id, research_type, query, sources, parameters,
                        tenant_id, project_id, priority, status, agent_id
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """, research_id, request.research_type.value, request.query, request.sources,
                request.parameters, request.tenant_id, request.project_id, 
                request.priority.value, "in_progress", "research_team")
            
            # Ejecutar investigación según el tipo
            if request.research_type == ResearchType.WEB_RESEARCH:
                results = await self._conduct_web_research(request)
            elif request.research_type == ResearchType.DATA_MINING:
                results = await self._conduct_data_mining(request)
            elif request.research_type == ResearchType.ACADEMIC_RESEARCH:
                results = await self._conduct_academic_research(request)
            elif request.research_type == ResearchType.COMPETITOR_ANALYSIS:
                results = await self._conduct_competitor_analysis(request)
            elif request.research_type == ResearchType.MARKET_RESEARCH:
                results = await self._conduct_market_research(request)
            elif request.research_type == ResearchType.TECHNICAL_RESEARCH:
                results = await self._conduct_technical_research(request)
            elif request.research_type == ResearchType.TREND_ANALYSIS:
                results = await self._conduct_trend_analysis(request)
            else:
                results = await self._conduct_general_research(request)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            sources_analyzed = len(request.sources) if request.sources else 0
            data_points_collected = len(results.get("data_points", [])) if isinstance(results, dict) else 0
            
            # Generar resumen automático
            summary = self._generate_research_summary(request.research_type.value, results)
            
            # Actualizar job en la base de datos
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE research_jobs 
                    SET results = $1, insights = $2, summary = $3, execution_time = $4,
                        sources_analyzed = $5, data_points_collected = $6, status = $7,
                        completed_at = NOW()
                    WHERE research_id = $8
                """, results, results.get("insights", []), summary, execution_time,
                sources_analyzed, data_points_collected, "completed", research_id)
            
            RESEARCH_DURATION.observe(execution_time)
            
            self.logger.info(
                "Research completed",
                research_id=research_id,
                research_type=request.research_type,
                execution_time=execution_time,
                sources_analyzed=sources_analyzed
            )
            
            return ResearchResponse(
                research_id=research_id,
                status=ResearchStatus.COMPLETED,
                results=results,
                insights=results.get("insights", []),
                summary=summary,
                execution_time=execution_time,
                sources_analyzed=sources_analyzed,
                data_points_collected=data_points_collected
            )
            
        except Exception as e:
            RESEARCH_ERRORS.inc()
            
            # Actualizar job como fallido
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE research_jobs 
                    SET status = $1, completed_at = NOW()
                    WHERE research_id = $2
                """, "failed", research_id)
            
            self.logger.error("Research failed", error=str(e), research_id=research_id)
            
            return ResearchResponse(
                research_id=research_id,
                status=ResearchStatus.FAILED,
                summary=f"Research failed: {str(e)}"
            )
    
    async def _conduct_web_research(self, request: ResearchRequest) -> Dict[str, Any]:
        """Realizar investigación web"""
        results = {
            "type": "web_research",
            "query": request.query,
            "sources_analyzed": len(request.sources),
            "data_points": [],
            "insights": [],
            "summary_stats": {}
        }
        
        # Cache de resultados para evitar rescraping
        cache_key = f"web_research:{hash(request.query)}"
        cached_results = await self.redis_client.get(cache_key)
        
        if cached_results:
            self.logger.info("Returning cached web research results")
            return json.loads(cached_results)
        
        # Simular investigación web (en implementación real usaríamos web scraping)
        for url in request.sources:
            try:
                # En implementación real, hacer request HTTP real
                # response = await self.http_client.get(url)
                
                # Simular datos extraídos
                data_point = {
                    "url": url,
                    "title": f"Research result for {request.query} from {url}",
                    "content": f"Content related to {request.query}",
                    "relevance_score": 0.8,
                    "extracted_at": datetime.now().isoformat()
                }
                
                results["data_points"].append(data_point)
                
            except Exception as e:
                self.logger.warning("Failed to analyze URL", url=url, error=str(e))
        
        # Cache por 1 hora
        await self.redis_client.setex(cache_key, 3600, json.dumps(results))
        
        return results
    
    async def _conduct_data_mining(self, request: ResearchRequest) -> Dict[str, Any]:
        """Realizar minería de datos"""
        results = {
            "type": "data_mining",
            "query": request.query,
            "patterns_found": [],
            "trends_identified": [],
            "anomalies_detected": [],
            "data_quality_score": 0.85
        }
        
        # Simular análisis de datos
        patterns = [
            {
                "pattern_type": "frequency",
                "description": f"Frequent occurrence of {request.query} related terms",
                "confidence": 0.75
            },
            {
                "pattern_type": "correlation",
                "description": f"Strong correlation between {request.query} and industry trends",
                "confidence": 0.82
            }
        ]
        
        results["patterns_found"] = patterns
        return results
    
    async def _conduct_academic_research(self, request: ResearchRequest) -> Dict[str, Any]:
        """Realizar investigación académica"""
        results = {
            "type": "academic_research",
            "query": request.query,
            "papers_found": [],
            "citations_identified": [],
            "research_gaps": [],
            "methodology_recommendations": []
        }
        
        # Simular búsqueda académica
        papers = [
            {
                "title": f"Research Paper: {request.query}",
                "authors": ["Smith, J.", "Johnson, A."],
                "year": 2024,
                "journal": "Journal of Research",
                "abstract": f"Abstract for {request.query} research",
                "relevance_score": 0.9
            }
        ]
        
        results["papers_found"] = papers
        return results
    
    async def _conduct_competitor_analysis(self, request: ResearchRequest) -> Dict[str, Any]:
        """Realizar análisis de competencia"""
        results = {
            "type": "competitor_analysis",
            "query": request.query,
            "competitors_identified": [],
            "market_share_analysis": {},
            "competitive_advantages": [],
            "threat_assessment": []
        }
        
        # Simular análisis de competencia
        competitors = [
            {
                "name": f"Competitor for {request.query}",
                "market_position": "leader",
                "strengths": ["Brand recognition", "Market share"],
                "weaknesses": ["High prices", "Limited innovation"]
            }
        ]
        
        results["competitors_identified"] = competitors
        return results
    
    async def _conduct_market_research(self, request: ResearchRequest) -> Dict[str, Any]:
        """Realizar investigación de mercado"""
        results = {
            "type": "market_research",
            "query": request.query,
            "market_size": 1000000000,  # $1B
            "growth_rate": 0.15,  # 15%
            "key_players": [],
            "market_trends": [],
            "opportunities": []
        }
        
        # Simular datos de mercado
        opportunities = [
            {
                "opportunity": f"Growth in {request.query} sector",
                "potential_value": 50000000,
                "timeframe": "12 months"
            }
        ]
        
        results["opportunities"] = opportunities
        return results
    
    async def _conduct_technical_research(self, request: ResearchRequest) -> Dict[str, Any]:
        """Realizar investigación técnica"""
        results = {
            "type": "technical_research",
            "query": request.query,
            "technologies_analyzed": [],
            "architecture_recommendations": [],
            "implementation_challenges": [],
            "performance_metrics": {}
        }
        
        # Simular análisis técnico
        technologies = [
            {
                "technology": f"Tech for {request.query}",
                "adoption_rate": 0.65,
                "maturity_level": "mature",
                "recommendation": "recommended"
            }
        ]
        
        results["technologies_analyzed"] = technologies
        return results
    
    async def _conduct_trend_analysis(self, request: ResearchRequest) -> Dict[str, Any]:
        """Realizar análisis de tendencias"""
        results = {
            "type": "trend_analysis",
            "query": request.query,
            "trends_identified": [],
            "trend_trajectories": {},
            "future_predictions": [],
            "confidence_intervals": []
        }
        
        # Simular análisis de tendencias
        trends = [
            {
                "trend": f"Growing interest in {request.query}",
                "direction": "upward",
                "strength": 0.8,
                "duration": "ongoing"
            }
        ]
        
        results["trends_identified"] = trends
        return results
    
    async def _conduct_general_research(self, request: ResearchRequest) -> Dict[str, Any]:
        """Realizar investigación general"""
        results = {
            "type": "general_research",
            "query": request.query,
            "findings": [],
            "recommendations": [],
            "next_steps": []
        }
        
        # Simular hallazgos generales
        findings = [
            {
                "finding": f"General finding about {request.query}",
                "evidence": "supporting data",
                "reliability": 0.75
            }
        ]
        
        results["findings"] = findings
        return results
    
    def _generate_research_summary(self, research_type: str, results: Dict[str, Any]) -> str:
        """Generar resumen de investigación"""
        summary_parts = []
        
        if "query" in results:
            summary_parts.append(f"Research focused on: {results['query']}")
        
        if "data_points" in results:
            summary_parts.append(f"Found {len(results['data_points'])} relevant data points")
        
        if "papers_found" in results:
            summary_parts.append(f"Identified {len(results['papers_found'])} academic papers")
        
        if "competitors_identified" in results:
            summary_parts.append(f"Analyzed {len(results['competitors_identified'])} competitors")
        
        if "opportunities" in results:
            summary_parts.append(f"Discovered {len(results['opportunities'])} market opportunities")
        
        summary_parts.append(f"Research type: {research_type}")
        
        return ". ".join(summary_parts)
    
    async def web_scraping(self, request: WebScrapingRequest) -> Dict[str, Any]:
        """Realizar web scraping"""
        try:
            WEB_SCRAPES.inc()
            job_id = str(uuid.uuid4())
            
            results = {
                "job_id": job_id,
                "urls": request.urls,
                "extracted_data": [],
                "scraping_stats": {
                    "total_urls": len(request.urls),
                    "successful": 0,
                    "failed": 0
                }
            }
            
            for url in request.urls:
                try:
                    # Simular scraping (en implementación real usaríamos BeautifulSoup/Selenium)
                    extracted_data = {
                        "url": url,
                        "title": f"Title from {url}",
                        "content": f"Extracted content from {url}",
                        "metadata": {
                            "selectors_matched": len(request.selectors),
                            "extraction_time": datetime.now().isoformat()
                        }
                    }
                    
                    results["extracted_data"].append(extracted_data)
                    results["scraping_stats"]["successful"] += 1
                    
                    # Rate limiting
                    if request.rate_limit > 0:
                        await asyncio.sleep(request.rate_limit)
                        
                except Exception as e:
                    results["scraping_stats"]["failed"] += 1
                    self.logger.warning("Failed to scrape URL", url=url, error=str(e))
            
            # Guardar resultados
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO web_scraping_jobs (
                        job_id, urls, selectors, output_format, rate_limit, 
                        user_agent, results, status, completed_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW())
                """, job_id, request.urls, request.selectors, request.output_format,
                request.rate_limit, request.user_agent, results, "completed")
            
            return results
            
        except Exception as e:
            self.logger.error("Web scraping failed", error=str(e))
            return {"error": str(e), "job_id": job_id}
    
    async def data_analysis(self, request: DataAnalysisRequest) -> Dict[str, Any]:
        """Realizar análisis de datos"""
        try:
            DATA_ANALYSIS.inc()
            analysis_id = str(uuid.uuid4())
            
            results = {
                "analysis_id": analysis_id,
                "analysis_type": request.analysis_type,
                "data_sources": request.data_sources,
                "analysis_results": {},
                "statistical_summary": {},
                "visualization_data": {}
            }
            
            # Simular análisis según tipo
            if request.analysis_type == "statistical":
                results["analysis_results"] = {
                    "mean": 42.5,
                    "median": 40.0,
                    "std_dev": 15.2,
                    "min": 10.0,
                    "max": 100.0,
                    "sample_size": len(request.data_sources)
                }
            elif request.analysis_type == "trend":
                results["analysis_results"] = {
                    "trend_direction": "upward",
                    "trend_strength": 0.75,
                    "slope": 0.15,
                    "r_squared": 0.82
                }
            elif request.analysis_type == "correlation":
                results["analysis_results"] = {
                    "correlation_matrix": [[1.0, 0.65], [0.65, 1.0]],
                    "significant_correlations": [
                        {"var1": "x", "var2": "y", "correlation": 0.65, "p_value": 0.01}
                    ]
                }
            elif request.analysis_type == "pattern":
                results["analysis_results"] = {
                    "patterns_detected": 3,
                    "pattern_types": ["cyclical", "seasonal", "random"],
                    "pattern_confidence": 0.78
                }
            
            # Guardar resultados
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO data_analysis_jobs (
                        analysis_id, data_sources, analysis_type, parameters,
                        output_format, results, status, completed_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
                """, analysis_id, request.data_sources, request.analysis_type,
                request.parameters, request.output_format, results, "completed")
            
            return results
            
        except Exception as e:
            self.logger.error("Data analysis failed", error=str(e))
            return {"error": str(e), "analysis_id": analysis_id}
    
    async def generate_insights(self, request: InsightGenerationRequest) -> Dict[str, Any]:
        """Generar insights basados en resultados de investigación"""
        try:
            insight_id = str(uuid.uuid4())
            
            # Analizar patrones en los resultados
            insights = []
            confidence_scores = []
            
            for result in request.research_results:
                if request.insight_type == "business":
                    insight = self._generate_business_insight(result, request.target_audience)
                elif request.insight_type == "technical":
                    insight = self._generate_technical_insight(result, request.target_audience)
                elif request.insight_type == "strategic":
                    insight = self._generate_strategic_insight(result, request.target_audience)
                else:
                    insight = self._generate_general_insight(result, request.target_audience)
                
                insights.append(insight)
                confidence_scores.append(insight.get("confidence", 0.5))
            
            # Calcular confianza promedio
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
            
            insight_content = {
                "insights": insights,
                "summary": f"Generated {len(insights)} {request.insight_type} insights",
                "confidence_average": round(avg_confidence, 2)
            }
            
            # Guardar insight
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO generated_insights (
                        insight_id, research_ids, insight_type, target_audience,
                        content, confidence_score
                    ) VALUES ($1, $2, $3, $4, $5, $6)
                """, insight_id, [r.get("research_id", "unknown") for r in request.research_results],
                request.insight_type, request.target_audience, insight_content, avg_confidence)
            
            INSIGHTS_GENERATED.set(len(insights))
            
            return {
                "insight_id": insight_id,
                "insight_type": request.insight_type,
                "target_audience": request.target_audience,
                "insights": insights,
                "confidence_average": avg_confidence
            }
            
        except Exception as e:
            self.logger.error("Insight generation failed", error=str(e))
            return {"error": str(e)}
    
    def _generate_business_insight(self, result: Dict[str, Any], audience: str) -> Dict[str, Any]:
        """Generar insight de negocio"""
        return {
            "type": "business",
            "title": "Market Opportunity Identified",
            "description": "Analysis reveals significant business opportunity in the researched area",
            "recommendation": "Consider strategic investment in this area",
            "impact": "high",
            "confidence": 0.8,
            "evidence": "Market research data and trend analysis",
            "audience": audience
        }
    
    def _generate_technical_insight(self, result: Dict[str, Any], audience: str) -> Dict[str, Any]:
        """Generar insight técnico"""
        return {
            "type": "technical",
            "title": "Technology Stack Optimization",
            "description": "Technical analysis suggests optimization opportunities",
            "recommendation": "Implement recommended technology improvements",
            "complexity": "medium",
            "confidence": 0.75,
            "evidence": "Technical research and analysis",
            "audience": audience
        }
    
    def _generate_strategic_insight(self, result: Dict[str, Any], audience: str) -> Dict[str, Any]:
        """Generar insight estratégico"""
        return {
            "type": "strategic",
            "title": "Strategic Direction Recommendation",
            "description": "Research supports strategic direction for the organization",
            "recommendation": "Align strategy with identified opportunities",
            "timeline": "12-18 months",
            "confidence": 0.7,
            "evidence": "Comprehensive research analysis",
            "audience": audience
        }
    
    def _generate_general_insight(self, result: Dict[str, Any], audience: str) -> Dict[str, Any]:
        """Generar insight general"""
        return {
            "type": "general",
            "title": "Key Finding",
            "description": "Analysis reveals important findings that warrant attention",
            "recommendation": "Review findings and consider next steps",
            "priority": "medium",
            "confidence": 0.65,
            "evidence": "Research results",
            "audience": audience
        }
    
    async def get_research_status(self, research_id: str) -> Optional[Dict[str, Any]]:
        """Obtener estado de investigación"""
        try:
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT * FROM research_jobs WHERE research_id = $1
                """, research_id)
                
                if not row:
                    return None
                
                return {
                    "research_id": str(row['research_id']),
                    "status": row['status'],
                    "research_type": row['research_type'],
                    "query": row['query'],
                    "progress": 100 if row['status'] == 'completed' else 50 if row['status'] == 'in_progress' else 0,
                    "created_at": row['created_at'].isoformat(),
                    "completed_at": row['completed_at'].isoformat() if row['completed_at'] else None,
                    "execution_time": row['execution_time'],
                    "summary": row['summary']
                }
                
        except Exception as e:
            self.logger.error("Error getting research status", error=str(e))
            return None
    
    async def list_research_history(self, tenant_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Listar historial de investigaciones"""
        try:
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT research_id, research_type, query, status, created_at, 
                           completed_at, execution_time, summary
                    FROM research_jobs 
                    WHERE tenant_id = $1
                    ORDER BY created_at DESC
                    LIMIT $2
                """, tenant_id, limit)
                
                history = []
                for row in rows:
                    history.append({
                        "research_id": str(row['research_id']),
                        "research_type": row['research_type'],
                        "query": row['query'],
                        "status": row['status'],
                        "created_at": row['created_at'].isoformat(),
                        "completed_at": row['completed_at'].isoformat() if row['completed_at'] else None,
                        "execution_time": row['execution_time'],
                        "summary": row['summary']
                    })
                
                return history
                
        except Exception as e:
            self.logger.error("Error listing research history", error=str(e))
            return []

# Instancia del servicio
research_service = ResearchService()

# Endpoints de la API
@app.on_event("startup")
async def startup_event():
    """Inicialización del servicio"""
    await research_service.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    """Cierre del servicio"""
    if service_state.db_pool:
        await service_state.db_pool.close()
    if service_state.redis_client:
        await service_state.redis_client.close()
    if service_state.http_client:
        await service_state.http_client.close()

@app.get("/health")
async def health_check():
    """Health check del servicio"""
    try:
        # Verificar conexiones
        async with service_state.db_pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        
        await service_state.redis_client.ping()
        
        return {
            "status": "healthy",
            "service": "research_team",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.post("/api/v1/research", response_model=ResearchResponse)
async def conduct_research_endpoint(request: ResearchRequest):
    """Realizar investigación"""
    return await research_service.conduct_research(request)

@app.get("/api/v1/research/{research_id}/status")
async def get_research_status_endpoint(research_id: str):
    """Obtener estado de investigación"""
    status = await research_service.get_research_status(research_id)
    if not status:
        raise HTTPException(status_code=404, detail="Research not found")
    return status

@app.get("/api/v1/research/history/{tenant_id}")
async def list_research_history_endpoint(tenant_id: str, limit: int = 50):
    """Listar historial de investigaciones"""
    return await research_service.list_research_history(tenant_id, limit)

@app.post("/api/v1/web_scraping")
async def web_scraping_endpoint(request: WebScrapingRequest):
    """Realizar web scraping"""
    return await research_service.web_scraping(request)

@app.post("/api/v1/data_analysis")
async def data_analysis_endpoint(request: DataAnalysisRequest):
    """Realizar análisis de datos"""
    return await research_service.data_analysis(request)

@app.post("/api/v1/generate_insights")
async def generate_insights_endpoint(request: InsightGenerationRequest):
    """Generar insights"""
    return await research_service.generate_insights(request)

@app.get("/metrics")
async def metrics_endpoint():
    """Endpoint de métricas Prometheus"""
    return generate_latest()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )