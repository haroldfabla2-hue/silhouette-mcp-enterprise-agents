"""
Support & Self-Repair Team - HAAS+ Multi-Agent System
====================================================

Servicio especializado en soporte y auto-reparación con capacidades de:
- Self-Repair: Auto-reparación de servicios
- Incident Management: Gestión de incidentes
- Monitoring: Monitoreo y alertas
- Health Checks: Verificaciones de salud
- Auto-Scaling: Escalamiento automático
- Rollback: Reversión de cambios

Puerto: 8016
"""

import os
import json
import uuid
import asyncio
from datetime import datetime, timezone, timedelta
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
    title="Support & Self-Repair Team",
    description="Soporte y auto-reparación para el sistema HAAS+",
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
INCIDENTS_CREATED = Counter('incidents_created_total', 'Total incidents created')
INCIDENTS_RESOLVED = Counter('incidents_resolved_total', 'Total incidents resolved')
SELF_REPAIRS_ATTEMPTED = Counter('self_repairs_attempted_total', 'Total self repairs attempted')
HEALTH_CHECKS = Counter('health_checks_total', 'Total health checks performed')
AUTO_SCALING_EVENTS = Counter('auto_scaling_events_total', 'Total auto scaling events')
SERVICE_AVAILABILITY = Gauge('service_availability_percentage', 'Service availability percentage')

# Modelos de datos
class IncidentSeverity(str, Enum):
    CRITICAL = "P0"
    HIGH = "P1"
    MEDIUM = "P2"
    LOW = "P3"

class IncidentStatus(str, Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVING = "resolving"
    RESOLVED = "resolved"
    CLOSED = "closed"

class ServiceHealth(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

class RepairAction(str, Enum):
    RESTART_SERVICE = "restart_service"
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    ROLLBACK = "rollback"
    CLEANUP = "cleanup"
    RESTORE = "restore"

class IncidentRequest(BaseModel):
    service_name: str = Field(..., description="Nombre del servicio")
    incident_type: str = Field(..., description="Tipo de incidente")
    severity: IncidentSeverity = Field(..., description="Severidad del incidente")
    description: str = Field(..., description="Descripción del incidente")
    tenant_id: str = Field(..., description="ID del tenant")
    auto_repair: bool = Field(True, description="Intentar auto-reparación")

class HealthCheckRequest(BaseModel):
    service_names: List[str] = Field(..., description="Servicios a verificar")
    check_type: str = Field("comprehensive", description="Tipo de verificación: basic, comprehensive, deep")

class RepairRequest(BaseModel):
    service_name: str = Field(..., description="Nombre del servicio a reparar")
    action: RepairAction = Field(..., description="Acción de reparación")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parámetros de la acción")
    max_attempts: int = Field(3, description="Número máximo de intentos")

class AutoScalingRequest(BaseModel):
    service_name: str = Field(..., description="Nombre del servicio")
    scaling_type: str = Field(..., description="Tipo de escalamiento: horizontal, vertical")
    target_replicas: Optional[int] = Field(None, description="Replicas objetivo")
    scale_factor: Optional[float] = Field(None, description="Factor de escalamiento")

class ServiceState:
    def __init__(self):
        self.db_pool: Optional[asyncpg.Pool] = None
        self.redis_client: Optional[redis.Redis] = None
        self.http_client: Optional[httpx.AsyncClient] = None
        self.monitoring_active: bool = False

# Instancia global del estado del servicio
service_state = ServiceState()

class SupportService:
    """Servicio principal de soporte y auto-reparación"""
    
    def __init__(self):
        self.logger = logger.bind(service="Support")
        self.known_services = [
            "orchestrator", "planner", "api-gateway", "context_management_team",
            "research_team", "code_generation_team", "testing_team", 
            "notifications_communication_team"
        ]
    
    async def initialize(self):
        """Inicializar conexiones y monitoreo"""
        try:
            # Conexión a PostgreSQL
            self.db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=5, max_size=20)
            
            # Cliente Redis
            self.redis_client = redis.from_url(REDIS_URL, decode_responses=True)
            
            # Cliente HTTP
            self.http_client = httpx.AsyncClient(timeout=30.0)
            
            # Crear tablas necesarias
            await self._create_tables()
            
            # Iniciar monitoreo
            self.monitoring_active = True
            asyncio.create_task(self._monitoring_worker())
            asyncio.create_task(self._health_check_worker())
            asyncio.create_task(self._auto_repair_worker())
            
            self.logger.info("Support service initialized successfully")
            
        except Exception as e:
            self.logger.error("Failed to initialize Support service", error=str(e))
            raise
    
    async def _create_tables(self):
        """Crear tablas para soporte y auto-reparación"""
        async with self.db_pool.acquire() as conn:
            # Tabla de incidentes
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS incidents (
                    incident_id UUID PRIMARY KEY,
                    service_name TEXT NOT NULL,
                    incident_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    status TEXT DEFAULT 'open',
                    description TEXT NOT NULL,
                    tenant_id TEXT NOT NULL,
                    auto_repair_attempted BOOLEAN DEFAULT FALSE,
                    repair_actions JSONB DEFAULT '[]',
                    resolution_details JSONB DEFAULT '{}',
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    resolved_at TIMESTAMPTZ,
                    agent_id TEXT NOT NULL DEFAULT 'support_team'
                );
            """)
            
            # Tabla de health checks
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS health_checks (
                    check_id UUID PRIMARY KEY,
                    service_name TEXT NOT NULL,
                    check_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    response_time FLOAT,
                    error_details TEXT,
                    metrics JSONB DEFAULT '{}',
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)
            
            # Tabla de servicios
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS services_status (
                    service_name TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    last_health_check TIMESTAMPTZ,
                    availability_percentage FLOAT DEFAULT 100.0,
                    uptime_seconds INTEGER DEFAULT 0,
                    total_requests INTEGER DEFAULT 0,
                    failed_requests INTEGER DEFAULT 0,
                    metadata JSONB DEFAULT '{}',
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)
            
            # Tabla de auto-reparaciones
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS auto_repairs (
                    repair_id UUID PRIMARY KEY,
                    service_name TEXT NOT NULL,
                    action TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    parameters JSONB DEFAULT '{}',
                    attempts INTEGER DEFAULT 0,
                    max_attempts INTEGER DEFAULT 3,
                    success BOOLEAN DEFAULT FALSE,
                    error_details TEXT,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    completed_at TIMESTAMPTZ
                );
            """)
            
            # Tabla de escalamiento automático
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS auto_scaling_events (
                    event_id UUID PRIMARY KEY,
                    service_name TEXT NOT NULL,
                    scaling_type TEXT NOT NULL,
                    trigger_reason TEXT NOT NULL,
                    action TEXT NOT NULL,
                    parameters JSONB DEFAULT '{}',
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    completed_at TIMESTAMPTZ
                );
            """)
            
            # Índices
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_incidents_tenant ON incidents(tenant_id);
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_incidents_service ON incidents(service_name);
            """)
            
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_health_checks_service ON health_checks(service_name);
            """)
            
            self.logger.info("Database tables created successfully")
    
    async def create_incident(self, request: IncidentRequest) -> Dict[str, Any]:
        """Crear nuevo incidente"""
        try:
            INCIDENTS_CREATED.inc()
            incident_id = str(uuid.uuid4())
            
            # Insertar incidente en base de datos
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO incidents (
                        incident_id, service_name, incident_type, severity,
                        description, tenant_id, auto_repair_attempted, agent_id
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """, incident_id, request.service_name, request.incident_type,
                request.severity.value, request.description, request.tenant_id,
                request.auto_repair, "support_team")
            
            # Intentar auto-reparación si está habilitada
            repair_attempted = False
            if request.auto_repair:
                repair_result = await self._attempt_auto_repair(request)
                repair_attempted = repair_result.get("attempted", False)
                
                # Actualizar incidente con resultado de reparación
                async with self.db_pool.acquire() as conn:
                    await conn.execute("""
                        UPDATE incidents 
                        SET auto_repair_attempted = $1, repair_actions = $2, status = $3
                        WHERE incident_id = $4
                    """, repair_attempted, json.dumps(repair_result.get("actions", [])),
                    "investigating" if not repair_result.get("resolved", False) else "resolving",
                    incident_id)
            
            # Notificar a otros servicios
            await self._notify_incident(incident_id, request)
            
            self.logger.info(
                "Incident created",
                incident_id=incident_id,
                service_name=request.service_name,
                severity=request.severity,
                auto_repair_attempted=repair_attempted
            )
            
            return {
                "incident_id": incident_id,
                "status": "created",
                "auto_repair_attempted": repair_attempted,
                "next_steps": "Incident created and processing started"
            }
            
        except Exception as e:
            self.logger.error("Error creating incident", error=str(e))
            return {"error": str(e)}
    
    async def _attempt_auto_repair(self, incident: IncidentRequest) -> Dict[str, Any]:
        """Intentar auto-reparación del incidente"""
        try:
            SELF_REPAIRS_ATTEMPTED.inc()
            actions_taken = []
            resolved = False
            
            # Determinar acciones de reparación según el tipo de incidente
            if incident.incident_type in ["service_down", "connection_timeout"]:
                # Intentar reiniciar servicio
                repair_request = RepairRequest(
                    service_name=incident.service_name,
                    action=RepairAction.RESTART_SERVICE,
                    max_attempts=3
                )
                result = await self._perform_repair(repair_request)
                actions_taken.append({
                    "action": "restart_service",
                    "result": result
                })
                resolved = result.get("success", False)
            
            elif incident.incident_type in ["high_load", "performance_issues"]:
                # Intentar escalamiento
                scaling_request = AutoScalingRequest(
                    service_name=incident.service_name,
                    scaling_type="horizontal",
                    scale_factor=1.5
                )
                result = await self._perform_auto_scaling(scaling_request)
                actions_taken.append({
                    "action": "scale_up",
                    "result": result
                })
                resolved = result.get("success", False)
            
            elif incident.incident_type in ["memory_leak", "resource_exhaustion"]:
                # Intentar limpieza
                repair_request = RepairRequest(
                    service_name=incident.service_name,
                    action=RepairAction.CLEANUP,
                    parameters={"type": "resources"}
                )
                result = await self._perform_repair(repair_request)
                actions_taken.append({
                    "action": "cleanup",
                    "result": result
                })
                resolved = result.get("success", False)
            
            return {
                "attempted": True,
                "resolved": resolved,
                "actions": actions_taken
            }
            
        except Exception as e:
            self.logger.error("Error in auto repair", error=str(e))
            return {
                "attempted": True,
                "resolved": False,
                "error": str(e)
            }
    
    async def _perform_repair(self, request: RepairRequest) -> Dict[str, Any]:
        """Realizar acción de reparación"""
        try:
            repair_id = str(uuid.uuid4())
            
            # Guardar reparación en base de datos
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO auto_repairs (
                        repair_id, service_name, action, parameters, max_attempts
                    ) VALUES ($1, $2, $3, $4, $5)
                """, repair_id, request.service_name, request.action.value,
                json.dumps(request.parameters), request.max_attempts)
            
            # Realizar acción según el tipo
            success = False
            error_details = None
            
            for attempt in range(request.max_attempts):
                try:
                    if request.action == RepairAction.RESTART_SERVICE:
                        success = await self._restart_service(request.service_name)
                    elif request.action == RepairAction.CLEANUP:
                        success = await self._cleanup_service(request.service_name, request.parameters)
                    elif request.action == RepairAction.ROLLBACK:
                        success = await self._rollback_service(request.service_name, request.parameters)
                    elif request.action == RepairAction.RESTORE:
                        success = await self._restore_service(request.service_name, request.parameters)
                    
                    if success:
                        break
                        
                except Exception as e:
                    error_details = str(e)
                    self.logger.warning(
                        "Repair attempt failed",
                        service=request.service_name,
                        action=request.action,
                        attempt=attempt + 1,
                        error=str(e)
                    )
            
            # Actualizar reparación en base de datos
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE auto_repairs 
                    SET status = $1, attempts = $2, success = $3, error_details = $4,
                        completed_at = NOW()
                    WHERE repair_id = $5
                """, "completed" if success else "failed", attempt + 1,
                success, error_details, repair_id)
            
            return {
                "success": success,
                "attempts": attempt + 1,
                "error": error_details
            }
            
        except Exception as e:
            self.logger.error("Error performing repair", error=str(e))
            return {"success": False, "error": str(e)}
    
    async def _restart_service(self, service_name: str) -> bool:
        """Reiniciar servicio"""
        try:
            # En implementación real, usar Docker API o systemctl
            self.logger.info("Attempting to restart service", service=service_name)
            
            # Simular reinicio exitoso
            await asyncio.sleep(2)
            
            # Verificar que el servicio se reinició correctamente
            health_status = await self._check_service_health(service_name)
            return health_status == ServiceHealth.HEALTHY
            
        except Exception as e:
            self.logger.error("Error restarting service", service=service_name, error=str(e))
            return False
    
    async def _cleanup_service(self, service_name: str, parameters: Dict[str, Any]) -> bool:
        """Limpiar recursos del servicio"""
        try:
            self.logger.info("Attempting to cleanup service", service=service_name, parameters=parameters)
            
            cleanup_type = parameters.get("type", "general")
            
            if cleanup_type == "resources":
                # Limpiar caché, logs antiguos, etc.
                await self._cleanup_cache(service_name)
                await self._cleanup_logs(service_name)
            
            return True
            
        except Exception as e:
            self.logger.error("Error cleaning up service", service=service_name, error=str(e))
            return False
    
    async def _rollback_service(self, service_name: str, parameters: Dict[str, Any]) -> bool:
        """Revertir servicio a versión anterior"""
        try:
            self.logger.info("Attempting to rollback service", service=service_name, parameters=parameters)
            
            version = parameters.get("version", "previous")
            # En implementación real, usar sistema de deployment
            
            return True
            
        except Exception as e:
            self.logger.error("Error rolling back service", service=service_name, error=str(e))
            return False
    
    async def _restore_service(self, service_name: str, parameters: Dict[str, Any]) -> bool:
        """Restaurar servicio desde backup"""
        try:
            self.logger.info("Attempting to restore service", service=service_name, parameters=parameters)
            
            backup_id = parameters.get("backup_id")
            # En implementación real, usar sistema de backup
            
            return True
            
        except Exception as e:
            self.logger.error("Error restoring service", service=service_name, error=str(e))
            return False
    
    async def _cleanup_cache(self, service_name: str):
        """Limpiar caché del servicio"""
        try:
            cache_key = f"cache:{service_name}"
            await self.redis_client.delete(cache_key)
            self.logger.info("Cache cleaned", service=service_name)
        except Exception as e:
            self.logger.error("Error cleaning cache", service=service_name, error=str(e))
    
    async def _cleanup_logs(self, service_name: str):
        """Limpiar logs antiguos del servicio"""
        try:
            # En implementación real, limpiar archivos de log
            self.logger.info("Logs cleanup completed", service=service_name)
        except Exception as e:
            self.logger.error("Error cleaning logs", service=service_name, error=str(e))
    
    async def _perform_auto_scaling(self, request: AutoScalingRequest) -> Dict[str, Any]:
        """Realizar escalamiento automático"""
        try:
            AUTO_SCALING_EVENTS.inc()
            event_id = str(uuid.uuid4())
            
            # Guardar evento de escalamiento
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO auto_scaling_events (
                        event_id, service_name, scaling_type, trigger_reason,
                        action, parameters, status
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                """, event_id, request.service_name, request.scaling_type,
                "automatic_trigger", "scale", json.dumps(request.parameters), "in_progress")
            
            # Realizar escalamiento
            success = await self._execute_scaling(request)
            
            # Actualizar evento
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE auto_scaling_events 
                    SET status = $1, completed_at = NOW()
                    WHERE event_id = $2
                """, "completed" if success else "failed", event_id)
            
            return {
                "success": success,
                "event_id": event_id
            }
            
        except Exception as e:
            self.logger.error("Error performing auto scaling", error=str(e))
            return {"success": False, "error": str(e)}
    
    async def _execute_scaling(self, request: AutoScalingRequest) -> bool:
        """Ejecutar escalamiento"""
        try:
            self.logger.info("Executing scaling", service=request.service_name, scaling_type=request.scaling_type)
            
            # En implementación real, usar Docker Swarm, Kubernetes API, etc.
            # Simular escalamiento
            await asyncio.sleep(3)
            
            return True
            
        except Exception as e:
            self.logger.error("Error executing scaling", service=request.service_name, error=str(e))
            return False
    
    async def _check_service_health(self, service_name: str) -> ServiceHealth:
        """Verificar salud del servicio"""
        try:
            health_url = f"http://{service_name}:8000/health"
            response = await self.http_client.get(health_url, timeout=10.0)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    return ServiceHealth.HEALTHY
                else:
                    return ServiceHealth.DEGRADED
            else:
                return ServiceHealth.UNHEALTHY
                
        except Exception as e:
            self.logger.warning("Health check failed", service=service_name, error=str(e))
            return ServiceHealth.UNHEALTHY
    
    async def perform_health_checks(self, request: HealthCheckRequest) -> Dict[str, Any]:
        """Realizar verificaciones de salud"""
        try:
            HEALTH_CHECKS.inc()
            check_results = {}
            
            for service_name in request.service_names:
                try:
                    start_time = datetime.now()
                    health_status = await self._check_service_health(service_name)
                    response_time = (datetime.now() - start_time).total_seconds()
                    
                    # Guardar resultado de health check
                    check_id = str(uuid.uuid4())
                    async with self.db_pool.acquire() as conn:
                        await conn.execute("""
                            INSERT INTO health_checks (
                                check_id, service_name, check_type, status, response_time
                            ) VALUES ($1, $2, $3, $4, $5)
                        """, check_id, service_name, request.check_type, 
                        health_status.value, response_time)
                    
                    # Actualizar estado del servicio
                    await self._update_service_status(service_name, health_status, response_time)
                    
                    check_results[service_name] = {
                        "status": health_status.value,
                        "response_time": response_time,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                except Exception as e:
                    check_results[service_name] = {
                        "status": "error",
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
                    self.logger.error("Health check failed", service=service_name, error=str(e))
            
            return {
                "check_results": check_results,
                "total_services": len(request.service_names),
                "healthy_services": len([r for r in check_results.values() if r.get("status") == "healthy"])
            }
            
        except Exception as e:
            self.logger.error("Error performing health checks", error=str(e))
            return {"error": str(e)}
    
    async def _update_service_status(self, service_name: str, health: ServiceHealth, response_time: float):
        """Actualizar estado del servicio"""
        try:
            async with self.db_pool.acquire() as conn:
                # Actualizar o insertar estado del servicio
                await conn.execute("""
                    INSERT INTO services_status (
                        service_name, status, last_health_check, uptime_seconds,
                        updated_at
                    ) VALUES ($1, $2, NOW(), 0, NOW())
                    ON CONFLICT (service_name)
                    DO UPDATE SET 
                        status = $2, 
                        last_health_check = NOW(),
                        updated_at = NOW()
                """, service_name, health.value)
                
                # Calcular disponibilidad
                availability = 100.0 if health == ServiceHealth.HEALTHY else 50.0
                await conn.execute("""
                    UPDATE services_status 
                    SET availability_percentage = $1
                    WHERE service_name = $2
                """, availability, service_name)
            
        except Exception as e:
            self.logger.error("Error updating service status", service=service_name, error=str(e))
    
    async def _notify_incident(self, incident_id: str, incident: IncidentRequest):
        """Notificar incidente a otros servicios"""
        try:
            notification = {
                "incident_id": incident_id,
                "service_name": incident.service_name,
                "severity": incident.severity.value,
                "description": incident.description,
                "timestamp": datetime.now().isoformat(),
                "source": "support_team"
            }
            
            # Notificar a notificaciones
            try:
                await self.http_client.post(
                    "http://notifications_communication_team:8000/api/v1/send_message",
                    json={
                        "envelope": {
                            "message_id": str(uuid.uuid4()),
                            "conversation_id": str(uuid.uuid4()),
                            "performative": "ERROR",
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "tenant_id": incident.tenant_id,
                            "sender_id": "support_team",
                            "receiver_id": "notifications_team",
                            "priority": incident.severity.value,
                            "idempotency_key": str(uuid.uuid4())
                        },
                        "content": {
                            "goal": f"Incident detected: {incident.incident_type}",
                            "context": notification
                        }
                    },
                    timeout=10.0
                )
            except Exception as e:
                self.logger.warning("Failed to notify incident", error=str(e))
                
        except Exception as e:
            self.logger.error("Error notifying incident", error=str(e))
    
    # Workers de monitoreo
    async def _monitoring_worker(self):
        """Worker de monitoreo continuo"""
        while self.monitoring_active:
            try:
                # Verificar servicios conocidos
                for service_name in self.known_services:
                    health = await self._check_service_health(service_name)
                    
                    if health in [ServiceHealth.UNHEALTHY, ServiceHealth.DEGRADED]:
                        # Crear incidente automáticamente
                        incident = IncidentRequest(
                            service_name=service_name,
                            incident_type="health_check_failure",
                            severity=IncidentSeverity.HIGH if health == ServiceHealth.UNHEALTHY else IncidentSeverity.MEDIUM,
                            description=f"Service {service_name} health status: {health.value}",
                            tenant_id="system",
                            auto_repair=True
                        )
                        await self.create_incident(incident)
                
                await asyncio.sleep(30)  # Verificar cada 30 segundos
                
            except Exception as e:
                self.logger.error("Error in monitoring worker", error=str(e))
                await asyncio.sleep(10)
    
    async def _health_check_worker(self):
        """Worker de health checks programados"""
        while self.monitoring_active:
            try:
                # Health check general cada 5 minutos
                health_request = HealthCheckRequest(
                    service_names=self.known_services,
                    check_type="comprehensive"
                )
                await self.perform_health_checks(health_request)
                
                await asyncio.sleep(300)  # Cada 5 minutos
                
            except Exception as e:
                self.logger.error("Error in health check worker", error=str(e))
                await asyncio.sleep(60)
    
    async def _auto_repair_worker(self):
        """Worker de auto-reparación"""
        while self.monitoring_active:
            try:
                # Buscar reparaciones pendientes
                async with self.db_pool.acquire() as conn:
                    pending_repairs = await conn.fetch("""
                        SELECT repair_id, service_name, action, parameters, max_attempts
                        FROM auto_repairs 
                        WHERE status = 'pending' AND attempts < max_attempts
                    """)
                
                for repair_row in pending_repairs:
                    repair_request = RepairRequest(
                        service_name=repair_row['service_name'],
                        action=RepairAction(repair_row['action']),
                        parameters=repair_row['parameters'],
                        max_attempts=repair_row['max_attempts']
                    )
                    
                    await self._perform_repair(repair_request)
                
                await asyncio.sleep(60)  # Verificar cada minuto
                
            except Exception as e:
                self.logger.error("Error in auto repair worker", error=str(e))
                await asyncio.sleep(30)
    
    async def get_incident_status(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Obtener estado de incidente"""
        try:
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT * FROM incidents WHERE incident_id = $1
                """, incident_id)
                
                if not row:
                    return None
                
                return {
                    "incident_id": str(row['incident_id']),
                    "service_name": row['service_name'],
                    "incident_type": row['incident_type'],
                    "severity": row['severity'],
                    "status": row['status'],
                    "description": row['description'],
                    "auto_repair_attempted": row['auto_repair_attempted'],
                    "created_at": row['created_at'].isoformat(),
                    "resolved_at": row['resolved_at'].isoformat() if row['resolved_at'] else None
                }
                
        except Exception as e:
            self.logger.error("Error getting incident status", error=str(e))
            return None
    
    async def get_services_status(self) -> List[Dict[str, Any]]:
        """Obtener estado de todos los servicios"""
        try:
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM services_status ORDER BY service_name
                """)
                
                services = []
                for row in rows:
                    services.append({
                        "service_name": row['service_name'],
                        "status": row['status'],
                        "availability_percentage": row['availability_percentage'],
                        "last_health_check": row['last_health_check'].isoformat() if row['last_health_check'] else None,
                        "uptime_seconds": row['uptime_seconds'],
                        "total_requests": row['total_requests'],
                        "failed_requests": row['failed_requests'],
                        "updated_at": row['updated_at'].isoformat()
                    })
                
                return services
                
        except Exception as e:
            self.logger.error("Error getting services status", error=str(e))
            return []

# Instancia del servicio
support_service = SupportService()

# Endpoints de la API
@app.on_event("startup")
async def startup_event():
    """Inicialización del servicio"""
    await support_service.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    """Cierre del servicio"""
    support_service.monitoring_active = False
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
            "service": "support_team",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "monitoring_active": support_service.monitoring_active
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.post("/api/v1/incidents")
async def create_incident_endpoint(request: IncidentRequest):
    """Crear incidente"""
    return await support_service.create_incident(request)

@app.get("/api/v1/incidents/{incident_id}")
async def get_incident_status_endpoint(incident_id: str):
    """Obtener estado de incidente"""
    status = await support_service.get_incident_status(incident_id)
    if not status:
        raise HTTPException(status_code=404, detail="Incident not found")
    return status

@app.post("/api/v1/health_checks")
async def health_check_endpoint(request: HealthCheckRequest):
    """Realizar health checks"""
    return await support_service.perform_health_checks(request)

@app.get("/api/v1/services/status")
async def get_services_status_endpoint():
    """Obtener estado de servicios"""
    return await support_service.get_services_status()

@app.post("/api/v1/repair")
async def repair_service_endpoint(request: RepairRequest):
    """Reparar servicio manualmente"""
    return await support_service._perform_repair(request)

@app.post("/api/v1/auto_scaling")
async def auto_scaling_endpoint(request: AutoScalingRequest):
    """Escalamiento automático"""
    return await support_service._perform_auto_scaling(request)

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