# SDKs de Integración Multi-App
## Ejemplos de Implementación para Iris, Silhouette y Apps

**Autor:** Silhouette Anónimo  
**Fecha:** 08-Nov-2025  
**Versión:** 1.0

---

## 📦 SDK para Iris (Computer Vision)

### Instalación y Configuración

```bash
# NPM
npm install @haas/iris-sdk

# Yarn
yarn add @haas/iris-sdk

# Configuración
export IRIS_API_KEY="your_iris_api_key"
export HAAS_ENDPOINT="https://haas-platform.com/api"
```

### SDK Principal

```typescript
// iris-sdk.ts
import axios, { AxiosInstance } from 'axios';

export interface IrisConfig {
  apiKey: string;
  endpoint: string;
  tenantId: string;
  timeout?: number;
  retries?: number;
}

export interface ImageAnalysisRequest {
  imageUrl?: string;
  imageData?: string;
  analysisType: 'basic' | 'comprehensive' | 'medical' | 'creative';
  options?: {
    detectObjects?: boolean;
    extractText?: boolean;
    analyzeColors?: boolean;
    generateInsights?: boolean;
    createWorkflow?: boolean;
    crossAppIntegration?: boolean;
  };
}

export interface ImageAnalysisResult {
  analysisId: string;
  originalImage: string;
  results: {
    objects?: DetectedObject[];
    text?: ExtractedText[];
    colors?: ColorAnalysis;
    style?: StyleAnalysis;
    medicalFindings?: MedicalFinding[];
    insights?: AIGeneratedInsight[];
  };
  confidence: number;
  processingTime: number;
  crossAppSuggestions?: CrossAppWorkflow[];
  metadata: {
    tenantId: string;
    appId: string;
    timestamp: string;
  };
}

export class IrisSDK {
  private client: AxiosInstance;
  private config: IrisConfig;

  constructor(config: IrisConfig) {
    this.config = config;
    this.client = axios.create({
      baseURL: config.endpoint,
      timeout: config.timeout || 30000,
      headers: {
        'Authorization': `Bearer ${config.apiKey}`,
        'X-Tenant-ID': config.tenantId,
        'X-App-ID': 'iris',
        'Content-Type': 'application/json'
      }
    });
  }

  // Análisis de imagen principal
  async analyzeImage(request: ImageAnalysisRequest): Promise<ImageAnalysisResult> {
    try {
      const response = await this.client.post('/iris/analyze', {
        ...request,
        tenant_id: this.config.tenantId
      });
      
      return response.data;
    } catch (error) {
      throw new Error(`Iris SDK Error: ${error.message}`);
    }
  }

  // Análisis médico especializado
  async analyzeMedicalImage(request: {
    imageUrl: string;
    analysisType: 'radiology' | 'dermatology' | 'ophthalmology' | 'pathology';
    patientContext?: any;
  }): Promise<MedicalAnalysisResult> {
    const response = await this.client.post('/iris/medical/analyze', {
      ...request,
      tenant_id: this.config.tenantId
    });
    
    return response.data;
  }

  // Generación de contenido visual
  async generateVisualContent(request: {
    prompt: string;
    style: 'medical' | 'creative' | 'technical' | 'artistic';
    outputFormat: 'png' | 'jpg' | 'svg';
    variations: number;
    crossAppWorkflow?: boolean;
  }): Promise<VisualContentResult> {
    const response = await this.client.post('/iris/generate', {
      ...request,
      tenant_id: this.config.tenantId
    });
    
    return response.data;
  }

  // Workflows cross-app
  async createCrossAppWorkflow(workflow: {
    sourceImage: string;
    targetApps: ('silhouette' | 'nwc' | 'brandistry')[];
    objective: string;
  }): Promise<CrossAppWorkflowResult> {
    const response = await this.client.post('/iris/workflow/create', {
      ...workflow,
      tenant_id: this.config.tenantId
    });
    
    return response.data;
  }

  // Gestión de contexto compartido
  async updateSharedContext(context: {
    userId: string;
    contextType: 'user_preference' | 'project' | 'session';
    data: any;
  }): Promise<void> {
    await this.client.post('/context/update', {
      ...context,
      tenant_id: this.config.tenantId,
      app_id: 'iris'
    });
  }
}

// Ejemplo de uso
const iris = new IrisSDK({
  apiKey: process.env.IRIS_API_KEY!,
  endpoint: process.env.HAAS_ENDPOINT!,
  tenantId: 'tenant_iris_v1'
});

// Uso básico
const analysis = await iris.analyzeImage({
  imageUrl: 'https://example.com/medical-scan.jpg',
  analysisType: 'medical',
  options: {
    detectObjects: true,
    generateInsights: true,
    crossAppIntegration: true
  }
});

console.log('Análisis completado:', analysis.results);
```

---

## 🎨 SDK para Silhouette (Design AI)

### Instalación y Configuración

```bash
npm install @haas/silhouette-sdk
```

### SDK Principal

```typescript
// silhouette-sdk.ts
export interface SilhouetteConfig {
  apiKey: string;
  endpoint: string;
  tenantId: string;
  timeout?: number;
}

export interface DesignRequest {
  prompt: string;
  style: 'modern' | 'classic' | 'minimalist' | 'creative' | 'medical' | 'technical';
  outputFormat: 'png' | 'jpg' | 'svg' | 'pdf';
  dimensions?: {
    width: number;
    height: number;
  };
  variations?: number;
  crossAppIntegration?: boolean;
  designContext?: {
    industry?: string;
    targetAudience?: string;
    brandPersonality?: string;
    existingAssets?: string[];
  };
}

export interface DesignResult {
  designId: string;
  designs: {
    url: string;
    format: string;
    dimensions: { width: number; height: number };
    style: string;
    description: string;
  }[];
  brandSuggestions?: BrandSuggestion[];
  crossAppIntegration?: {
    iris: VisualAnalysis[];
    nwc: WorkflowSuggestions[];
    brandistry: ContentStrategy[];
  };
  metadata: {
    processingTime: number;
    confidence: number;
    tenantId: string;
  };
}

export class SilhouetteSDK {
  private client: AxiosInstance;
  private config: SilhouetteConfig;

  constructor(config: SilhouetteConfig) {
    this.config = config;
    this.client = axios.create({
      baseURL: config.endpoint,
      headers: {
        'Authorization': `Bearer ${config.apiKey}`,
        'X-Tenant-ID': config.tenantId,
        'X-App-ID': 'silhouette'
      }
    });
  }

  // Generación de diseño principal
  async generateDesign(request: DesignRequest): Promise<DesignResult> {
    const response = await this.client.post('/silhouette/generate', {
      ...request,
      tenant_id: this.config.tenantId
    });
    
    return response.data;
  }

  // Crear sistema de diseño completo
  async createDesignSystem(request: {
    brandName: string;
    industry: string;
    style: string;
    colorPalette?: string[];
    typography?: string;
    includeBrandGuide?: boolean;
    crossAppOptimization?: boolean;
  }): Promise<DesignSystemResult> {
    const response = await this.client.post('/silhouette/design-system', {
      ...request,
      tenant_id: this.config.tenantId
    });
    
    return response.data;
  }

  // Generar assets de marca
  async generateBrandAssets(request: {
    brandName: string;
    logoStyle: 'text' | 'symbol' | 'combination' | 'abstract';
    tagline?: string;
    businessType: string;
    includeSocialMedia?: boolean;
    includeBusinessCards?: boolean;
  }): Promise<BrandAssetsResult> {
    const response = await this.client.post('/silhouette/brand-assets', {
      ...request,
      tenant_id: this.config.tenantId
    });
    
    return response.data;
  }

  // Workflows cross-app
  async createIntegratedWorkflow(request: {
    designBrief: string;
    targetApps: ('iris' | 'nwc' | 'brandistry')[];
    integrationType: 'concurrent' | 'sequential' | 'iterative';
  }): Promise<IntegratedWorkflowResult> {
    const response = await this.client.post('/silhouette/integrated-workflow', {
      ...request,
      tenant_id: this.config.tenantId
    });
    
    return response.data;
  }
}

// Ejemplo de uso
const silhouette = new SilhouetteSDK({
  apiKey: process.env.SILHOUETTE_API_KEY!,
  endpoint: process.env.HAAS_ENDPOINT!,
  tenantId: 'tenant_silhouette_v1'
});

// Generar diseño con integración
const design = await silhouette.generateDesign({
  prompt: 'Diseño moderno para aplicación de salud digital',
  style: 'medical',
  outputFormat: 'png',
  variations: 3,
  crossAppIntegration: true,
  designContext: {
    industry: 'healthcare',
    targetAudience: 'patients_and_doctors',
    brandPersonality: 'trustworthy_innovative'
  }
});

console.log('Diseños generados:', design.designs);
```

---

## ⚙️ SDK para NWC (Workflow Automation)

### Instalación y Configuración

```bash
npm install @haas/nwc-sdk
```

### SDK Principal

```typescript
// nwc-sdk.ts
export interface NWCConfig {
  apiKey: string;
  endpoint: string;
  tenantId: string;
}

export interface WorkflowRequest {
  workflowName: string;
  description: string;
  triggerType: 'manual' | 'scheduled' | 'event' | 'api';
  steps: WorkflowStep[];
  inputs?: Record<string, any>;
  outputs?: Record<string, any>;
  crossAppIntegration?: boolean;
}

export interface WorkflowStep {
  stepId: string;
  stepName: string;
  appId: 'nwc' | 'iris' | 'silhouette' | 'brandistry';
  action: string;
  inputs: Record<string, any>;
  outputs: Record<string, any>;
  conditions?: WorkflowCondition[];
  errorHandling?: ErrorHandling;
}

export class NWCSdk {
  private client: AxiosInstance;
  private config: NWCConfig;

  constructor(config: NWCConfig) {
    this.config = config;
    this.client = axios.create({
      baseURL: config.endpoint,
      headers: {
        'Authorization': `Bearer ${config.apiKey}`,
        'X-Tenant-ID': config.tenantId,
        'X-App-ID': 'nwc'
      }
    });
  }

  // Crear workflow
  async createWorkflow(request: WorkflowRequest): Promise<WorkflowResult> {
    const response = await this.client.post('/nwc/workflow/create', {
      ...request,
      tenant_id: this.config.tenantId
    });
    
    return response.data;
  }

  // Ejecutar workflow
  async executeWorkflow(workflowId: string, inputs?: Record<string, any>): Promise<WorkflowExecutionResult> {
    const response = await this.client.post(`/nwc/workflow/${workflowId}/execute`, {
      inputs,
      tenant_id: this.config.tenantId
    });
    
    return response.data;
  }

  // Optimizar workflow existente
  async optimizeWorkflow(request: {
    workflowId: string;
    optimizationGoals: ('speed' | 'reliability' | 'cost' | 'accuracy')[];
    targetMetrics?: Record<string, number>;
  }): Promise<OptimizationResult> {
    const response = await this.client.post('/nwc/workflow/optimize', {
      ...request,
      tenant_id: this.config.tenantId
    });
    
    return response.data;
  }

  // Crear workflow cross-app
  async createCrossAppWorkflow(request: {
    workflowName: string;
    involvedApps: string[];
    dataFlow: Record<string, any>;
    synchronization: 'real-time' | 'batch' | 'event-driven';
  }): Promise<CrossAppWorkflowResult> {
    const response = await this.client.post('/nwc/cross-app-workflow', {
      ...request,
      tenant_id: this.config.tenantId
    });
    
    return response.data;
  }
}

// Ejemplo de uso
const nwc = new NWCSdk({
  apiKey: process.env.NWC_API_KEY!,
  endpoint: process.env.HAAS_ENDPOINT!,
  tenantId: 'tenant_nwc_v1'
});

// Crear workflow complejo
const workflow = await nwc.createWorkflow({
  workflowName: 'customer_onboarding_unified',
  description: 'Proceso completo de onboarding usando múltiples apps',
  triggerType: 'manual',
  crossAppIntegration: true,
  steps: [
    {
      stepId: 'design_creation',
      stepName: 'Crear diseño de onboarding',
      appId: 'silhouette',
      action: 'generate_onboarding_design',
      inputs: { company_name: '{{company}}', style: 'modern' },
      outputs: { design_assets: 'design_result' }
    },
    {
      stepId: 'visual_analysis',
      stepName: 'Analizar diseño con IA',
      appId: 'iris',
      action: 'analyze_ux_design',
      inputs: { design: '{{design_assets}}' },
      outputs: { ux_feedback: 'analysis_result' }
    },
    {
      stepId: 'workflow_automation',
      stepName: 'Automatizar proceso',
      appId: 'nwc',
      action: 'create_automation',
      inputs: { ux_feedback: '{{ux_feedback}}', design: '{{design_assets}}' },
      outputs: { automation: 'workflow_result' }
    }
  ]
});

console.log('Workflow creado:', workflow.workflowId);
```

---

## 🏥 SDK para MedLuxe (Healthcare AI)

### SDK Principal

```typescript
// medluxe-sdk.ts
export interface MedLuxeConfig {
  apiKey: string;
  endpoint: string;
  tenantId: string;
  compliance?: ('HIPAA' | 'GDPR' | 'SOC2')[];
}

export interface MedicalAnalysisRequest {
  patientData: {
    age: number;
    gender: 'male' | 'female' | 'other';
    medicalHistory: string[];
    currentSymptoms: string[];
  };
  analysisType: 'differential_diagnosis' | 'treatment_plan' | 'risk_assessment' | 'drug_interaction';
  urgency: 'routine' | 'urgent' | 'emergency';
  includeCrossApp?: boolean;
}

export class MedLuxeSDK {
  private client: AxiosInstance;
  private config: MedLuxeConfig;

  constructor(config: MedLuxeConfig) {
    this.config = config;
    this.client = axios.create({
      baseURL: config.endpoint,
      headers: {
        'Authorization': `Bearer ${config.apiKey}`,
        'X-Tenant-ID': config.tenantId,
        'X-App-ID': 'medluxe',
        'X-Compliance': config.compliance?.join(',') || 'HIPAA'
      }
    });
  }

  // Análisis médico con IA
  async analyzeMedicalCase(request: MedicalAnalysisRequest): Promise<MedicalAnalysisResult> {
    const response = await this.client.post('/medluxe/analyze', {
      ...request,
      tenant_id: this.config.tenantId
    });
    
    return response.data;
  }

  // Integración con imágenes médicas (Iris)
  async analyzeWithImaging(request: {
    patientData: MedicalAnalysisRequest['patientData'];
    medicalImages: string[];
    analysisType: 'radiology' | 'dermatology' | 'ophthalmology';
  }): Promise<IntegratedMedicalResult> {
    const response = await this.client.post('/medluxe/imaging-analysis', {
      ...request,
      tenant_id: this.config.tenantId
    });
    
    return response.data;
  }
}
```

---

## 🏷️ SDK para Brandistry (Branding AI)

### SDK Principal

```typescript
// brandistry-sdk.ts
export interface BrandistryConfig {
  apiKey: string;
  endpoint: string;
  tenantId: string;
}

export interface BrandStrategyRequest {
  companyName: string;
  industry: string;
  targetAudience: string;
  brandPersonality: string[];
  competitors?: string[];
  goals: string[];
  budget?: number;
  timeline?: string;
  crossAppIntegration?: boolean;
}

export class BrandistrySDK {
  async createBrandStrategy(request: BrandStrategyRequest): Promise<BrandStrategyResult> {
    const response = await this.client.post('/brandistry/strategy', {
      ...request,
      tenant_id: this.config.tenantId
    });
    
    return response.data;
  }

  // Integración con diseño (Silhouette)
  async createIntegratedBranding(request: BrandStrategyRequest & {
    designAssets?: string[];
  }): Promise<IntegratedBrandingResult> {
    const response = await this.client.post('/brandistry/integrated', {
      ...request,
      tenant_id: this.config.tenantId
    });
    
    return response.data;
  }
}
```

---

## 🔧 SDK Unificado (Multi-App)

### Cliente Unificado

```typescript
// unified-client.ts
export interface UnifiedClientConfig {
  apiKey: string;
  endpoint: string;
  tenants: {
    iris: string;
    silhouette: string;
    nwc: string;
    medluxe?: string;
    brandistry?: string;
  };
}

export class UnifiedHaaSClient {
  private iris: IrisSDK;
  private silhouette: SilhouetteSDK;
  private nwc: NWCSdk;
  private medluxe?: MedLuxeSDK;
  private brandistry?: BrandistrySDK;
  private config: UnifiedClientConfig;

  constructor(config: UnifiedClientConfig) {
    this.config = config;
    this.iris = new IrisSDK({
      apiKey: config.apiKey,
      endpoint: config.endpoint,
      tenantId: config.tenants.iris
    });
    this.silhouette = new SilhouetteSDK({
      apiKey: config.apiKey,
      endpoint: config.endpoint,
      tenantId: config.tenants.silhouette
    });
    this.nwc = new NWCSdk({
      apiKey: config.apiKey,
      endpoint: config.endpoint,
      tenantId: config.tenants.nwc
    });
    
    if (config.tenants.medluxe) {
      this.medluxe = new MedLuxeSDK({
        apiKey: config.apiKey,
        endpoint: config.endpoint,
        tenantId: config.tenants.medluxe
      });
    }
    
    if (config.tenants.brandistry) {
      this.brandistry = new BrandistrySDK({
        apiKey: config.apiKey,
        endpoint: config.endpoint,
        tenantId: config.tenants.brandistry
      });
    }
  }

  // Workflow integrado completo
  async executeIntegratedWorkflow(request: {
    name: string;
    steps: Array<{
      app: 'iris' | 'silhouette' | 'nwc' | 'medluxe' | 'brandistry';
      action: string;
      inputs: any;
    }>;
    parallel?: boolean;
  }): Promise<IntegratedWorkflowResult> {
    // Implementación de workflow integrado
    const results = [];
    
    for (const step of request.steps) {
      let result;
      switch (step.app) {
        case 'iris':
          result = await this.iris.analyzeImage(step.inputs);
          break;
        case 'silhouette':
          result = await this.silhouette.generateDesign(step.inputs);
          break;
        case 'nwc':
          result = await this.nwc.createWorkflow(step.inputs);
          break;
        case 'medluxe':
          result = await this.medluxe!.analyzeMedicalCase(step.inputs);
          break;
        case 'brandistry':
          result = await this.brandistry!.createBrandStrategy(step.inputs);
          break;
      }
      results.push({ step: step.app, result });
    }
    
    return { workflowId: 'integrated', results };
  }

  // Gestión de contexto compartido
  async shareContext(userId: string, data: any): Promise<void> {
    await this.iris.updateSharedContext({ userId, contextType: 'user_preference', data });
  }

  // Obtener apps disponibles
  getAvailableApps(): string[] {
    return ['iris', 'silhouette', 'nwc', ...(this.medluxe ? ['medluxe'] : []), ...(this.brandistry ? ['brandistry'] : [])];
  }
}

// Ejemplo de uso unificado
const haas = new UnifiedHaaSClient({
  apiKey: process.env.HAAS_API_KEY!,
  endpoint: process.env.HAAS_ENDPOINT!,
  tenants: {
    iris: 'tenant_iris_v1',
    silhouette: 'tenant_silhouette_v1',
    nwc: 'tenant_nwc_v1',
    medluxe: 'tenant_medluxe_v1',
    brandistry: 'tenant_brandistry_v1'
  }
});

// Ejemplo: Crear startup completa
const startupWorkflow = await haas.executeIntegratedWorkflow({
  name: 'create_startup',
  steps: [
    {
      app: 'brandistry',
      action: 'create_brand_strategy',
      inputs: {
        companyName: 'TechHealth',
        industry: 'healthcare',
        targetAudience: 'doctors_and_patients',
        brandPersonality: ['innovative', 'trustworthy', 'professional']
      }
    },
    {
      app: 'silhouette',
      action: 'generate_design',
      inputs: {
        prompt: 'Modern healthcare app design',
        style: 'medical',
        designContext: {
          industry: 'healthcare',
          brandPersonality: 'innovative_trustworthy'
        }
      }
    },
    {
      app: 'iris',
      action: 'analyze_ux_design',
      inputs: {
        imageUrl: '{{previous_design_url}}',
        analysisType: 'comprehensive'
      }
    },
    {
      app: 'nwc',
      action: 'create_workflow',
      inputs: {
        workflowName: 'patient_onboarding',
        triggerType: 'manual',
        steps: [
          {
            stepName: 'Design check',
            appId: 'iris',
            action: 'analyze_ux_design'
          }
        ]
      }
    }
  ]
});

console.log('Startup creada exitosamente:', startupWorkflow);
```

---

## 🧪 Ejemplos de Testing

### Test de Integración

```typescript
// integration.test.ts
import { UnifiedHaaSClient } from './unified-client';
import { jest } from '@jest/globals';

describe('HaaS Multi-App Integration', () => {
  let haas: UnifiedHaaSClient;

  beforeAll(() => {
    haas = new UnifiedHaaSClient({
      apiKey: process.env.HAAS_API_KEY!,
      endpoint: process.env.HAAS_ENDPOINT!,
      tenants: {
        iris: 'tenant_test',
        silhouette: 'tenant_test',
        nwc: 'tenant_test'
      }
    });
  });

  test('should create integrated workflow', async () => {
    const workflow = await haas.executeIntegratedWorkflow({
      name: 'test_workflow',
      steps: [
        {
          app: 'silhouette',
          action: 'generate_design',
          inputs: { prompt: 'test design' }
        }
      ]
    });

    expect(workflow.workflowId).toBeDefined();
    expect(workflow.results).toHaveLength(1);
  });

  test('should share context between apps', async () => {
    const testContext = {
      userPreferences: { theme: 'dark', language: 'en' },
      lastSession: '2025-11-08'
    };

    await haas.shareContext('test_user', testContext);
    // Verificar que el contexto se compartió correctamente
  });
});
```

---

## 📊 Monitoreo y Métricas

### Cliente de Métricas

```typescript
// metrics-client.ts
export class HaaSMetrics {
  async getAppMetrics(appId: string): Promise<AppMetrics> {
    // Implementación de métricas por app
  }

  async getCrossAppUsage(): Promise<CrossAppMetrics> {
    // Métricas de uso cross-app
  }

  async getSystemHealth(): Promise<SystemHealth> {
    // Salud del sistema completo
  }
}
```

Este SDK unificado permite a los desarrolladores integrar fácilmente todas las aplicaciones (Iris, Silhouette, NWC, MedLuxe, Brandistry) en un solo sistema multiagente, manteniendo el aislamiento por tenant pero permitiendo workflows colaborativos entre aplicaciones.

**La clave está en la unificación de la infraestructura mientras se mantiene la especialización de cada aplicación.**