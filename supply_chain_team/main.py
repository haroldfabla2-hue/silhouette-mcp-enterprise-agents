"""
SUPPLY CHAIN TEAM - LOGISTICS & PROCUREMENT
Equipo especializado en gestión de cadena de suministro, logística y compras.

Agentes Especializados:
- Procurement Managers: Gestión de compras y proveedores
- Logistics Coordinators: Coordinación de transporte y distribución
- Inventory Managers: Gestión de inventarios y stock
- Supplier Relationship Managers: Relaciones con proveedores
- Supply Chain Analysts: Análisis de datos y optimización
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
class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class InventoryStatus(str, Enum):
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    REORDERING = "reordering"

class PurchaseOrder(BaseModel):
    id: Optional[str] = None
    order_number: str
    supplier_id: str
    items: List[Dict[str, Any]]
    total_amount: float
    status: OrderStatus = OrderStatus.PENDING
    order_date: Optional[datetime] = None
    expected_delivery: Optional[datetime] = None
    actual_delivery: Optional[datetime] = None

class InventoryItem(BaseModel):
    id: Optional[str] = None
    name: str
    sku: str
    current_stock: int
    minimum_stock: int
    maximum_stock: int
    status: InventoryStatus = InventoryStatus.IN_STOCK
    supplier_id: Optional[str] = None
    unit_cost: float
    last_updated: Optional[datetime] = None

class Supplier(BaseModel):
    id: Optional[str] = None
    name: str
    contact_email: str
    contact_phone: Optional[str] = None
    address: str
    category: str
    performance_rating: float
    payment_terms: str
    created_at: Optional[datetime] = None

class Shipment(BaseModel):
    id: Optional[str] = None
    order_id: str
    tracking_number: str
    carrier: str
    estimated_delivery: Optional[datetime]
    actual_delivery: Optional[datetime] = None
    status: str = "in_transit"
    destination: str

# FastAPI App
app = FastAPI(
    title="Supply Chain Team API",
    description="API para el equipo de cadena de suministro y logística",
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
    "procurement_manager": {
        "name": "Procurement Manager",
        "capabilities": [
            "supplier_negotiation",
            "purchase_order_creation",
            "contract_management",
            "cost_optimization"
        ]
    },
    "logistics_coordinator": {
        "name": "Logistics Coordinator",
        "capabilities": [
            "shipping_coordination",
            "transport_planning",
            "delivery_tracking",
            "freight_optimization"
        ]
    },
    "inventory_manager": {
        "name": "Inventory Manager",
        "capabilities": [
            "stock_monitoring",
            "reorder_planning",
            "warehouse_management",
            "demand_forecasting"
        ]
    },
    "supplier_relationship_manager": {
        "name": "Supplier Relationship Manager",
        "capabilities": [
            "supplier_development",
            "performance_evaluation",
            "relationship_management",
            "risk_assessment"
        ]
    },
    "supply_chain_analyst": {
        "name": "Supply Chain Analyst",
        "capabilities": [
            "data_analysis",
            "process_optimization",
            "performance_monitoring",
            "predictive_modeling"
        ]
    }
}

# API Endpoints
@app.get("/")
async def root():
    return {
        "team": "Supply Chain Team",
        "version": "1.0.0",
        "status": "operational",
        "agents": len(AGENTS),
        "description": "Equipo especializado en cadena de suministro y logística"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "supply-chain-team",
        "timestamp": datetime.now().isoformat(),
        "agents_active": len(AGENTS)
    }

@app.get("/agents")
async def get_agents():
    return {"agents": AGENTS, "total": len(AGENTS)}

@app.post("/purchase-orders")
async def create_purchase_order(po: PurchaseOrder, background_tasks: BackgroundTasks):
    """Crear nueva orden de compra"""
    po.id = str(uuid.uuid4())
    po.order_date = datetime.now()
    
    po_data = po.dict()
    redis_client.set(f"purchase_order:{po.id}", json.dumps(po_data))
    redis_client.lpush("purchase_orders", po.id)
    
    # Process order in background
    background_tasks.add_task(process_purchase_order, po.id)
    
    logger.info(f"Orden de compra creada: {po.id}")
    return {"status": "created", "purchase_order": po_data}

@app.get("/purchase-orders")
async def list_purchase_orders(status: Optional[OrderStatus] = None):
    """Listar órdenes de compra"""
    po_ids = redis_client.lrange("purchase_orders", 0, -1)
    purchase_orders = []
    
    for po_id in po_ids:
        po_data = redis_client.get(f"purchase_order:{po_id}")
        if po_data:
            po = json.loads(po_data)
            if status is None or po.get("status") == status:
                purchase_orders.append(po)
    
    return {"purchase_orders": purchase_orders, "total": len(purchase_orders)}

@app.get("/purchase-orders/{po_id}")
async def get_purchase_order(po_id: str):
    """Obtener detalles de orden de compra"""
    po_data = redis_client.get(f"purchase_order:{po_id}")
    if not po_data:
        raise HTTPException(status_code=404, detail="Orden de compra no encontrada")
    
    return json.loads(po_data)

@app.post("/inventory")
async def create_inventory_item(item: InventoryItem):
    """Crear nuevo item de inventario"""
    item.id = str(uuid.uuid4())
    item.last_updated = datetime.now()
    
    # Update status based on stock levels
    if item.current_stock <= 0:
        item.status = InventoryStatus.OUT_OF_STOCK
    elif item.current_stock <= item.minimum_stock:
        item.status = InventoryStatus.LOW_STOCK
    
    item_data = item.dict()
    redis_client.set(f"inventory_item:{item.id}", json.dumps(item_data))
    redis_client.lpush("inventory_items", item.id)
    
    logger.info(f"Item de inventario creado: {item.id}")
    return {"status": "created", "inventory_item": item_data}

@app.get("/inventory")
async def list_inventory(status: Optional[InventoryStatus] = None):
    """Listar inventario"""
    item_ids = redis_client.lrange("inventory_items", 0, -1)
    inventory = []
    
    for item_id in item_ids:
        item_data = redis_client.get(f"inventory_item:{item_id}")
        if item_data:
            item = json.loads(item_data)
            if status is None or item.get("status") == status:
                inventory.append(item)
    
    return {"inventory": inventory, "total": len(inventory)}

@app.post("/suppliers")
async def create_supplier(supplier: Supplier):
    """Crear nuevo proveedor"""
    supplier.id = str(uuid.uuid4())
    supplier.created_at = datetime.now()
    
    supplier_data = supplier.dict()
    redis_client.set(f"supplier:{supplier.id}", json.dumps(supplier_data))
    redis_client.lpush("suppliers", supplier.id)
    
    logger.info(f"Proveedor creado: {supplier.id}")
    return {"status": "created", "supplier": supplier_data}

@app.get("/suppliers")
async def list_suppliers(category: Optional[str] = None):
    """Listar proveedores"""
    supplier_ids = redis_client.lrange("suppliers", 0, -1)
    suppliers = []
    
    for supplier_id in supplier_ids:
        supplier_data = redis_client.get(f"supplier:{supplier_id}")
        if supplier_data:
            supplier_obj = json.loads(supplier_data)
            if category is None or supplier_obj.get("category") == category:
                suppliers.append(supplier_obj)
    
    return {"suppliers": suppliers, "total": len(suppliers)}

@app.post("/shipments")
async def create_shipment(shipment: Shipment, background_tasks: BackgroundTasks):
    """Crear nuevo shipment"""
    shipment.id = str(uuid.uuid4())
    
    shipment_data = shipment.dict()
    redis_client.set(f"shipment:{shipment.id}", json.dumps(shipment_data))
    redis_client.lpush("shipments", shipment.id)
    
    # Track shipment in background
    background_tasks.add_task(track_shipment, shipment.id)
    
    logger.info(f"Shipment creado: {shipment.id}")
    return {"status": "created", "shipment": shipment_data}

@app.get("/shipments")
async def list_shipments():
    """Listar shipments"""
    shipment_ids = redis_client.lrange("shipments", 0, -1)
    shipments = []
    
    for shipment_id in shipment_ids:
        shipment_data = redis_client.get(f"shipment:{shipment_id}")
        if shipment_data:
            shipments.append(json.loads(shipment_data))
    
    return {"shipments": shipments, "total": len(shipments)}

@app.get("/dashboard")
async def get_supply_chain_dashboard():
    """Obtener dashboard de cadena de suministro"""
    # Purchase order statistics
    po_ids = redis_client.lrange("purchase_orders", 0, -1)
    po_stats = {"pending": 0, "confirmed": 0, "shipped": 0, "delivered": 0, "cancelled": 0}
    
    for po_id in po_ids:
        po_data = redis_client.get(f"purchase_order:{po_id}")
        if po_data:
            po = json.loads(po_data)
            status = po.get("status", "pending")
            if status in po_stats:
                po_stats[status] += 1
    
    # Inventory statistics
    item_ids = redis_client.lrange("inventory_items", 0, -1)
    inv_stats = {"in_stock": 0, "low_stock": 0, "out_of_stock": 0, "reordering": 0}
    
    for item_id in item_ids:
        item_data = redis_client.get(f"inventory_item:{item_id}")
        if item_data:
            item = json.loads(item_data)
            status = item.get("status", "in_stock")
            if status in inv_stats:
                inv_stats[status] += 1
    
    total_suppliers = len(redis_client.lrange("suppliers", 0, -1))
    total_shipments = len(redis_client.lrange("shipments", 0, -1))
    
    return {
        "purchase_orders": po_stats,
        "inventory": inv_stats,
        "total_suppliers": total_suppliers,
        "total_shipments": total_shipments,
        "last_updated": datetime.now().isoformat()
    }

@app.post("/reorder/{item_id}")
async def trigger_reorder(item_id: str, background_tasks: BackgroundTasks):
    """Disparar reorden de item"""
    item_data = redis_client.get(f"inventory_item:{item_id}")
    if not item_data:
        raise HTTPException(status_code=404, detail="Item de inventario no encontrado")
    
    item = json.loads(item_data)
    item["status"] = InventoryStatus.REORDERING
    item["last_updated"] = datetime.now().isoformat()
    
    redis_client.set(f"inventory_item:{item_id}", json.dumps(item))
    
    # Create automatic purchase order
    background_tasks.add_task(create_auto_reorder, item_id)
    
    return {"status": "reorder_triggered", "item_id": item_id}

# Background Tasks
async def process_purchase_order(po_id: str):
    """Procesar orden de compra en background"""
    try:
        logger.info(f"Procesando orden de compra: {po_id}")
        
        # Update status to confirmed
        po_data = redis_client.get(f"purchase_order:{po_id}")
        if po_data:
            po = json.loads(po_data)
            po["status"] = OrderStatus.CONFIRMED
            po["confirmed_at"] = datetime.now().isoformat()
            redis_client.set(f"purchase_order:{po_id}", json.dumps(po))
            
        logger.info(f"Orden de compra procesada: {po_id}")
        
    except Exception as e:
        logger.error(f"Error procesando orden de compra {po_id}: {e}")

async def track_shipment(shipment_id: str):
    """Rastrear shipment en background"""
    try:
        logger.info(f"Rastreando shipment: {shipment_id}")
        
        # Simulate shipment tracking
        await asyncio.sleep(2)
        
        shipment_data = redis_client.get(f"shipment:{shipment_id}")
        if shipment_data:
            shipment = json.loads(shipment_data)
            shipment["status"] = "delivered"
            shipment["actual_delivery"] = datetime.now().isoformat()
            redis_client.set(f"shipment:{shipment_id}", json.dumps(shipment))
            
        logger.info(f"Shipment entregado: {shipment_id}")
        
    except Exception as e:
        logger.error(f"Error rastreando shipment {shipment_id}: {e}")

async def create_auto_reorder(item_id: str):
    """Crear reorden automático en background"""
    try:
        logger.info(f"Creando reorden automático para: {item_id}")
        
        # Simulate reorder process
        await asyncio.sleep(1)
        
        # Update item status back to in_stock (simulated)
        item_data = redis_client.get(f"inventory_item:{item_id}")
        if item_data:
            item = json.loads(item_data)
            item["status"] = InventoryStatus.IN_STOCK
            item["last_updated"] = datetime.now().isoformat()
            redis_client.set(f"inventory_item:{item_id}", json.dumps(item))
            
        logger.info(f"Reorden automático creado para: {item_id}")
        
    except Exception as e:
        logger.error(f"Error creando reorden automático {item_id}: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8032)