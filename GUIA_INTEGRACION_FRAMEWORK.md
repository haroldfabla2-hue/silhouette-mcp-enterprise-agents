# 🚀 Guía de Integración - Framework Multiagente Empresarial

## 📋 Resumen del Sistema

Tu sistema multiagente empresarial está compuesto por:

- **25 Servicios Docker**: 24 equipos especializados + 1 servidor MCP
- **14 Herramientas del Mundo Real**: APIs integradas (OpenAI, GitHub, AWS, etc.)
- **Múltiples Interfaces**: REST APIs, WebSockets, Swagger, dashboards
- **Arquitectura Robusta**: Event Sourcing + CQRS + Graph Database

## 🔧 Formas de Integración

### 1. **Como Framework Completo (Recomendado)**
Tus aplicaciones pueden usar el sistema completo como un framework empresarial.

### 2. **Como Servicios Independientes**
Usa solo los servicios que necesites.

### 3. **Como Servidor MCP**
Accede a las 14 herramientas del mundo real.

### 4. **Como Plataforma de Agentes**
Orquestra agentes especializados para tareas específicas.

## 🌐 Interfaces Disponibles

### APIs REST Principales
```
http://localhost:8000        - API Gateway (orquestador principal)
http://localhost:8001        - Desarrollo
http://localhost:8002        - Marketing
http://localhost:8003        - Ventas
http://localhost:8004        - MCP Server (14 herramientas)
http://localhost:8005        - Finanzas
...
```

### Documentación Interactiva
```
http://localhost:8004/docs    - Swagger UI del MCP Server
http://localhost:8004/openapi.json - Especificación OpenAPI
```

### Dashboards de Monitoreo
```
http://localhost:3000         - Grafana (métricas)
http://localhost:9090         - Prometheus (métricas)
http://localhost:15672        - RabbitMQ (colas)
http://localhost:7474         - Neo4j (grafos)
```

## 💻 Ejemplos de Integración por Tipo de App

### **1. Aplicación Web (React/Vue/Angular)**

```javascript
// Ejemplo con fetch API
class MultiAgenteClient {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
    }
    
    // Usar herramienta AI (OpenAI)
    async generarContenido(tema, tipo = 'blog') {
        const response = await fetch(`${this.baseURL}/mcp/tools/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                tool: 'openai_chat',
                parameters: {
                    prompt: `Genera contenido sobre ${tema} tipo ${tipo}`,
                    model: 'gpt-4',
                    max_tokens: 1000
                }
            })
        });
        return await response.json();
    }
    
    // Usar herramienta de desarrollo
    async crearRepoGitHub(nombre, descripcion) {
        const response = await fetch(`${this.baseURL}/mcp/tools/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                tool: 'github_repository',
                parameters: {
                    name: nombre,
                    description: descripcion,
                    private: false
                }
            })
        });
        return await response.json();
    }
    
    // Consultar datos financieros
    async obtenerCotizacion(symbol) {
        const response = await fetch(`${this.baseURL}/mcp/tools/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                tool: 'stock_price',
                parameters: {
                    symbol: symbol,
                    start_date: '2025-01-01',
                    end_date: '2025-11-08'
                }
            })
        });
        return await response.json();
    }
}

// Uso en tu aplicación
const cliente = new MultiAgenteClient();

// Generar contenido de blog
cliente.generarContenido('Inteligencia Artificial', 'blog')
    .then(result => console.log('Contenido generado:', result));

// Crear repositorio en GitHub
cliente.crearRepoGitHub('mi-nuevo-proyecto', 'Proyecto creado via API')
    .then(result => console.log('Repositorio creado:', result));
```

### **2. Aplicación Mobile (React Native/Flutter)**

```dart
// Ejemplo Flutter/Dart
class MultiAgenteService {
    static const String baseURL = 'http://localhost:8000';
    
    // Buscar información en Google
    static Future<Map<String, dynamic>> buscarGoogle(String query) async {
        final response = await http.post(
            Uri.parse('$baseURL/mcp/tools/execute'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
                'tool': 'google_search',
                'parameters': {
                    'query': query,
                    'num_results': 5
                }
            })
        );
        return jsonDecode(response.body);
    }
    
    // Enviar email
    static Future<Map<String, dynamic>> enviarEmail({
        required String to,
        required String subject,
        required String body
    }) async {
        final response = await http.post(
            Uri.parse('$baseURL/mcp/tools/execute'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
                'tool': 'send_email',
                'parameters': {
                    'to': to,
                    'subject': subject,
                    'body': body
                }
            })
        );
        return jsonDecode(response.body);
    }
}

// Uso en tu app Flutter
Future<void> miFuncion() async {
    // Buscar información
    var resultados = await MultiAgenteService.buscarGoogle('machine learning');
    print('Resultados: $resultados');
    
    // Enviar notificación por email
    await MultiAgenteService.enviarEmail(
        to: 'usuario@empresa.com',
        subject: 'Nueva actualización',
        body: 'Tu aplicación ha sido actualizada'
    );
}
```

### **3. Aplicación Python/Backend**

```python
import aiohttp
import asyncio
from typing import Dict, Any

class MultiAgenteClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    # Herramienta de análisis de datos
    async def analizar_ventas(self, datos: list) -> Dict[str, Any]:
        async with self.session.post(
            f"{self.base_url}/mcp/tools/execute",
            json={
                "tool": "data_analysis",
                "parameters": {
                    "data": datos,
                    "analysis_type": "sales_trend"
                }
            }
        ) as response:
            return await response.json()
    
    # Herramienta de mapas
    async def buscar_ubicaciones(self, query: str) -> Dict[str, Any]:
        async with self.session.post(
            f"{self.base_url}/mcp/tools/execute",
            json={
                "tool": "google_maps_search",
                "parameters": {
                    "query": query,
                    "location": "Madrid, España",
                    "radius": 10000
                }
            }
        ) as response:
            return await response.json()
    
    # Integración Salesforce
    async def sincronizar_salesforce(self, datos: Dict) -> Dict[str, Any]:
        async with self.session.post(
            f"{self.base_url}/mcp/tools/execute",
            json={
                "tool": "salesforce_api",
                "parameters": {
                    "action": "upsert_lead",
                    "data": datos
                }
            }
        ) as response:
            return await response.json()

# Uso en aplicación Python
async def main():
    async with MultiAgenteClient() as cliente:
        # Análisis de ventas
        ventas_data = [
            {"fecha": "2025-01", "ventas": 10000, "region": "Madrid"},
            {"fecha": "2025-02", "ventas": 15000, "region": "Barcelona"}
        ]
        analisis = await cliente.analizar_ventas(ventas_data)
        print("Análisis de ventas:", analisis)
        
        # Buscar ubicaciones
        ubicaciones = await cliente.buscar_ubicaciones("cafetería Madrid centro")
        print("Ubicaciones encontradas:", ubicaciones)

# Ejecutar
asyncio.run(main())
```

### **4. Aplicación Node.js/Express**

```javascript
const express = require('express');
const axios = require('axios');
const app = express();

class MultiAgenteIntegration {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
    }
    
    // Integración completa con equipos especializados
    async coordinarMarketingYCiencias() {
        try {
            // Paso 1: Usar equipo de Marketing para generar estrategia
            const estrategia = await axios.post(`${this.baseURL}/marketing/generate_strategy`, {
                product: 'nuevo_servicio_cloud',
                target_audience: 'PYMES',
                budget: 50000
            });
            
            // Paso 2: Usar equipo de Ciencias para análisis técnico
            const analisis = await axios.post(`${this.baseURL}/ciencias/technical_analysis`, {
                technology_stack: ['AWS', 'Docker', 'Kubernetes'],
                scalability_requirements: '10000_users',
                performance_targets: '99.9%_uptime'
            });
            
            // Paso 3: Usar MCP para validación de datos de mercado
            const validacion = await axios.post(`${this.baseURL}/mcp/tools/execute`, {
                tool: 'google_search',
                parameters: {
                    query: 'cloud services PYMES trends 2025',
                    num_results: 10
                }
            });
            
            return {
                estrategia_marketing: estrategia.data,
                analisis_tecnico: analisis.data,
                validacion_mercado: validacion.data
            };
        } catch (error) {
            throw new Error(`Error en coordinación: ${error.message}`);
        }
    }
}

const integration = new MultiAgenteIntegration();

// Endpoint de tu aplicación que usa el framework
app.post('/lanzar-producto', async (req, res) => {
    try {
        const resultado = await integration.coordinarMarketingYCiencias();
        res.json({
            success: true,
            data: resultado,
            message: 'Producto analizado y estrategia generada'
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

app.listen(3000, () => {
    console.log('Tu aplicación corriendo en puerto 3000');
    console.log('Integrada con Framework Multiagente');
});
```

## 🛠️ SDKs y Librerías Recomendadas

### **JavaScript/TypeScript SDK**

```typescript
// multiagente-sdk.ts
export interface MultiAgenteConfig {
    baseURL: string;
    apiKey?: string;
    timeout: number;
}

export class MultiAgenteSDK {
    private config: MultiAgenteConfig;
    
    constructor(config: MultiAgenteConfig) {
        this.config = config;
    }
    
    // Métodos para cada equipo
    async marketing(action: string, data: any) {
        return this.callService('marketing', action, data);
    }
    
    async desarrollo(action: string, data: any) {
        return this.callService('desarrollo', action, data);
    }
    
    async ventas(action: string, data: any) {
        return this.callService('ventas', action, data);
    }
    
    // MCP Tools
    async mcp(tool: string, parameters: any) {
        return this.callService('mcp', 'execute', { tool, parameters });
    }
    
    private async callService(service: string, action: string, data: any) {
        const response = await fetch(`${this.config.baseURL}/${service}/${action}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...(this.config.apiKey && { 'Authorization': `Bearer ${this.config.apiKey}` })
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`Error en ${service}: ${response.statusText}`);
        }
        
        return await response.json();
    }
}
```

### **Python SDK**

```python
# multiagente_sdk.py
import aiohttp
import asyncio
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class MultiAgenteConfig:
    base_url: str
    api_key: Optional[str] = None
    timeout: int = 30

class MultiAgenteSDK:
    def __init__(self, config: MultiAgenteConfig):
        self.config = config
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    # Equipos especializados
    async def marketing(self, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._call_service('marketing', action, data)
    
    async def desarrollo(self, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._call_service('desarrollo', action, data)
    
    async def ventas(self, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self._call_service('ventas', action, data)
    
    # Herramientas MCP
    async def mcp(self, tool: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        return await self._call_service('mcp', 'execute', {
            'tool': tool,
            'parameters': parameters
        })
    
    async def _call_service(self, service: str, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        headers = {'Content-Type': 'application/json'}
        if self.config.api_key:
            headers['Authorization'] = f'Bearer {self.config.api_key}'
        
        async with self.session.post(
            f"{self.config.base_url}/{service}/{action}",
            headers=headers,
            json=data
        ) as response:
            response.raise_for_status()
            return await response.json()
```

## 🚀 Casos de Uso Empresariales

### **1. E-commerce Platform**
- **Marketing Team**: Genera campañas personalizadas
- **MCP Tools**: Analiza tendencias de mercado con Google
- **Sales Team**: Gestiona leads y oportunidades
- **Customer Service**: Automatiza respuestas con AI

### **2. SaaS Startup**
- **Development Team**: Automatiza CI/CD y deployment
- **MCP Tools**: Integra GitHub, AWS para infraestructura
- **Finance Team**: Monitorea métricas financieras
- **Marketing Team**: Analiza competencia y usuarios

### **3. Agencia Digital**
- **MCP Tools**: Usa todas las APIs (Google Ads, Facebook, email)
- **Creative Team**: Genera contenido con AI
- **Analytics Team**: Analiza datos con herramientas de BI
- **Client Management**: Automatiza reportes y comunicaciones

## 🔒 Autenticación y Seguridad

```javascript
// Configuración con API Key
const client = new MultiAgenteSDK({
    baseURL: 'http://localhost:8000',
    apiKey: 'tu-api-key-segura',
    timeout: 30000
});

// Uso seguro
client.mcp('openai_chat', {
    prompt: 'Analiza esta propuesta de negocio',
    model: 'gpt-4'
});
```

## 📊 Monitoreo y Métricas

```javascript
// Endpoint de health check para todos los servicios
async function checkSystemHealth() {
    const services = [
        'http://localhost:8000/health',      // API Gateway
        'http://localhost:8001/health',      // Desarrollo
        'http://localhost:8002/health',      // Marketing
        'http://localhost:8003/health',      // Ventas
        'http://localhost:8004/health',      // MCP Server
        'http://localhost:8005/health',      // Finanzas
        // ... todos los 25 servicios
    ];
    
    const healthChecks = await Promise.allSettled(
        services.map(url => fetch(url).then(r => r.json()))
    );
    
    return healthChecks.map((result, index) => ({
        service: services[index],
        status: result.status === 'fulfilled' ? 'healthy' : 'unhealthy',
        data: result.status === 'fulfilled' ? result.value : null
    }));
}
```

## 🎯 Próximos Pasos

1. **Despliega el sistema** con `docker-compose up -d`
2. **Prueba los endpoints** en http://localhost:8004/docs
3. **Integra** con tu aplicación usando los ejemplos
4. **Monitorea** con los dashboards en http://localhost:3000
5. **Escala** añadiendo más equipos especializados según necesidades

## 💡 Tips de Integración

- **Usa el API Gateway (puerto 8000)** para orquestación compleja
- **Usa servicios específicos** para tareas especializadas
- **Usa MCP Server (puerto 8004)** para herramientas del mundo real
- **Monitorea siempre** con los dashboards de Grafana
- **Implementa retry logic** para mayor robustez
- **Cachea respuestas** frecuentes con Redis

¡Tu sistema multiagente está listo para ser usado como framework completo por cualquier aplicación! 🚀