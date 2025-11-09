"""
RISK MANAGEMENT TEAM - RISK ASSESSMENT & MITIGATION
Equipo especializado en evaluación de riesgos, gestión de crisis y continuidad del negocio.

Agentes Especializados:
- Risk Analysts: Análisis de riesgos operativos, financieros y estratégicos
- Crisis Managers: Gestión de crisis y planes de continuidad
- Compliance Officers: Gestión de riesgos regulatorios y de cumplimiento
- Business Continuity Managers: Planes de continuidad del negocio
- Insurance Specialists: Gestión de seguros y transferencia de riesgos
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic Models
class RiskCategory(str, Enum):
    OPERATIONAL = "operational"
    FINANCIAL = "financial"
    STRATEGIC = "strategic"
    COMPLIANCE = "compliance"
    CYBER = "cyber"
    REPUTATIONAL = "reputational"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RiskAssessment(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    category: RiskCategory
    risk_level: RiskLevel
    probability: float  # 0-1
    impact: float  # 0-1
    current_controls: List[str]
    recommended_actions: List[str]
    owner: str
    status: str = "open"
    created_at: Optional[datetime] = None

class CrisisPlan(BaseModel):
    id: Optional[str] = None
    title: str
    scenario: str
    impact_level: str
    response_team: List[str]
    communication_plan: Dict[str, str]
    recovery_steps: List[str]
    timeline: str
    created_at: Optional[datetime] = None

class Incident(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    severity: RiskLevel
    affected_areas: List[str]
    response_status: str = "initial_assessment"
    created_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

class BusinessContinuityPlan(BaseModel):
    id: Optional[str] = None
    business_function: str
    recovery_time_objective: str  # RTO
    recovery_point_objective: str  # RPO
    critical_dependencies: List[str]
    backup_procedures: List[str]
    contact_information: Dict[str, str]
    created_at: Optional[datetime] = None

# FastAPI App
app = FastAPI(
    title="Risk Management Team API",
    description="API para el equipo de gestión de riesgos",
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
    "risk_analyst": {
        "name": "Risk Analyst",
        "capabilities": [
            "risk_identification",
            "quantitative_analysis",
            "risk_modeling",
            "statistical_analysis"
        ]
    },
    "crisis_manager": {
        "name": "Crisis Manager",
        "capabilities": [
            "crisis_response",
            "communication_coordination",
            "stakeholder_management",
            "situation_assessment"
        ]
    },
    "compliance_officer": {
        "name": "Compliance Officer",
        "capabilities": [
            "regulatory_monitoring",
            "policy_development",
            "audit_coordination",
            "training_delivery"
        ]
    },
    "business_continuity_manager": {
        "name": "Business Continuity Manager",
        "capabilities": [
            "bcp_development",
            "disaster_recovery",
            "exercise_coordination",
            "vendor_assessment"
        ]
    },
    "insurance_specialist": {
        "name": "Insurance Specialist",
        "capabilities": [
            "insurance_analysis",
            "policy_review",
            "claim_management",
            "risk_transfer_evaluation"
        ]
    }
}

# API Endpoints
@app.get("/")
async def root():
    return {
        "team": "Risk Management Team",
        "version": "1.0.0",
        "status": "operational",
        "agents": len(AGENTS),
        "description": "Equipo especializado en gestión de riesgos y continuidad del negocio"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "risk-management-team",
        "timestamp": datetime.now().isoformat(),
        "agents_active": len(AGENTS)
    }

@app.get("/agents")
async def get_agents():
    return {"agents": AGENTS, "total": len(AGENTS)}

@app.post("/risk-assessments")
async def create_risk_assessment(assessment: RiskAssessment):
    """Crear nueva evaluación de riesgo"""
    assessment.id = str(uuid.uuid4())
    assessment.created_at = datetime.now()
    
    assessment_data = assessment.dict()
    redis_client.set(f"risk_assessment:{assessment.id}", json.dumps(assessment_data))
    redis_client.lpush("risk_assessments", assessment.id)
    
    logger.info(f"Evaluación de riesgo creada: {assessment.id}")
    return {"status": "created", "assessment": assessment_data}

@app.get("/risk-assessments")
async def list_risk_assessments(category: Optional[RiskCategory] = None, level: Optional[RiskLevel] = None):
    """Listar evaluaciones de riesgo"""
    assessment_ids = redis_client.lrange("risk_assessments", 0, -1)
    assessments = []
    
    for assessment_id in assessment_ids:
        assessment_data = redis_client.get(f"risk_assessment:{assessment_id}")
        if assessment_data:
            assessment = json.loads(assessment_data)
            if (category is None or assessment.get("category") == category) and \
               (level is None or assessment.get("risk_level") == level):
                assessments.append(assessment)
    
    return {"assessments": assessments, "total": len(assessments)}

@app.get("/risk-assessments/{assessment_id}")
async def get_risk_assessment(assessment_id: str):
    """Obtener detalles de evaluación de riesgo específica"""
    assessment_data = redis_client.get(f"risk_assessment:{assessment_id}")
    if not assessment_data:
        raise HTTPException(status_code=404, detail="Evaluación de riesgo no encontrada")
    
    return json.loads(assessment_data)

@app.post("/crisis-plans")
async def create_crisis_plan(plan: CrisisPlan):
    """Crear nuevo plan de crisis"""
    plan.id = str(uuid.uuid4())
    plan.created_at = datetime.now()
    
    plan_data = plan.dict()
    redis_client.set(f"crisis_plan:{plan.id}", json.dumps(plan_data))
    redis_client.lpush("crisis_plans", plan.id)
    
    logger.info(f"Plan de crisis creado: {plan.id}")
    return {"status": "created", "plan": plan_data}

@app.get("/crisis-plans")
async def list_crisis_plans():
    """Listar planes de crisis"""
    plan_ids = redis_client.lrange("crisis_plans", 0, -1)
    plans = []
    
    for plan_id in plan_ids:
        plan_data = redis_client.get(f"crisis_plan:{plan_id}")
        if plan_data:
            plans.append(json.loads(plan_data))
    
    return {"plans": plans, "total": len(plans)}

@app.post("/incidents")
async def create_incident(incident: Incident):
    """Crear nuevo incidente de riesgo"""
    incident.id = str(uuid.uuid4())
    incident.created_at = datetime.now()
    
    incident_data = incident.dict()
    redis_client.set(f"incident:{incident.id}", json.dumps(incident_data))
    redis_client.lpush("incidents", incident.id)
    
    logger.info(f"Incidente de riesgo creado: {incident.id}")
    return {"status": "created", "incident": incident_data}

@app.get("/incidents")
async def list_incidents(severity: Optional[RiskLevel] = None):
    """Listar incidentes de riesgo"""
    incident_ids = redis_client.lrange("incidents", 0, -1)
    incidents = []
    
    for incident_id in incident_ids:
        incident_data = redis_client.get(f"incident:{incident_id}")
        if incident_data:
            incident_obj = json.loads(incident_data)
            if severity is None or incident_obj.get("severity") == severity:
                incidents.append(incident_obj)
    
    return {"incidents": incidents, "total": len(incidents)}

@app.put("/incidents/{incident_id}/resolve")
async def resolve_incident(incident_id: str):
    """Resolver incidente de riesgo"""
    incident_data = redis_client.get(f"incident:{incident_id}")
    if not incident_data:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")
    
    incident = json.loads(incident_data)
    incident["response_status"] = "resolved"
    incident["resolved_at"] = datetime.now().isoformat()
    
    redis_client.set(f"incident:{incident_id}", json.dumps(incident))
    return {"status": "resolved", "incident": incident}

@app.post("/business-continuity-plans")
async def create_bcp(plan: BusinessContinuityPlan):
    """Crear plan de continuidad del negocio"""
    plan.id = str(uuid.uuid4())
    plan.created_at = datetime.now()
    
    plan_data = plan.dict()
    redis_client.set(f"bcp:{plan.id}", json.dumps(plan_data))
    redis_client.lpush("bcps", plan.id)
    
    logger.info(f"Plan de continuidad creado: {plan.id}")
    return {"status": "created", "plan": plan_data}

@app.get("/business-continuity-plans")
async def list_bcps():
    """Listar planes de continuidad del negocio"""
    bcp_ids = redis_client.lrange("bcps", 0, -1)
    bcps = []
    
    for bcp_id in bcp_ids:
        bcp_data = redis_client.get(f"bcp:{bcp_id}")
        if bcp_data:
            bcps.append(json.loads(bcp_data))
    
    return {"bcps": bcps, "total": len(bcps)}

@app.get("/dashboard")
async def get_risk_dashboard():
    """Obtener dashboard de gestión de riesgos"""
    # Risk assessment statistics
    assessment_ids = redis_client.lrange("risk_assessments", 0, -1)
    risk_stats = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    
    for assessment_id in assessment_ids:
        assessment_data = redis_client.get(f"risk_assessment:{assessment_id}")
        if assessment_data:
            assessment = json.loads(assessment_data)
            level = assessment.get("risk_level", "low")
            if level in risk_stats:
                risk_stats[level] += 1
    
    # Incident statistics
    incident_ids = redis_client.lrange("incidents", 0, -1)
    incident_stats = {"open": 0, "in_progress": 0, "resolved": 0, "critical": 0}
    
    for incident_id in incident_ids:
        incident_data = redis_client.get(f"incident:{incident_id}")
        if incident_data:
            incident = json.loads(incident_data)
            status = incident.get("response_status", "open")
            severity = incident.get("severity", "low")
            
            if status in incident_stats:
                incident_stats[status] += 1
            if severity == "critical":
                incident_stats["critical"] += 1
    
    # Plan statistics
    total_crisis_plans = len(redis_client.lrange("crisis_plans", 0, -1))
    total_bcps = len(redis_client.lrange("bcps", 0, -1))
    
    return {
        "risk_assessments": risk_stats,
        "incidents": incident_stats,
        "total_crisis_plans": total_crisis_plans,
        "total_bcps": total_bcps,
        "last_updated": datetime.now().isoformat()
    }

@app.post("/risk-simulation")
async def run_risk_simulation(scenario: str, background_tasks: BackgroundTasks):
    """Ejecutar simulación de riesgo"""
    simulation_id = str(uuid.uuid4())
    
    simulation_data = {
        "simulation_id": simulation_id,
        "scenario": scenario,
        "status": "running",
        "started_at": datetime.now().isoformat()
    }
    
    redis_client.set(f"simulation:{simulation_id}", json.dumps(simulation_data))
    redis_client.lpush("simulations", simulation_id)
    
    # Run simulation in background
    background_tasks.add_task(run_simulation, simulation_id)
    
    return {"status": "initiated", "simulation_id": simulation_id}

@app.get("/risk-simulation/{simulation_id}")
async def get_simulation_result(simulation_id: str):
    """Obtener resultado de simulación de riesgo"""
    simulation_data = redis_client.get(f"simulation:{simulation_id}")
    if not simulation_data:
        raise HTTPException(status_code=404, detail="Simulación no encontrada")
    
    return json.loads(simulation_data)

@app.post("/stress-test")
async def perform_stress_test(test_type: str, background_tasks: BackgroundTasks):
    """Realizar test de estrés"""
    test_id = str(uuid.uuid4())
    
    test_data = {
        "test_id": test_id,
        "test_type": test_type,
        "status": "running",
        "started_at": datetime.now().isoformat()
    }
    
    redis_client.set(f"stress_test:{test_id}", json.dumps(test_data))
    redis_client.lpush("stress_tests", test_id)
    
    # Run stress test in background
    background_tasks.add_task(run_stress_test, test_id)
    
    return {"status": "initiated", "test_id": test_id}

@app.get("/risk-metrics")
async def get_risk_metrics():
    """Obtener métricas de riesgo"""
    import random
    
    return {
        "value_at_risk": round(random.uniform(0.1, 0.8), 3),
        "expected_shortfall": round(random.uniform(0.05, 0.4), 3),
        "var_confidence": 0.95,
        "stress_test_result": "passed" if random.random() > 0.1 else "failed",
        "liquidity_ratio": round(random.uniform(0.8, 1.5), 2),
        "capital_adequacy": round(random.uniform(1.2, 3.0), 2),
        "timestamp": datetime.now().isoformat()
    }

# Background Tasks
async def run_simulation(simulation_id: str):
    """Ejecutar simulación de riesgo en background"""
    try:
        logger.info(f"Ejecutando simulación de riesgo: {simulation_id}")
        
        # Simulate risk analysis
        await asyncio.sleep(2)
        
        simulation_data = redis_client.get(f"simulation:{simulation_id}")
        if simulation_data:
            sim = json.loads(simulation_data)
            sim["status"] = "completed"
            sim["results"] = {
                "probability_impact": random.uniform(0.1, 0.9),
                "mitigation_cost": random.uniform(10000, 500000),
                "residual_risk": random.uniform(0.05, 0.3),
                "recommendations": [
                    "Implement additional controls",
                    "Update crisis response plan",
                    "Review insurance coverage"
                ]
            }
            sim["completed_at"] = datetime.now().isoformat()
            redis_client.set(f"simulation:{simulation_id}", json.dumps(sim))
            
        logger.info(f"Simulación completada: {simulation_id}")
        
    except Exception as e:
        logger.error(f"Error ejecutando simulación {simulation_id}: {e}")

async def run_stress_test(test_id: str):
    """Ejecutar test de estrés en background"""
    try:
        logger.info(f"Ejecutando test de estrés: {test_id}")
        
        # Simulate stress testing
        await asyncio.sleep(1)
        
        test_data = redis_client.get(f"stress_test:{test_id}")
        if test_data:
            test = json.loads(test_data)
            test["status"] = "completed"
            test["results"] = {
                "passed": random.random() > 0.15,  # 85% pass rate
                "breach_points": random.randint(0, 3),
                "recovery_time": random.uniform(0.5, 4.0),
                "impact_assessment": "low" if random.random() > 0.3 else "medium"
            }
            test["completed_at"] = datetime.now().isoformat()
            redis_client.set(f"stress_test:{test_id}", json.dumps(test))
            
        logger.info(f"Test de estrés completado: {test_id}")
        
    except Exception as e:
        logger.error(f"Error ejecutando test de estrés {test_id}: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8030)