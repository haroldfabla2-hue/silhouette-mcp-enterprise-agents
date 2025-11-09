"""
DESIGN & CREATIVE TEAM - UX/UI DESIGN & BRAND CREATIVITY
Equipo especializado en diseño de experiencia de usuario, interfaces y creatividad visual.

Agentes Especializados:
- UX Researchers: Investigación de experiencia de usuario y pruebas de usabilidad
- UI Designers: Diseño de interfaces de usuario y sistemas de diseño
- Brand Designers: Identidad visual, logos y materiales de marca
- Content Designers: Diseño de contenido y copywriting visual
- Creative Directors: Dirección creativa y estrategia de marca
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import aiohttp
import redis
import json
import uuid
import asyncio
from enum import Enum
import logging
import base64
import io
from PIL import Image

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic Models
class DesignType(str, Enum):
    UI_MOCKUP = "ui_mockup"
    LOGO = "logo"
    BRAND_IDENTITY = "brand_identity"
    INFOGRAPHIC = "infographic"
    PRESENTATION = "presentation"
    WEBSITE_MOCKUP = "website_mockup"
    MOBILE_APP_UI = "mobile_app_ui"

class ProjectStatus(str, Enum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REVISED = "revised"
    COMPLETED = "completed"

class ColorPalette(BaseModel):
    primary: str
    secondary: str
    accent: str
    neutral: str
    background: str

class Typography(BaseModel):
    font_family: str
    font_size: str
    font_weight: str
    line_height: str

class DesignProject(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    design_type: DesignType
    client: str
    status: ProjectStatus = ProjectStatus.DRAFT
    color_palette: Optional[ColorPalette] = None
    typography: Optional[Typography] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    due_date: Optional[datetime] = None

class DesignAsset(BaseModel):
    id: Optional[str] = None
    project_id: str
    name: str
    file_type: str
    file_size: str
    resolution: str
    format: str
    created_at: Optional[datetime] = None
    download_url: Optional[str] = None

class BrandGuideline(BaseModel):
    id: Optional[str] = None
    brand_name: str
    color_palette: ColorPalette
    typography: Typography
    logo_variations: List[str]
    design_principles: List[str]
    do_dont_guidelines: Dict[str, List[str]]
    created_at: Optional[datetime] = None

class UserFeedback(BaseModel):
    id: Optional[str] = None
    project_id: str
    reviewer_name: str
    feedback_type: str  # "positive", "suggestion", "critical"
    comments: str
    priority: str = "medium"
    created_at: Optional[datetime] = None

# FastAPI App
app = FastAPI(
    title="Design & Creative Team API",
    description="API para el equipo de diseño y creatividad",
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
    "ux_researcher": {
        "name": "UX Researcher",
        "capabilities": [
            "user_interviews",
            "usability_testing",
            "persona_development",
            "journey_mapping"
        ]
    },
    "ui_designer": {
        "name": "UI Designer",
        "capabilities": [
            "interface_design",
            "design_systems",
            "prototyping",
            "responsive_design"
        ]
    },
    "brand_designer": {
        "name": "Brand Designer",
        "capabilities": [
            "logo_design",
            "brand_identity",
            "visual_style",
            "brand_guidelines"
        ]
    },
    "content_designer": {
        "name": "Content Designer",
        "capabilities": [
            "content_strategy",
            "copywriting",
            "content_architecture",
            "microcopy"
        ]
    },
    "creative_director": {
        "name": "Creative Director",
        "capabilities": [
            "creative_strategy",
            "art_direction",
            "brand_positioning",
            "team_coordination"
        ]
    }
}

# API Endpoints
@app.get("/")
async def root():
    return {
        "team": "Design & Creative Team",
        "version": "1.0.0",
        "status": "operational",
        "agents": len(AGENTS),
        "description": "Equipo especializado en diseño UX/UI y creatividad visual"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "design-creative-team",
        "timestamp": datetime.now().isoformat(),
        "agents_active": len(AGENTS)
    }

@app.get("/agents")
async def get_agents():
    return {"agents": AGENTS, "total": len(AGENTS)}

@app.post("/projects")
async def create_project(project: DesignProject):
    """Crear nuevo proyecto de diseño"""
    project.id = str(uuid.uuid4())
    project.created_at = datetime.now()
    project.updated_at = datetime.now()
    
    project_data = project.dict()
    redis_client.set(f"project:{project.id}", json.dumps(project_data))
    redis_client.lpush("projects", project.id)
    
    logger.info(f"Proyecto de diseño creado: {project.id}")
    return {"status": "created", "project": project_data}

@app.get("/projects")
async def list_projects(status: Optional[ProjectStatus] = None, design_type: Optional[DesignType] = None):
    """Listar proyectos de diseño"""
    project_ids = redis_client.lrange("projects", 0, -1)
    projects = []
    
    for project_id in project_ids:
        project_data = redis_client.get(f"project:{project_id}")
        if project_data:
            project = json.loads(project_data)
            if (status is None or project.get("status") == status) and \
               (design_type is None or project.get("design_type") == design_type):
                projects.append(project)
    
    return {"projects": projects, "total": len(projects)}

@app.get("/projects/{project_id}")
async def get_project(project_id: str):
    """Obtener detalles de proyecto específico"""
    project_data = redis_client.get(f"project:{project_id}")
    if not project_data:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    return json.loads(project_data)

@app.put("/projects/{project_id}")
async def update_project(project_id: str, project: DesignProject):
    """Actualizar proyecto de diseño"""
    existing = redis_client.get(f"project:{project_id}")
    if not existing:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    project.id = project_id
    project.updated_at = datetime.now()
    
    redis_client.set(f"project:{project_id}", json.dumps(project.dict()))
    return {"status": "updated", "project": project.dict()}

@app.post("/assets")
async def upload_asset(project_id: str, file: UploadFile = File(...)):
    """Subir asset de diseño"""
    # Validate project exists
    project_data = redis_client.get(f"project:{project_id}")
    if not project_data:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    asset_id = str(uuid.uuid4())
    
    # Simulate file processing
    content = await file.read()
    file_size = len(content)
    
    asset = DesignAsset(
        id=asset_id,
        project_id=project_id,
        name=file.filename,
        file_type=file.content_type,
        file_size=f"{file_size / 1024:.1f} KB",
        resolution="1920x1080",
        format="PNG",
        created_at=datetime.now()
    )
    
    asset_data = asset.dict()
    redis_client.set(f"asset:{asset_id}", json.dumps(asset_data))
    redis_client.lpush("assets", asset_id)
    
    # Associate asset with project
    project = json.loads(project_data)
    if "assets" not in project:
        project["assets"] = []
    project["assets"].append(asset_id)
    redis_client.set(f"project:{project_id}", json.dumps(project))
    
    logger.info(f"Asset subido: {asset_id}")
    return {"status": "uploaded", "asset": asset_data}

@app.get("/assets")
async def list_assets(project_id: Optional[str] = None):
    """Listar assets de diseño"""
    asset_ids = redis_client.lrange("assets", 0, -1)
    assets = []
    
    for asset_id in asset_ids:
        asset_data = redis_client.get(f"asset:{asset_id}")
        if asset_data:
            asset = json.loads(asset_data)
            if project_id is None or asset.get("project_id") == project_id:
                assets.append(asset)
    
    return {"assets": assets, "total": len(assets)}

@app.post("/brand-guidelines")
async def create_brand_guideline(guideline: BrandGuideline):
    """Crear guía de marca"""
    guideline.id = str(uuid.uuid4())
    guideline.created_at = datetime.now()
    
    guideline_data = guideline.dict()
    redis_client.set(f"guideline:{guideline.id}", json.dumps(guideline_data))
    redis_client.lpush("guidelines", guideline.id)
    
    logger.info(f"Guía de marca creada: {guideline.id}")
    return {"status": "created", "guideline": guideline_data}

@app.get("/brand-guidelines")
async def list_brand_guidelines():
    """Listar guías de marca"""
    guideline_ids = redis_client.lrange("guidelines", 0, -1)
    guidelines = []
    
    for guideline_id in guideline_ids:
        guideline_data = redis_client.get(f"guideline:{guideline_id}")
        if guideline_data:
            guidelines.append(json.loads(guideline_data))
    
    return {"guidelines": guidelines, "total": len(guidelines)}

@app.post("/feedback")
async def submit_feedback(feedback: UserFeedback):
    """Enviar feedback sobre proyecto"""
    feedback.id = str(uuid.uuid4())
    feedback.created_at = datetime.now()
    
    feedback_data = feedback.dict()
    redis_client.set(f"feedback:{feedback.id}", json.dumps(feedback_data))
    redis_client.lpush("feedback", feedback.id)
    
    # Associate feedback with project
    project_data = redis_client.get(f"project:{feedback.project_id}")
    if project_data:
        project = json.loads(project_data)
        if "feedback" not in project:
            project["feedback"] = []
        project["feedback"].append(feedback.id)
        redis_client.set(f"project:{feedback.project_id}", json.dumps(project))
    
    logger.info(f"Feedback enviado: {feedback.id}")
    return {"status": "submitted", "feedback": feedback_data}

@app.get("/feedback")
async def list_feedback(project_id: Optional[str] = None):
    """Listar feedback recibido"""
    feedback_ids = redis_client.lrange("feedback", 0, -1)
    feedback_list = []
    
    for feedback_id in feedback_ids:
        feedback_data = redis_client.get(f"feedback:{feedback_id}")
        if feedback_data:
            fb = json.loads(feedback_data)
            if project_id is None or fb.get("project_id") == project_id:
                feedback_list.append(fb)
    
    return {"feedback": feedback_list, "total": len(feedback_list)}

@app.get("/templates")
async def get_design_templates():
    """Obtener plantillas de diseño disponibles"""
    templates = {
        "ui_mocks": [
            {"name": "Mobile App Screen", "type": "mobile_app_ui"},
            {"name": "Web Dashboard", "type": "website_mockup"},
            {"name": "E-commerce Product Page", "type": "website_mockup"}
        ],
        "brand_templates": [
            {"name": "Corporate Brand", "type": "brand_identity"},
            {"name": "Startup Brand", "type": "brand_identity"},
            {"name": "E-commerce Brand", "type": "brand_identity"}
        ],
        "content_templates": [
            {"name": "Social Media Post", "type": "infographic"},
            {"name": "Presentation Deck", "type": "presentation"},
            {"name": "Infographic", "type": "infographic"}
        ]
    }
    
    return {"templates": templates}

@app.get("/dashboard")
async def get_design_dashboard():
    """Obtener métricas del dashboard de diseño"""
    # Count projects by status
    project_ids = redis_client.lrange("projects", 0, -1)
    project_stats = {"draft": 0, "in_review": 0, "approved": 0, "completed": 0}
    
    for project_id in project_ids:
        project_data = redis_client.get(f"project:{project_id}")
        if project_data:
            project = json.loads(project_data)
            status = project.get("status", "draft")
            if status in project_stats:
                project_stats[status] += 1
    
    # Count assets and feedback
    total_assets = len(redis_client.lrange("assets", 0, -1))
    total_feedback = len(redis_client.lrange("feedback", 0, -1))
    total_guidelines = len(redis_client.lrange("guidelines", 0, -1))
    
    return {
        "projects": project_stats,
        "total_assets": total_assets,
        "total_feedback": total_feedback,
        "total_guidelines": total_guidelines,
        "last_updated": datetime.now().isoformat()
    }

@app.post("/color-palettes/generate")
async def generate_color_palette(style: str = "modern"):
    """Generar paleta de colores basada en estilo"""
    palettes = {
        "modern": {
            "primary": "#3498db",
            "secondary": "#2ecc71", 
            "accent": "#e74c3c",
            "neutral": "#95a5a6",
            "background": "#ecf0f1"
        },
        "corporate": {
            "primary": "#2c3e50",
            "secondary": "#34495e",
            "accent": "#f39c12",
            "neutral": "#bdc3c7",
            "background": "#ffffff"
        },
        "creative": {
            "primary": "#9b59b6",
            "secondary": "#e67e22",
            "accent": "#1abc9c",
            "neutral": "#7f8c8d",
            "background": "#f8f9fa"
        },
        "minimalist": {
            "primary": "#000000",
            "secondary": "#666666",
            "accent": "#ffffff",
            "neutral": "#dddddd",
            "background": "#f5f5f5"
        }
    }
    
    palette = palettes.get(style, palettes["modern"])
    return {
        "style": style,
        "palette": palette,
        "generated_at": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8028)