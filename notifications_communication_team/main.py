"""
Notifications & Communication Team - HAAS+ Multi-Agent System
=============================================================

Servicio especializado en comunicación dinámica entre agentes con capacidades de:
- Intelligent Notification: Notificaciones inteligentes y direccionadas
- Message Mediation: Mediación de mensajes entre agentes
- Dynamic Routing: Enrutamiento dinámico basado en dependencias
- Priority Management: Gestión de prioridades y back-pressure
- Event Aggregation: Agregación y filtrado de eventos
- Communication Audit: Auditoría de comunicaciones

Puerto: 8017
Basado en: Playbook de Comunicación Dinámica entre Agentes (HAAS + MCP)
"""

import os
import json
import uuid
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
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
    title="Notifications & Communication Team",
    description="Comunicación dinámica y notificaciones inteligentes para HAAS+",
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
MESSAGES_RECEIVED = Counter('messages_received_total', 'Total messages received')
MESSAGES_SENT = Counter('messages_sent_total', 'Total messages sent')
MESSAGES_ROUTED = Counter('messages_routed_total', 'Total messages routed')
MESSAGE_ROUTING_LATENCY = Histogram('message_routing_latency_seconds', 'Message routing latency')
NOTIFICATION_DEDUPLICATION = Counter('notifications_deduplicated_total', 'Total notifications deduplicated')
PRIORITY_MESSAGE_COUNT = Gauge('priority_message_queue_size', 'Priority message queue size by level')
BACK_PRESSURE_EVENTS = Counter('back_pressure_events_total', 'Total back pressure events')

# Modelos de datos según Playbook de Comunicación Dinámica
class Performative(str, Enum):
    REQUEST = "REQUEST"
    INFORM = "INFORM"
    PROPOSE = "PROPOSE"
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    HALT = "HALT"
    ERROR = "ERROR"
    ACK = "ACK"
    HEARTBEAT = "HEARTBEAT"

class MessagePriority(str, Enum):
    P0 = "P0"  # Control (HALT, ERROR, REPLAN)
    P1 = "P1"  # Estado (INFORM, ACK, HEARTBEAT)
    P2 = "P2"  # Trabajo (REQUEST/PROPOSE/ACCEPT/REJECT)
    P3 = "P3"  # Observabilidad (METRIC, TRACE, AUDIT)

class DeliverySemantics(str, Enum):
    AT_LEAST_ONCE = "at_least_once"
    AT_MOST_ONCE = "at_most_once"
    EXACTLY_ONCE = "exactly_once"

class ChannelType(str, Enum):
    CONTROL = "control"    # Alta prioridad: HALT, ERROR, REPLAN
    STATE = "state"        # Media: INFORM, ACK, HEARTBEAT
    WORK = "work"          # Normal: REQUEST/PROPOSE/ACCEPT/REJECT
    OBSERVABILITY = "observability"  # Observabilidad: METRIC, TRACE, AUDIT

# Envelope según especificación del playbook
class MessageEnvelope(BaseModel):
    message_id: str
    conversation_id: str
    performative: Performative
    timestamp: str
    tenant_id: str
    project_id: Optional[str] = None
    plan_id: Optional[str] = None
    task_id: Optional[str] = None
    sender_id: str
    receiver_id: str
    priority: MessagePriority
    delivery: Dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str
    trace: Dict[str, Any] = Field(default_factory=dict)
    schema_version: str = "1.0"
    nl_summary: str = ""

# Content según especificación del playbook
class MessageContent(BaseModel):
    goal: str
    context: Dict[str, Any] = Field(default_factory=dict)
    constraints: List[str] = Field(default_factory=list)
    attachments: List[Dict[str, Any]] = Field(default_factory=list)
    replan_scope: Optional[str] = None
    error: Optional[Dict[str, Any]] = None

class MessageRequest(BaseModel):
    envelope: MessageEnvelope
    content: MessageContent

class MessageResponse(BaseModel):
    message_id: str
    status: str
    routed_to: List[str] = []
    delivery_confirmation: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class RoutingRequest(BaseModel):
    envelope: MessageEnvelope
    routing_strategy: str = "dependency_based"  # dependency_based, role_based, severity_based
    recipients: Optional[List[str]] = None

class BackPressureConfig(BaseModel):
    agent_id: str
    capacity: int = 100
    rate_limit: int = 10  # messages per second
    priority_weights: Dict[str, int] = Field(default_factory=lambda: {
        "P0": 5, "P1": 3, "P2": 2, "P3": 1
    })

class SilencePolicy(BaseModel):
    policy_name: str
    match_conditions: Dict[str, Any]
    window_seconds: int = 60
    max_events: int = 10
    enabled: bool = True

class ServiceState:
    def __init__(self):
        self.db_pool: Optional[asyncpg.Pool] = None
        self.redis_client: Optional[redis.Redis] = None
        self.http_client: Optional[httpx.AsyncClient] = None
        self.message_queue: Dict[str, asyncio.Queue] = {}
        self.rate_limiters: Dict[str, Dict] = {}

# Instancia global del estado del servicio
service_state = ServiceState()

class NotificationService:
    """Servicio principal de comunicación y notificaciones"""
    
    def __init__(self):
        self.logger = logger.bind(service="Notifications")
    
    async def initialize(self):
        """Inicializar conexiones y colas de mensajes"""
        try:
            # Conexión a PostgreSQL
            self.db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=10, max_size=30)
            
            # Cliente Redis
            self.redis_client = redis.from_url(REDIS_URL, decode_responses=True)
            
            # Cliente HTTP
            self.http_client = httpx.AsyncClient(timeout=30.0)
            
            # Crear tablas necesarias
            await self._create_tables()
            
            # Inicializar colas de mensajes por prioridad
            for priority in MessagePriority:
                self.message_queue[priority.value] = asyncio.Queue(maxsize=1000)
            
            # Inicializar rate limiters
            await self._initialize_rate_limiters()
            
            # Iniciar workers de procesamiento
            asyncio.create_task(self._message_routing_worker())
            asyncio.create_task(self._back_pressure_monitor())
            asyncio.create_task(self._heartbeat_sender())
            
            self.logger.info("Notification service initialized successfully")
            
        except Exception as e:
            self.logger.error("Failed to initialize Notification service", error=str(e))
            raise
    
    async def _create_tables(self):
        """Crear tablas para comunicación dinámica"""
        async with self.db_pool.acquire() as conn:
            # Tabla de mensajes envelopes
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS message_envelopes (
                    message_id UUID PRIMARY KEY,
                    conversation_id UUID NOT NULL,
                    performative TEXT NOT NULL,
                    timestamp TIMESTAMPTZ NOT NULL,
                    tenant_id TEXT NOT NULL,
                    project_id TEXT,
                    plan_id TEXT,
                    task_id TEXT,
                    sender_id TEXT NOT NULL,
                    receiver_id TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    delivery_semantics TEXT DEFAULT 'at_least_once',
                    idempotency_key UUID NOT NULL,
                    trace_id UUID,
                    span_id UUID,
                    parent_span_id UUID,
                    schema_version TEXT DEFAULT '1.0',
                    nl_summary TEXT DEFAULT '',
                    delivery_status TEXT DEFAULT 'pending',
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    delivered_at TIMESTAMPTZ
                );
            """)
            
            # Tabla de contenidos de mensajes
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS message_contents (
                    message_id UUID PRIMARY KEY,
                    goal TEXT NOT NULL,
                    context JSONB DEFAULT '{}',
                    constraints TEXT[] DEFAULT '{}',
                    attachments JSONB DEFAULT '[]',
                    replan_scope TEXT,
                    error_code TEXT,
                    error_stack TEXT,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)
            
            # Tabla de deduplicación de mensajes
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS message_dedup (
                    idempotency_key UUID PRIMARY KEY,
                    tenant_id TEXT NOT NULL,
                    message_id UUID NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    UNIQUE(tenant_id, idempotency_key)
                );
            """)
            
            # Tabla de configuración de rate limiting
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS rate_limit_config (
                    agent_id TEXT PRIMARY KEY,
                    capacity INTEGER NOT NULL,
                    rate_limit INTEGER NOT NULL,
                    priority_weights JSONB DEFAULT '{}',
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)
            
            # Tabla de políticas de silenciamiento
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS silence_policies (
                    policy_name TEXT PRIMARY KEY,
                    match_conditions JSONB NOT NULL,
                    window_seconds INTEGER NOT NULL,
                    max_events INTEGER NOT NULL,
                    enabled BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)
            
            # Tabla de entrega de mensajes
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS message_delivery (
                    delivery_id UUID PRIMARY KEY,
                    message_id UUID NOT NULL,
                    recipient_id TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    attempts INTEGER DEFAULT 0,
                    last_attempt_at TIMESTAMPTZ,
                    delivery_confirmation JSONB DEFAULT '{}',
                    error_details TEXT,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)
            
            # Índices para optimización
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_tenant ON message_envelopes(tenant_id);
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_priority ON message_envelopes(priority);
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_performative ON message_envelopes(performative);
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_conversation ON message_envelopes(conversation_id);
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_dedup_tenant ON message_dedup(tenant_id);
            """)
            
            self.logger.info("Database tables created successfully")
    
    async def _initialize_rate_limiters(self):
        """Inicializar rate limiters en Redis"""
        try:
            # Rate limiter token bucket para cada agente
            default_configs = {
                "code_generation_team": {"capacity": 50, "rate": 5, "priority_weights": {"P0": 10, "P1": 5, "P2": 2, "P3": 1}},
                "testing_team": {"capacity": 30, "rate": 3, "priority_weights": {"P0": 8, "P1": 4, "P2": 2, "P3": 1}},
                "context_management_team": {"capacity": 100, "rate": 10, "priority_weights": {"P0": 8, "P1": 4, "P2": 3, "P3": 1}},
                "research_team": {"capacity": 25, "rate": 2, "priority_weights": {"P0": 5, "P1": 3, "P2": 2, "P3": 1}},
            }
            
            for agent_id, config in default_configs.items():
                await self.redis_client.hset(
                    f"rate_limiter:{agent_id}",
                    mapping={
                        "capacity": config["capacity"],
                        "rate": config["rate"],
                        "priority_weights": json.dumps(config["priority_weights"])
                    }
                )
            
            self.logger.info("Rate limiters initialized")
            
        except Exception as e:
            self.logger.error("Error initializing rate limiters", error=str(e))
    
    async def send_message(self, request: MessageRequest) -> MessageResponse:
        """Enviar mensaje según especificación del playbook"""
        try:
            MESSAGES_RECEIVED.inc()
            start_time = datetime.now()
            
            envelope = request.envelope
            content = request.content
            
            # Verificar deduplicación
            if await self._check_duplicate(envelope.idempotency_key, envelope.tenant_id):
                NOTIFICATION_DEDUPLICATION.inc()
                return MessageResponse(
                    message_id=envelope.message_id,
                    status="duplicate"
                )
            
            # Guardar envelope y contenido
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO message_envelopes (
                        message_id, conversation_id, performative, timestamp, tenant_id,
                        project_id, plan_id, task_id, sender_id, receiver_id, priority,
                        delivery_semantics, idempotency_key, trace_id, span_id, 
                        parent_span_id, schema_version, nl_summary
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18)
                """, 
                envelope.message_id, envelope.conversation_id, envelope.performative.value,
                envelope.timestamp, envelope.tenant_id, envelope.project_id, envelope.plan_id,
                envelope.task_id, envelope.sender_id, envelope.receiver_id, envelope.priority.value,
                envelope.delivery.get("semantics", "at_least_once"), envelope.idempotency_key,
                envelope.trace.get("trace_id"), envelope.trace.get("span_id"),
                envelope.trace.get("parent_span_id"), envelope.schema_version, envelope.nl_summary
                )
                
                await conn.execute("""
                    INSERT INTO message_contents (
                        message_id, goal, context, constraints, attachments, 
                        replan_scope, error_code, error_stack
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """, envelope.message_id, content.goal, content.context, content.constraints,
                content.attachments, content.replan_scope, 
                content.error.get("code") if content.error else None,
                content.error.get("stack") if content.error else None
                )
            
            # Marcar como deduplicado
            await self._mark_as_duplicate(envelope.idempotency_key, envelope.tenant_id, envelope.message_id)
            
            # Enrutar mensaje
            routed_to = await self._route_message(envelope)
            
            # Calcular latencia
            latency = (datetime.now() - start_time).total_seconds()
            MESSAGE_ROUTING_LATENCY.observe(latency)
            
            MESSAGES_SENT.inc()
            MESSAGES_ROUTED.inc()
            
            self.logger.info(
                "Message sent and routed",
                message_id=envelope.message_id,
                performative=envelope.performative,
                priority=envelope.priority,
                routed_to=routed_to,
                latency=latency
            )
            
            return MessageResponse(
                message_id=envelope.message_id,
                status="routed",
                routed_to=routed_to
            )
            
        except Exception as e:
            self.logger.error("Error sending message", error=str(e), message_id=request.envelope.message_id)
            return MessageResponse(
                message_id=request.envelope.message_id,
                status="error",
                error=str(e)
            )
    
    async def _check_duplicate(self, idempotency_key: str, tenant_id: str) -> bool:
        """Verificar si el mensaje es duplicado"""
        try:
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT message_id FROM message_dedup 
                    WHERE idempotency_key = $1 AND tenant_id = $2
                """, idempotency_key, tenant_id)
                
                return row is not None
                
        except Exception as e:
            self.logger.error("Error checking duplicate", error=str(e))
            return False
    
    async def _mark_as_duplicate(self, idempotency_key: str, tenant_id: str, message_id: str):
        """Marcar mensaje como duplicado"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO message_dedup (idempotency_key, tenant_id, message_id)
                    VALUES ($1, $2, $3)
                """, idempotency_key, tenant_id, message_id)
                
        except Exception as e:
            self.logger.error("Error marking duplicate", error=str(e))
    
    async def _route_message(self, envelope: MessageEnvelope) -> List[str]:
        """Enrutar mensaje según estrategias del playbook"""
        try:
            recipients = []
            
            # Estrategia 1: Enrutamiento por dependencias (predeterminado)
            if envelope.task_id or envelope.plan_id or envelope.project_id:
                recipients.extend(await self._route_by_dependencies(envelope))
            
            # Estrategia 2: Enrutamiento por rol/capacidad
            if envelope.performative == Performative.REQUEST:
                recipients.extend(await self._route_by_capability(envelope))
            
            # Estrategia 3: Enrutamiento por severidad y SLA
            if envelope.priority in [MessagePriority.P0, MessagePriority.P1]:
                recipients.extend(await self._route_by_severity(envelope))
            
            # Eliminar duplicados y mantener orden
            recipients = list(dict.fromkeys(recipients))
            
            return recipients[:5]  # Limitar a 5 recipients máximo
            
        except Exception as e:
            self.logger.error("Error routing message", error=str(e))
            return []
    
    async def _route_by_dependencies(self, envelope: MessageEnvelope) -> List[str]:
        """Enrutar por dependencias usando consulta SQL del playbook"""
        try:
            async with self.db_pool.acquire() as conn:
                # Consulta SQL del playbook para descendientes afectados
                rows = await conn.fetch("""
                    WITH RECURSIVE affected(task_id) AS (
                        SELECT to_task FROM task_edges 
                        WHERE tenant_id=$1 AND project_id=$2 AND from_task=$3
                        UNION 
                        SELECT te.to_task FROM task_edges te JOIN affected a
                          ON te.tenant_id=$1 AND te.project_id=$2 AND te.from_task=a.task_id
                    )
                    SELECT owner_agent_id FROM tasks_read 
                    WHERE tenant_id=$1 AND project_id=$2
                      AND task_id IN (SELECT task_id FROM affected);
                """, envelope.tenant_id, envelope.project_id, envelope.task_id)
                
                recipients = [str(row['owner_agent_id']) for row in rows]
                
                # Si no hay dependencias específicas, usar receptor directo
                if not recipients and envelope.receiver_id != "DYNAMIC":
                    recipients = [envelope.receiver_id]
                
                return recipients
                
        except Exception as e:
            # Si falla la consulta de dependencias, usar receptor directo
            self.logger.warning("Dependency routing failed, using direct recipient", error=str(e))
            return [envelope.receiver_id] if envelope.receiver_id != "DYNAMIC" else []
    
    async def _route_by_capability(self, envelope: MessageEnvelope) -> List[str]:
        """Enrutar por capacidad usando capabilities declaradas"""
        try:
            # Analizar goal y constraints para determinar capability
            capability_agents = []
            
            goal_lower = envelope.nl_summary.lower()
            
            # Mapear capacidades a agentes
            capability_map = {
                "code": ["code_generation_team"],
                "test": ["testing_team"],
                "context": ["context_management_team"],
                "research": ["research_team"],
                "design": ["design_development_team"],
                "analysis": ["context_management_team", "research_team"],
                "documentation": ["context_management_team"],
                "api": ["code_generation_team"],
                "database": ["code_generation_team"],
                "security": ["security_compliance_team"]
            }
            
            for keyword, agents in capability_map.items():
                if keyword in goal_lower:
                    capability_agents.extend(agents)
            
            # Eliminar duplicados
            capability_agents = list(set(capability_agents))
            
            return capability_agents
            
        except Exception as e:
            self.logger.error("Error routing by capability", error=str(e))
            return []
    
    async def _route_by_severity(self, envelope: MessageEnvelope) -> List[str]:
        """Enrutar por severidad y SLA"""
        try:
            recipients = []
            
            # P0: Notificar a líderes y soporte
            if envelope.priority == MessagePriority.P0:
                recipients.extend([
                    "orchestrator",  # Líder de orquestación
                    "suport_self_repair_team",  # Equipo de soporte
                    envelope.sender_id  # También al emisor
                ])
            
            # P1: Notificar a equipos relacionados y responsables
            elif envelope.priority == MessagePriority.P1:
                recipients.extend([
                    "planner",  # Planificador para re-planificación
                    envelope.receiver_id
                ])
            
            return list(set(recipients))
            
        except Exception as e:
            self.logger.error("Error routing by severity", error=str(e))
            return []
    
    async def _message_routing_worker(self):
        """Worker para procesamiento de cola de mensajes"""
        while True:
            try:
                # Procesar mensajes por prioridad
                for priority in [MessagePriority.P0, MessagePriority.P1, MessagePriority.P2, MessagePriority.P3]:
                    queue = self.message_queue.get(priority.value)
                    if queue and not queue.empty():
                        try:
                            message = await asyncio.wait_for(queue.get(), timeout=1.0)
                            await self._process_message(message)
                        except asyncio.TimeoutError:
                            continue
                        except Exception as e:
                            self.logger.error("Error processing message from queue", error=str(e))
                
                await asyncio.sleep(0.1)  # Pausa breve
                
            except Exception as e:
                self.logger.error("Error in message routing worker", error=str(e))
                await asyncio.sleep(1)
    
    async def _process_message(self, message: Dict[str, Any]):
        """Procesar mensaje individual"""
        try:
            # Verificar rate limiting
            sender_id = message.get("sender_id")
            if sender_id and await self._check_rate_limit(sender_id, message.get("priority", "P3")):
                BACK_PRESSURE_EVENTS.inc()
                self.logger.warning("Rate limit exceeded", agent_id=sender_id)
                return
            
            # Aplicar políticas de silenciamiento
            if await self._check_silence_policy(message):
                self.logger.info("Message silenced by policy", message_id=message.get("message_id"))
                return
            
            # Entregar mensaje
            await self._deliver_message(message)
            
        except Exception as e:
            self.logger.error("Error processing message", error=str(e))
    
    async def _check_rate_limit(self, agent_id: str, priority: str) -> bool:
        """Verificar rate limiting usando token bucket de Redis"""
        try:
            now = datetime.now().timestamp()
            bucket_key = f"rate_limiter:{agent_id}"
            
            # Obtener configuración del rate limiter
            config = await self.redis_client.hgetall(bucket_key)
            if not config:
                return False  # No limit configured
            
            capacity = int(config.get("capacity", 100))
            rate = float(config.get("rate", 10))
            priority_weights = json.loads(config.get("priority_weights", "{}"))
            
            weight = priority_weights.get(priority, 1)
            
            # Token bucket algorithm
            bucket_tokens_key = f"{bucket_key}:tokens"
            last_refill_key = f"{bucket_key}:last_refill"
            
            # Obtener tokens actuales
            tokens = await self.redis_client.get(bucket_tokens_key)
            if tokens is None:
                tokens = capacity
            else:
                tokens = int(tokens)
            
            # Refill tokens
            last_refill = await self.redis_client.get(last_refill_key)
            if last_refill is None:
                last_refill = now
            else:
                last_refill = float(last_refill)
            
            # Calcular tokens disponibles
            time_passed = now - last_refill
            tokens += time_passed * rate
            tokens = min(tokens, capacity)
            
            # Verificar si hay suficientes tokens
            if tokens >= weight:
                # Consumir tokens
                tokens -= weight
                await self.redis_client.setex(bucket_tokens_key, 60, tokens)
                await self.redis_client.setex(last_refill_key, 60, now)
                return False  # Within limits
            else:
                return True  # Exceeded limits
                
        except Exception as e:
            self.logger.error("Error checking rate limit", error=str(e))
            return False
    
    async def _check_silence_policy(self, message: Dict[str, Any]) -> bool:
        """Verificar si el mensaje debe ser silenciado"""
        try:
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM silence_policies WHERE enabled = TRUE
                """)
                
                for policy in rows:
                    conditions = policy['match_conditions']
                    policy_name = policy['policy_name']
                    
                    # Verificar condiciones
                    if self._matches_policy(message, conditions):
                        # Verificar si se excedió el límite en la ventana
                        window_key = f"silence:{policy_name}:{message.get('message_id', '')}"
                        count = await self.redis_client.incr(window_key)
                        if count == 1:
                            await self.redis_client.expire(window_key, policy['window_seconds'])
                        
                        if count > policy['max_events']:
                            return True  # Silence this message
                
                return False
                
        except Exception as e:
            self.logger.error("Error checking silence policy", error=str(e))
            return False
    
    def _matches_policy(self, message: Dict[str, Any], conditions: Dict[str, Any]) -> bool:
        """Verificar si un mensaje cumple las condiciones de una política"""
        try:
            for key, expected_value in conditions.items():
                message_value = message.get(key)
                
                if key == "performative" and message_value != expected_value:
                    return False
                elif key == "priority" and message_value != expected_value:
                    return False
                elif key == "sender_id" and message_value != expected_value:
                    return False
                elif isinstance(expected_value, list) and message_value not in expected_value:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error("Error matching policy", error=str(e))
            return False
    
    async def _deliver_message(self, message: Dict[str, Any]):
        """Entregar mensaje a destinatarios"""
        try:
            message_id = message.get("message_id")
            recipients = message.get("routed_to", [])
            
            for recipient in recipients:
                # Registrar entrega
                delivery_id = str(uuid.uuid4())
                async with self.db_pool.acquire() as conn:
                    await conn.execute("""
                        INSERT INTO message_delivery (
                            delivery_id, message_id, recipient_id, status, attempts
                        ) VALUES ($1, $2, $3, $4, $5)
                    """, delivery_id, message_id, recipient, "attempted", 1)
                
                # Simular entrega a través de HTTP
                target_url = f"http://{recipient}:8000/api/v1/receive_message"
                try:
                    response = await self.http_client.post(
                        target_url,
                        json=message,
                        timeout=10.0
                    )
                    
                    # Actualizar estado de entrega
                    async with self.db_pool.acquire() as conn:
                        await conn.execute("""
                            UPDATE message_delivery 
                            SET status = $1, last_attempt_at = NOW(), delivery_confirmation = $2
                            WHERE delivery_id = $3
                        """, "delivered", {"status_code": response.status_code}, delivery_id)
                    
                except Exception as e:
                    # Marcar como fallido
                    async with self.db_pool.acquire() as conn:
                        await conn.execute("""
                            UPDATE message_delivery 
                            SET status = $1, last_attempt_at = NOW(), error_details = $2
                            WHERE delivery_id = $3
                        """, "failed", str(e), delivery_id)
            
        except Exception as e:
            self.logger.error("Error delivering message", error=str(e))
    
    async def _back_pressure_monitor(self):
        """Monitor de back-pressure"""
        while True:
            try:
                # Verificar tamaños de colas
                for priority, queue in self.message_queue.items():
                    size = queue.qsize()
                    PRIORITY_MESSAGE_COUNT.labels(priority=priority).set(size)
                    
                    # Si la cola está llena, aplicar back-pressure
                    if size > queue.maxsize * 0.8:
                        BACK_PRESSURE_EVENTS.inc()
                        self.logger.warning(
                            "High queue usage detected",
                            priority=priority,
                            queue_size=size,
                            max_size=queue.maxsize
                        )
                
                await asyncio.sleep(10)  # Verificar cada 10 segundos
                
            except Exception as e:
                self.logger.error("Error in back pressure monitor", error=str(e))
                await asyncio.sleep(5)
    
    async def _heartbeat_sender(self):
        """Envío periódico de heartbeats"""
        while True:
            try:
                # Generar heartbeat
                heartbeat = {
                    "message_id": str(uuid.uuid4()),
                    "performative": Performative.HEARTBEAT,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "sender_id": "notifications_team",
                    "capacity": 100,
                    "queue_sizes": {
                        priority: queue.qsize() 
                        for priority, queue in self.message_queue.items()
                    }
                }
                
                # Enviar a todos los agentes
                agents = ["orchestrator", "planner", "code_generation_team", "testing_team"]
                for agent in agents:
                    try:
                        target_url = f"http://{agent}:8000/api/v1/heartbeat"
                        await self.http_client.post(target_url, json=heartbeat, timeout=5.0)
                    except Exception as e:
                        self.logger.warning("Failed to send heartbeat", agent=agent, error=str(e))
                
                await asyncio.sleep(30)  # Heartbeat cada 30 segundos
                
            except Exception as e:
                self.logger.error("Error in heartbeat sender", error=str(e))
                await asyncio.sleep(10)
    
    async def configure_rate_limiting(self, config: BackPressureConfig):
        """Configurar rate limiting para un agente"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO rate_limit_config (agent_id, capacity, rate_limit, priority_weights)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (agent_id)
                    DO UPDATE SET capacity = $2, rate_limit = $3, priority_weights = $4, updated_at = NOW()
                """, config.agent_id, config.capacity, config.rate_limit, 
                json.dumps(config.priority_weights))
            
            # Actualizar en Redis
            await self.redis_client.hset(
                f"rate_limiter:{config.agent_id}",
                mapping={
                    "capacity": config.capacity,
                    "rate": config.rate_limit,
                    "priority_weights": json.dumps(config.priority_weights)
                }
            )
            
            self.logger.info("Rate limiting configured", agent_id=config.agent_id)
            
        except Exception as e:
            self.logger.error("Error configuring rate limiting", error=str(e))
    
    async def create_silence_policy(self, policy: SilencePolicy):
        """Crear política de silenciamiento"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO silence_policies (
                        policy_name, match_conditions, window_seconds, max_events, enabled
                    ) VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (policy_name)
                    DO UPDATE SET match_conditions = $2, window_seconds = $3, 
                                max_events = $4, enabled = $5
                """, policy.policy_name, json.dumps(policy.match_conditions),
                policy.window_seconds, policy.max_events, policy.enabled)
            
            self.logger.info("Silence policy created", policy_name=policy.policy_name)
            
        except Exception as e:
            self.logger.error("Error creating silence policy", error=str(e))

# Instancia del servicio
notification_service = NotificationService()

# Endpoints de la API
@app.on_event("startup")
async def startup_event():
    """Inicialización del servicio"""
    await notification_service.initialize()

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
            "service": "notifications_communication_team",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "queue_sizes": {
                priority: queue.qsize() 
                for priority, queue in notification_service.message_queue.items()
            }
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.post("/api/v1/send_message", response_model=MessageResponse)
async def send_message_endpoint(request: MessageRequest):
    """Enviar mensaje según especificación del playbook"""
    return await notification_service.send_message(request)

@app.post("/api/v1/route_message")
async def route_message_endpoint(request: RoutingRequest):
    """Enrutar mensaje a destinatarios"""
    routed_to = await notification_service._route_message(request.envelope)
    return {
        "message_id": request.envelope.message_id,
        "routed_to": routed_to,
        "strategy": request.routing_strategy
    }

@app.post("/api/v1/configure_rate_limiting")
async def configure_rate_limiting_endpoint(config: BackPressureConfig):
    """Configurar rate limiting para un agente"""
    await notification_service.configure_rate_limiting(config)
    return {"status": "configured", "agent_id": config.agent_id}

@app.post("/api/v1/silence_policy")
async def create_silence_policy_endpoint(policy: SilencePolicy):
    """Crear política de silenciamiento"""
    await notification_service.create_silence_policy(policy)
    return {"status": "created", "policy_name": policy.policy_name}

@app.get("/api/v1/queue_status")
async def get_queue_status():
    """Obtener estado de colas de mensajes"""
    return {
        "queue_sizes": {
            priority: queue.qsize() 
            for priority, queue in notification_service.message_queue.items()
        },
        "priority_levels": [p.value for p in MessagePriority],
        "total_messages": sum(queue.qsize() for queue in notification_service.message_queue.values())
    }

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