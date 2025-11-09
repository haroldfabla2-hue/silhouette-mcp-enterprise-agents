# SDK Python para Framework Multiagente

## Instalación

```bash
pip install multiagente-sdk
# o con poetry
poetry add multiagente-sdk
```

## Configuración Básica

```python
from multiagente_sdk import MultiAgenteSDK, MultiAgenteConfig

# Configuración básica
config = MultiAgenteConfig(
    base_url="http://localhost:8000",
    api_key="tu-api-key-secreta",
    timeout=30,
    retry_attempts=3,
    cache_enabled=True,
    cache_ttl=300
)

# Inicializar cliente
async with MultiAgenteSDK(config) as cliente:
    # Tu código aquí
    pass
```

## Uso por Categorías

### 1. **Herramientas AI y Machine Learning**

```python
import asyncio
from multiagente_sdk import MultiAgenteSDK, MultiAgenteConfig

async def ejemplo_ai():
    config = MultiAgenteConfig(base_url="http://localhost:8000")
    async with MultiAgenteSDK(config) as cliente:
        
        # Generar contenido con OpenAI
        contenido = await cliente.ai.generar_contenido(
            prompt="Escribe un artículo sobre tendencias de IA en 2025",
            model="gpt-4",
            max_tokens=2000,
            temperatura=0.7
        )
        print("Contenido generado:", contenido.data)
        
        # Analizar sentimientos
        sentimientos = await cliente.ai.analizar_sentimientos([
            "Este producto es increíble",
            "No me gusta la nueva actualización",
            "El servicio al cliente fue excelente"
        ])
        print("Análisis de sentimientos:", sentimientos.data)
        
        # Generar imágenes
        imagen = await cliente.ai.generar_imagen(
            prompt="Logo moderno para empresa de tecnología, estilo minimalista",
            size="1024x1024",
            quality="hd"
        )
        print("Imagen generada:", imagen.data)

# Ejecutar ejemplo
asyncio.run(ejemplo_ai())
```

### 2. **Herramientas de Desarrollo y DevOps**

```python
async def ejemplo_desarrollo():
    config = MultiAgenteConfig(base_url="http://localhost:8000")
    async with MultiAgenteSDK(config) as cliente:
        
        # Crear repositorio en GitHub
        repo = await cliente.desarrollo.crear_repo(
            name="nuevo-proyecto-api",
            description="API REST para gestión de usuarios",
            private=False,
            auto_init=True
        )
        print("Repositorio creado:", repo.data)
        
        # Desplegar a AWS
        deploy = await cliente.desarrollo.desplegar_aws(
            service="ecs",
            task_definition="user-service:1",
            cluster="production",
            service_name="user-service",
            desired_count=3
        )
        print("Despliegue iniciado:", deploy.data)
        
        # Análisis de código
        analisis = await cliente.desarrollo.analizar_codigo(
            repository="https://github.com/empresa/api-service",
            analysis_type="security,performance,quality",
            branch="main"
        )
        print("Análisis de código:", analisis.data)

asyncio.run(ejemplo_desarrollo())
```

### 3. **Herramientas de Marketing Digital**

```python
async def ejemplo_marketing():
    config = MultiAgenteConfig(base_url="http://localhost:8000")
    async with MultiAgenteSDK(config) as cliente:
        
        # Crear campaña de Google Ads
        campana = await cliente.marketing.crear_campana(
            nombre="Lanzamiento Producto Q1 2025",
            presupuesto=5000,
            ubicaciones=["Madrid", "Barcelona", "Valencia"],
            palabras_clave=["software empresarial", "CRM", "automatización"],
            tipo_campana="SEARCH"
        )
        print("Campaña creada:", campana.data)
        
        # Análisis de competencia
        competencia = await cliente.marketing.analizar_competencia(
            empresa="mi-empresa",
            sector="software empresarial",
            pais="España",
            metricas=["traffic", "keywords", "social_presence"]
        )
        print("Análisis competencia:", competencia.data)
        
        # Email marketing
        email = await cliente.marketing.enviar_email(
            lista="newsletter-suscriptores",
            asunto="Novedad: Nuevas funcionalidades disponibles",
            contenido="<h1>¡Hola!</h1><p>Tenemos nuevas funciones...</p>",
            programacion="2025-11-09 10:00:00"
        )
        print("Email programado:", email.data)

asyncio.run(ejemplo_marketing())
```

### 4. **Herramientas de Ventas y CRM**

```python
async def ejemplo_ventas():
    config = MultiAgenteConfig(base_url="http://localhost:8000")
    async with MultiAgenteSDK(config) as cliente:
        
        # Crear lead en Salesforce
        lead = await cliente.ventas.crear_lead(
            empresa="Tech Solutions SL",
            contacto="Juan Pérez",
            email="juan@techsolutions.com",
            telefono="+34 600 123 456",
            origen="Website",
            valor_estimado=15000
        )
        print("Lead creado:", lead.data)
        
        # Seguimiento de oportunidades
        oportunidad = await cliente.ventas.actualizar_oportunidad(
            id="OPP001",
            etapa="Propuesta",
            probabilidad=75,
            cierre_estimado="2025-12-15",
            valor=25000
        )
        print("Oportunidad actualizada:", oportunidad.data)
        
        # Análisis de pipeline
        pipeline = await cliente.ventas.analizar_pipeline(
            periodo="Q1 2025",
            equipo="ventas-norte",
            metricas=["conversion_rate", "avg_deal_size", "sales_cycle"]
        )
        print("Análisis pipeline:", pipeline.data)

asyncio.run(ejemplo_ventas())
```

### 5. **Herramientas Financieras**

```python
async def ejemplo_finanzas():
    config = MultiAgenteConfig(base_url="http://localhost:8000")
    async with MultiAgenteSDK(config) as cliente:
        
        # Cotización de acciones
        cotizacion = await cliente.finanzas.cotizacion_accion(
            symbol="AAPL",
            start_date="2025-01-01",
            end_date="2025-11-08",
            interval="1d"
        )
        print("Cotización AAPL:", cotizacion.data)
        
        # Análisis de noticias financieras
        noticias = await cliente.finanzas.noticias_accion(
            symbol="TSLA",
            limit=10,
            sort_by="published_at"
        )
        print("Noticias Tesla:", noticias.data)
        
        # Métricas de empresa
        metricas = await cliente.finanzas.metricas_empresa(
            symbol="MSFT",
            period="quarterly"
        )
        print("Métricas Microsoft:", metricas.data)

asyncio.run(ejemplo_finanzas())
```

## Métodos de Orquestación Completa

```python
from typing import Dict, Any, List
from multiagente_sdk import MultiAgenteSDK, MultiAgenteConfig

class ProductLauncher:
    def __init__(self, config: MultiAgenteConfig):
        self.config = config
        self.cliente = None
    
    async def __aenter__(self):
        self.cliente = MultiAgenteSDK(self.config)
        await self.cliente.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.cliente:
            await self.cliente.__aexit__(exc_type, exc_val, exc_tb)
    
    async def lanzar_producto_completo(self, datos_producto: Dict[str, Any]):
        """
        Proceso completo de lanzamiento de producto
        """
        try:
            # Paso 1: Análisis técnico
            analisis_tech = await self.cliente.desarrollo.analizar_viabilidad(
                stack=datos_producto.get("tecnologia", []),
                escalabilidad=datos_producto.get("usuarios_esperados", 0),
                presupuesto=datos_producto.get("presupuesto", 0)
            )
            
            # Paso 2: Investigación de mercado
            mercado = await self.cliente.marketing.investigar_mercado(
                categoria=datos_producto.get("categoria", ""),
                ubicacion=datos_producto.get("mercado", []),
                competencia=datos_producto.get("competidores", [])
            )
            
            # Paso 3: Estrategia de marketing
            estrategia = await self.cliente.marketing.crear_estrategia(
                producto=datos_producto.get("nombre", ""),
                audiencia=mercado.data.get("target_audience", ""),
                presupuesto=datos_producto.get("presupuesto_marketing", 0),
                canales=["google_ads", "social_media", "email"]
            )
            
            # Paso 4: Configuración CRM
            config_crm = await self.cliente.ventas.configurar_pipeline(
                producto=datos_producto.get("nombre", ""),
                etapas=["Prospecto", "Calificado", "Propuesta", "Negociación", "Cerrado"],
                valores=datos_producto.get("precios", {})
            )
            
            # Paso 5: Desarrollo del producto
            desarrollo = await self.cliente.desarrollo.iniciar_desarrollo(
                metodologia="agile",
                sprints=8,
                tecnologias=datos_producto.get("tecnologia", []),
                integraciones=["payment", "analytics", "crm"]
            )
            
            return {
                "analisis": analisis_tech.data,
                "mercado": mercado.data,
                "estrategia": estrategia.data,
                "crm": config_crm.data,
                "desarrollo": desarrollo.data,
                "estado": "completado"
            }
            
        except Exception as error:
            print(f"Error en lanzamiento: {error}")
            raise error

# Uso del Product Launcher
async def main():
    config = MultiAgenteConfig(base_url="http://localhost:8000")
    
    async with ProductLauncher(config) as launcher:
        resultado = await launcher.lanzar_producto_completo({
            "nombre": "App de Gestión Empresarial",
            "categoria": "B2B SaaS",
            "tecnologia": ["React", "Node.js", "PostgreSQL", "AWS"],
            "usuarios_esperados": 10000,
            "presupuesto": 100000,
            "presupuesto_marketing": 50000,
            "mercado": ["España", "México", "Argentina"],
            "competidores": ["Salesforce", "HubSpot", "Monday.com"],
            "precios": {
                "básico": 29,
                "profesional": 59,
                "empresarial": 99
            }
        })
        
        print("Producto lanzado:", resultado)

asyncio.run(main())
```

## Herramientas MCP Específicas

```python
class MCPTools:
    def __init__(self, cliente: MultiAgenteSDK):
        self.cliente = cliente
    
    async def buscar_google(self, query: str, num_results: int = 10):
        """Buscar en Google"""
        return await self.cliente.mcp('google_search', {
            'query': query,
            'num_results': num_results
        })
    
    async def buscar_lugares(self, ubicacion: str, tipo: str, radio: int = 5000):
        """Buscar lugares en Google Maps"""
        return await self.cliente.mcp('google_maps_search', {
            'query': f"{tipo} near {ubicacion}",
            'location': ubicacion,
            'radius': radio
        })
    
    async def crear_repo_github(self, nombre: str, descripcion: str):
        """Crear repositorio en GitHub"""
        return await self.cliente.mcp('github_repository', {
            'name': nombre,
            'description': descripcion,
            'private': False,
            'auto_init': True
        })
    
    async def subir_archivo_s3(self, bucket: str, key: str, archivo: bytes):
        """Subir archivo a AWS S3"""
        import base64
        return await self.cliente.mcp('aws_s3_upload', {
            'bucket': bucket,
            'key': key,
            'file': base64.b64encode(archivo).decode('utf-8')
        })
    
    async def cotizacion_stocks(self, symbol: str, start_date: str, end_date: str):
        """Obtener cotización de acciones"""
        return await self.cliente.mcp('stock_price', {
            'symbol': symbol,
            'start_date': start_date,
            'end_date': end_date,
            'interval': '1d'
        })

# Uso
async def ejemplo_mcp():
    config = MultiAgenteConfig(base_url="http://localhost:8000")
    async with MultiAgenteSDK(config) as cliente:
        mcp = MCPTools(cliente)
        
        resultados = await mcp.buscar_google("mejores prácticas desarrollo web 2025")
        lugares = await mcp.buscar_lugares("Madrid", "co-working", 10000)
        repo = await mcp.crear_repo_github("mi-proyecto", "Descripción del proyecto")

asyncio.run(ejemplo_mcp())
```

## Manejo de Errores y Reintentos

```python
import asyncio
from multiagente_sdk.exceptions import (
    MultiAgenteError, 
    RateLimitError, 
    AuthenticationError,
    NetworkError
)

async def operacion_robusta():
    config = MultiAgenteConfig(
        base_url="http://localhost:8000",
        retry_attempts=3,
        retry_delay=1.0,
        retry_backoff_factor=2.0
    )
    
    async with MultiAgenteSDK(config) as cliente:
        for attempt in range(3):
            try:
                resultado = await cliente.ai.generar_contenido(
                    prompt="Escribe sobre el futuro de la IA"
                )
                return resultado
                
            except RateLimitError as error:
                if attempt < 2:  # No es el último intento
                    wait_time = config.retry_delay * (config.retry_backoff_factor ** attempt)
                    print(f"Rate limit alcanzado, reintentando en {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise error
                    
            except (NetworkError, MultiAgenteError) as error:
                if attempt < 2:
                    wait_time = config.retry_delay * (config.retry_backoff_factor ** attempt)
                    print(f"Error de red, reintentando en {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise error
            
            except AuthenticationError as error:
                raise error  # No reintentar errores de autenticación

# Uso con manejo de errores específico
try:
    resultado = await operacion_robusta()
    print("Operación exitosa:", resultado.data)
except AuthenticationError:
    print("Error de autenticación, verifica tu API key")
except RateLimitError:
    print("Límite de rate alcanzado, intenta más tarde")
except MultiAgenteError as error:
    print(f"Error del servidor: {error}")
```

## Cache y Optimización

```python
from multiagente_sdk.cache import RedisCache, MemoryCache

# Configuración con cache Redis
config = MultiAgenteConfig(
    base_url="http://localhost:8000",
    cache_enabled=True,
    cache_backend="redis",  # o "memory"
    cache_config={
        "host": "localhost",
        "port": 6379,
        "db": 0,
        "password": "haaspass"
    },
    cache_ttl=300  # 5 minutos
)

# Cache manual
async def ejemplo_cache():
    config = MultiAgenteConfig(base_url="http://localhost:8000", cache_enabled=True)
    async with MultiAgenteSDK(config) as cliente:
        
        # Las llamadas consecutivas se cachean automáticamente
        resultado1 = await cliente.marketing.analizar_competencia({
            "empresa": "mi-empresa",
            "sector": "software"
        })
        
        resultado2 = await cliente.marketing.analizar_competencia({
            "empresa": "mi-empresa",
            "sector": "software"
        })  # Usará cache
        
        # Cache manual
        await cliente.cache.set("mi-clave", {"data": "valor"}, ttl=600)
        valor = await cliente.cache.get("mi-clave")
        
        print("Valor del cache:", valor)

asyncio.run(ejemplo_cache())
```

## Webhooks y Eventos

```python
from multiagente_sdk.webhooks import WebhookHandler

async def ejemplo_webhooks():
    config = MultiAgenteConfig(base_url="http://localhost:8000")
    async with MultiAgenteSDK(config) as cliente:
        
        # Configurar callback para eventos
        def on_mcp_execution_completed(data):
            print(f"Ejecución MCP completada: {data}")
        
        def on_team_processing(data):
            print(f"Equipo procesando: {data['team']} - {data['status']}")
        
        # Registrar callbacks
        cliente.webhooks.on("mcp_execution_completed", on_mcp_execution_completed)
        cliente.webhooks.on("team_processing", on_team_processing)
        
        # Escuchar todos los eventos
        cliente.webhooks.on("*", lambda event, data: print(f"Evento {event}: {data}"))

asyncio.run(ejemplo_webhooks())
```

## Testing y Mocking

```python
from multiagente_sdk.testing import MockSDK

async def test_con_mock():
    # En modo mock, todas las respuestas son simuladas
    config = MultiAgenteConfig(
        base_url="http://localhost:8000",
        mock_mode=True,
        mock_delay=1.0  # Simular latencia
    )
    
    async with MultiAgenteSDK(config) as cliente:
        resultado = await cliente.ai.generar_contenido(
            prompt="Test content"
        )
        print("Resultado simulado:", resultado.data)

asyncio.run(test_con_mock())

# O usar MockSDK directamente
async def test_directo():
    async with MockSDK() as cliente:
        resultado = await cliente.ai.generar_contenido(
            prompt="Test content"
        )
        assert resultado.data["content"] == "Contenido simulado"
        print("Test passed!")

asyncio.run(test_directo())
```

## Integración con Frameworks Web

### FastAPI

```python
from fastapi import FastAPI, HTTPException
from multiagente_sdk import MultiAgenteSDK, MultiAgenteConfig
import asyncio

app = FastAPI()

config = MultiAgenteConfig(base_url="http://localhost:8000")
cliente = MultiAgenteSDK(config)

@app.post("/generar-contenido")
async def generar_contenido(request: dict):
    try:
        async with cliente:
            resultado = await cliente.ai.generar_contenido(**request)
            return {"success": True, "data": resultado.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/lanzar-producto")
async def lanzar_producto(datos: dict):
    try:
        async with cliente:
            # Usar el Product Launcher
            from multiagente_sdk import ProductLauncher
            async with ProductLauncher(config) as launcher:
                resultado = await launcher.lanzar_producto_completo(datos)
                return {"success": True, "data": resultado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Django

```python
# settings.py
MULTIAGENTE_CONFIG = {
    'base_url': 'http://localhost:8000',
    'api_key': 'tu-api-key',
    'cache_enabled': True
}

# views.py
import asyncio
from django.http import JsonResponse
from multiagente_sdk import MultiAgenteSDK, MultiAgenteConfig

async def generar_contenido_view(request):
    if request.method == 'POST':
        data = request.POST.dict()
        
        config = MultiAgenteConfig(**settings.MULTIAGENTE_CONFIG)
        async with MultiAgenteSDK(config) as cliente:
            try:
                resultado = await cliente.ai.generar_contenido(**data)
                return JsonResponse({
                    'success': True,
                    'data': resultado.data
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                })
```

Este SDK de Python proporciona una integración completa y robusta con el Framework Multiagente! 🚀