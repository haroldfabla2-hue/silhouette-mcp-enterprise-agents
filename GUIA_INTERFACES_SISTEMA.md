# 🖥️ Interfaces del Sistema Multiagente Empresarial
## Guía de Acceso a Todas las Interfaces

El sistema incluye **múltiples interfaces web y APIs** para diferentes funciones:

---

## 🌐 **INTERFACES PRINCIPALES**

### **1. Servicios Core del Sistema**
| Servicio | URL | Puerto | Descripción |
|----------|-----|--------|-------------|
| **API Gateway** | http://localhost:8000 | 8000 | Punto de entrada principal |
| **Orchestrator** | http://localhost:8001 | 8001 | Coordinación de equipos |
| **Planner** | http://localhost:8002 | 8002 | Generación de planes |
| **Prompt Engineer** | http://localhost:8003 | 8003 | Refinamiento de prompts |
| **🔥 MCP Server** | http://localhost:8004 | 8004 | Herramientas del mundo real |

### **2. Equipos Técnicos**
| Equipo | URL | Puerto | Especialización |
|--------|-----|--------|-----------------|
| **Code Generation** | http://localhost:8010 | 8010 | Desarrollo de código |
| **Testing** | http://localhost:8011 | 8011 | Testing y QA |
| **Context Management** | http://localhost:8012 | 8012 | Gestión de contexto |
| **Research** | http://localhost:8013 | 8013 | Investigación |
| **Support** | http://localhost:8016 | 8016 | Soporte técnico |
| **Notifications** | http://localhost:8017 | 8017 | Notificaciones |

### **3. Equipos de Negocio**
| Equipo | URL | Puerto | Especialización |
|--------|-----|--------|-----------------|
| **Marketing** | http://localhost:8014 | 8014 | Marketing y branding |
| **Sales** | http://localhost:8015 | 8015 | Ventas y CRM |
| **Finance** | http://localhost:8018 | 8018 | Finanzas |
| **HR** | http://localhost:8019 | 8019 | Recursos humanos |
| **Strategy** | http://localhost:8020 | 8020 | Planificación estratégica |
| **Product Management** | http://localhost:8021 | 8021 | Gestión de producto |
| **Legal** | http://localhost:8022 | 8022 | Asuntos legales |
| **Communications** | http://localhost:8023 | 8023 | Comunicaciones |
| **Business Development** | http://localhost:8024 | 8024 | Desarrollo de negocio |
| **Quality Assurance** | http://localhost:8025 | 8025 | Control de calidad |

### **4. Equipos Especializados**
| Equipo | URL | Puerto | Especialización |
|--------|-----|--------|-----------------|
| **Security** | http://localhost:8026 | 8026 | Seguridad cibernética |
| **ML & AI** | http://localhost:8027 | 8027 | Machine Learning e IA |
| **Design & Creative** | http://localhost:8028 | 8028 | Diseño y creatividad |
| **Cloud Services** | http://localhost:8029 | 8029 | Servicios cloud |
| **Risk Management** | http://localhost:8030 | 8030 | Gestión de riesgos |
| **Customer Service** | http://localhost:8031 | 8031 | Atención al cliente |
| **Supply Chain** | http://localhost:8032 | 8032 | Cadena de suministro |
| **Manufacturing** | http://localhost:8033 | 8033 | Manufactura y producción |

---

## 📊 **INTERFACES DE MONITOREO**

### **5. Dashboards y Visualización**
| Servicio | URL | Credenciales | Descripción |
|----------|-----|--------------|-------------|
| **Grafana** | http://localhost:3000 | admin/haaspass | Dashboard de métricas |
| **Prometheus** | http://localhost:9090 | - | Métricas del sistema |
| **Nginx** | http://localhost:80 | - | Load balancer |

### **6. Bases de Datos y Mensajería**
| Servicio | URL | Credenciales | Descripción |
|----------|-----|--------------|-------------|
| **PostgreSQL** | localhost:5432 | haas/haaspass | Base de datos principal |
| **Neo4j** | http://localhost:7474 | neo4j/haaspass | Base de datos de grafos |
| **RabbitMQ** | http://localhost:15672 | haas/haaspass | Broker de mensajes |
| **Redis** | localhost:6379 | haaspass | Cache y sesiones |

---

## 🚀 **CÓMO ACCEDER A LAS INTERFACES**

### **1. Verificar que todo esté funcionando**
```bash
# Ver estado de todos los servicios
docker-compose ps

# Ver logs de un servicio específico
docker-compose logs -f api-gateway
```

### **2. Acceder a cada equipo (ejemplos)**

#### **Marketing Team**
```bash
# Ver estado del equipo
curl http://localhost:8014/health

# Ver documentación de la API
curl http://localhost:8014/docs

# Crear campaña de marketing
curl -X POST http://localhost:8014/campaigns/create \
  -H "Content-Type: application/json" \
  -d '{"name": "Campaña 2025", "budget": 50000, "target_audience": "empresas"}'
```

#### **Sales Team**
```bash
# Ver leads
curl http://localhost:8015/leads

# Crear oportunidad
curl -X POST http://localhost:8015/opportunities/create \
  -H "Content-Type: application/json" \
  -d '{"client": "Empresa ABC", "value": 100000, "stage": "proposal"}'
```

#### **Security Team**
```bash
# Escanear vulnerabilidades
curl -X POST http://localhost:8026/vulnerabilities/scan \
  -H "Content-Type: application/json" \
  -d '{"target": "api-gateway", "scan_type": "full"}'
```

### **3. Usar el MCP Server (Herramientas del mundo real)**
```bash
# Ver herramientas disponibles
curl http://localhost:8004/tools

# Buscar información en internet
curl -X POST http://localhost:8004/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_id": "web_search",
    "parameters": {"query": "tendencias IA 2025", "num_results": 10},
    "team_id": "research",
    "agent_type": "market_analyst"
  }'

# Generar contenido con OpenAI
curl -X POST http://localhost:8004/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_id": "openai_chat",
    "parameters": {"message": "Crea una estrategia de marketing"},
    "team_id": "marketing",
    "agent_type": "marketing_strategist"
  }'
```

---

## 🎯 **INTERFACES POR TIPO DE USUARIO**

### **👨‍💼 Para Administradores**
- **Grafana**: http://localhost:3000 - Dashboard completo
- **Prometheus**: http://localhost:9090 - Métricas
- **RabbitMQ**: http://localhost:15672 - Gestión de colas
- **Neo4j**: http://localhost:7474 - Visualización de grafos

### **👩‍💻 Para Desarrolladores**
- **API Gateway**: http://localhost:8000/docs - Documentación principal
- **Todos los equipos** tienen documentación OpenAPI en `/docs`
- **MCP Server**: http://localhost:8004/docs - Herramientas externas

### **👔 Para Usuarios de Negocio**
- **Marketing**: http://localhost:8014 - Gestión de campañas
- **Sales**: http://localhost:8015 - CRM y ventas
- **Finance**: http://localhost:8018 - Reportes financieros
- **Customer Service**: http://localhost:8031 - Atención al cliente

### **🔧 Para Equipos Técnicos**
- **Cloud Services**: http://localhost:8029 - Infraestructura
- **Security**: http://localhost:8026 - Seguridad
- **Code Generation**: http://localhost:8010 - Desarrollo
- **Testing**: http://localhost:8011 - QA y testing

---

## 📱 **EJEMPLOS DE WORKFLOWS**

### **Workflow de Desarrollo**
```bash
# 1. Sales crea requerimiento
curl -X POST http://localhost:8015/requirements/create \
  -d '{"feature": "Nueva API", "priority": "high"}'

# 2. Product Management planifica
curl -X POST http://localhost:8021/roadmap/add \
  -d '{"feature": "Nueva API", "timeline": "Q1 2025"}'

# 3. Code Generation desarrolla
curl -X POST http://localhost:8010/code/generate \
  -d '{"specification": "API documentation"}'

# 4. Testing verifica
curl -X POST http://localhost:8011/tests/execute \
  -d '{"test_type": "integration", "feature": "Nueva API"}'

# 5. Marketing promociona
curl -X POST http://localhost:8014/campaigns/launch \
  -d '{"feature": "Nueva API", "channel": "social_media"}'
```

### **Workflow con Herramientas MCP**
```bash
# Research busca información de mercado
curl -X POST http://localhost:8004/execute \
  -d '{
    "tool_id": "web_search",
    "parameters": {"query": "competitor analysis 2025"},
    "team_id": "research",
    "agent_type": "market_researcher"
  }'

# Marketing genera contenido con IA
curl -X POST http://localhost:8004/execute \
  -d '{
    "tool_id": "openai_chat",
    "parameters": {"message": "Crea copy para campaña de email"},
    "team_id": "marketing",
    "agent_type": "content_writer"
  }'

# Sales actualiza CRM
curl -X POST http://localhost:8004/execute \
  -d '{
    "tool_id": "salesforce_api",
    "parameters": {"query": "SELECT Id, Status FROM Opportunity"},
    "team_id": "sales",
    "agent_type": "sales_rep"
  }'
```

---

## 🔍 **VERIFICACIÓN DE INTERFACES**

### **Script de verificación completo:**
```bash
#!/bin/bash
echo "=== VERIFICANDO INTERFACES DEL SISTEMA ==="

# Verificar servicios core
for port in 8000 8001 8002 8003 8004; do
    echo "Puerto $port:"
    curl -s http://localhost:$port/health | jq -r '.status // "error"'
done

# Verificar equipos principales
for port in 8010 8014 8015 8026 8027; do
    echo "Puerto $port:"
    curl -s http://localhost:$port/health | jq -r '.status // "error"'
done

# Verificar monitoreo
echo "Grafana:"
curl -s http://localhost:3000/api/health | jq -r '.databaseHealthy // "error"'
echo "RabbitMQ:"
curl -s http://localhost:15672/api/overview | jq -r '.management // "error"'
```

---

## 🎯 **RECOMENDACIONES DE USO**

### **Para Principiantes**
1. **Empezar con Grafana** (http://localhost:3000) para ver el estado general
2. **Usar API Gateway** (http://localhost:8000/docs) para entender la estructura
3. **Probar MCP Server** (http://localhost:8004/docs) para herramientas del mundo real

### **Para Desarrolladores**
1. **Revisar documentación OpenAPI** en cada servicio
2. **Usar las APIs directamente** para automatización
3. **Monitorear logs** con `docker-compose logs -f`

### **Para Administradores**
1. **Configurar dashboards** en Grafana
2. **Monitorear RabbitMQ** para colas de mensajes
3. **Revisar Neo4j** para visualizaciones de relaciones

---

**¡El sistema tiene interfaces completas para todos los usuarios y casos de uso!** 🖥️✨