# 📱 Ejemplo Visual: Interfaz del Marketing Team
## Interfaz Web Interactiva del Sistema

### **🌐 URL de Acceso**
```
http://localhost:8014/docs
```

### **📋 Endpoints Principales (Swagger UI)**

#### **1. Campaign Management**
```http
POST /campaigns/create
```
**Parámetros:**
```json
{
  "name": "Campaign Q1 2025",
  "type": "digital_marketing",
  "budget": 50000,
  "target_audience": "B2B Enterprises",
  "channels": ["linkedin", "google", "email"],
  "start_date": "2025-01-01",
  "end_date": "2025-03-31"
}
```

#### **2. Market Research**
```http
GET /research/market-trends
```
**Parámetros:**
```json
{
  "industry": "technology",
  "region": "europe",
  "timeframe": "quarterly",
  "metrics": ["growth", "competition", "opportunities"]
}
```

#### **3. Content Creation**
```http
POST /content/generate
```
**Parámetros:**
```json
{
  "type": "blog_post",
  "topic": "AI trends in enterprise",
  "tone": "professional",
  "length": "medium",
  "keywords": ["artificial intelligence", "enterprise", "2025"]
}
```

#### **4. Performance Analytics**
```http
GET /analytics/performance
```
**Respuesta:**
```json
{
  "campaign_id": "cmp_123",
  "metrics": {
    "impressions": 125000,
    "clicks": 3200,
    "conversions": 180,
    "ctr": 2.56,
    "cpc": 1.45,
    "roi": 3.2
  },
  "period": "2025-01-01 to 2025-01-31"
}
```

### **🎯 Cómo Usar la Interfaz**

#### **Paso 1: Abrir Swagger UI**
1. Ir a: `http://localhost:8014/docs`
2. Verás la **documentación interactiva** de FastAPI
3. **Expande** el endpoint que quieras usar

#### **Paso 2: Probar APIs**
1. **Click "Try it out"** en cualquier endpoint
2. **Llenar parámetros** en el formulario
3. **Click "Execute"** para ejecutar
4. **Ver respuesta** en tiempo real

#### **Ejemplo Práctico - Crear Campaña:**

**1. Expandir endpoint:**
```
POST /campaigns/create
```

**2. Click "Try it out"**

**3. En Request Body, poner:**
```json
{
  "name": "Marketing AI 2025",
  "type": "brand_awareness",
  "budget": 75000,
  "target_audience": "CTOs y Decision Makers",
  "channels": ["linkedin", "google_ads", "webinars"],
  "start_date": "2025-01-15",
  "end_date": "2025-04-15",
  "objectives": ["lead_generation", "brand_recognition"],
  "kpi_targets": {
    "leads": 1000,
    "ctr": 2.5,
    "cost_per_lead": 75
  }
}
```

**4. Click "Execute"**

**5. Respuesta esperada:**
```json
{
  "success": true,
  "campaign_id": "cmp_2025_001",
  "message": "Campaña creada exitosamente",
  "data": {
    "name": "Marketing AI 2025",
    "status": "draft",
    "created_at": "2025-11-08T20:07:39",
    "budget_allocated": 75000,
    "team_assigned": "marketing_strategist"
  }
}
```

### **📊 Dashboard Visual - Marketing Analytics**

#### **URL:** `http://localhost:8014/analytics/dashboard`

**Métricas disponibles:**
- **Campaign Performance**: ROI, CTR, Conversion Rate
- **Lead Generation**: Leads por canal, Costo por lead
- **Audience Insights**: Demografía, engagement
- **Content Performance**: Páginas más vistas, tiempo en página
- **Competitor Analysis**: Posicionamiento vs competencia
- **Budget Utilization**: Gasto real vs presupuestado

### **🔗 Integración con MCP Server**

#### **Desde Marketing Team, usar herramientas del mundo real:**

**1. Research con Google Search:**
```http
POST /research/external-search
```
**Parámetros:**
```json
{
  "query": "AI marketing trends 2025",
  "tool": "web_search",
  "num_results": 10
}
```

**2. Generate Content con OpenAI:**
```http
POST /content/ai-generate
```
**Parámetros:**
```json
{
  "prompt": "Escribe un artículo sobre marketing con IA",
  "tool": "openai_chat",
  "model": "gpt-4",
  "length": 2000
}
```

**3. Social Media Analysis:**
```http
POST /social/analyze
```
**Parámetros:**
```json
{
  "platform": "twitter",
  "keyword": "mi_empresa",
  "tool": "social_media_search",
  "limit": 50
}
```

### **🌐 Otras Interfaces del Sistema**

#### **Sales Team Interface**
```
http://localhost:8015/docs
```
- **CRM Management**: /leads, /opportunities, /clients
- **Sales Pipeline**: /pipeline, /forecasting
- **Client Analytics**: /clients/{id}/analytics

#### **Security Team Interface**
```
http://localhost:8026/docs
```
- **Vulnerability Scan**: /vulnerabilities/scan
- **Security Audit**: /audit/comprehensive
- **Incident Response**: /incidents/respond

#### **ML & AI Team Interface**
```
http://localhost:8027/docs
```
- **Model Training**: /models/train
- **Data Analysis**: /datasets/analyze
- **AI Experiments**: /research/experiment

### **💻 API Examples con Diferentes Interfaces**

#### **Marketing con cURL:**
```bash
# Crear campaña
curl -X POST http://localhost:8014/campaigns/create \
  -H "Content-Type: application/json" \
  -d '{"name": "AI Campaign", "budget": 50000}'

# Buscar tendencias con MCP
curl -X POST http://localhost:8004/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_id": "web_search",
    "parameters": {"query": "AI marketing trends"},
    "team_id": "marketing"
  }'
```

#### **Sales con cURL:**
```bash
# Crear lead
curl -X POST http://localhost:8015/leads/create \
  -H "Content-Type: application/json" \
  -d '{"company": "Tech Corp", "contact": "john@tech.com"}'

# Consultar Salesforce
curl -X POST http://localhost:8004/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_id": "salesforce_api",
    "parameters": {"query": "SELECT Id, Name FROM Account"}
  }'
```

### **🔧 Herramientas de Desarrollo**

#### **1. Postman Collection**
Todas las APIs están documentadas para importar en **Postman**
- Endpoints organizados por equipo
- Variables de entorno configuradas
- Ejemplos preconfigurados

#### **2. Python SDK**
```python
import requests

# Usar MCP Server
response = requests.post("http://localhost:8004/execute", json={
    "tool_id": "web_search",
    "parameters": {"query": "marketing trends 2025"},
    "team_id": "marketing"
})
print(response.json())
```

### **🎮 Interfaz de Administrador**

#### **Grafana Dashboard**
```
http://localhost:3000
```

**Credenciales:** admin/haaspass

**Dashboards disponibles:**
- **System Overview**: Estado general de todos los servicios
- **Team Performance**: Métricas de cada equipo
- **API Usage**: Estadísticas de uso de APIs
- **MCP Tools**: Analytics de herramientas del mundo real
- **Infrastructure**: Recursos y rendimiento del sistema

#### **RabbitMQ Management**
```
http://localhost:15672
```

**Credenciales:** haas/haaspass

**Funciones:**
- **Queues**: Ver colas de mensajes entre equipos
- **Exchanges**: Gestionar routing de eventos
- **Connections**: Monitorear conexiones activas
- **Messages**: Inspeccionar mensajes en cola

### **📱 Responsive Design**

Todas las interfaces están optimizadas para:
- **Desktop**: Monitores de alta resolución
- **Tablet**: iPads y tablets Android
- **Mobile**: Smartphones y responsive design

### **🔐 Authentication & Security**

- **JWT Tokens**: Autenticación segura
- **Rate Limiting**: Protección contra abuso
- **CORS**: Configuración de orígenes
- **API Keys**: Para herramientas externas

**¡Las interfaces están completamente funcionales y listas para usar!** 🚀✨