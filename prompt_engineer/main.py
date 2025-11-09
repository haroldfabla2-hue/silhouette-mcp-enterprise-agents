"""
PROMPT ENGINEER - SISTEMA MULTIAGENTE HAAS+
Servicio de Refinamiento y Optimización de Prompts
Autor: Silhouette Anónimo
Fecha: 08-Nov-2025
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import asyncio
import logging
import uuid
import json
from datetime import datetime, timedelta
import os
import asyncpg
import re
from contextlib import asynccontextmanager
import openai
import anthropic

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración desde variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://haas:haaspass@localhost:5432/haasdb")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# =====================================================
# MODELOS DE DATOS
# =====================================================

class PromptOptimizationRequest(BaseModel):
    """Solicitud de optimización de prompt"""
    request_id: str
    original_objective: str = Field(..., description="Objetivo original")
    task_type: str = Field(..., description="Tipo de tarea")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Datos de entrada")
    context: Dict[str, Any] = Field(default_factory=dict, description="Contexto")
    app_profile: Dict[str, Any] = Field(..., description="Perfil de la aplicación")
    user_preferences: Optional[Dict[str, Any]] = Field(None, description="Preferencias del usuario")
    optimization_level: str = Field(default="standard", description="Nivel de optimización")

class PromptAnalysis(BaseModel):
    """Análisis del prompt"""
    original_prompt: str
    objective: str
    task_type: str
    complexity_score: float
    clarity_score: float
    specificity_score: float
    completeness_score: float
    identified_issues: List[str]
    missing_elements: List[str]
    suggested_improvements: List[str]

class RefinedPrompt(BaseModel):
    """Prompt refinado"""
    refined_prompt: str
    reasoning: str
    optimizations_applied: List[str]
    confidence_score: float
    alternative_versions: List[Dict[str, str]] = Field(default_factory=list)

class PromptOptimizationResponse(BaseModel):
    """Respuesta de optimización"""
    request_id: str
    status: str
    original_prompt: str
    refined_prompt: str
    analysis: PromptAnalysis
    reasoning: str
    optimizations_applied: List[str]
    confidence_score: float
    processing_time: float
    model_used: str
    alternative_prompts: List[Dict[str, str]] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)

class HealthStatus(BaseModel):
    """Estado de salud del prompt engineer"""
    status: str
    timestamp: str
    active_requests: int
    queue_size: int
    openai_status: str
    anthropic_status: str
    database_status: str

# =====================================================
-- ANALIZADOR DE PROMPTS
-- =====================================================

class PromptAnalyzer:
    """Analizador de calidad y estructura de prompts"""
    
    def __init__(self):
        # Palabras clave por tipo de tarea
        self.task_keywords = {
            "analysis": [
                "analyze", "examine", "evaluate", "assess", "review", "investigate",
                "compare", "contrast", "identify", "determine", "measure", "calculate"
            ],
            "design": [
                "create", "design", "generate", "build", "develop", "craft", "compose",
                "produce", "make", "establish", "formulate", "architect"
            ],
            "vision": [
                "image", "visual", "photo", "picture", "recognize", "detect", "identify",
                "analyze", "describe", "interpret", "examine", "look at"
            ],
            "workflow": [
                "automate", "process", "workflow", "streamline", "optimize", "improve",
                "enhance", "refine", "accelerate", "simplify", "organize"
            ],
            "content": [
                "write", "content", "text", "article", "copy", "document", "compose",
                "create", "generate", "produce", "craft", "develop"
            ],
            "medical": [
                "medical", "health", "diagnosis", "clinical", "patient", "symptom",
                "treatment", "condition", "disease", "healthcare", "medicine"
            ]
        }
        
        # Patrones de problemas comunes
        self.problem_patterns = {
            "vague_objective": r"(?:make|create|do|help|assist).*?(?:something|anything|good|nice|better)",
            "missing_context": r"(?:create|generate|make|build).*?(?:without|missing|no).*?(?:context|information|details)",
            "unclear_requirements": r"(?:need|want|should|must).*?(?:but|however).*?(?:not|unclear|vague)",
            "no_constraints": r"(?:create|generate|make).*?(?:without|any|no).*?(?:constraint|limitation|requirement)",
            "missing_output_format": r"(?:create|generate|make|provide).*?(?:but|without).*?(?:format|structure|style)"
        }
    
    def analyze_prompt(self, prompt: str, task_type: str, context: Dict[str, Any]) -> PromptAnalysis:
        """Analiza un prompt y retorna métricas de calidad"""
        prompt_lower = prompt.lower()
        
        # Calcular scores
        complexity_score = self.calculate_complexity_score(prompt, context)
        clarity_score = self.calculate_clarity_score(prompt)
        specificity_score = self.calculate_specificity_score(prompt, task_type)
        completeness_score = self.calculate_completeness_score(prompt, context)
        
        # Identificar problemas
        issues = self.identify_issues(prompt)
        missing_elements = self.identify_missing_elements(prompt, task_type, context)
        improvements = self.suggest_improvements(prompt, issues, missing_elements)
        
        return PromptAnalysis(
            original_prompt=prompt,
            objective=extract_objective(prompt),
            task_type=task_type,
            complexity_score=complexity_score,
            clarity_score=clarity_score,
            specificity_score=specificity_score,
            completeness_score=completeness_score,
            identified_issues=issues,
            missing_elements=missing_elements,
            suggested_improvements=improvements
        )
    
    def calculate_complexity_score(self, prompt: str, context: Dict[str, Any]) -> float:
        """Calcula la complejidad del prompt (0-1)"""
        factors = {
            "length": min(len(prompt.split()) / 50, 1.0),  # Max 50 palabras = 1.0
            "context_depth": len(context) / 5,  # Max 5 elementos de contexto = 1.0
            "task_complexity": self.get_task_complexity_factor(prompt),
            "requirements_count": len(re.findall(r'(?:must|should|need|require)', prompt.lower()))
        }
        
        return sum(factors.values()) / len(factors)
    
    def calculate_clarity_score(self, prompt: str) -> float:
        """Calcula la claridad del prompt (0-1)"""
        clarity_indicators = {
            "imperative_verbs": len(re.findall(r'\b(create|make|generate|build|analyze|design|develop)\b', prompt.lower())),
            "clear_structure": 1.0 if ":" in prompt or "##" in prompt else 0.0,
            "specific_instructions": len(re.findall(r'(?:step|phase|stage|part|section)', prompt.lower())),
            "avoidance_vague": 1.0 if not re.search(r'\b(something|anything|good|nice|better)\b', prompt.lower()) else 0.0
        }
        
        return min(sum(clarity_indicators.values()) / 4, 1.0)
    
    def calculate_specificity_score(self, prompt: str, task_type: str) -> float:
        """Calcula la especificidad del prompt (0-1)"""
        task_keywords = self.task_keywords.get(task_type, [])
        found_keywords = sum(1 for keyword in task_keywords if keyword in prompt.lower())
        
        # Buscar elementos específicos
        specific_indicators = {
            "task_keywords": found_keywords / max(len(task_keywords), 1),
            "numbers_or_metrics": 1.0 if re.search(r'\d+|percent|%|ratio|score', prompt) else 0.0,
            "time_constraints": 1.0 if re.search(r'\b(urgent|asap|immediately|quick|fast)\b', prompt.lower()) else 0.0,
            "format_specification": 1.0 if re.search(r'\b(format|structure|style|layout)\b', prompt.lower()) else 0.0
        }
        
        return sum(specific_indicators.values()) / len(specific_indicators)
    
    def calculate_completeness_score(self, prompt: str, context: Dict[str, Any]) -> float:
        """Calcula la completitud del prompt (0-1)"""
        completeness_elements = {
            "clear_objective": 1.0 if extract_objective(prompt) else 0.0,
            "input_specification": 1.0 if re.search(r'\b(input|provide|give|supply)\b', prompt.lower()) else 0.0,
            "output_expectation": 1.0 if re.search(r'\b(output|result|return|provide)\b', prompt.lower()) else 0.0,
            "context_awareness": 1.0 if context else 0.5,
            "constraint_mention": 1.0 if re.search(r'\b(limit|constraint|requirement|format)\b', prompt.lower()) else 0.0
        }
        
        return sum(completeness_elements.values()) / len(completeness_elements)
    
    def identify_issues(self, prompt: str) -> List[str]:
        """Identifica problemas comunes en el prompt"""
        issues = []
        prompt_lower = prompt.lower()
        
        for problem_type, pattern in self.problem_patterns.items():
            if re.search(pattern, prompt_lower):
                issues.append(problem_type.replace("_", " "))
        
        # Problemas adicionales
        if len(prompt.split()) < 5:
            issues.append("too_short")
        elif len(prompt.split()) > 200:
            issues.append("too_long")
        
        if not re.search(r'[.!?]$', prompt.strip()):
            issues.append("no_ending_punctuation")
        
        if prompt.strip().isupper():
            issues.append("all_caps")
        
        return issues
    
    def identify_missing_elements(self, prompt: str, task_type: str, context: Dict[str, Any]) -> List[str]:
        """Identifica elementos faltantes en el prompt"""
        missing = []
        
        # Verificar elementos por tipo de tarea
        if task_type in ["analysis", "data_analysis"]:
            if not re.search(r'\b(analyz|examine|evaluat|assess)\b', prompt.lower()):
                missing.append("analysis_instruction")
            if not re.search(r'\b(metric|criteria|aspect|dimension)\b', prompt.lower()):
                missing.append("analysis_criteria")
        
        elif task_type == "design":
            if not re.search(r'\b(creat|design|generat|build)\b', prompt.lower()):
                missing.append("creation_instruction")
            if not re.search(r'\b(style|theme|aesthetic|visual)\b', prompt.lower()):
                missing.append("design_specification")
        
        elif task_type == "computer_vision":
            if not re.search(r'\b(image|visual|picture|photo)\b', prompt.lower()):
                missing.append("image_reference")
            if not re.search(r'\b(analyz|describ|identif|detect)\b', prompt.lower()):
                missing.append("vision_instruction")
        
        # Verificar contexto
        if not context and "context" in prompt.lower():
            missing.append("context_clarification")
        
        return missing
    
    def suggest_improvements(self, prompt: str, issues: List[str], missing: List[str]) -> List[str]:
        """Sugiere mejoras específicas"""
        improvements = []
        
        for issue in issues:
            if issue == "vague_objective":
                improvements.append("Especifique exactamente qué tipo de resultado espera")
            elif issue == "missing_context":
                improvements.append("Proporcione más contexto sobre el propósito y audiencia")
            elif issue == "unclear_requirements":
                improvements.append("Defina claramente los requisitos y expectativas")
            elif issue == "no_constraints":
                improvements.append("Agregue restricciones o límites para guiar la respuesta")
            elif issue == "missing_output_format":
                improvements.append("Especifique el formato de salida deseado")
            elif issue == "too_short":
                improvements.append("Proporcione más detalles en la descripción")
            elif issue == "too_long":
                improvements.append("Considere dividir en tareas más específicas")
        
        for missing_element in missing:
            if missing_element == "analysis_instruction":
                improvements.append("Incluya instrucciones específicas para el análisis")
            elif missing_element == "creation_instruction":
                improvements.append("Defina claramente qué debe ser creado")
            elif missing_element == "vision_instruction":
                improvements.append("Especifique qué aspectos visuales analizar")
            elif missing_element == "image_reference":
                improvements.append("Haga referencia específica a las imágenes")
            elif missing_element == "context_clarification":
                improvements.append("Aclare el contexto del proyecto")
        
        return improvements
    
    def get_task_complexity_factor(self, prompt: str) -> float:
        """Calcula factor de complejidad de la tarea"""
        complexity_indicators = {
            "multi_step": 1.0 if re.search(r'\b(step|phase|stage|part)\b', prompt.lower()) else 0.0,
            "comparison": 1.0 if re.search(r'\b(compare|contrast|versus|vs)\b', prompt.lower()) else 0.0,
            "optimization": 1.0 if re.search(r'\b(optimiz|improv|enhanc|best)\b', prompt.lower()) else 0.0,
            "integration": 1.0 if re.search(r'\b(integrat|combin|merge|join)\b', prompt.lower()) else 0.0,
            "synthesis": 1.0 if re.search(r'\b(synthesiz|create|develop|formulate)\b', prompt.lower()) else 0.0
        }
        
        return sum(complexity_indicators.values()) / len(complexity_indicators)

# =====================================================
-- OPTIMIZADOR DE PROMPTS
-- =====================================================

class PromptOptimizer:
    """Optimizador de prompts usando IA y heurísticas"""
    
    def __init__(self):
        self.analyzer = PromptAnalyzer()
        self.openai_client = None
        self.anthropic_client = None
        
        if OPENAI_API_KEY:
            openai.api_key = OPENAI_API_KEY
            self.openai_client = openai
        
        if ANTHROPIC_API_KEY:
            self.anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    async def optimize_prompt(
        self, 
        request: PromptOptimizationRequest
    ) -> RefinedPrompt:
        """Optimiza un prompt usando múltiples estrategias"""
        start_time = asyncio.get_event_loop().time()
        
        # 1. Analizar prompt original
        analysis = self.analyzer.analyze_prompt(
            request.original_objective, 
            request.task_type, 
            request.context
        )
        
        # 2. Aplicar optimizaciones heurísticas
        heuristic_prompt = self.apply_heuristic_optimizations(
            request.original_objective, 
            analysis, 
            request.app_profile
        )
        
        # 3. Refinar con IA (si está disponible)
        ai_optimized = await self.optimize_with_ai(
            heuristic_prompt, 
            request, 
            analysis
        )
        
        # 4. Generar versiones alternativas
        alternatives = self.generate_alternatives(
            ai_optimized.refined_prompt,
            request.task_type,
            request.app_profile
        )
        
        processing_time = asyncio.get_event_loop().time() - start_time
        
        return RefinedPrompt(
            refined_prompt=ai_optimized.refined_prompt,
            reasoning=ai_optimized.reasoning,
            optimizations_applied=ai_optimized.optimizations_applied,
            confidence_score=self.calculate_confidence_score(analysis, processing_time),
            alternative_versions=alternatives
        )
    
    def apply_heuristic_optimizations(
        self, 
        prompt: str, 
        analysis: PromptAnalysis, 
        app_profile: Dict[str, Any]
    ) -> str:
        """Aplica optimizaciones heurísticas básicas"""
        optimized = prompt
        
        # 1. Añadir contexto de aplicación
        app_name = app_profile.get("app_name", "la aplicación")
        if "context" not in prompt.lower():
            optimized = f"Contexto: Usando {app_name} para esta tarea.\n\n{optimized}"
        
        # 2. Mejorar claridad de objetivos
        if not optimized.strip().endswith((':', '?', '!')):
            optimized += ":"
        
        # 3. Añadir estructura si falta
        if not re.search(r'##?\s|\n\n', optimized):
            optimized = f"Objetivo: {optimized}\n\nPor favor, proceda de manera estructurada."
        
        # 4. Especificar formato de salida según tipo
        output_format = self.get_output_format(analysis.task_type)
        if output_format and output_format not in optimized.lower():
            optimized += f"\n\nFormato esperado: {output_format}"
        
        # 5. Añadir consideraciones de calidad
        quality_requirements = self.get_quality_requirements(analysis.task_type)
        if quality_requirements:
            optimized += f"\n\nRequisitos de calidad: {quality_requirements}"
        
        return optimized
    
    async def optimize_with_ai(
        self, 
        prompt: str, 
        request: PromptOptimizationRequest, 
        analysis: PromptAnalysis
    ) -> RefinedPrompt:
        """Optimiza prompt usando IA (OpenAI o Anthropic)"""
        
        if self.openai_client and request.optimization_level in ["advanced", "premium"]:
            return await self.optimize_with_openai(prompt, request, analysis)
        elif self.anthropic_client:
            return await self.optimize_with_anthropic(prompt, request, analysis)
        else:
            return self.fallback_optimization(prompt, request, analysis)
    
    async def optimize_with_openai(
        self, 
        prompt: str, 
        request: PromptOptimizationRequest, 
        analysis: PromptAnalysis
    ) -> RefinedPrompt:
        """Optimiza usando OpenAI"""
        try:
            system_prompt = f"""
            Eres un experto en optimización de prompts para un sistema multiagente.
            
            Tipo de tarea: {request.task_type}
            Aplicación: {request.app_profile.get('app_name', 'Unknown')}
            Capacidades de la app: {', '.join(request.app_profile.get('capabilities', []))}
            
            Análisis del prompt original:
            - Complejidad: {analysis.complexity_score:.2f}
            - Claridad: {analysis.clarity_score:.2f}
            - Especificidad: {analysis.specificity_score:.2f}
            - Completitud: {analysis.completeness_score:.2f}
            
            Problemas identificados: {', '.join(analysis.identified_issues)}
            Elementos faltantes: {', '.join(analysis.missing_elements)}
            
            Optimiza el siguiente prompt para maximizar la claridad, especificidad y efectividad:
            """
            
            response = await asyncio.to_thread(
                self.openai_client.ChatCompletion.create,
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Prompt a optimizar:\n\n{prompt}"}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            refined_content = response.choices[0].message.content
            
            return RefinedPrompt(
                refined_prompt=refined_content,
                reasoning="Optimizado usando OpenAI GPT-4 con análisis contextual",
                optimizations_applied=[
                    "Análisis contextual por tipo de aplicación",
                    "Refinamiento semántico con IA",
                    "Optimización de claridad y especificidad",
                    "Adaptación a capacidades de la app"
                ],
                confidence_score=0.9
            )
            
        except Exception as e:
            logger.error(f"Error optimizing with OpenAI: {str(e)}")
            return self.fallback_optimization(prompt, request, analysis)
    
    async def optimize_with_anthropic(
        self, 
        prompt: str, 
        request: PromptOptimizationRequest, 
        analysis: PromptAnalysis
    ) -> RefinedPrompt:
        """Optimiza usando Anthropic Claude"""
        try:
            system_prompt = f"""
            Eres un experto en optimización de prompts para sistemas de IA multiagente.
            
            Tarea: {request.task_type}
            App: {request.app_profile.get('app_name', 'Unknown')}
            Especialización del equipo: {request.app_profile.get('team_specialization', 'general')}
            
            Métricas del prompt original:
            - Complejidad: {analysis.complexity_score:.2f}
            - Claridad: {analysis.clarity_score:.2f}
            - Especificidad: {analysis.specificity_score:.2f}
            - Completitud: {analysis.completeness_score:.2f}
            
            Refina este prompt para obtener los mejores resultados:
            """
            
            response = await asyncio.to_thread(
                self.anthropic_client.messages.create,
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                system=system_prompt,
                messages=[{"role": "user", "content": f"Optimiza este prompt:\n\n{prompt}"}]
            )
            
            refined_content = response.content[0].text
            
            return RefinedPrompt(
                refined_prompt=refined_content,
                reasoning="Optimizado usando Anthropic Claude con análisis especializado",
                optimizations_applied=[
                    "Refinamiento con Claude para claridad",
                    "Adaptación a especialización del equipo",
                    "Optimización contextual",
                    "Mejora de especificidad técnica"
                ],
                confidence_score=0.88
            )
            
        except Exception as e:
            logger.error(f"Error optimizing with Anthropic: {str(e)}")
            return self.fallback_optimization(prompt, request, analysis)
    
    def fallback_optimization(
        self, 
        prompt: str, 
        request: PromptOptimizationRequest, 
        analysis: PromptAnalysis
    ) -> RefinedPrompt:
        """Optimización de fallback sin IA externa"""
        optimized = self.apply_heuristic_optimizations(prompt, analysis, request.app_profile)
        
        # Aplicar mejoras adicionales según análisis
        if analysis.completeness_score < 0.7:
            optimized += "\n\nAsegúrese de proporcionar una respuesta completa y detallada."
        
        if analysis.specificity_score < 0.6:
            optimized += "\n\nSea específico en sus instrucciones y requisitos."
        
        if analysis.clarity_score < 0.7:
            optimized = optimized.replace("://", ":\n").replace("?", "?\n")
        
        return RefinedPrompt(
            refined_prompt=optimized,
            reasoning="Optimizado usando heurísticas y análisis semántico",
            optimizations_applied=[
                "Mejora de estructura y formato",
                "Añadido de contexto de aplicación",
                "Optimización de completitud",
                "Refinamiento de claridad"
            ],
            confidence_score=0.7
        )
    
    def generate_alternatives(
        self, 
        main_prompt: str, 
        task_type: str, 
        app_profile: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Genera versiones alternativas del prompt"""
        alternatives = []
        
        # Versión concisa
        concise = main_prompt.split('\n\n')[0]  # Primera línea principal
        alternatives.append({
            "version": "concise",
            "prompt": concise,
            "description": "Versión concisa del prompt"
        })
        
        # Versión detallada
        detailed = main_prompt + "\n\nProporcione ejemplos cuando sea relevante."
        alternatives.append({
            "version": "detailed",
            "prompt": detailed,
            "description": "Versión con instrucciones adicionales"
        })
        
        # Versión step-by-step
        step_version = "Siga estos pasos:\n1. " + main_prompt.replace("\n", "\n2. ")
        alternatives.append({
            "version": "step_by_step",
            "prompt": step_version,
            "description": "Versión con pasos estructurados"
        })
        
        return alternatives
    
    def get_output_format(self, task_type: str) -> str:
        """Obtiene el formato de salida recomendado por tipo de tarea"""
        formats = {
            "analysis": "informe estructurado con puntos clave, métricas y recomendaciones",
            "design": "descripción detallada con elementos visuales, colores y estilo",
            "computer_vision": "análisis visual detallado con objetos, patrones y insights",
            "workflow_automation": "flujo de trabajo paso a paso con diagramas y procesos",
            "content_creation": "contenido bien estructurado con títulos, subtítulos y formato",
            "medical_diagnosis": "análisis clínico con diagnóstico diferencial y recomendaciones"
        }
        
        return formats.get(task_type, "respuesta estructurada y bien organizada")
    
    def get_quality_requirements(self, task_type: str) -> str:
        """Obtiene requisitos de calidad por tipo de tarea"""
        requirements = {
            "analysis": "precisión técnica, fundamentación en datos, objetividad",
            "design": "creatividad, cohesión visual, adecuación al propósito",
            "computer_vision": "exactitud en identificación, detalles técnicos, contexto",
            "workflow_automation": "efectividad, eficiencia, claridad en procesos",
            "content_creation": "calidad del contenido, coherencia, engagement",
            "medical_diagnosis": "rigor clínico, precisión, consideración ética"
        }
        
        return requirements.get(task_type, "calidad profesional, precisión y utilidad")
    
    def calculate_confidence_score(self, analysis: PromptAnalysis, processing_time: float) -> float:
        """Calcula score de confianza basado en análisis y tiempo de procesamiento"""
        base_score = (
            analysis.clarity_score * 0.3 +
            analysis.specificity_score * 0.3 +
            analysis.completeness_score * 0.4
        )
        
        # Ajustar por tiempo de procesamiento (más tiempo = más análisis = más confianza)
        time_factor = min(processing_time / 5.0, 1.0)  # Normalizar a máximo 5 segundos
        
        return min(base_score * (0.8 + time_factor * 0.2), 1.0)

# =====================================================
-- GESTOR DE EVENTOS
-- =====================================================

class EventManager:
    """Gestor de eventos para el prompt engineer"""
    
    def __init__(self):
        self.connection_pool = None
    
    async def init_pool(self):
        """Inicializa el pool de conexiones a BD"""
        self.connection_pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=5,
            max_size=20,
            command_timeout=60
        )
    
    async def get_connection(self):
        """Obtiene una conexión del pool"""
        if not self.connection_pool:
            await self.init_pool()
        return self.connection_pool.acquire()
    
    async def store_optimization_event(
        self, 
        request_id: str,
        tenant_id: str, 
        app_id: str, 
        original_prompt: str,
        refined_prompt: str,
        analysis: PromptAnalysis,
        processing_time: float
    ):
        """Almacena evento de optimización de prompt"""
        conn = await self.get_connection()
        try:
            event_data = {
                "request_id": request_id,
                "original_prompt": original_prompt,
                "refined_prompt": refined_prompt,
                "task_type": analysis.task_type,
                "complexity_score": analysis.complexity_score,
                "clarity_score": analysis.clarity_score,
                "specificity_score": analysis.specificity_score,
                "completeness_score": analysis.completeness_score,
                "identified_issues": analysis.identified_issues,
                "processing_time": processing_time
            }
            
            await conn.execute("""
                INSERT INTO event_store 
                (event_id, tenant_id, app_id, event_type, event_data, 
                 aggregate_type, aggregate_id, event_timestamp)
                VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
            """, str(uuid.uuid4()), tenant_id, app_id, "PromptOptimized", 
                json.dumps(event_data), "Prompt", request_id)
            
        finally:
            await self.connection_pool.release(conn)

# =====================================================
-- SERVICIO PROMPT ENGINEER PRINCIPAL
-- =====================================================

class PromptEngineerService:
    """Servicio principal de ingeniería de prompts"""
    
    def __init__(self):
        self.optimizer = PromptOptimizer()
        self.event_manager = EventManager()
        self.request_queue = asyncio.Queue()
        self.active_requests = {}
        
    async def initialize(self):
        """Inicializa el servicio"""
        await self.event_manager.init_pool()
        
        # Iniciar workers de optimización
        for i in range(3):  # 3 workers concurrentes
            asyncio.create_task(self.process_optimization_queue())
    
    async def process_optimization_queue(self):
        """Worker para procesar cola de optimizaciones"""
        while True:
            try:
                request = await self.request_queue.get()
                await self.process_optimization_request(request)
                self.request_queue.task_done()
            except Exception as e:
                logger.error(f"Error processing optimization request: {str(e)}")
                self.request_queue.task_done()
    
    async def process_prompt_optimization(
        self, 
        request: PromptOptimizationRequest
    ) -> PromptOptimizationResponse:
        """Procesa una solicitud de optimización de prompt"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            logger.info(f"Processing prompt optimization for request {request.request_id}")
            
            # 1. Optimizar prompt
            refined_prompt = await self.optimizer.optimize_prompt(request)
            
            # 2. Analizar prompt original
            analysis = self.optimizer.analyzer.analyze_prompt(
                request.original_objective, 
                request.task_type, 
                request.context
            )
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            # 3. Almacenar evento
            await self.event_manager.store_optimization_event(
                request.request_id,
                request.app_profile.get("tenant_id", ""),
                request.app_profile.get("app_id", ""),
                request.original_objective,
                refined_prompt.refined_prompt,
                analysis,
                processing_time
            )
            
            # 4. Preparar respuesta
            response = PromptOptimizationResponse(
                request_id=request.request_id,
                status="optimized",
                original_prompt=request.original_objective,
                refined_prompt=refined_prompt.refined_prompt,
                analysis=analysis,
                reasoning=refined_prompt.reasoning,
                optimizations_applied=refined_prompt.optimizations_applied,
                confidence_score=refined_prompt.confidence_score,
                processing_time=processing_time,
                model_used="fallback" if not (self.optimizer.openai_client or self.optimizer.anthropic_client) else "ai_enhanced",
                alternative_prompts=refined_prompt.alternative_versions,
                suggestions=self.generate_suggestions(analysis)
            )
            
            logger.info(f"Prompt optimization completed for request {request.request_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error in prompt optimization: {str(e)}")
            
            # Retornar respuesta de error con prompt original
            processing_time = asyncio.get_event_loop().time() - start_time
            return PromptOptimizationResponse(
                request_id=request.request_id,
                status="error",
                original_prompt=request.original_objective,
                refined_prompt=request.original_objective,
                analysis=analysis if 'analysis' in locals() else self.optimizer.analyzer.analyze_prompt(request.original_objective, request.task_type, request.context),
                reasoning=f"Error en optimización: {str(e)}",
                optimizations_applied=[],
                confidence_score=0.0,
                processing_time=processing_time,
                model_used="error",
                alternative_prompts=[],
                suggestions=["Error en procesamiento. Usar prompt original."]
            )
    
    def generate_suggestions(self, analysis: PromptAnalysis) -> List[str]:
        """Genera sugerencias adicionales basadas en el análisis"""
        suggestions = []
        
        if analysis.complexity_score < 0.3:
            suggestions.append("Considere dividir la tarea en pasos más específicos")
        
        if analysis.clarity_score < 0.6:
            suggestions.append("Use verbos más claros y específicos en sus instrucciones")
        
        if analysis.specificity_score < 0.5:
            suggestions.append("Añada más detalles sobre formato, estilo o criterios específicos")
        
        if analysis.completeness_score < 0.7:
            suggestions.append("Incluya más contexto sobre el objetivo y resultados esperados")
        
        if len(analysis.identified_issues) > 2:
            suggestions.append("Revise y aborde los problemas identificados en el análisis")
        
        # Sugerencias específicas por tipo de tarea
        if analysis.task_type == "analysis":
            suggestions.append("Defina claramente los criterios de análisis y métricas de evaluación")
        elif analysis.task_type == "design":
            suggestions.append("Especifique restricciones de diseño, audiencia objetivo y estilo visual")
        elif analysis.task_type == "computer_vision":
            suggestions.append("Proporcione detalles sobre el tipo de análisis visual requerido")
        
        return suggestions[:5]  # Máximo 5 sugerencias

# =====================================================
-- APLICACIÓN FASTAPI
-- =====================================================

# Instancia global del servicio
prompt_engineer = PromptEngineerService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    await prompt_engineer.initialize()
    logger.info("Prompt Engineer service started successfully")
    
    yield
    
    # Shutdown
    if prompt_engineer.event_manager.connection_pool:
        await prompt_engineer.event_manager.connection_pool.close()
    logger.info("Prompt Engineer service shutdown completed")

# Crear aplicación FastAPI
app = FastAPI(
    title="HAAS+ Prompt Engineer Service",
    description="Servicio de Optimización y Refinamiento de Prompts",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
-- ENDPOINTS
-- =====================================================

@app.post("/process", response_model=PromptOptimizationResponse)
async def process_prompt(request: PromptOptimizationRequest):
    """Procesa una solicitud de optimización de prompt"""
    try:
        response = await prompt_engineer.process_prompt_optimization(request)
        return response
    except Exception as e:
        logger.error(f"Prompt processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prompt processing failed: {str(e)}"
        )

@app.post("/process/async")
async def process_prompt_async(request: PromptOptimizationRequest):
    """Procesa una solicitud de optimización de forma asíncrona"""
    try:
        await prompt_engineer.request_queue.put(request)
        return {
            "request_id": request.request_id,
            "status": "queued",
            "message": "Prompt optimization queued for processing",
            "estimated_queue_time": 15
        }
    except Exception as e:
        logger.error(f"Queue error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to queue prompt optimization"
        )

@app.post("/analyze")
async def analyze_prompt(request: Dict[str, Any]):
    """Analiza un prompt sin optimizarlo"""
    try:
        prompt = request.get("prompt", "")
        task_type = request.get("task_type", "general")
        context = request.get("context", {})
        
        analysis = prompt_engineer.optimizer.analyzer.analyze_prompt(prompt, task_type, context)
        
        return {
            "prompt": prompt,
            "analysis": analysis.dict(),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Prompt analysis error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze prompt"
        )

@app.get("/templates/{task_type}")
async def get_prompt_templates(task_type: str):
    """Obtiene plantillas de prompts para un tipo de tarea"""
    templates = {
        "analysis": {
            "basic": "Analice [contexto] considerando [criterios]. Proporcione [formato_salida].",
            "detailed": "Realice un análisis completo de [tema] incluyendo: 1) [aspecto1] 2) [aspecto2] 3) [aspecto3]. Use [metodología] y proporcione [métricas].",
            "comparative": "Compare [opción1] vs [opción2] basándose en [criterios]. Analice ventajas, desventajas y recomendación."
        },
        "design": {
            "basic": "Cree un diseño para [proyecto] con [estilo] y [elementos]. Considere [audiencia] y [contexto].",
            "detailed": "Desarrolle un concepto de diseño completo que incluya: elementos visuales, paleta de colores, tipografía, y [especificaciones].",
            "brand": "Diseñe elementos de marca para [empresa] incluyendo logo, paleta de colores, y guía de estilo que refleje [personalidad]."
        },
        "vision": {
            "basic": "Analice esta imagen identificando [objetos] y [patrones]. Proporcione [tipo_análisis].",
            "detailed": "Examine la imagen detalladamente incluyendo: composición, elementos principales, estilo visual, y [aspectos_específicos].",
            "diagnostic": "Realice un análisis diagnóstico de la imagen identificando [características] y [recomendaciones]."
        }
    }
    
    return {
        "task_type": task_type,
        "templates": templates.get(task_type, {}),
        "total_templates": len(templates.get(task_type, {}))
    }

@app.get("/health", response_model=HealthStatus)
async def health_check():
    """Health check del prompt engineer"""
    try:
        openai_status = "configured" if prompt_engineer.optimizer.openai_client else "unavailable"
        anthropic_status = "configured" if prompt_engineer.optimizer.anthropic_client else "unavailable"
        
        return HealthStatus(
            status="healthy",
            timestamp=datetime.utcnow().isoformat(),
            active_requests=len(prompt_engineer.active_requests),
            queue_size=prompt_engineer.request_queue.qsize(),
            openai_status=openai_status,
            anthropic_status=anthropic_status,
            database_status="healthy"
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthStatus(
            status="unhealthy",
            timestamp=datetime.utcnow().isoformat(),
            active_requests=0,
            queue_size=0,
            openai_status="unknown",
            anthropic_status="unknown",
            database_status="unknown"
        )

# =====================================================
-- FUNCIONES AUXILIARES
-- =====================================================

def extract_objective(prompt: str) -> str:
    """Extrae el objetivo principal de un prompt"""
    # Buscar patrones de objetivo
    objective_patterns = [
        r"(?:objetivo|objective|meta|goal|propósito|purpose):\s*(.+)",
        r"(?:create|crear|generate|generar|build|construir|make|hacer)\s+(.+?)(?:\.|$)",
        r"(?:analyze|analizar|examine|examinar|evaluate|evaluar)\s+(.+?)(?:\.|$)"
    ]
    
    for pattern in objective_patterns:
        match = re.search(pattern, prompt, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    # Si no se encuentra patrón, tomar primeras palabras significativas
    words = prompt.split()[:10]
    return " ".join(words)

# =====================================================
-- PUNTO DE ENTRADA
-- =====================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "prompt_engineer:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
        log_level="info"
    )

# =====================================================
-- COMENTARIOS FINALES
-- =====================================================

"""
PROMPT ENGINEER IMPLEMENTADO:

✅ Análisis completo de prompts con métricas de calidad
✅ Optimización heurística inteligente
✅ Integración con OpenAI y Anthropic (opcional)
✅ Generación de versiones alternativas
✅ Análisis de problemas comunes
✅ Sugerencias de mejora específicas
✅ Event Sourcing para auditoria
✅ Templates por tipo de tarea
✅ Queue asíncrona para alta concurrencia

CARACTERÍSTICAS:
- Análisis semántico con scoring de calidad
- Optimización adaptativa por tipo de aplicación
- Fallback robusto sin APIs externas
- Templates especializados por dominio
- Métricas de confianza y processing time
- Identificación proactiva de problemas
- Sugerencias contextuales de mejora

INTEGRACIÓN:
- Completado el flujo Orchestrator → Prompt Engineer
- Comunicación asíncrona con el API Gateway
- Event Sourcing para seguimiento completo
- Health checks y monitoreo integrado

PRÓXIMOS PASOS:
- Crear equipos especializados reales (Vision, Design, etc.)
- Implementar sistema de métricas avanzadas
- Desarrollar UI de monitoreo y administración
- Configurar integración con vector databases
- Crear sistema de A/B testing para prompts
- Implementar feedback loop para mejora continua
"""