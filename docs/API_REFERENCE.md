# 📊 API Reference - Framework Silhouette V4.0

## 📋 Resumen de la API

La API del Framework Silhouette V4.0 proporciona endpoints completos para interactuar con todos los 78+ equipos de agentes, sistema de orquestación, workflows dinámicos y sistema audiovisual.

### 🔗 Base URL
- **Producción:** `https://api.silhouette-framework.com/v1`
- **Desarrollo:** `http://localhost:8030/v1`

### 🔐 Autenticación
Todos los endpoints requieren autenticación JWT:
```http
Authorization: Bearer <your_jwt_token>
```

### 📝 Rate Limiting
- **Tier 1 (Free):** 100 requests/hour
- **Tier 2 (Professional):** 1000 requests/hour
- **Tier 3 (Enterprise):** 10000 requests/hour

## 🏢 Core Framework API

### Orchestrator API

#### GET /orchestrator/health
Verifica el estado de salud del orquestador principal.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-09T23:27:43Z",
  "uptime": 123456,
  "active_teams": 78,
  "total_tasks": 15420,
  "version": "4.0.0"
}
```

#### GET /orchestrator/teams
Lista todos los equipos disponibles.

**Query Parameters:**
- `status` (optional): Filter by team status (active, inactive, error)
- `category` (optional): Filter by team category (business, audiovisual, technical, workflow)

**Response:**
```json
{
  "teams": [
    {
      "id": "audiovisual-team",
      "name": "Audio Visual Team",
      "category": "audiovisual",
      "status": "active",
      "port": 8000,
      "capabilities": [
        "video_production",
        "image_search",
        "script_generation"
      ],
      "health": {
        "status": "healthy",
        "uptime": 98765,
        "last_health_check": "2025-11-09T23:27:00Z"
      }
    }
  ],
  "total": 78,
  "active": 76,
  "inactive": 2
}
```

#### POST /orchestrator/assign-task
Asigna una tarea a uno o más equipos.

**Request:**
```json
{
  "task": {
    "id": "task-123",
    "type": "create_marketing_video",
    "priority": "high",
    "data": {
      "project": {
        "title": "Product Launch Video",
        "platform": "instagram",
        "duration": 30,
        "audience": "entrepreneurs"
      }
    },
    "requirements": {
      "quality_threshold": 90,
      "deadline": "2025-11-10T12:00:00Z",
      "max_retry_attempts": 3
    }
  },
  "teams": [
    "audiovisual-team",
    "marketing_team"
  ],
  "workflow": "parallel"
}
```

**Response:**
```json
{
  "assignment_id": "assignment-456",
  "status": "assigned",
  "assigned_teams": [
    {
      "team_id": "audiovisual-team",
      "status": "assigned",
      "estimated_completion": "2025-11-09T23:45:00Z"
    },
    {
      "team_id": "marketing_team",
      "status": "assigned",
      "estimated_completion": "2025-11-09T23:50:00Z"
    }
  ],
  "coordinator": "orchestrator",
  "created_at": "2025-11-09T23:27:43Z"
}
```

#### GET /orchestrator/task/{task_id}
Obtiene el estado de una tarea específica.

**Response:**
```json
{
  "task_id": "task-123",
  "status": "in_progress",
  "progress": 65,
  "current_step": "video_composition",
  "assigned_teams": [
    {
      "team_id": "audiovisual-team",
      "status": "completed",
      "result": {
        "video_url": "https://assets.silhouette.com/videos/product-launch-123.mp4",
        "quality_score": 94.5,
        "duration": 30
      }
    },
    {
      "team_id": "marketing_team",
      "status": "in_progress",
      "progress": 80
    }
  ],
  "timeline": {
    "created": "2025-11-09T23:27:43Z",
    "started": "2025-11-09T23:28:00Z",
    "estimated_completion": "2025-11-09T23:50:00Z"
  }
}
```

### Planner API

#### POST /planner/create-plan
Crea un plan de ejecución para un proyecto complejo.

**Request:**
```json
{
  "project": {
    "name": "Product Launch Campaign",
    "type": "marketing_campaign",
    "timeline": "2_weeks",
    "budget": 50000,
    "teams_required": [
      "business_development_team",
      "marketing_team",
      "sales_team",
      "audiovisual-team",
      "research_team"
    ],
    "dependencies": [
      {
        "step": "market_research",
        "teams": ["research_team"],
        "duration": "3_days"
      },
      {
        "step": "strategy_development",
        "teams": ["business_development_team"],
        "depends_on": ["market_research"],
        "duration": "2_days"
      },
      {
        "step": "content_creation",
        "teams": ["audiovisual-team", "marketing_team"],
        "depends_on": ["strategy_development"],
        "duration": "5_days"
      }
    ]
  }
}
```

**Response:**
```json
{
  "plan_id": "plan-789",
  "project_name": "Product Launch Campaign",
  "estimated_duration": "12_days",
  "steps": [
    {
      "step_id": "step-1",
      "name": "market_research",
      "teams": ["research_team"],
      "start_date": "2025-11-10T09:00:00Z",
      "end_date": "2025-11-13T17:00:00Z",
      "parallel": false,
      "dependencies": []
    },
    {
      "step_id": "step-2",
      "name": "strategy_development",
      "teams": ["business_development_team"],
      "start_date": "2025-11-13T09:00:00Z",
      "end_date": "2025-11-15T17:00:00Z",
      "parallel": false,
      "dependencies": ["step-1"]
    }
  ],
  "optimization_suggestions": [
    {
      "type": "parallelization",
      "suggestion": "Content creation can start 1 day earlier",
      "time_savings": "1_day"
    }
  ]
}
```

## 🎬 AudioVisual System API

### AudioVisual Team API

#### POST /teams/audiovisual/execute-project
Ejecuta un proyecto completo de producción audiovisual.

**Request:**
```json
{
  "project": {
    "title": "AI in Marketing 2025",
    "platform": "instagram_reels",
    "duration": 30,
    "audience": {
      "age_range": "25-40",
      "interests": ["marketing", "AI", "entrepreneurship"],
      "platform_usage": "high"
    },
    "objective": "education_and_engagement",
    "style": "professional_casual",
    "branding": {
      "colors": ["#FF6B6B", "#4ECDC4"],
      "fonts": ["Arial", "Helvetica"],
      "logo": "https://yourdomain.com/logo.png"
    },
    "assets": {
      "search_images": true,
      "generate_script": true,
      "create_animation_prompts": true,
      "verify_quality": true
    },
    "requirements": {
      "quality_threshold": 90,
      "max_generation_time": 300,
      "formats": ["mp4", "webm"]
    }
  }
}
```

**Response:**
```json
{
  "project_id": "av-project-123",
  "status": "completed",
  "execution_time": 245.5,
  "results": {
    "video": {
      "url": "https://assets.silhouette.com/videos/ai-marketing-2025-123.mp4",
      "duration": 30,
      "format": "mp4",
      "resolution": "1080x1920",
      "size_mb": 45.2
    },
    "assets_generated": {
      "script": {
        "content": "Hook: Did you know that AI is revolutionizing digital marketing in 2025?...",
        "hooks": [
          "Did you know that AI is revolutionizing digital marketing in 2025?",
          "Traditional marketing strategies are becoming obsolete"
        ],
        "cta": "Follow for more AI marketing insights! 👆"
      },
      "images": [
        {
          "url": "https://images.silhouette.com/marketing-ai-1.jpg",
          "source": "unsplash",
          "license": "free",
          "quality_score": 95.2
        }
      ],
      "animation_prompts": [
        {
          "provider": "runway",
          "prompt": "Professional marketing presentation with AI elements, smooth transitions, modern office setting",
          "duration": 3,
          "seed": 12345
        }
      ]
    },
    "qa_results": {
      "overall_score": 94.5,
      "components": {
        "content_quality": 96.0,
        "visual_quality": 93.5,
        "audio_quality": 94.0,
        "platform_compliance": 95.0,
        "brand_consistency": 94.5
      },
      "approved": true,
      "recommendations": [
        "Consider adding more dynamic transitions",
        "Audio volume could be slightly increased"
      ]
    },
    "predictions": {
      "engagement_rate": 8.2,
      "viral_potential": 7.5,
      "target_audience_match": 94.0,
      "platform_optimization_score": 91.0
    }
  },
  "metadata": {
    "generated_at": "2025-11-09T23:27:43Z",
    "processing_time": 245.5,
    "api_version": "4.0.0",
    "cost": {
      "api_calls": 12,
      "estimated_cost": 2.45
    }
  }
}
```

#### POST /teams/audiovisual/generate-script
Genera un guión optimizado para una plataforma específica.

**Request:**
```json
{
  "brief": {
    "topic": "Machine Learning for Beginners",
    "platform": "youtube_shorts",
    "duration": 60,
    "audience": "students and professionals",
    "tone": "educational_friendly",
    "key_points": [
      "What is machine learning?",
      "Basic concepts",
      "Practical applications",
      "How to get started"
    ],
    "call_to_action": "Subscribe for more ML tutorials!"
  }
}
```

**Response:**
```json
{
  "script_id": "script-456",
  "platform": "youtube_shorts",
  "duration": 60,
  "script": {
    "hook": "Want to understand machine learning in under 60 seconds?",
    "intro": "Hey there! Today we're diving into machine learning - and trust me, it's simpler than you think!",
    "body": [
      {
        "segment": "definition",
        "duration": 15,
        "content": "Machine learning is like teaching computers to learn from examples, just like how you learned to recognize faces!",
        "visual_cues": ["animation of brain learning", "examples of pattern recognition"]
      },
      {
        "segment": "examples",
        "duration": 25,
        "content": "You use ML every day - Netflix recommendations, Google search, even your email spam filter!",
        "visual_cues": ["Netflix interface", "Google search", "email inbox"]
      },
      {
        "segment": "getting_started",
        "duration": 15,
        "content": "Ready to start? Begin with Python and scikit-learn - they're beginner-friendly!",
        "visual_cues": ["Python logo", "code examples", "learning path"]
      }
    ],
    "cta": "Subscribe for more tech tutorials that actually make sense! 🔔"
  },
  "optimization": {
    "engagement_score": 89.5,
    "viral_potential": 7.2,
    "platform_best_practices": [
      "Use trending audio for better reach",
      "Add captions for accessibility",
      "Post during peak hours (7-9 PM)"
    ]
  }
}
```

### Image Search API

#### POST /teams/image-search/search
Busca imágenes basadas en criterios específicos.

**Request:**
```json
{
  "query": "artificial intelligence marketing data analytics",
  "filters": {
    "min_quality": 90,
    "orientation": "landscape",
    "color_scheme": "modern_tech",
    "license": "free",
    "min_resolution": "1920x1080",
    "count": 10
  },
  "preferences": {
    "style": "professional",
    "mood": "innovative",
    "theme": "business_technology"
  }
}
```

**Response:**
```json
{
  "search_id": "search-789",
  "query": "artificial intelligence marketing data analytics",
  "total_results": 156,
  "images": [
    {
      "id": "img-001",
      "url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71",
      "download_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1920",
      "source": "unsplash",
      "license": "unsplash_license",
      "metadata": {
        "width": 1920,
        "height": 1080,
        "file_size": 245760,
        "format": "jpg",
        "colors": ["#1a1a1a", "#4a90e2", "#ffffff"]
      },
      "quality_score": 95.2,
      "tags": ["technology", "data", "analytics", "business", "modern"],
      "ai_analysis": {
        "content_type": "business_technology",
        "mood": "professional",
        "suitability_score": 94.5,
        "best_use_cases": ["presentation", "website_hero", "social_media"]
      }
    }
  ],
  "optimization_suggestions": [
    {
      "type": "variation",
      "suggestion": "Consider using vertical version for Instagram posts",
      "potential": 15
    }
  ]
}
```

## 🏢 Business Teams API

### Marketing Team API

#### POST /teams/marketing/create-campaign
Crea una campaña de marketing completa.

**Request:**
```json
{
  "campaign": {
    "name": "Product Launch Q1 2025",
    "objective": "brand_awareness_and_sales",
    "target_audience": {
      "demographics": {
        "age_range": "25-45",
        "income": "middle_to_upper",
        "location": "urban_areas"
      },
      "psychographics": {
        "interests": ["technology", "productivity", "efficiency"],
        "values": ["innovation", "quality", "time_saving"],
        "pain_points": ["time_management", "workplace_efficiency"]
      }
    },
    "channels": [
      "social_media",
      "email_marketing",
      "content_marketing",
      "paid_advertising"
    ],
    "timeline": "6_weeks",
    "budget": 25000,
    "kpis": [
      "brand_awareness_increase",
      "website_traffic",
      "lead_generation",
      "sales_conversion"
    ]
  }
}
```

**Response:**
```json
{
  "campaign_id": "campaign-123",
  "status": "created",
  "plan": {
    "strategy": {
      "positioning": "Premium productivity solution for modern professionals",
      "messaging": "Transform your workflow with AI-powered efficiency",
      "unique_value_proposition": "The only tool you need to 10x your productivity"
    },
    "content_calendar": [
      {
        "week": 1,
        "content": [
          {
            "channel": "social_media",
            "type": "awareness_post",
            "content": "Teaser campaign highlighting productivity pain points",
            "format": "carousel_post"
          }
        ]
      }
    ],
    "asset_requirements": [
      {
        "type": "video",
        "specifications": "30-second explainer video",
        "timeline": "week_1-2"
      }
    ],
    "budget_allocation": {
      "content_creation": 8000,
      "paid_advertising": 12000,
      "tools_and_software": 2000,
      "contingency": 3000
    }
  },
  "estimated_metrics": {
    "reach": 50000,
    "engagement_rate": 4.2,
    "leads_generated": 500,
    "estimated_conversion": 50
  },
  "next_steps": [
    "Content creation approval",
    "Asset production",
    "Campaign launch"
  ]
}
```

### Sales Team API

#### POST /teams/sales/create-pipeline
Crea y optimiza un pipeline de ventas.

**Request:**
```json
{
  "pipeline": {
    "name": "Enterprise Software Sales Q1",
    "target_market": "enterprise",
    "product": "Silhouette Framework Enterprise",
    "sales_cycle": "90_days",
    "deal_size": {
      "min": 50000,
      "max": 500000
    },
    "stages": [
      {
        "name": "prospecting",
        "probability": 10,
        "avg_duration": 7
      },
      {
        "name": "qualification",
        "probability": 25,
        "avg_duration": 14
      }
    ]
  }
}
```

**Response:**
```json
{
  "pipeline_id": "pipeline-456",
  "optimization_suggestions": {
    "process_improvements": [
      {
        "area": "qualification",
        "suggestion": "Implement BANT framework for faster qualification",
        "time_savings": "5_days"
      }
    ],
    "tools_integration": [
      "CRM_integration",
      "lead_scoring_automation",
      "follow_up_sequences"
    ],
    "performance_metrics": [
      "conversion_rate_by_stage",
      "avg_time_in_stage",
      "deal_velocity"
    ]
  }
}
```

## 🔧 Infrastructure API

### Optimization Team API

#### GET /optimization-team/metrics
Obtiene métricas de rendimiento del sistema.

**Response:**
```json
{
  "timestamp": "2025-11-09T23:27:43Z",
  "system_metrics": {
    "response_time": {
      "average": 245.5,
      "p95": 450.2,
      "p99": 890.1
    },
    "throughput": {
      "requests_per_second": 125.5,
      "tasks_per_minute": 2500
    },
    "error_rate": {
      "overall": 0.02,
      "by_service": {
        "audiovisual": 0.01,
        "business_teams": 0.03,
        "orchestrator": 0.005
      }
    }
  },
  "optimization_status": {
    "active_optimizations": 5,
    "last_optimization": "2025-11-09T23:20:00Z",
    "performance_improvement": 15.2,
    "resource_savings": 23.5
  }
}
```

#### POST /optimization-team/optimize
Ejecuta una optimización del sistema.

**Request:**
```json
{
  "optimization_request": {
    "type": "performance",
    "target": "response_time",
    "scope": "audiovisual_teams",
    "constraints": {
      "max_downtime": 30,
      "quality_impact": "minimal",
      "cost_impact": "neutral"
    },
    "parameters": {
      "optimization_algorithm": "machine_learning",
      "learning_period": "7_days",
      "confidence_threshold": 0.85
    }
  }
}
```

**Response:**
```json
{
  "optimization_id": "opt-789",
  "status": "in_progress",
  "analysis": {
    "current_performance": {
      "response_time": 450.2,
      "target_improvement": "20%",
      "bottlenecks_identified": [
        "image_processing_queue",
        "database_connection_pool"
      ]
    },
    "optimization_plan": {
      "immediate_actions": [
        {
          "action": "increase_connection_pool",
          "target": "database",
          "expected_improvement": "15%"
        }
      ],
      "medium_term_actions": [
        {
          "action": "implement_caching",
          "target": "image_processing",
          "expected_improvement": "30%"
        }
      ]
    },
    "estimated_impact": {
      "response_time_reduction": "25%",
      "resource_savings": "18%",
      "implementation_time": "45_minutes"
    }
  }
}
```

## 📊 Metrics and Analytics API

### GET /metrics/performance
Obtiene métricas de rendimiento del framework.

**Query Parameters:**
- `time_range` (optional): Time range for metrics (1h, 24h, 7d, 30d)
- `granularity` (optional): Data granularity (1m, 5m, 1h, 1d)
- `services` (optional): Comma-separated list of services

**Response:**
```json
{
  "time_range": "24h",
  "granularity": "5m",
  "metrics": {
    "response_time": [
      {
        "timestamp": "2025-11-09T22:27:43Z",
        "value": 245.5,
        "service": "orchestrator"
      }
    ],
    "throughput": [
      {
        "timestamp": "2025-11-09T22:27:43Z",
        "value": 125.5,
        "unit": "requests_per_second"
      }
    ],
    "error_rate": [
      {
        "timestamp": "2025-11-09T22:27:43Z",
        "value": 0.02,
        "service": "audiovisual"
      }
    ]
  },
  "summary": {
    "total_requests": 125000,
    "success_rate": 99.8,
    "avg_response_time": 245.5,
    "peak_load": 450.2
  }
}
```

## 🔐 Webhook API

### POST /webhooks/register
Registra un webhook para notificaciones.

**Request:**
```json
{
  "webhook": {
    "url": "https://yourapp.com/webhooks/silhouette",
    "events": [
      "task.completed",
      "optimization.completed",
      "system.alert"
    ],
    "secret": "your_webhook_secret",
    "active": true
  }
}
```

**Response:**
```json
{
  "webhook_id": "webhook-123",
  "status": "active",
  "events": [
    "task.completed",
    "optimization.completed",
    "system.alert"
  ],
  "created_at": "2025-11-09T23:27:43Z"
}
```

### Webhook Payload Example
```json
{
  "event": "task.completed",
  "timestamp": "2025-11-09T23:45:00Z",
  "data": {
    "task_id": "task-123",
    "project_name": "Product Launch Video",
    "status": "completed",
    "result": {
      "video_url": "https://assets.silhouette.com/videos/video-123.mp4",
      "quality_score": 94.5
    },
    "execution_time": 245.5
  }
}
```

## 📚 SDKs y Librerías

### JavaScript/Node.js SDK

```javascript
const SilhouetteAPI = require('@silhouette/framework-api');

const client = new SilhouetteAPI({
  baseURL: 'https://api.silhouette-framework.com/v1',
  auth: {
    token: 'your_jwt_token'
  }
});

// Crear proyecto audiovisual
const project = await client.audiovisual.createProject({
  title: "AI Marketing Video",
  platform: "instagram_reels",
  duration: 30
});

console.log('Video URL:', project.results.video.url);
```

### Python SDK

```python
from silhouette_api import SilhouetteClient

client = SilhouetteClient(
    base_url='https://api.silhouette-framework.com/v1',
    auth_token='your_jwt_token'
)

# Crear campaña de marketing
campaign = client.marketing.create_campaign({
    'name': 'Product Launch Q1',
    'objective': 'brand_awareness',
    'channels': ['social_media', 'email']
})

print(f"Campaign ID: {campaign['campaign_id']}")
```

### cURL Examples

```bash
# Verificar salud del sistema
curl -X GET "https://api.silhouette-framework.com/v1/orchestrator/health" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Crear proyecto audiovisual
curl -X POST "https://api.silhouette-framework.com/v1/teams/audiovisual/execute-project" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project": {
      "title": "Test Video",
      "platform": "instagram",
      "duration": 30
    }
  }'
```

## 📖 Error Handling

### Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid project configuration",
    "details": {
      "field": "duration",
      "constraint": "must_be_between_15_and_300",
      "received": 600
    },
    "request_id": "req-123456",
    "timestamp": "2025-11-09T23:27:43Z"
  }
}
```

### Common Error Codes
- `AUTHENTICATION_ERROR` (401): Invalid or missing authentication
- `AUTHORIZATION_ERROR` (403): Insufficient permissions
- `VALIDATION_ERROR` (400): Invalid request data
- `RATE_LIMIT_EXCEEDED` (429): Rate limit exceeded
- `SERVICE_UNAVAILABLE` (503): Service temporarily unavailable
- `INTERNAL_ERROR` (500): Internal server error

## 🔄 Rate Limiting Headers

Las respuestas incluyen headers de rate limiting:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642690000
X-RateLimit-Window: 3600
```

---

Esta API Reference proporciona acceso completo a todas las funcionalidades del Framework Silhouette V4.0, permitiendo integración perfecta con sistemas externos y desarrollo de aplicaciones personalizadas.
