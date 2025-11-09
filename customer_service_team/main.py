"""
CUSTOMER SERVICE TEAM - SUPPORT & HELPDESK
Equipo especializado en atención al cliente, soporte técnico y gestión de tickets.

Agentes Especializados:
- Customer Service Representatives: Atención general de clientes y consultas
- Technical Support Agents: Soporte técnico especializado
- Quality Assurance Specialists: Monitoreo de calidad del servicio
- Training Coordinators: Capacitación y desarrollo del equipo
- Customer Success Managers: Gestión de satisfacción y retención
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
class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    RESOLVED = "resolved"
    CLOSED = "closed"

class CustomerType(str, Enum):
    INDIVIDUAL = "individual"
    BUSINESS = "business"
    ENTERPRISE = "enterprise"
    VIP = "vip"

class Ticket(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    priority: TicketPriority
    status: TicketStatus = TicketStatus.OPEN
    customer_id: str
    customer_type: CustomerType
    category: str
    assigned_agent: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

class Customer(BaseModel):
    id: Optional[str] = None
    name: str
    email: str
    phone: Optional[str] = None
    customer_type: CustomerType
    satisfaction_score: float = 0.0
    total_tickets: int = 0
    created_at: Optional[datetime] = None

class AgentPerformance(BaseModel):
    id: Optional[str] = None
    agent_name: str
    total_tickets: int = 0
    resolved_tickets: int = 0
    avg_resolution_time: float
    satisfaction_rating: float
    period: str

class KnowledgeBase(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    category: str
    tags: List[str]
    views: int = 0
    helpful_votes: int = 0
    created_at: Optional[datetime] = None

# FastAPI App
app = FastAPI(
    title="Customer Service Team API",
    description="API para el equipo de atención al cliente",
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
    "customer_service_rep": {
        "name": "Customer Service Representative",
        "capabilities": [
            "customer_inquiry_handling",
            "order_support",
            "general_assistance",
            "escalation_management"
        ]
    },
    "technical_support_agent": {
        "name": "Technical Support Agent",
        "capabilities": [
            "technical_troubleshooting",
            "system_diagnostics",
            "solution_implementation",
            "remote_assistance"
        ]
    },
    "quality_assurance_specialist": {
        "name": "Quality Assurance Specialist",
        "capabilities": [
            "service_monitoring",
            "quality_assessment",
            "process_improvement",
            "compliance_checking"
        ]
    },
    "training_coordinator": {
        "name": "Training Coordinator",
        "capabilities": [
            "agent_training",
            "skill_development",
            "material_preparation",
            "performance_coaching"
        ]
    },
    "customer_success_manager": {
        "name": "Customer Success Manager",
        "capabilities": [
            "customer_retention",
            "satisfaction_tracking",
            "relationship_management",
            "value_optimization"
        ]
    }
}

# API Endpoints
@app.get("/")
async def root():
    return {
        "team": "Customer Service Team",
        "version": "1.0.0",
        "status": "operational",
        "agents": len(AGENTS),
        "description": "Equipo especializado en atención al cliente y soporte"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "customer-service-team",
        "timestamp": datetime.now().isoformat(),
        "agents_active": len(AGENTS)
    }

@app.get("/agents")
async def get_agents():
    return {"agents": AGENTS, "total": len(AGENTS)}

@app.post("/tickets")
async def create_ticket(ticket: Ticket):
    """Crear nuevo ticket de soporte"""
    ticket.id = str(uuid.uuid4())
    ticket.created_at = datetime.now()
    ticket.updated_at = datetime.now()
    
    ticket_data = ticket.dict()
    redis_client.set(f"ticket:{ticket.id}", json.dumps(ticket_data))
    redis_client.lpush("tickets", ticket.id)
    
    # Auto-assign if high priority
    if ticket.priority in [TicketPriority.HIGH, TicketPriority.URGENT]:
        background_tasks = BackgroundTasks()
        background_tasks.add_task(auto_assign_ticket, ticket.id)
    
    logger.info(f"Ticket creado: {ticket.id}")
    return {"status": "created", "ticket": ticket_data}

@app.get("/tickets")
async def list_tickets(status: Optional[TicketStatus] = None, priority: Optional[TicketPriority] = None):
    """Listar tickets de soporte"""
    ticket_ids = redis_client.lrange("tickets", 0, -1)
    tickets = []
    
    for ticket_id in ticket_ids:
        ticket_data = redis_client.get(f"ticket:{ticket_id}")
        if ticket_data:
            ticket_obj = json.loads(ticket_data)
            if (status is None or ticket_obj.get("status") == status) and \
               (priority is None or ticket_obj.get("priority") == priority):
                tickets.append(ticket_obj)
    
    return {"tickets": tickets, "total": len(tickets)}

@app.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: str):
    """Obtener detalles de ticket específico"""
    ticket_data = redis_client.get(f"ticket:{ticket_id}")
    if not ticket_data:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    
    return json.loads(ticket_data)

@app.put("/tickets/{ticket_id}")
async def update_ticket(ticket_id: str, ticket: Ticket):
    """Actualizar ticket de soporte"""
    existing = redis_client.get(f"ticket:{ticket_id}")
    if not existing:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    
    ticket.id = ticket_id
    ticket.updated_at = datetime.now()
    
    # Auto-resolve if marked as resolved
    if ticket.status == TicketStatus.RESOLVED:
        ticket.resolved_at = datetime.now()
    
    redis_client.set(f"ticket:{ticket_id}", json.dumps(ticket.dict()))
    return {"status": "updated", "ticket": ticket.dict()}

@app.put("/tickets/{ticket_id}/assign")
async def assign_ticket(ticket_id: str, agent_name: str):
    """Asignar ticket a agente"""
    ticket_data = redis_client.get(f"ticket:{ticket_id}")
    if not ticket_data:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    
    ticket = json.loads(ticket_data)
    ticket["assigned_agent"] = agent_name
    ticket["status"] = TicketStatus.IN_PROGRESS
    ticket["updated_at"] = datetime.now().isoformat()
    
    redis_client.set(f"ticket:{ticket_id}", json.dumps(ticket))
    return {"status": "assigned", "ticket": ticket}

@app.post("/customers")
async def create_customer(customer: Customer):
    """Crear nuevo cliente"""
    customer.id = str(uuid.uuid4())
    customer.created_at = datetime.now()
    
    customer_data = customer.dict()
    redis_client.set(f"customer:{customer.id}", json.dumps(customer_data))
    redis_client.lpush("customers", customer.id)
    
    logger.info(f"Cliente creado: {customer.id}")
    return {"status": "created", "customer": customer_data}

@app.get("/customers")
async def list_customers(customer_type: Optional[CustomerType] = None):
    """Listar clientes"""
    customer_ids = redis_client.lrange("customers", 0, -1)
    customers = []
    
    for customer_id in customer_ids:
        customer_data = redis_client.get(f"customer:{customer_id}")
        if customer_data:
            customer_obj = json.loads(customer_data)
            if customer_type is None or customer_obj.get("customer_type") == customer_type:
                customers.append(customer_obj)
    
    return {"customers": customers, "total": len(customers)}

@app.get("/customers/{customer_id}")
async def get_customer(customer_id: str):
    """Obtener detalles de cliente específico"""
    customer_data = redis_client.get(f"customer:{customer_id}")
    if not customer_data:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    return json.loads(customer_data)

@app.get("/agent-performance")
async def get_agent_performance():
    """Obtener métricas de rendimiento de agentes"""
    import random
    
    agents = [agent["name"] for agent in AGENTS.values()]
    performance = []
    
    for agent_name in agents:
        perf = AgentPerformance(
            agent_name=agent_name,
            total_tickets=random.randint(50, 200),
            resolved_tickets=random.randint(40, 180),
            avg_resolution_time=random.uniform(1.0, 8.0),
            satisfaction_rating=random.uniform(3.5, 5.0),
            period="current_month"
        )
        performance.append(perf.dict())
    
    return {"performance": performance, "total_agents": len(performance)}

@app.post("/knowledge-base")
async def create_kb_article(article: KnowledgeBase):
    """Crear artículo de base de conocimiento"""
    article.id = str(uuid.uuid4())
    article.created_at = datetime.now()
    
    article_data = article.dict()
    redis_client.set(f"kb_article:{article.id}", json.dumps(article_data))
    redis_client.lpush("kb_articles", article.id)
    
    logger.info(f"Artículo de KB creado: {article.id}")
    return {"status": "created", "article": article_data}

@app.get("/knowledge-base")
async def list_kb_articles(category: Optional[str] = None):
    """Listar artículos de base de conocimiento"""
    article_ids = redis_client.lrange("kb_articles", 0, -1)
    articles = []
    
    for article_id in article_ids:
        article_data = redis_client.get(f"kb_article:{article_id}")
        if article_data:
            article_obj = json.loads(article_data)
            if category is None or article_obj.get("category") == category:
                articles.append(article_obj)
    
    return {"articles": articles, "total": len(articles)}

@app.get("/dashboard")
async def get_customer_service_dashboard():
    """Obtener dashboard de servicio al cliente"""
    # Ticket statistics
    ticket_ids = redis_client.lrange("tickets", 0, -1)
    ticket_stats = {
        "open": 0, "in_progress": 0, "pending": 0, 
        "resolved": 0, "closed": 0, "urgent": 0
    }
    
    for ticket_id in ticket_ids:
        ticket_data = redis_client.get(f"ticket:{ticket_id}")
        if ticket_data:
            ticket = json.loads(ticket_data)
            status = ticket.get("status", "open")
            priority = ticket.get("priority", "low")
            
            if status in ticket_stats:
                ticket_stats[status] += 1
            if priority == "urgent":
                ticket_stats["urgent"] += 1
    
    # Customer statistics
    customer_ids = redis_client.lrange("customers", 0, -1)
    total_customers = len(customer_ids)
    
    # Knowledge base statistics
    kb_articles = len(redis_client.lrange("kb_articles", 0, -1))
    
    return {
        "tickets": ticket_stats,
        "total_customers": total_customers,
        "kb_articles": kb_articles,
        "active_agents": len(AGENTS),
        "last_updated": datetime.now().isoformat()
    }

@app.get("/satisfaction-survey")
async def get_satisfaction_survey():
    """Obtener métricas de satisfacción de clientes"""
    import random
    
    return {
        "overall_satisfaction": round(random.uniform(3.5, 5.0), 2),
        "response_time_rating": round(random.uniform(3.0, 5.0), 2),
        "resolution_quality": round(random.uniform(3.5, 4.8), 2),
        "agent_helpfulness": round(random.uniform(3.8, 4.9), 2),
        "net_promoter_score": random.randint(30, 80),
        "survey_responses": random.randint(100, 500),
        "period": "last_30_days",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/escalate/{ticket_id}")
async def escalate_ticket(ticket_id: str, reason: str):
    """Escalar ticket a nivel superior"""
    ticket_data = redis_client.get(f"ticket:{ticket_id}")
    if not ticket_data:
        raise HTTPException(status_code=404, detail="Ticket no encontrado")
    
    ticket = json.loads(ticket_data)
    ticket["status"] = "escalated"
    ticket["escalation_reason"] = reason
    ticket["escalated_at"] = datetime.now().isoformat()
    
    # Increase priority
    if ticket.get("priority") == TicketPriority.LOW:
        ticket["priority"] = TicketPriority.MEDIUM
    elif ticket.get("priority") == TicketPriority.MEDIUM:
        ticket["priority"] = TicketPriority.HIGH
    
    redis_client.set(f"ticket:{ticket_id}", json.dumps(ticket))
    return {"status": "escalated", "ticket": ticket}

# Background Tasks
async def auto_assign_ticket(ticket_id: str):
    """Asignar ticket automáticamente a agente disponible"""
    try:
        logger.info(f"Asignando automáticamente ticket: {ticket_id}")
        
        # Simple round-robin assignment
        agents = list(AGENTS.keys())
        selected_agent = agents[len(ticket_id) % len(agents)]
        
        ticket_data = redis_client.get(f"ticket:{ticket_id}")
        if ticket_data:
            ticket = json.loads(ticket_data)
            ticket["assigned_agent"] = AGENTS[selected_agent]["name"]
            ticket["status"] = TicketStatus.IN_PROGRESS
            ticket["updated_at"] = datetime.now().isoformat()
            redis_client.set(f"ticket:{ticket_id}", json.dumps(ticket))
            
        logger.info(f"Ticket asignado a {AGENTS[selected_agent]['name']}")
        
    except Exception as e:
        logger.error(f"Error auto-asignando ticket {ticket_id}: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8031)