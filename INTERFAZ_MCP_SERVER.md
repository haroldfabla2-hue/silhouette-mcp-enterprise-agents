# 🖥️ Ejemplo: Interfaz del MCP Server
## Cómo Acceder y Usar la Interfaz

### **🌐 URL Principal**
```
http://localhost:8004
```

### **📚 Documentación API Interactiva**
```
http://localhost:8004/docs
```
- **Swagger UI** - Interfaz visual para probar APIs
- **OpenAPI Specification** - Documentación técnica completa
- **Try it out** - Ejecutar comandos directamente desde la web

### **🔍 Endpoints Principales**

#### **1. Información del Servidor**
```http
GET http://localhost:8004/
```
**Respuesta:**
```json
{
  "message": "MCP Server - Sistema Multiagente Empresarial",
  "version": "1.0.0",
  "status": "operational",
  "tools_available": 14,
  "architecture": "Event Sourcing + CQRS + Graph Database"
}
```

#### **2. Estado de Salud**
```http
GET http://localhost:8004/health
```
**Respuesta:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-08T20:07:39",
  "services": {
    "redis": true,
    "database": true,
    "tools_loaded": 14
  }
}
```

#### **3. Listar Herramientas**
```http
GET http://localhost:8004/tools
```
**Respuesta:**
```json
[
  {
    "tool_id": "web_search",
    "name": "Búsqueda Web",
    "description": "Realizar búsquedas en Google y otros motores",
    "category": "search",
    "team_access": ["research", "marketing", "sales", "strategy"]
  },
  {
    "tool_id": "openai_chat",
    "name": "Chat OpenAI", 
    "description": "Generar texto con GPT",
    "category": "ai",
    "team_access": ["code_generation", "research", "marketing"]
  }
]
```

#### **4. Ejecutar Herramienta (Interfaz Web)**
```http
POST http://localhost:8004/execute
```

**Datos del formulario:**
```json
{
  "tool_id": "web_search",
  "parameters": {
    "query": "tendencias marketing 2025",
    "num_results": 10,
    "lang": "es"
  },
  "team_id": "marketing",
  "agent_type": "marketing_strategist",
  "priority": 1,
  "timeout": 30
}
```

#### **5. Analytics Dashboard**
```http
GET http://localhost:8004/analytics/overview
```
**Respuesta:**
```json
{
  "total_tools": 14,
  "total_teams": 24,
  "category_distribution": {
    "search": 3,
    "ai": 2,
    "communication": 2,
    "development": 2
  },
  "most_used_tools": [
    {"tool_id": "web_search", "uses": 150, "success_rate": 0.98}
  ]
}
```

### **🎯 Interfaz Web Interactive**

#### **Para Usar desde el Navegador:**

1. **Abrir**: http://localhost:8004/docs
2. **Click en "Authorize"** si necesitas autenticación
3. **Expandir endpoint** que quieras usar
4. **Click "Try it out"**
5. **Llenar parámetros** en el formulario
6. **Click "Execute"** para ejecutar
7. **Ver respuesta** en tiempo real

#### **Ejemplo Visual - Buscar en Web:**
1. Ir a http://localhost:8004/docs
2. Expandir `POST /execute`
3. Click "Try it out"
4. Poner en Request body:
```json
{
  "tool_id": "web_search",
  "parameters": {
    "query": "inteligencia artificial 2025",
    "num_results": 5
  },
  "team_id": "research",
  "agent_type": "ai_researcher"
}
```
5. Click "Execute"
6. Ver resultado en la respuesta

### **📊 Otras Interfaces del Sistema**

#### **Grafana Dashboard**
- **URL**: http://localhost:3000
- **Credenciales**: admin/haaspass
- **Dashboards**: 
  - System Overview
  - Team Performance  
  - API Usage Statistics
  - MCP Tools Analytics

#### **RabbitMQ Management**
- **URL**: http://localhost:15672
- **Credenciales**: haas/haaspass
- **Funciones**:
  - Ver colas de mensajes
  - Monitorear flujos de trabajo
  - Gestionar exchanges

#### **Neo4j Browser**
- **URL**: http://localhost:7474
- **Credenciales**: neo4j/haaspass
- **Consultas**: Visualizar relaciones entre equipos

### **💻 API Examples con cURL**

#### **Buscar tendencias de mercado:**
```bash
curl -X POST "http://localhost:8004/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_id": "web_search",
    "parameters": {
      "query": "tendencias marketing digital 2025",
      "num_results": 10,
      "lang": "es"
    },
    "team_id": "marketing",
    "agent_type": "marketing_strategist"
  }'
```

#### **Generar contenido con IA:**
```bash
curl -X POST "http://localhost:8004/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_id": "openai_chat",
    "parameters": {
      "model": "gpt-4",
      "message": "Crea una estrategia de contenido para LinkedIn",
      "temperature": 0.7
    },
    "team_id": "marketing",
    "agent_type": "content_creator"
  }'
```

#### **Consultar GitHub:**
```bash
curl -X POST "http://localhost:8004/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_id": "github_api",
    "parameters": {
      "endpoint": "/repos/owner/repo/issues",
      "method": "GET"
    },
    "team_id": "code_generation",
    "agent_type": "developer"
  }'
```

### **🔄 Estado de las Interfaces**
Para verificar que todas las interfaces estén funcionando:
```bash
# Script de verificación
for port in 8000 8001 8002 8003 8004 8010 8014 8015 8026 8027 8029; do
  echo "Puerto $port:"
  curl -s http://localhost:$port/health | grep -o '"status":"[^"]*"' 2>/dev/null || echo "Servicio disponible"
  echo ""
done
```

### **🎮 Interfaces por Equipo**

| Equipo | Interfaz Web | API Docs | Función Principal |
|--------|-------------|----------|-------------------|
| **Marketing** | localhost:8014 | /docs | Campañas y estrategia |
| **Sales** | localhost:8015 | /docs | CRM y ventas |
| **Security** | localhost:8026 | /docs | Auditoría de seguridad |
| **ML & AI** | localhost:8027 | /docs | Modelos y análisis |
| **Cloud Services** | localhost:8029 | /docs | Infraestructura |
| **MCP Server** | localhost:8004 | /docs | Herramientas externas |

### **✨ Características de las Interfaces**

#### **✅ OpenAPI/Swagger**
- Documentación automática
- Try-it-out en vivo
- Validación de datos
- Ejemplos de uso

#### **✅ CORS Enabled**
- Acceso desde cualquier origen
- Integración con frontend
- APIs abiertas para integración

#### **✅ Health Checks**
- Monitoreo automático
- Alertas de estado
- Métricas de rendimiento

#### **✅ Rate Limiting**
- Protección contra abuso
- Cuotas por equipo
- Límites personalizables

#### **✅ Logging**
- Registro de todas las operaciones
- Trazabilidad completa
- Debugging avanzado

**¡Las interfaces están listas para usar tan pronto como ejecutes `docker-compose up -d`!** 🚀