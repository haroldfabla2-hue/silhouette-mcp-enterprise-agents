"""
Context Management Team - HAAS+ Multi-Agent System
================================================

Servicio especializado en gestión de contexto compartido entre agentes con capacidades de:
- Context Analyzers: Analización de contexto y dependencias
- Context Organizers: Organización y estructuración de contexto
- Context Auditors: Auditoría y validación de consistencia

Puerto: 8012
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
    title="Context Management Team",
    description="Gestión de contexto compartido entre agentes HAAS+",
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
CONTEXT_ANALYSIS_REQUESTS = Counter('context_analysis_requests_total', 'Total context analysis requests')
CONTEXT_ANALYSIS_DURATION = Histogram('context_analysis_duration_seconds', 'Context analysis duration')
CONTEXT_ANALYSIS_ERRORS = Counter('context_analysis_errors_total', 'Total context analysis errors')
CONTEXT_RETRIEVAL_REQUESTS = Counter('context_retrieval_requests_total', 'Total context retrieval requests')
CONTEXT_AUDIT_COMPLETED = Counter('context_audit_completed_total', 'Total context audits completed')
CONTEXT_SHARE_COUNT = Gauge('context_shares_total', 'Total context shares across agents')

# Modelos de datos
class ContextType(str, Enum):
    CONVERSATION = "conversation"
    PROJECT = "project"
    TASK = "task"
    ARTIFACT = "artifact"
    PLAN = "plan"

class ContextPriority(str, Enum):
    CRITICAL = "P0"
    HIGH = "P1"
    MEDIUM = "P2"
    LOW = "P3"

class AnalysisType(str, Enum):
    DEPENDENCY_MAP = "dependency_map"
    CONTEXT_FRESHNESS = "context_freshness"
    CONTEXT_COMPLETENESS = "context_completeness"
    CONFLICT_DETECTION = "conflict_detection"

class AuditStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class ContextMetadata(BaseModel):
    context_id: str
    context_type: ContextType
    tenant_id: str
    project_id: Optional[str] = None
    plan_id: Optional[str] = None
    task_id: Optional[str] = None
    agent_id: str
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    size_bytes: int = 0
    priority: ContextPriority = ContextPriority.MEDIUM
    dependencies: List[str] = []
    context_hash: str
    version: int = 1

class ContextRequest(BaseModel):
    context_type: ContextType
    tenant_id: str = Field(..., description="ID del tenant")
    project_id: Optional[str] = Field(None, description="ID del proyecto")
    plan_id: Optional[str] = Field(None, description="ID del plan")
    task_id: Optional[str] = Field(None, description="ID de la tarea")
    content: Union[str, Dict[str, Any]] = Field(..., description="Contenido del contexto")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadatos adicionales")
    priority: ContextPriority = ContextPriority.MEDIUM
    ttl_seconds: Optional[int] = Field(3600, description="Tiempo de vida en segundos")

class ContextResponse(BaseModel):
    context_id: str
    success: bool
    message: str
    context_metadata: Optional[ContextMetadata] = None
    analysis_results: Optional[Dict[str, Any]] = None

class AnalysisRequest(BaseModel):
    analysis_type: AnalysisType
    context_ids: List[str] = Field(..., description="IDs de contexto a analizar")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Parámetros de análisis")

class AuditRequest(BaseModel):
    context_ids: List[str] = Field(..., description="IDs de contexto a auditar")
    audit_types: List[str] = Field(default_factory=lambda: ["consistency", "freshness", "completeness"])

class OrganizeRequest(BaseModel):
    context_id: str
    organization_type: str = Field(..., description="Tipo de organización: hierarchical, temporal, dependency")
    target_structure: Optional[Dict[str, Any]] = None

class ServiceState:
    def __init__(self):
        self.db_pool: Optional[asyncpg.Pool] = None
        self.redis_client: Optional[redis.Redis] = None
        self.http_client: Optional[httpx.AsyncClient] = None

# Instancia global del estado del servicio
service_state = ServiceState()

class ContextManagerService:
    """Servicio principal de gestión de contexto"""
    
    def __init__(self):
        self.logger = logger.bind(service="ContextManager")
    
    async def initialize(self):
        """Inicializar conexiones a base de datos y servicios"""
        try:
            # Conexión a PostgreSQL
            self.db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=5, max_size=20)
            
            # Cliente Redis
            self.redis_client = redis.from_url(REDIS_URL, decode_responses=True)
            
            # Cliente HTTP
            self.http_client = httpx.AsyncClient(timeout=30.0)
            
            # Crear tablas necesarias
            await self._create_tables()
            
            self.logger.info("Context Manager service initialized successfully")
            
        except Exception as e:
            self.logger.error("Failed to initialize Context Manager service", error=str(e))
            raise
    
    async def _create_tables(self):
        """Crear tablas para gestión de contexto"""
        async with self.db_pool.acquire() as conn:
            # Tabla de contexto compartido
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS shared_contexts (
                    context_id UUID PRIMARY KEY,
                    context_type TEXT NOT NULL,
                    tenant_id TEXT NOT NULL,
                    project_id TEXT,
                    plan_id TEXT,
                    task_id TEXT,
                    agent_id TEXT NOT NULL,
                    content JSONB NOT NULL,
                    metadata JSONB DEFAULT '{}',
                    priority TEXT DEFAULT 'P2',
                    dependencies TEXT[] DEFAULT '{}',
                    context_hash TEXT NOT NULL,
                    version INTEGER DEFAULT 1,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    last_accessed TIMESTAMPTZ DEFAULT NOW(),
                    access_count INTEGER DEFAULT 0,
                    size_bytes INTEGER DEFAULT 0,
                    expires_at TIMESTAMPTZ,
                    is_active BOOLEAN DEFAULT TRUE
                );
            """)
            
            # Índices para optimización
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_shared_contexts_tenant ON shared_contexts(tenant_id);
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_shared_contexts_project ON shared_contexts(project_id);
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_shared_contexts_type ON shared_contexts(context_type);
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_shared_contexts_last_accessed ON shared_contexts(last_accessed);
            """)
            
            # Tabla de análisis de contexto
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS context_analyses (
                    analysis_id UUID PRIMARY KEY,
                    analysis_type TEXT NOT NULL,
                    context_ids TEXT[] NOT NULL,
                    parameters JSONB DEFAULT '{}',
                    results JSONB DEFAULT '{}',
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    completed_at TIMESTAMPTZ,
                    agent_id TEXT NOT NULL
                );
            """)
            
            # Tabla de auditoría de contexto
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS context_audits (
                    audit_id UUID PRIMARY KEY,
                    context_ids TEXT[] NOT NULL,
                    audit_types TEXT[] NOT NULL,
                    results JSONB DEFAULT '{}',
                    issues_found JSONB DEFAULT '{}',
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    completed_at TIMESTAMPTZ,
                    agent_id TEXT NOT NULL
                );
            """)
            
            self.logger.info("Database tables created successfully")
    
    async def create_context(self, request: ContextRequest) -> ContextResponse:
        """Crear nuevo contexto compartido"""
        try:
            CONTEXT_ANALYSIS_REQUESTS.inc()
            
            context_id = str(uuid.uuid4())
            content_str = json.dumps(request.content) if isinstance(request.content, dict) else request.content
            content_hash = str(hash(content_str))
            size_bytes = len(content_str.encode('utf-8'))
            
            # Metadatos del contexto
            metadata = ContextMetadata(
                context_id=context_id,
                context_type=request.context_type,
                tenant_id=request.tenant_id,
                project_id=request.project_id,
                plan_id=request.plan_id,
                task_id=request.task_id,
                agent_id="context_manager",  # Asumimos que viene del context manager
                created_at=datetime.now(timezone.utc),
                last_accessed=datetime.now(timezone.utc),
                size_bytes=size_bytes,
                priority=request.priority,
                context_hash=content_hash
            )
            
            # Calcular expiración
            expires_at = None
            if request.ttl_seconds:
                expires_at = datetime.now(timezone.utc).timestamp() + request.ttl_seconds
            
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO shared_contexts (
                        context_id, context_type, tenant_id, project_id, plan_id, task_id,
                        content, metadata, priority, context_hash, size_bytes, expires_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                """, 
                context_id, request.context_type.value, request.tenant_id, request.project_id,
                request.plan_id, request.task_id, request.content, request.metadata,
                request.priority.value, content_hash, size_bytes, expires_at
                )
            
            # Cache en Redis
            cache_key = f"context:{context_id}"
            context_data = {
                "metadata": asdict(metadata),
                "content": request.content,
                "metadata_dict": request.metadata
            }
            await self.redis_client.setex(
                cache_key, 
                request.ttl_seconds or 3600, 
                json.dumps(context_data)
            )
            
            # Notificar a otros agentes
            await self._notify_context_created(context_id, request.tenant_id)
            
            self.logger.info(
                "Context created successfully",
                context_id=context_id,
                context_type=request.context_type,
                tenant_id=request.tenant_id,
                size_bytes=size_bytes
            )
            
            return ContextResponse(
                context_id=context_id,
                success=True,
                message="Context created successfully",
                context_metadata=metadata
            )
            
        except Exception as e:
            CONTEXT_ANALYSIS_ERRORS.inc()
            self.logger.error("Error creating context", error=str(e), context_id=context_id)
            return ContextResponse(
                context_id=context_id,
                success=False,
                message=f"Error creating context: {str(e)}"
            )
    
    async def get_context(self, context_id: str, tenant_id: str) -> Optional[ContextMetadata]:
        """Obtener contexto por ID"""
        try:
            # Intentar cache primero
            cache_key = f"context:{context_id}"
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                data = json.loads(cached_data)
                return ContextMetadata(**data["metadata"])
            
            # Consultar base de datos
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT * FROM shared_contexts 
                    WHERE context_id = $1 AND tenant_id = $2 AND is_active = TRUE
                """, context_id, tenant_id)
                
                if not row:
                    return None
                
                # Actualizar último acceso
                await conn.execute("""
                    UPDATE shared_contexts 
                    SET last_accessed = NOW(), access_count = access_count + 1
                    WHERE context_id = $1
                """, context_id)
                
                # Crear metadatos
                metadata = ContextMetadata(
                    context_id=str(row['context_id']),
                    context_type=ContextType(row['context_type']),
                    tenant_id=row['tenant_id'],
                    project_id=row['project_id'],
                    plan_id=row['plan_id'],
                    task_id=row['task_id'],
                    agent_id=row['agent_id'],
                    created_at=row['created_at'],
                    last_accessed=row['last_accessed'],
                    access_count=row['access_count'] + 1,
                    size_bytes=row['size_bytes'],
                    priority=ContextPriority(row['priority']),
                    dependencies=row['dependencies'] or [],
                    context_hash=row['context_hash'],
                    version=row['version']
                )
                
                return metadata
                
        except Exception as e:
            self.logger.error("Error getting context", error=str(e), context_id=context_id)
            return None
    
    async def analyze_context(self, request: AnalysisRequest) -> Dict[str, Any]:
        """Analizar contexto según tipo especificado"""
        try:
            analysis_id = str(uuid.uuid4())
            start_time = datetime.now()
            
            CONTEXT_ANALYSIS_DURATION.time()
            
            results = {}
            
            if request.analysis_type == AnalysisType.DEPENDENCY_MAP:
                results = await self._analyze_dependencies(request.context_ids)
            elif request.analysis_type == AnalysisType.CONTEXT_FRESHNESS:
                results = await self._analyze_freshness(request.context_ids)
            elif request.analysis_type == AnalysisType.CONTEXT_COMPLETENESS:
                results = await self._analyze_completeness(request.context_ids)
            elif request.analysis_type == AnalysisType.CONFLICT_DETECTION:
                results = await self._detect_conflicts(request.context_ids)
            
            # Guardar resultado de análisis
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO context_analyses (
                        analysis_id, analysis_type, context_ids, parameters, 
                        results, status, completed_at, agent_id
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """, analysis_id, request.analysis_type.value, request.context_ids,
                request.parameters, results, "completed", datetime.now(), "context_manager")
            
            return {
                "analysis_id": analysis_id,
                "analysis_type": request.analysis_type,
                "results": results,
                "duration_seconds": (datetime.now() - start_time).total_seconds()
            }
            
        except Exception as e:
            CONTEXT_ANALYSIS_ERRORS.inc()
            self.logger.error("Error analyzing context", error=str(e), analysis_type=request.analysis_type)
            return {"error": str(e)}
    
    async def _analyze_dependencies(self, context_ids: List[str]) -> Dict[str, Any]:
        """Analizar dependencias entre contextos"""
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT context_id, dependencies, context_type, plan_id, task_id
                FROM shared_contexts 
                WHERE context_id = ANY($1) AND is_active = TRUE
            """, context_ids)
            
            dependency_graph = {}
            for row in rows:
                context_id = str(row['context_id'])
                dependencies = row['dependencies'] or []
                
                # Mapear dependencias
                dependency_details = []
                for dep_id in dependencies:
                    dep_row = await conn.fetchrow("""
                        SELECT context_type, tenant_id, created_at
                        FROM shared_contexts 
                        WHERE context_id = $1 AND is_active = TRUE
                    """, dep_id)
                    
                    if dep_row:
                        dependency_details.append({
                            "context_id": dep_id,
                            "type": dep_row['context_type'],
                            "tenant_id": dep_row['tenant_id'],
                            "created_at": dep_row['created_at'].isoformat()
                        })
                
                dependency_graph[context_id] = {
                    "context_type": row['context_type'],
                    "plan_id": row['plan_id'],
                    "task_id": row['task_id'],
                    "direct_dependencies": dependencies,
                    "dependency_details": dependency_details
                }
            
            return {
                "dependency_graph": dependency_graph,
                "total_contexts": len(rows),
                "analysis_type": "dependency_mapping"
            }
    
    async def _analyze_freshness(self, context_ids: List[str]) -> Dict[str, Any]:
        """Analizar frescura del contexto"""
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT context_id, last_accessed, created_at, access_count
                FROM shared_contexts 
                WHERE context_id = ANY($1) AND is_active = TRUE
            """, context_ids)
            
            freshness_analysis = {}
            now = datetime.now()
            
            for row in rows:
                context_id = str(row['context_id'])
                created_at = row['created_at']
                last_accessed = row['last_accessed']
                access_count = row['access_count']
                
                # Calcular antigüedad en horas
                age_hours = (now - created_at).total_seconds() / 3600
                idle_hours = (now - last_accessed).total_seconds() / 3600
                
                # Clasificar frescura
                if age_hours < 1:
                    freshness_level = "fresh"
                elif age_hours < 24:
                    freshness_level = "recent"
                elif age_hours < 168:  # 1 semana
                    freshness_level = "aging"
                else:
                    freshness_level = "stale"
                
                freshness_analysis[context_id] = {
                    "age_hours": round(age_hours, 2),
                    "idle_hours": round(idle_hours, 2),
                    "access_count": access_count,
                    "freshness_level": freshness_level,
                    "created_at": created_at.isoformat(),
                    "last_accessed": last_accessed.isoformat()
                }
            
            # Resumen estadístico
            levels = [ctx["freshness_level"] for ctx in freshness_analysis.values()]
            summary = {
                "fresh": levels.count("fresh"),
                "recent": levels.count("recent"),
                "aging": levels.count("aging"),
                "stale": levels.count("stale")
            }
            
            return {
                "freshness_analysis": freshness_analysis,
                "summary": summary,
                "total_contexts": len(rows)
            }
    
    async def _analyze_completeness(self, context_ids: List[str]) -> Dict[str, Any]:
        """Analizar completitud del contexto"""
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT context_id, context_type, content, metadata, size_bytes
                FROM shared_contexts 
                WHERE context_id = ANY($1) AND is_active = TRUE
            """, context_ids)
            
            completeness_analysis = {}
            
            for row in rows:
                context_id = str(row['context_id'])
                context_type = row['context_type']
                content = row['content']
                metadata = row['metadata'] or {}
                size_bytes = row['size_bytes']
                
                # Análisis de completitud según tipo
                completeness_score = 0
                missing_fields = []
                
                # Campos requeridos por tipo de contexto
                required_fields = {
                    "conversation": ["messages", "participants", "timestamp"],
                    "project": ["name", "description", "status", "timeline"],
                    "task": ["title", "description", "status", "assignee"],
                    "artifact": ["name", "type", "content", "version"],
                    "plan": ["title", "objectives", "phases", "timeline"]
                }
                
                required = required_fields.get(context_type, [])
                if required:
                    for field in required:
                        if field in content or field in metadata:
                            completeness_score += 1
                        else:
                            missing_fields.append(field)
                
                completeness_percentage = (completeness_score / len(required)) * 100 if required else 100
                
                completeness_analysis[context_id] = {
                    "context_type": context_type,
                    "size_bytes": size_bytes,
                    "completeness_score": completeness_score,
                    "required_fields": len(required),
                    "completeness_percentage": round(completeness_percentage, 2),
                    "missing_fields": missing_fields
                }
            
            return {
                "completeness_analysis": completeness_analysis,
                "total_contexts": len(rows)
            }
    
    async def _detect_conflicts(self, context_ids: List[str]) -> Dict[str, Any]:
        """Detectar conflictos en el contexto"""
        conflicts = []
        
        # Agrupar contextos por tenant y tipo para detectar conflictos
        context_groups = {}
        
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT context_id, tenant_id, context_type, content, plan_id, task_id
                FROM shared_contexts 
                WHERE context_id = ANY($1) AND is_active = TRUE
            """, context_ids)
            
            for row in rows:
                tenant_id = row['tenant_id']
                context_type = row['context_type']
                plan_id = row['plan_id']
                task_id = row['task_id']
                
                key = f"{tenant_id}:{context_type}:{plan_id}:{task_id}"
                
                if key not in context_groups:
                    context_groups[key] = []
                
                context_groups[key].append({
                    "context_id": str(row['context_id']),
                    "content": row['content']
                })
        
        # Detectar conflictos
        for group_key, contexts in context_groups.items():
            if len(contexts) > 1:
                # Verificar si el contenido es diferente
                contents = [ctx["content"] for ctx in contexts]
                if len(set(str(c) for c in contents)) > 1:
                    conflicts.append({
                        "group_key": group_key,
                        "conflict_type": "content_divergence",
                        "contexts": [{"context_id": ctx["context_id"]} for ctx in contexts],
                        "description": f"Multiple contexts with different content for {group_key}"
                    })
        
        return {
            "conflicts_detected": len(conflicts),
            "conflicts": conflicts,
            "total_contexts": len(context_ids)
        }
    
    async def audit_context(self, request: AuditRequest) -> Dict[str, Any]:
        """Auditar contextos"""
        try:
            audit_id = str(uuid.uuid4())
            start_time = datetime.now()
            
            CONTEXT_AUDIT_COMPLETED.inc()
            
            issues = []
            recommendations = []
            
            # Auditoría de consistencia
            if "consistency" in request.audit_types:
                consistency_issues = await self._audit_consistency(request.context_ids)
                issues.extend(consistency_issues)
            
            # Auditoría de frescura
            if "freshness" in request.audit_types:
                freshness_issues = await self._audit_freshness(request.context_ids)
                issues.extend(freshness_issues)
            
            # Auditoría de completitud
            if "completeness" in request.audit_types:
                completeness_issues = await self._audit_completeness(request.context_ids)
                issues.extend(completeness_issues)
            
            # Generar recomendaciones
            if any("stale" in issue.get("details", "") for issue in issues):
                recommendations.append("Update or archive stale contexts")
            
            if any("incomplete" in issue.get("details", "") for issue in issues):
                recommendations.append("Complete missing fields in contexts")
            
            # Guardar resultado de auditoría
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO context_audits (
                        audit_id, context_ids, audit_types, results, issues_found, 
                        status, completed_at, agent_id
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """, audit_id, request.context_ids, request.audit_types,
                {"recommendations": recommendations}, issues, "completed", 
                datetime.now(), "context_manager")
            
            return {
                "audit_id": audit_id,
                "issues_found": len(issues),
                "issues": issues,
                "recommendations": recommendations,
                "duration_seconds": (datetime.now() - start_time).total_seconds()
            }
            
        except Exception as e:
            self.logger.error("Error auditing context", error=str(e))
            return {"error": str(e)}
    
    async def _audit_consistency(self, context_ids: List[str]) -> List[Dict[str, Any]]:
        """Auditar consistencia del contexto"""
        issues = []
        
        async with self.db_pool.acquire() as conn:
            # Verificar contextos duplicados
            rows = await conn.fetch("""
                SELECT context_id, context_hash, tenant_id, project_id
                FROM shared_contexts 
                WHERE context_id = ANY($1) AND is_active = TRUE
            """, context_ids)
            
            hash_groups = {}
            for row in rows:
                hash_val = row['context_hash']
                if hash_val not in hash_groups:
                    hash_groups[hash_val] = []
                hash_groups[hash_val].append(str(row['context_id']))
            
            # Detectar duplicados
            for hash_val, context_list in hash_groups.items():
                if len(context_list) > 1:
                    issues.append({
                        "type": "duplicate_contexts",
                        "context_ids": context_list,
                        "hash": hash_val,
                        "details": f"Found {len(context_list)} contexts with identical content"
                    })
        
        return issues
    
    async def _audit_freshness(self, context_ids: List[str]) -> List[Dict[str, Any]]:
        """Auditar frescura del contexto"""
        issues = []
        now = datetime.now()
        
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT context_id, last_accessed, created_at
                FROM shared_contexts 
                WHERE context_id = ANY($1) AND is_active = TRUE
            """, context_ids)
            
            for row in rows:
                age_hours = (now - row['created_at']).total_seconds() / 3600
                idle_hours = (now - row['last_accessed']).total_seconds() / 3600
                
                # Contextos más de 7 días sin acceso
                if idle_hours > 168:
                    issues.append({
                        "type": "stale_context",
                        "context_id": str(row['context_id']),
                        "details": f"Context has not been accessed for {idle_hours:.1f} hours"
                    })
                
                # Contextos muy antiguos (30+ días)
                if age_hours > 720:
                    issues.append({
                        "type": "very_old_context",
                        "context_id": str(row['context_id']),
                        "details": f"Context is {age_hours:.1f} hours old"
                    })
        
        return issues
    
    async def _audit_completeness(self, context_ids: List[str]) -> List[Dict[str, Any]]:
        """Auditar completitud del contexto"""
        issues = []
        
        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT context_id, context_type, content, metadata
                FROM shared_contexts 
                WHERE context_id = ANY($1) AND is_active = TRUE
            """, context_ids)
            
            for row in rows:
                content = row['content'] or {}
                metadata = row['metadata'] or {}
                
                # Verificar contenido mínimo
                if not content or (isinstance(content, str) and not content.strip()):
                    issues.append({
                        "type": "empty_content",
                        "context_id": str(row['context_id']),
                        "details": "Context has no content"
                    })
                
                # Verificar metadatos básicos
                if not metadata.get("version"):
                    issues.append({
                        "type": "missing_version",
                        "context_id": str(row['context_id']),
                        "details": "Context missing version information"
                    })
        
        return issues
    
    async def organize_context(self, request: OrganizeRequest) -> Dict[str, Any]:
        """Organizar contexto según especificación"""
        try:
            # Obtener contexto actual
            context = await self.get_context(request.context_id, "default")  # Asumir tenant por ahora
            
            if not context:
                return {"error": "Context not found"}
            
            organized_structure = {}
            
            if request.organization_type == "hierarchical":
                organized_structure = await self._organize_hierarchically(context, request.target_structure)
            elif request.organization_type == "temporal":
                organized_structure = await self._organize_temporally(context)
            elif request.organization_type == "dependency":
                organized_structure = await self._organize_by_dependency(context)
            
            return {
                "organization_type": request.organization_type,
                "original_context": asdict(context),
                "organized_structure": organized_structure
            }
            
        except Exception as e:
            self.logger.error("Error organizing context", error=str(e))
            return {"error": str(e)}
    
    async def _organize_hierarchically(self, context: ContextMetadata, target_structure: Optional[Dict] = None) -> Dict[str, Any]:
        """Organizar contexto de forma jerárquica"""
        hierarchy = {
            "root": context.context_id,
            "levels": {
                "tenant": context.tenant_id,
                "project": context.project_id,
                "plan": context.plan_id,
                "task": context.task_id
            },
            "context_info": {
                "type": context.context_type,
                "priority": context.priority,
                "dependencies": context.dependencies
            }
        }
        
        return hierarchy
    
    async def _organize_temporally(self, context: ContextMetadata) -> Dict[str, Any]:
        """Organizar contexto por tiempo"""
        temporal_org = {
            "created": context.created_at.isoformat(),
            "last_accessed": context.last_accessed.isoformat(),
            "age_info": {
                "created_seconds_ago": (datetime.now() - context.created_at).total_seconds(),
                "last_accessed_seconds_ago": (datetime.now() - context.last_accessed).total_seconds()
            },
            "context_timeline": [
                {
                    "event": "created",
                    "timestamp": context.created_at.isoformat(),
                    "description": "Context was created"
                },
                {
                    "event": "last_accessed",
                    "timestamp": context.last_accessed.isoformat(),
                    "description": f"Context accessed {context.access_count} times"
                }
            ]
        }
        
        return temporal_org
    
    async def _organize_by_dependency(self, context: ContextMetadata) -> Dict[str, Any]:
        """Organizar contexto por dependencias"""
        dependency_org = {
            "context_id": context.context_id,
            "dependencies": context.dependencies,
            "dependency_count": len(context.dependencies),
            "dependency_analysis": {
                "has_dependencies": len(context.dependencies) > 0,
                "dependency_types": "mixed" if context.dependencies else "none"
            }
        }
        
        return dependency_org
    
    async def _notify_context_created(self, context_id: str, tenant_id: str):
        """Notificar creación de contexto a otros agentes"""
        try:
            notification = {
                "message_type": "context_created",
                "context_id": context_id,
                "tenant_id": tenant_id,
                "timestamp": datetime.now().isoformat(),
                "source": "context_management_team"
            }
            
            # Usar Redis para notificaciones rápidas
            await self.redis_client.publish(
                f"notifications:{tenant_id}", 
                json.dumps(notification)
            )
            
        except Exception as e:
            self.logger.error("Error notifying context creation", error=str(e))
    
    async def cleanup_expired_contexts(self):
        """Limpiar contextos expirados"""
        try:
            async with self.db_pool.acquire() as conn:
                # Marcar como inactivos los contextos expirados
                result = await conn.execute("""
                    UPDATE shared_contexts 
                    SET is_active = FALSE 
                    WHERE expires_at IS NOT NULL 
                    AND expires_at < NOW()
                """)
                
                rows_affected = int(result.split()[-1]) if result else 0
                
                if rows_affected > 0:
                    self.logger.info(f"Marked {rows_affected} expired contexts as inactive")
                
                return {"cleaned_up": rows_affected}
                
        except Exception as e:
            self.logger.error("Error cleaning up expired contexts", error=str(e))
            return {"error": str(e)}

# Instancia del servicio
context_service = ContextManagerService()

# Endpoints de la API
@app.on_event("startup")
async def startup_event():
    """Inicialización del servicio"""
    await context_service.initialize()

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
            "service": "context_management_team",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.post("/api/v1/create_context", response_model=ContextResponse)
async def create_context_endpoint(request: ContextRequest):
    """Crear nuevo contexto compartido"""
    return await context_service.create_context(request)

@app.get("/api/v1/get_context/{context_id}")
async def get_context_endpoint(context_id: str, tenant_id: str = "default"):
    """Obtener contexto por ID"""
    context = await context_service.get_context(context_id, tenant_id)
    if not context:
        raise HTTPException(status_code=404, detail="Context not found")
    return asdict(context)

@app.post("/api/v1/analyze_context")
async def analyze_context_endpoint(request: AnalysisRequest):
    """Analizar contexto"""
    return await context_service.analyze_context(request)

@app.post("/api/v1/audit_context")
async def audit_context_endpoint(request: AuditRequest):
    """Auditar contextos"""
    return await context_service.audit_context(request)

@app.post("/api/v1/organize_context")
async def organize_context_endpoint(request: OrganizeRequest):
    """Organizar contexto"""
    return await context_service.organize_context(request)

@app.post("/api/v1/cleanup_expired")
async def cleanup_expired_endpoint():
    """Limpiar contextos expirados"""
    return await context_service.cleanup_expired_contexts()

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