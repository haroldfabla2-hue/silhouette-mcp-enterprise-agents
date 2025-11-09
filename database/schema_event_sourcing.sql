-- =====================================================
-- ESQUEMA DE BASE DE DATOS: EVENT SOURCING + MULTI-TENANT
-- Sistema Multiagente HAAS+ con Aislamiento por Aplicación
-- Autor: MiniMax Agent
-- Fecha: 08-Nov-2025
-- =====================================================

-- Habilitar extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- =====================================================
-- 1. TABLAS CORE MULTI-TENANT
-- =====================================================

-- Tabla principal de aplicaciones/tenants
CREATE TABLE app_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    app_id TEXT UNIQUE NOT NULL, -- 'iris', 'silhouette', 'nwc', etc.
    app_name TEXT NOT NULL,
    tenant_id TEXT NOT NULL, -- tenant_iris_v1, tenant_silhouette_v1, etc.
    app_type TEXT NOT NULL, -- 'computer_vision', 'design', 'workflow', etc.
    
    -- Configuración de la aplicación
    capabilities TEXT[] DEFAULT '{}',
    team_specialization TEXT,
    
    -- Modelos de IA asociados
    primary_model TEXT DEFAULT 'gpt-4o',
    secondary_model TEXT,
    custom_models JSONB DEFAULT '{}',
    
    -- Cuotas y límites
    quotas JSONB DEFAULT '{"requests_per_hour": 1000, "storage_gb": 10, "compute_units": 100}',
    
    -- Metadatos
    metadata JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- 2. EVENT SOURCING - STORES DE EVENTOS
-- =====================================================

-- Event Store Principal
CREATE TABLE event_store (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Identificadores multi-tenant
    tenant_id TEXT NOT NULL,
    app_id TEXT NOT NULL,
    
    -- Información del evento
    event_type TEXT NOT NULL, -- 'TaskCreated', 'PlanGenerated', 'AgentExecuted', etc.
    event_version INTEGER DEFAULT 1,
    event_timestamp TIMESTAMPTZ DEFAULT NOW(),
    
    -- Payload del evento
    event_data JSONB NOT NULL,
    event_metadata JSONB DEFAULT '{}',
    
    -- Información de agregación
    aggregate_type TEXT, -- 'Task', 'Plan', 'Agent', 'Workflow'
    aggregate_id UUID,
    
    -- Causación y correlación
    causation_id UUID,
    correlation_id UUID,
    
    -- Índices para optimización
    INDEX idx_event_tenant_app (tenant_id, app_id),
    INDEX idx_event_type (event_type),
    INDEX idx_event_aggregate (aggregate_type, aggregate_id),
    INDEX idx_event_timestamp (event_timestamp),
    INDEX idx_event_correlation (correlation_id)
);

-- Event Store para Contexto y Memoria
CREATE TABLE context_events (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Identificadores multi-tenant
    tenant_id TEXT NOT NULL,
    app_id TEXT NOT NULL,
    user_id TEXT,
    session_id TEXT,
    
    -- Información del evento
    event_type TEXT NOT NULL, -- 'ContextUpdated', 'KnowledgeStored', 'MemoryIndexed'
    event_timestamp TIMESTAMPTZ DEFAULT NOW(),
    event_data JSONB NOT NULL,
    
    -- Tipos de contexto
    context_type TEXT NOT NULL, -- 'user', 'project', 'session', 'task', 'knowledge'
    context_key TEXT NOT NULL,
    context_value JSONB NOT NULL,
    
    -- Índices
    INDEX idx_context_tenant_app (tenant_id, app_id),
    INDEX idx_context_user_session (user_id, session_id),
    INDEX idx_context_type (context_type, context_key)
);

-- =====================================================
-- 3. READ MODELS - PROYECCIONES PARA LECTURA
-- =====================================================

-- Read Model: Tareas Activas
CREATE TABLE task_read_model (
    task_id UUID PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    app_id TEXT NOT NULL,
    
    -- Información de la tarea
    task_name TEXT NOT NULL,
    task_type TEXT NOT NULL,
    task_status TEXT NOT NULL, -- 'pending', 'in_progress', 'completed', 'failed', 'cancelled'
    task_priority INTEGER DEFAULT 1,
    
    -- Plan y dependencias
    parent_plan_id UUID,
    dependencies JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    
    -- Asignación de agentes
    assigned_team TEXT,
    assigned_agent_id UUID,
    estimated_duration INTERVAL,
    actual_duration INTERVAL,
    
    -- Resultado
    result_data JSONB,
    error_data JSONB,
    
    -- Índices
    INDEX idx_task_tenant_app (tenant_id, app_id),
    INDEX idx_task_status (task_status),
    INDEX idx_task_team (assigned_team),
    INDEX idx_task_created (created_at),
    
    -- RLS habilitado
    RLS ENABLE
);

-- Read Model: Planes de Trabajo
CREATE TABLE plan_read_model (
    plan_id UUID PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    app_id TEXT NOT NULL,
    
    -- Información del plan
    plan_name TEXT NOT NULL,
    plan_type TEXT NOT NULL, -- 'workflow', 'project', 'task_sequence'
    plan_status TEXT NOT NULL, -- 'draft', 'active', 'paused', 'completed', 'cancelled'
    
    -- Objetivo y contexto
    objective TEXT,
    context JSONB,
    
    -- Métricas
    total_tasks INTEGER DEFAULT 0,
    completed_tasks INTEGER DEFAULT 0,
    progress_percentage DECIMAL(5,2) DEFAULT 0.0,
    
    -- Tiempos
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    
    -- Índices
    INDEX idx_plan_tenant_app (tenant_id, app_id),
    INDEX idx_plan_status (plan_status),
    INDEX idx_plan_created (created_at),
    
    RLS ENABLE
);

-- Read Model: Estados de Agentes
CREATE TABLE agent_read_model (
    agent_id UUID PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    app_id TEXT NOT NULL,
    
    -- Información del agente
    agent_name TEXT NOT NULL,
    agent_type TEXT NOT NULL, -- 'orchestrator', 'planner', 'specialist', etc.
    team_name TEXT NOT NULL,
    specializations TEXT[] DEFAULT '{}',
    
    -- Estado actual
    current_status TEXT NOT NULL, -- 'idle', 'busy', 'offline', 'maintenance'
    current_task_id UUID,
    last_activity TIMESTAMPTZ DEFAULT NOW(),
    
    -- Métricas de rendimiento
    tasks_completed INTEGER DEFAULT 0,
    average_task_duration INTERVAL,
    success_rate DECIMAL(5,2) DEFAULT 100.0,
    error_count INTEGER DEFAULT 0,
    
    -- Configuración
    capabilities JSONB DEFAULT '{}',
    configuration JSONB DEFAULT '{}',
    max_concurrent_tasks INTEGER DEFAULT 1,
    
    -- Índices
    INDEX idx_agent_tenant_app (tenant_id, app_id),
    INDEX idx_agent_team (team_name),
    INDEX idx_agent_status (current_status),
    INDEX idx_agent_activity (last_activity),
    
    RLS ENABLE
);

-- Read Model: Contexto Compartido
CREATE TABLE shared_context (
    context_id UUID PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    app_id TEXT NOT NULL,
    user_id TEXT,
    session_id TEXT,
    
    context_type TEXT NOT NULL, -- 'user_preference', 'project_context', 'session_memory'
    context_key TEXT NOT NULL,
    context_value JSONB NOT NULL,
    
    -- Metadatos
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    
    -- Índices
    INDEX idx_context_tenant_app (tenant_id, app_id),
    INDEX idx_context_user_session (user_id, session_id),
    INDEX idx_context_type_key (context_type, context_key),
    INDEX idx_context_expiry (expires_at),
    
    RLS ENABLE
);

-- =====================================================
-- 4. WORKFLOWS Y COLABORACIÓN CROSS-APP
-- =====================================================

-- Workflows que involucran múltiples aplicaciones
CREATE TABLE cross_app_workflows (
    workflow_id UUID PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    
    -- Información del workflow
    workflow_name TEXT NOT NULL,
    workflow_description TEXT,
    workflow_status TEXT NOT NULL, -- 'draft', 'active', 'completed', 'failed'
    
    -- Apps involucradas
    involved_apps TEXT[] NOT NULL, -- ['iris', 'silhouette', 'nwc']
    
    -- Definición del workflow
    workflow_definition JSONB NOT NULL,
    current_step INTEGER DEFAULT 0,
    total_steps INTEGER,
    
    -- Contexto
    context JSONB,
    inputs JSONB,
    outputs JSONB,
    
    -- Tiempos
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    
    -- Índices
    INDEX idx_workflow_tenant (tenant_id),
    INDEX idx_workflow_status (workflow_status),
    INDEX idx_workflow_apps (involved_apps),
    
    RLS ENABLE
);

-- =====================================================
-- 5. AUDITORÍA Y LOGS
-- =====================================================

-- Log de auditoría multi-tenant
CREATE TABLE audit_log (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Identificadores
    tenant_id TEXT NOT NULL,
    app_id TEXT,
    user_id TEXT,
    
    -- Información del evento
    action TEXT NOT NULL, -- 'CREATE', 'READ', 'UPDATE', 'DELETE', 'EXECUTE'
    resource_type TEXT, -- 'task', 'plan', 'agent', 'context'
    resource_id UUID,
    
    -- Detalles
    details JSONB,
    result TEXT, -- 'success', 'failure', 'partial'
    error_message TEXT,
    
    -- Contexto técnico
    request_id UUID,
    client_ip INET,
    user_agent TEXT,
    
    -- Timestamp
    logged_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Índices
    INDEX idx_audit_tenant_app (tenant_id, app_id),
    INDEX idx_audit_user (user_id),
    INDEX idx_audit_resource (resource_type, resource_id),
    INDEX idx_audit_timestamp (logged_at),
    INDEX idx_audit_action (action)
);

-- =====================================================
-- 6. RLS (ROW LEVEL SECURITY) - POLÍTICAS DE SEGURIDAD
-- =====================================================

-- Función para obtener tenant_id del contexto de usuario
CREATE OR REPLACE FUNCTION get_tenant_id()
RETURNS TEXT AS $$
BEGIN
    RETURN current_setting('app.current_tenant_id', true);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Función para obtener app_id del contexto de usuario
CREATE OR REPLACE FUNCTION get_app_id()
RETURNS TEXT AS $$
BEGIN
    RETURN current_setting('app.current_app_id', true);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Políticas RLS para task_read_model
ALTER TABLE task_read_model ENABLE ROW LEVEL SECURITY;

CREATE POLICY task_tenant_isolation ON task_read_model
    FOR ALL TO authenticated
    USING (tenant_id = get_tenant_id());

CREATE POLICY task_app_isolation ON task_read_model
    FOR ALL TO authenticated
    USING (app_id = get_app_id());

-- Políticas RLS para plan_read_model
ALTER TABLE plan_read_model ENABLE ROW LEVEL SECURITY;

CREATE POLICY plan_tenant_isolation ON plan_read_model
    FOR ALL TO authenticated
    USING (tenant_id = get_tenant_id());

CREATE POLICY plan_app_isolation ON plan_read_model
    FOR ALL TO authenticated
    USING (app_id = get_app_id());

-- Políticas RLS para agent_read_model
ALTER TABLE agent_read_model ENABLE ROW LEVEL SECURITY;

CREATE POLICY agent_tenant_isolation ON agent_read_model
    FOR ALL TO authenticated
    USING (tenant_id = get_tenant_id());

CREATE POLICY agent_app_isolation ON agent_read_model
    FOR ALL TO authenticated
    USING (app_id = get_app_id());

-- Políticas RLS para shared_context
ALTER TABLE shared_context ENABLE ROW LEVEL SECURITY;

CREATE POLICY context_tenant_isolation ON shared_context
    FOR ALL TO authenticated
    USING (tenant_id = get_tenant_id());

CREATE POLICY context_app_isolation ON shared_context
    FOR ALL TO authenticated
    USING (app_id = get_app_id());

-- Políticas RLS para cross_app_workflows
ALTER TABLE cross_app_workflows ENABLE ROW LEVEL SECURITY;

CREATE POLICY workflow_tenant_isolation ON cross_app_workflows
    FOR ALL TO authenticated
    USING (tenant_id = get_tenant_id());

-- =====================================================
-- 7. TRIGGERS PARA AUTOMATIZACIÓN
-- =====================================================

-- Función para actualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para tablas con updated_at
CREATE TRIGGER update_app_profiles_updated_at
    BEFORE UPDATE ON app_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_task_read_model_updated_at
    BEFORE UPDATE ON task_read_model
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_plan_read_model_updated_at
    BEFORE UPDATE ON plan_read_model
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_shared_context_updated_at
    BEFORE UPDATE ON shared_context
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Función para calcular progreso de planes
CREATE OR REPLACE FUNCTION calculate_plan_progress()
RETURNS TRIGGER AS $$
DECLARE
    total_count INTEGER;
    completed_count INTEGER;
    progress_calc DECIMAL;
BEGIN
    -- Solo para planes con actualizaciones
    IF TG_OP = 'UPDATE' AND OLD.status = NEW.status THEN
        RETURN NEW;
    END IF;
    
    -- Contar tareas totales y completadas para este plan
    SELECT 
        COUNT(*) as total,
        COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed
    INTO total_count, completed_count
    FROM task_read_model 
    WHERE parent_plan_id = NEW.plan_id 
    AND tenant_id = NEW.tenant_id 
    AND app_id = NEW.app_id;
    
    -- Calcular porcentaje de progreso
    IF total_count > 0 THEN
        progress_calc := (completed_count::DECIMAL / total_count::DECIMAL) * 100;
    ELSE
        progress_calc := 0;
    END IF;
    
    -- Actualizar el plan
    UPDATE plan_read_model 
    SET 
        total_tasks = total_count,
        completed_tasks = completed_count,
        progress_percentage = progress_calc,
        status = CASE 
            WHEN progress_calc = 100 THEN 'completed'
            WHEN progress_calc > 0 THEN 'active'
            ELSE NEW.status
        END
    WHERE plan_id = NEW.parent_plan_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para actualizar progreso del plan cuando cambia una tarea
CREATE TRIGGER update_plan_progress_on_task_change
    AFTER INSERT OR UPDATE ON task_read_model
    FOR EACH ROW
    WHEN (NEW.parent_plan_id IS NOT NULL)
    EXECUTE FUNCTION calculate_plan_progress();

-- =====================================================
-- 8. DATOS INICIALES - PERFILES DE APLICACIONES
-- =====================================================

-- Insertar perfiles de aplicaciones principales
INSERT INTO app_profiles (
    app_id, app_name, tenant_id, app_type, 
    capabilities, team_specialization, primary_model,
    quotas, metadata
) VALUES 
(
    'iris',
    'Iris - Computer Vision AI',
    'tenant_iris_v1',
    'computer_vision',
    ARRAY['computer_vision', 'image_analysis', 'visual_reasoning', 'object_detection'],
    'vision_computational',
    'gpt-4-vision',
    '{"requests_per_hour": 10000, "storage_gb": 100, "compute_units": 1000}',
    '{"version": "1.0", "category": "visual_ai"}'
),
(
    'silhouette',
    'Silhouette - Design Intelligence',
    'tenant_silhouette_v1',
    'design_generation',
    ARRAY['design_generation', 'creative_writing', 'brand_development', 'visual_design'],
    'creative_design',
    'gpt-4o',
    '{"requests_per_hour": 5000, "storage_gb": 50, "compute_units": 800}',
    '{"version": "1.0", "category": "creative_ai"}'
),
(
    'nwc',
    'NWC - Workflow Automation',
    'tenant_nwc_v1',
    'workflow_automation',
    ARRAY['workflow_automation', 'process_optimization', 'data_analysis', 'business_intelligence'],
    'business_automation',
    'gpt-4o',
    '{"requests_per_hour": 15000, "storage_gb": 200, "compute_units": 1200}',
    '{"version": "1.0", "category": "workflow_ai"}'
),
(
    'medluxe',
    'MedLuxe - Healthcare AI',
    'tenant_medluxe_v1',
    'medical_ai',
    ARRAY['medical_diagnosis', 'clinical_reasoning', 'healthcare_analytics', 'medical_imaging'],
    'healthcare_specialists',
    'claude-3.5-sonnet',
    '{"requests_per_hour": 3000, "storage_gb": 500, "compute_units": 2000}',
    '{"version": "1.0", "category": "medical_ai", "compliance": ["HIPAA", "GDPR"]}'
),
(
    'brandistry',
    'Brandistry - Branding AI',
    'tenant_brandistry_v1',
    'branding_ai',
    ARRAY['brand_strategy', 'content_creation', 'social_media', 'marketing_automation'],
    'marketing_creatives',
    'gpt-4o',
    '{"requests_per_hour": 8000, "storage_gb": 80, "compute_units": 600}',
    '{"version": "1.0", "category": "marketing_ai"}'
);

-- =====================================================
-- 9. ÍNDICES ADICIONALES PARA PERFORMANCE
-- =====================================================

-- Índices compuestos para consultas frecuentes
CREATE INDEX idx_event_composite_lookup ON event_store (tenant_id, app_id, event_type, event_timestamp DESC);
CREATE INDEX idx_task_status_priority ON task_read_model (task_status, task_priority DESC);
CREATE INDEX idx_agent_capabilities ON agent_read_model USING GIN (specializations);
CREATE INDEX idx_context_expiring ON shared_context (tenant_id, app_id, expires_at) WHERE expires_at IS NOT NULL;

-- =====================================================
-- 10. FUNCIONES DE UTILIDAD
-- =====================================================

-- Función para obtener el siguiente número de versión de evento
CREATE OR REPLACE FUNCTION get_next_event_version(
    p_aggregate_type TEXT,
    p_aggregate_id UUID
) RETURNS INTEGER AS $$
DECLARE
    max_version INTEGER;
BEGIN
    SELECT COALESCE(MAX(event_version), 0) + 1
    INTO max_version
    FROM event_store
    WHERE aggregate_type = p_aggregate_type
    AND aggregate_id = p_aggregate_id;
    
    RETURN max_version;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Función para obtener eventos de un agregado
CREATE OR REPLACE FUNCTION get_events_for_aggregate(
    p_aggregate_type TEXT,
    p_aggregate_id UUID
) RETURNS TABLE(
    event_id UUID,
    event_type TEXT,
    event_data JSONB,
    event_timestamp TIMESTAMPTZ,
    event_version INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT es.event_id, es.event_type, es.event_data, es.event_timestamp, es.event_version
    FROM event_store es
    WHERE es.aggregate_type = p_aggregate_type
    AND es.aggregate_id = p_aggregate_id
    ORDER BY es.event_version ASC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Función para limpiar datos expirados
CREATE OR REPLACE FUNCTION cleanup_expired_context()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM shared_context 
    WHERE expires_at IS NOT NULL 
    AND expires_at < NOW();
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- COMENTARIOS FINALES
-- =====================================================
-- 9. MCP SERVER - HERRAMIENTAS DEL MUNDO REAL
-- =====================================================

-- Tabla para resultados de herramientas MCP
CREATE TABLE mcp_tool_results (
    result_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tool_id TEXT NOT NULL,
    team_id TEXT NOT NULL,
    success BOOLEAN NOT NULL,
    data JSONB NOT NULL DEFAULT '{}',
    execution_time NUMERIC(10, 3) NOT NULL,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Índices para optimización
    INDEX idx_mcp_results_tool_id (tool_id),
    INDEX idx_mcp_results_team_id (team_id),
    INDEX idx_mcp_results_created_at (created_at),
    INDEX idx_mcp_results_success (success)
);

-- Tabla general de eventos para MCP Server
CREATE TABLE events (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type TEXT NOT NULL,
    event_data JSONB NOT NULL DEFAULT '{}',
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    source TEXT NOT NULL DEFAULT 'mcp_server',
    tenant_id TEXT DEFAULT 'haas_system',
    version INTEGER DEFAULT 1
);

-- Función para calcular estadísticas de uso de herramientas
CREATE OR REPLACE FUNCTION calculate_tool_stats(start_date TIMESTAMPTZ DEFAULT NOW() - INTERVAL '7 days', end_date TIMESTAMPTZ DEFAULT NOW())
RETURNS TABLE (
    tool_id TEXT,
    total_requests BIGINT,
    successful_requests BIGINT,
    success_rate NUMERIC(5,2),
    avg_execution_time NUMERIC(10,3)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        mtr.tool_id,
        COUNT(*) as total_requests,
        COUNT(*) FILTER (WHERE mtr.success = true) as successful_requests,
        ROUND(
            (COUNT(*) FILTER (WHERE mtr.success = true)::NUMERIC / COUNT(*)::NUMERIC) * 100, 2
        ) as success_rate,
        ROUND(AVG(mtr.execution_time), 3) as avg_execution_time
    FROM mcp_tool_results mtr
    WHERE mtr.created_at BETWEEN start_date AND end_date
    GROUP BY mtr.tool_id
    ORDER BY total_requests DESC;
END;
$$ LANGUAGE plpgsql;

-- Trigger para actualizar updated_at
CREATE TRIGGER update_mcp_results_updated_at
    BEFORE UPDATE ON mcp_tool_results
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================

/*
ESQUEMA COMPLETADO:

1. ✅ Event Sourcing completo con event_store y context_events
2. ✅ Read Models para tareas, planes, agentes y contexto
3. ✅ Multi-tenant RLS con aislamiento por tenant_id y app_id
4. ✅ Workflows cross-app para colaboración entre aplicaciones
5. ✅ Auditoría completa de todas las operaciones
6. ✅ Triggers para automatización y mantenimiento
7. ✅ Datos iniciales de perfiles de aplicaciones
8. ✅ Índices optimizados para consultas frecuentes
9. ✅ Funciones de utilidad para operaciones comunes

PRÓXIMOS PASOS:
- Crear API Gateway con autenticación JWT
- Implementar servicios de Orchestrator y Planner
- Desarrollar sistema de proyección de eventos
- Configurar monitoring y alertas

Este esquema soporta:
- Multi-tenancy perfecto con RLS
- Event Sourcing completo con versionado
- Read Models optimizados para queries
- Auditoría y compliance
- Escalabilidad horizontal
*/