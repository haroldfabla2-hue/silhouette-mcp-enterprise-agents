# SDK JavaScript/TypeScript para Framework Multiagente

## Instalación

```bash
npm install multiagente-sdk
# o
yarn add multiagente-sdk
```

## Configuración Básica

```typescript
import { MultiAgenteSDK } from 'multiagente-sdk';

// Configuración con todas las opciones
const cliente = new MultiAgenteSDK({
    baseURL: 'http://localhost:8000',
    apiKey: 'tu-api-key-secreta',
    timeout: 30000,
    retryAttempts: 3,
    cache: {
        enabled: true,
        ttl: 300000 // 5 minutos
    }
});
```

## Uso por Categorías

### 1. **Herramientas AI y Machine Learning**

```typescript
// Generar contenido con OpenAI
const contenido = await cliente.ai.generarContenido({
    prompt: "Escribe un artículo sobre tendencias de IA en 2025",
    model: "gpt-4",
    maxTokens: 2000,
    temperatura: 0.7
});

console.log('Contenido generado:', contenido.data);

// Analizar sentimientos
const sentimiento = await cliente.ai.analizarSentimientos([
    "Este producto es increíble",
    "No me gusta la nueva actualización",
    "El servicio al cliente fue excelente"
]);

console.log('Análisis de sentimientos:', sentimiento.data);

// Generar imágenes
const imagen = await cliente.ai.generarImagen({
    prompt: "Logo moderno para empresa de tecnología, estilo minimalista",
    size: "1024x1024",
    quality: "hd"
});

console.log('Imagen generada:', imagen.data);
```

### 2. **Herramientas de Desarrollo y DevOps**

```typescript
// Crear repositorio en GitHub
const repo = await cliente.desarrollo.crearRepo({
    name: "nuevo-proyecto-api",
    description: "API REST para gestión de usuarios",
    private: false,
    auto_init: true
});

console.log('Repositorio creado:', repo.data);

// Desplegar a AWS
const deploy = await cliente.desarrollo.desplegarAWS({
    service: "ecs",
    taskDefinition: "user-service:1",
    cluster: "production",
    serviceName: "user-service",
    desiredCount: 3
});

console.log('Despliegue iniciado:', deploy.data);

// Análisis de código
const analisis = await cliente.desarrollo.analizarCodigo({
    repository: "https://github.com/empresa/api-service",
    analysisType: "security,performance,quality",
    branch: "main"
});

console.log('Análisis de código:', analisis.data);
```

### 3. **Herramientas de Marketing Digital**

```typescript
// Campaña de Google Ads
const campana = await cliente.marketing.crearCampana({
    nombre: "Lanzamiento Producto Q1 2025",
    presupuesto: 5000,
    ubicaciones: ["Madrid", "Barcelona", "Valencia"],
    palabrasClave: ["software empresarial", "CRM", "automatización"],
    tipoCampana: "SEARCH"
});

console.log('Campaña creada:', campana.data);

// Análisis de competencia
const competencia = await cliente.marketing.analizarCompetencia({
    empresa: "mi-empresa",
    sector: "software empresarial",
    pais: "España",
    metricas: ["traffic", "keywords", "social_presence"]
});

console.log('Análisis competencia:', competencia.data);

// Email marketing
const email = await cliente.marketing.enviarEmail({
    lista: "newsletter-suscriptores",
    asunto: "Novedad: Nuevas funcionalidades disponibles",
    contenido: "<h1>¡Hola!</h1><p>Tenemos nuevas funciones...</p>",
    programacion: "2025-11-09 10:00:00"
});

console.log('Email programado:', email.data);
```

### 4. **Herramientas de Ventas y CRM**

```typescript
// Crear lead en Salesforce
const lead = await cliente.ventas.crearLead({
    empresa: "Tech Solutions SL",
    contacto: "Juan Pérez",
    email: "juan@techsolutions.com",
    telefono: "+34 600 123 456",
    origen: "Website",
    valorEstimado: 15000
});

console.log('Lead creado:', lead.data);

// Seguimiento de oportunidades
const oportunidad = await cliente.ventas.actualizarOportunidad({
    id: "OPP001",
    etapa: "Propuesta",
    probabilidad: 75,
    cierreEstimado: "2025-12-15",
    valor: 25000
});

console.log('Oportunidad actualizada:', oportunidad.data);

// Análisis de pipeline
const pipeline = await cliente.ventas.analizarPipeline({
    periodo: "Q1 2025",
    equipo: "ventas-norte",
    metricas: ["conversion_rate", "avg_deal_size", "sales_cycle"]
});

console.log('Análisis pipeline:', pipeline.data);
```

### 5. **Herramientas Financieras**

```typescript
// Cotización de acciones
const cotizacion = await cliente.finanzas.cotizacionAccion({
    symbol: "AAPL",
    startDate: "2025-01-01",
    endDate: "2025-11-08",
    interval: "1d"
});

console.log('Cotización AAPL:', cotizacion.data);

// Análisis de noticias financieras
const noticias = await cliente.finanzas.noticiasAccion({
    symbol: "TSLA",
    limit: 10,
    sortBy: "publishedAt"
});

console.log('Noticias Tesla:', noticias.data);

// Métricas de empresa
const metricas = await cliente.finanzas.metricasEmpresa({
    symbol: "MSFT",
    period: "quarterly"
});

console.log('Métricas Microsoft:', metricas.data);
```

### 6. **Herramientas de Comunicación**

```typescript
// Enviar SMS
const sms = await cliente.comunicacion.enviarSMS({
    numero: "+34 600 123 456",
    mensaje: "Tu pedido ha sido confirmado. Número de seguimiento: #12345"
});

console.log('SMS enviado:', sms.data);

// Notificación push
const push = await cliente.comunicacion.enviarPush({
    tokens: ["device_token_1", "device_token_2"],
    titulo: "Actualización disponible",
    cuerpo: "Nueva versión 2.1.0 lista para descargar",
    datos: { version: "2.1.0", url: "https://app.com/update" }
});

console.log('Push enviado:', push.data);
```

## Métodos de Orquestación Completa

```typescript
// Proceso completo de lanzamiento de producto
async function lanzarProductoCompleto(datosProducto) {
    try {
        // Paso 1: Análisis técnico
        const analisisTech = await cliente.desarrollo.analizarViabilidad({
            stack: datosProducto.tecnologia,
            escalabilidad: datosProducto.usuariosEsperados,
            presupuesto: datosProducto.presupuesto
        });

        // Paso 2: Investigación de mercado
        const mercado = await cliente.marketing.investigarMercado({
            categoria: datosProducto.categoria,
            ubicacion: datosProducto.mercado,
            competencia: datosProducto.competidores
        });

        // Paso 3: Estrategia de marketing
        const estrategia = await cliente.marketing.crearEstrategia({
            producto: datosProducto.nombre,
            audiencia: mercado.targetAudience,
            presupuesto: datosProducto.presupuestoMarketing,
            canales: ["google_ads", "social_media", "email"]
        });

        // Paso 4: Configuración CRM
        const configCRM = await cliente.ventas.configurarPipeline({
            producto: datosProducto.nombre,
            etapas: ["Prospecto", "Calificado", "Propuesta", "Negociación", "Cerrado"],
            valores: datosProducto.precios
        });

        // Paso 5: Desarrollo del producto
        const desarrollo = await cliente.desarrollo.iniciarDesarrollo({
            metodologia: "agile",
            sprints: 8,
            tecnologias: datosProducto.tecnologia,
            integraciones: ["payment", "analytics", "crm"]
        });

        return {
            analisis: analisisTech.data,
            mercado: mercado.data,
            estrategia: estrategia.data,
            crm: configCRM.data,
            desarrollo: desarrollo.data,
            estado: "completado"
        };
    } catch (error) {
        console.error('Error en lanzamiento:', error);
        throw error;
    }
}

// Uso
const resultado = await lanzarProductoCompleto({
    nombre: "App de Gestión Empresarial",
    categoria: "B2B SaaS",
    tecnologia: ["React", "Node.js", "PostgreSQL", "AWS"],
    usuariosEsperados: 10000,
    presupuesto: 100000,
    presupuestoMarketing: 50000,
    mercado: ["España", "México", "Argentina"],
    competidores: ["Salesforce", "HubSpot", "Monday.com"]
});

console.log('Producto lanzado:', resultado);
```

## Herramientas MCP Específicas

```typescript
// Uso directo de herramientas MCP
class MCPTools {
    constructor(private cliente: MultiAgenteSDK) {}

    // Google Search
    async buscarGoogle(query: string, numResults = 10) {
        return await this.cliente.mcp('google_search', {
            query,
            num_results: numResults
        });
    }

    // Google Maps
    async buscarLugares(ubicacion: string, tipo: string, radio = 5000) {
        return await this.cliente.mcp('google_maps_search', {
            query: `${tipo} near ${ubicacion}`,
            location: ubicacion,
            radius: radio
        });
    }

    // GitHub
    async crearRepoGitHub(nombre: string, descripcion: string) {
        return await this.cliente.mcp('github_repository', {
            name: nombre,
            description: descripcion,
            private: false,
            auto_init: true
        });
    }

    // AWS S3
    async subirArchivoS3(bucket: string, key: string, archivo: Buffer) {
        return await this.cliente.mcp('aws_s3_upload', {
            bucket,
            key,
            file: archivo.toString('base64')
        });
    }

    // Stock API
    async cotizacionStocks(symbol: string, startDate: string, endDate: string) {
        return await this.cliente.mcp('stock_price', {
            symbol,
            start_date: startDate,
            end_date: endDate,
            interval: '1d'
        });
    }
}

// Uso
const mcp = new MCPTools(cliente);
const resultados = await mcp.buscarGoogle("mejores prácticas desarrollo web 2025");
const lugares = await mcp.buscarLugares("Madrid", "co-working", 10000);
const repo = await mcp.crearRepoGitHub("mi-proyecto", "Descripción del proyecto");
```

## Manejo de Errores y Reintentos

```typescript
// Configuración de reintentos automáticos
const cliente = new MultiAgenteSDK({
    baseURL: 'http://localhost:8000',
    retryConfig: {
        attempts: 3,
        delay: 1000, // 1 segundo
        backoffFactor: 2,
        retryCondition: (error) => {
            return error.status >= 500 || error.code === 'ECONNRESET';
        }
    }
});

// Uso con manejo de errores robusto
async function operacionRobusta() {
    try {
        const resultado = await cliente.ai.generarContenido({
            prompt: "Escribe sobre el futuro de la IA"
        });
        return resultado;
    } catch (error) {
        if (error.code === 'RATE_LIMIT') {
            // Esperar y reintentar
            await new Promise(resolve => setTimeout(resolve, 60000));
            return await operacionRobusta();
        }
        throw error;
    }
}
```

## Cache y Optimización

```typescript
// El SDK incluye cache automático
const cliente = new MultiAgenteSDK({
    baseURL: 'http://localhost:8000',
    cache: {
        enabled: true,
        defaultTTL: 300000, // 5 minutos
        maxSize: 1000 // máximo 1000 entradas
    }
});

// Las llamadas consecutivas se cachean automáticamente
const resultado1 = await cliente.marketing.analizarCompetencia({...});
const resultado2 = await cliente.marketing.analizarCompetencia({...}); // Usará cache

// Cache manual para operaciones costosas
cliente.cache.set('mi-clave', { data: 'valor' }, 600000); // 10 minutos
const valor = cliente.cache.get('mi-clave');
```

## Webhooks y Eventos

```typescript
// Configurar webhook para eventos
cliente.webhooks.on('mcp_execution_completed', (data) => {
    console.log('Ejecución MCP completada:', data);
});

cliente.webhooks.on('team_processing', (data) => {
    console.log('Equipo procesando:', data.team, data.status);
});

// Escuchar todos los eventos
cliente.webhooks.on('*', (event, data) => {
    console.log(`Evento ${event}:`, data);
});
```

## Testing y Desarrollo

```typescript
// Modo desarrollo con mocks
const clienteDev = new MultiAgenteSDK({
    baseURL: 'http://localhost:8000',
    mockMode: true, // Usar datos simulados
    mockDelay: 1000 // Simular latencia de red
});

// En modo mock, todas las respuestas son simuladas
const resultado = await clienteDev.ai.generarContenido({
    prompt: "Test content"
});
console.log(resultado); // Datos simulados consistentes
```

Este SDK hace que integrar el Framework Multiagente en cualquier aplicación JavaScript/TypeScript sea extremadamente sencillo y robusto! 🚀