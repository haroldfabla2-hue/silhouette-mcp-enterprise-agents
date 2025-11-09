"""
MANUFACTURING TEAM - PRODUCTION & OPERATIONS
Equipo especializado en manufactura, producción y operaciones de planta.

Agentes Especializados:
- Production Managers: Gestión de producción y planificación
- Quality Control Inspectors: Inspección de calidad en proceso
- Process Engineers: Optimización de procesos productivos
- Safety Coordinators: Seguridad industrial y cumplimiento
- Operations Analysts: Análisis de operaciones y eficiencia
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime
import aiohttp
import redis
import json
import uuid
import asyncio
from enum import Enum
import logging
import random
from datetime import timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic Models
class ProductionStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"

class QualityStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    PENDING = "pending"
    INSPECTION = "inspection"

class ProductionOrder(BaseModel):
    id: Optional[str] = None
    order_number: str
    product_id: str
    quantity: int
    production_status: ProductionStatus = ProductionStatus.PLANNED
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    assigned_line: str
    quality_status: QualityStatus = QualityStatus.PENDING

class ProductionLine(BaseModel):
    id: Optional[str] = None
    name: str
    capacity_per_hour: int
    current_utilization: float
    status: str = "operational"
    last_maintenance: Optional[datetime] = None
    next_maintenance: Optional[datetime] = None

class QualityInspection(BaseModel):
    id: Optional[str] = None
    production_order_id: str
    inspector: str
    inspection_date: Optional[datetime] = None
    quality_status: QualityStatus = QualityStatus.PENDING
    defects_found: int = 0
    notes: Optional[str] = None

# FastAPI App
app = FastAPI(
    title="Manufacturing Team API",
    description="API para el equipo de manufactura y producción",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection
redis_client = redis.Redis(
    host="localhost",
    port=6379,
    password="haaspass",
    decode_responses=True
)

# Initialize Redis connection
try:
    redis_client.ping()
    logger.info("Conectado a Redis exitosamente")
except:
    logger.error("No se pudo conectar a Redis")

# Agent Definitions
AGENTS = {
    "production_manager": {
        "name": "Production Manager",
        "capabilities": [
            "production_planning",
            "capacity_management",
            "schedule_optimization",
            "resource_allocation"
        ]
    },
    "quality_control_inspector": {
        "name": "Quality Control Inspector",
        "capabilities": [
            "incoming_inspection",
            "in_process_monitoring",
            "final_inspection",
            "defect_analysis"
        ]
    },
    "process_engineer": {
        "name": "Process Engineer",
        "capabilities": [
            "process_optimization",
            "lean_implementation",
            "automation_design",
            "efficiency_improvement"
        ]
    },
    "safety_coordinator": {
        "name": "Safety Coordinator",
        "capabilities": [
            "safety_training",
            "incident_investigation",
            "compliance_monitoring",
            "risk_assessment"
        ]
    },
    "operations_analyst": {
        "name": "Operations Analyst",
        "capabilities": [
            "performance_analytics",
            "kpi_monitoring",
            "process_improvement",
            "efficiency_analysis"
        ]
    }
}

# API Endpoints
@app.get("/")
async def root():
    return {
        "team": "Manufacturing Team",
        "version": "1.0.0",
        "status": "operational",
        "agents": len(AGENTS),
        "description": "Equipo especializado en manufactura y producción"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "manufacturing-team",
        "timestamp": datetime.now().isoformat(),
        "agents_active": len(AGENTS)
    }

@app.get("/agents")
async def get_agents():
    return {"agents": AGENTS, "total": len(AGENTS)}

@app.post("/production-orders")
async def create_production_order(order: ProductionOrder, background_tasks: BackgroundTasks):
    """Crear nueva orden de producción"""
    order.id = str(uuid.uuid4())
    order.start_date = datetime.now()
    
    order_data = order.dict()
    redis_client.set(f"production_order:{order.id}", json.dumps(order_data))
    redis_client.lpush("production_orders", order.id)
    
    # Start production in background
    background_tasks.add_task(start_production, order.id)
    
    logger.info(f"Orden de producción creada: {order.id}")
    return {"status": "created", "production_order": order_data}

@app.get("/production-orders")
async def list_production_orders(status: Optional[ProductionStatus] = None):
    """Listar órdenes de producción"""
    order_ids = redis_client.lrange("production_orders", 0, -1)
    orders = []
    
    for order_id in order_ids:
        order_data = redis_client.get(f"production_order:{order_id}")
        if order_data:
            order = json.loads(order_data)
            if status is None or order.get("production_status") == status:
                orders.append(order)
    
    return {"production_orders": orders, "total": len(orders)}

@app.get("/production-orders/{order_id}")
async def get_production_order(order_id: str):
    """Obtener detalles de orden de producción"""
    order_data = redis_client.get(f"production_order:{order_id}")
    if not order_data:
        raise HTTPException(status_code=404, detail="Orden de producción no encontrada")
    
    return json.loads(order_data)

@app.post("/production-lines")
async def create_production_line(line: ProductionLine):
    """Crear nueva línea de producción"""
    line.id = str(uuid.uuid4())
    
    line_data = line.dict()
    redis_client.set(f"production_line:{line.id}", json.dumps(line_data))
    redis_client.lpush("production_lines", line.id)
    
    logger.info(f"Línea de producción creada: {line.id}")
    return {"status": "created", "production_line": line_data}

@app.get("/production-lines")
async def list_production_lines():
    """Listar líneas de producción"""
    line_ids = redis_client.lrange("production_lines", 0, -1)
    lines = []
    
    for line_id in line_ids:
        line_data = redis_client.get(f"production_line:{line_id}")
        if line_data:
            lines.append(json.loads(line_data))
    
    return {"production_lines": lines, "total": len(lines)}

@app.post("/quality-inspections")
async def create_quality_inspection(inspection: QualityInspection, background_tasks: BackgroundTasks):
    """Crear nueva inspección de calidad"""
    inspection.id = str(uuid.uuid4())
    inspection.inspection_date = datetime.now()
    
    inspection_data = inspection.dict()
    redis_client.set(f"quality_inspection:{inspection.id}", json.dumps(inspection_data))
    redis_client.lpush("quality_inspections", inspection.id)
    
    # Process inspection in background
    background_tasks.add_task(conduct_inspection, inspection.id)
    
    logger.info(f"Inspección de calidad creada: {inspection.id}")
    return {"status": "created", "quality_inspection": inspection_data}

@app.get("/quality-inspections")
async def list_quality_inspections(status: Optional[QualityStatus] = None):
    """Listar inspecciones de calidad"""
    inspection_ids = redis_client.lrange("quality_inspections", 0, -1)
    inspections = []
    
    for inspection_id in inspection_ids:
        inspection_data = redis_client.get(f"quality_inspection:{inspection_id}")
        if inspection_data:
            inspection = json.loads(inspection_data)
            if status is None or inspection.get("quality_status") == status:
                inspections.append(inspection)
    
    return {"quality_inspections": inspections, "total": len(inspections)}

@app.get("/dashboard")
async def get_manufacturing_dashboard():
    """Obtener dashboard de manufactura"""
    import random
    
    # Production order statistics
    order_ids = redis_client.lrange("production_orders", 0, -1)
    prod_stats = {"planned": 0, "in_progress": 0, "completed": 0, "on_hold": 0, "cancelled": 0}
    
    for order_id in order_ids:
        order_data = redis_client.get(f"production_order:{order_id}")
        if order_data:
            order = json.loads(order_data)
            status = order.get("production_status", "planned")
            if status in prod_stats:
                prod_stats[status] += 1
    
    # Quality inspection statistics
    inspection_ids = redis_client.lrange("quality_inspections", 0, -1)
    quality_stats = {"passed": 0, "failed": 0, "pending": 0, "inspection": 0}
    
    for inspection_id in inspection_ids:
        inspection_data = redis_client.get(f"quality_inspection:{inspection_id}")
        if inspection_data:
            inspection = json.loads(inspection_data)
            status = inspection.get("quality_status", "pending")
            if status in quality_stats:
                quality_stats[status] += 1
    
    # Production metrics
    total_lines = len(redis_client.lrange("production_lines", 0, -1))
    avg_utilization = round(random.uniform(70, 95), 1)
    
    return {
        "production_orders": prod_stats,
        "quality_inspections": quality_stats,
        "total_production_lines": total_lines,
        "average_utilization": f"{avg_utilization}%",
        "oee": round(random.uniform(75, 90), 1),  # Overall Equipment Effectiveness
        "last_updated": datetime.now().isoformat()
    }

@app.post("/maintenance/{line_id}")
async def schedule_maintenance(line_id: str, background_tasks: BackgroundTasks):
    """Programar mantenimiento de línea de producción"""
    line_data = redis_client.get(f"production_line:{line_id}")
    if not line_data:
        raise HTTPException(status_code=404, detail="Línea de producción no encontrada")
    
    line = json.loads(line_data)
    line["status"] = "maintenance"
    line["last_maintenance"] = datetime.now().isoformat()
    
    redis_client.set(f"production_line:{line_id}", json.dumps(line))
    
    # Complete maintenance in background
    background_tasks.add_task(complete_maintenance, line_id)
    
    return {"status": "maintenance_scheduled", "line_id": line_id}

# Background Tasks
async def start_production(order_id: str):
    """Iniciar producción en background"""
    try:
        logger.info(f"Iniciando producción: {order_id}")
        
        # Update status to in progress
        order_data = redis_client.get(f"production_order:{order_id}")
        if order_data:
            order = json.loads(order_data)
            order["production_status"] = ProductionStatus.IN_PROGRESS
            redis_client.set(f"production_order:{order_id}", json.dumps(order))
        
        # Simulate production process
        await asyncio.sleep(3)
        
        # Complete production
        order_data = redis_client.get(f"production_order:{order_id}")
        if order_data:
            order = json.loads(order_data)
            order["production_status"] = ProductionStatus.COMPLETED
            order["end_date"] = datetime.now().isoformat()
            order["quality_status"] = QualityStatus.INSPECTION
            redis_client.set(f"production_order:{order_id}", json.dumps(order))
            
        logger.info(f"Producción completada: {order_id}")
        
    except Exception as e:
        logger.error(f"Error en producción {order_id}: {e}")

async def conduct_inspection(inspection_id: str):
    """Realizar inspección de calidad en background"""
    try:
        logger.info(f"Conduciendo inspección: {inspection_id}")
        
        # Simulate inspection process
        await asyncio.sleep(1)
        
        inspection_data = redis_client.get(f"quality_inspection:{inspection_id}")
        if inspection_data:
            inspection = json.loads(inspection_data)
            
            # Random quality result (90% pass rate)
            if random.random() > 0.1:
                inspection["quality_status"] = QualityStatus.PASSED
                inspection["defects_found"] = 0
            else:
                inspection["quality_status"] = QualityStatus.FAILED
                inspection["defects_found"] = random.randint(1, 5)
            
            redis_client.set(f"quality_inspection:{inspection_id}", json.dumps(inspection))
            
        logger.info(f"Inspección completada: {inspection_id}")
        
    except Exception as e:
        logger.error(f"Error en inspección {inspection_id}: {e}")

async def complete_maintenance(line_id: str):
    """Completar mantenimiento en background"""
    try:
        logger.info(f"Completando mantenimiento: {line_id}")
        
        # Simulate maintenance process
        await asyncio.sleep(2)
        
        line_data = redis_client.get(f"production_line:{line_id}")
        if line_data:
            line = json.loads(line_data)
            line["status"] = "operational"
            line["next_maintenance"] = (datetime.now() + timedelta(days=30)).isoformat()
            redis_client.set(f"production_line:{line_id}", json.dumps(line))
            
        logger.info(f"Mantenimiento completado: {line_id}")
        
    except Exception as e:
        logger.error(f"Error en mantenimiento {line_id}: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8033)