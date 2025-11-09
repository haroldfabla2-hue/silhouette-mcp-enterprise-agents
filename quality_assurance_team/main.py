"""
HAAS+ Multi-Agent System - Quality Assurance Team
================================================

Comprehensive quality assurance and testing management team for enterprise-level QA operations.
Implements quality planning, test management, defect tracking, compliance testing, and quality metrics.

Team Structure:
- Test Planning: Test strategy, test planning, resource allocation
- Quality Engineering: Automated testing, manual testing, performance testing
- Compliance Testing: Regulatory compliance, security testing, audit testing
- Defect Management: Bug tracking, root cause analysis, resolution tracking
- Quality Metrics: Quality KPIs, performance monitoring, trend analysis
- Process Improvement: Process optimization, best practices, continuous improvement
- Vendor Quality: Supplier quality, vendor audits, quality agreements
- Customer Quality: Customer satisfaction, quality feedback, issue resolution

Communication Patterns:
- Dynamic communication according to HAAS+ playbook specifications
- Event-driven architecture with message mediation through NOTI hub
- Performatives: REQUEST, INFORM, PROPOSE, ACCEPT, REJECT, HALT, ERROR, ACK, HEARTBEAT
- Back-pressure mechanisms with token bucket rate limiting (P0-P3 priorities)
- Message deduplication using SHA-256 hashes
- Dead Letter Queue handling for failed communications
"""

import asyncio
import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import aiohttp
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import redis.asyncio as redis
import numpy as np
import pandas as pd
from collections import defaultdict, deque

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestType(Enum):
    """Types of testing"""
    FUNCTIONAL = "functional"
    INTEGRATION = "integration"
    SYSTEM = "system"
    ACCEPTANCE = "acceptance"
    PERFORMANCE = "performance"
    SECURITY = "security"
    USABILITY = "usability"
    REGRESSION = "regression"
    EXPLORATORY = "exploratory"
    COMPLIANCE = "compliance"

class DefectSeverity(Enum):
    """Defect severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    TRIVIAL = "trivial"

class QualityStatus(Enum):
    """Quality status indicators"""
    PASS = "pass"
    FAIL = "fail"
    BLOCKED = "blocked"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    RETEST = "retest"

class QualityStandard(Enum):
    """Quality standards and frameworks"""
    ISO_9001 = "iso_9001"
    SIX_SIGMA = "six_sigma"
    LEAN = "lean"
    CMMI = "cmmi"
    AGILE_QA = "agile_qa"
    TDD = "tdd"
    BDD = "bdd"

class Priority(Enum):
    """Priority levels"""
    P0_CRITICAL = "p0_critical"
    P1_HIGH = "p1_high"
    P2_MEDIUM = "p2_medium"
    P3_LOW = "p3_low"

@dataclass
class QualityMetrics:
    """Key quality performance metrics"""
    project_id: str
    test_coverage: float = 0.0
    defect_density: float = 0.0
    pass_rate: float = 0.0
    mean_time_to_resolution: float = 0.0
    customer_satisfaction: float = 0.0
    process_compliance: float = 0.0
    automation_coverage: float = 0.0
    quality_cost: float = 0.0

class TestPlanningAgent:
    """Test planning and strategy specialist"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.test_plans = {}
        self.test_strategies = {}
        self.test_environments = {}
        
    async def create_test_plan(
        self,
        project_name: str,
        test_objectives: List[str],
        test_scope: Dict[str, Any],
        test_types: List[TestType],
        quality_standards: List[QualityStandard],
        resource_requirements: Dict[str, Any],
        timeline: Dict[str, str]
    ) -> Dict[str, Any]:
        """Create comprehensive test plan"""
        try:
            logger.info(f"Creating test plan for project: {project_name}")
            
            # Generate test plan ID
            plan_id = hashlib.sha256(
                f"{project_name}_{datetime.now().isoformat()}".encode()
            ).hexdigest()[:12]
            
            # Test strategy development
            test_strategy = await self._develop_test_strategy(
                test_objectives, test_types, quality_standards
            )
            
            # Test case design
            test_case_design = await self._design_test_cases(
                test_strategy, test_scope
            )
            
            # Test environment planning
            environment_planning = await self._plan_test_environments(
                test_types, resource_requirements
            )
            
            # Risk assessment
            test_risks = await self._assess_test_risks(
                test_strategy, test_scope, resource_requirements
            )
            
            # Resource allocation
            resource_allocation = await self._allocate_test_resources(
                test_strategy, test_case_design, resource_requirements
            )
            
            test_plan_data = {
                "plan_id": plan_id,
                "project_name": project_name,
                "test_objectives": test_objectives,
                "test_scope": test_scope,
                "test_types": [test_type.value for test_type in test_types],
                "quality_standards": [standard.value for standard in quality_standards],
                "resource_requirements": resource_requirements,
                "timeline": timeline,
                "status": "planning",
                "created_date": datetime.now().isoformat(),
                "test_strategy": test_strategy,
                "test_case_design": test_case_design,
                "environment_planning": environment_planning,
                "test_risks": test_risks,
                "resource_allocation": resource_allocation,
                "test_execution_metrics": {
                    "test_cases_planned": 0,
                    "test_cases_executed": 0,
                    "test_cases_passed": 0,
                    "defects_found": 0,
                    "execution_progress": 0.0
                }
            }
            
            # Store test plan
            await self.redis.setex(
                f"test_plan:{plan_id}",
                7776000,  # 90 days
                json.dumps(test_plan_data, default=str)
            )
            
            logger.info(f"Test plan {plan_id} created successfully")
            return test_plan_data
            
        except Exception as e:
            logger.error(f"Error creating test plan: {e}")
            raise
    
    async def manage_test_execution(
        self,
        plan_id: str,
        execution_schedule: List[Dict[str, Any]],
        test_results: List[Dict[str, Any]],
        defect_reports: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Manage test execution process"""
        try:
            logger.info(f"Managing test execution for plan: {plan_id}")
            
            # Get test plan
            plan_data = await self.redis.get(f"test_plan:{plan_id}")
            if not plan_data:
                raise ValueError(f"Test plan {plan_id} not found")
            
            # Test execution analysis
            execution_analysis = await self._analyze_test_execution(
                execution_schedule, test_results
            )
            
            # Defect analysis
            defect_analysis = await self._analyze_defects(
                defect_reports, test_results
            )
            
            # Quality assessment
            quality_assessment = await self._assess_quality_metrics(
                test_results, defect_analysis
            )
            
            # Test coverage analysis
            coverage_analysis = await self._analyze_test_coverage(
                execution_schedule, test_results
            )
            
            execution_management = {
                "execution_id": hashlib.sha256(
                    f"{plan_id}_{datetime.now().isoformat()}".encode()
                ).hexdigest()[:12],
                "plan_id": plan_id,
                "execution_date": datetime.now().isoformat(),
                "execution_schedule": execution_schedule,
                "test_results": test_results,
                "defect_reports": defect_reports,
                "execution_analysis": execution_analysis,
                "defect_analysis": defect_analysis,
                "quality_assessment": quality_assessment,
                "coverage_analysis": coverage_analysis,
                "execution_summary": await self._generate_execution_summary(
                    execution_analysis, quality_assessment
                )
            }
            
            # Store execution management data
            await self.redis.setex(
                f"test_execution:{execution_management['execution_id']}",
                7776000,  # 90 days
                json.dumps(execution_management, default=str)
            )
            
            logger.info(f"Test execution {execution_management['execution_id']} managed successfully")
            return execution_management
            
        except Exception as e:
            logger.error(f"Error managing test execution: {e}")
            raise

class DefectManagementAgent:
    """Defect tracking and resolution specialist"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.defect_tracking = {}
        self.root_cause_analysis = {}
        self.resolution_workflows = {}
        
    async def track_defect(
        self,
        defect_description: str,
        severity: DefectSeverity,
        affected_components: List[str],
        reproduction_steps: List[str],
        expected_behavior: str,
        actual_behavior: str,
        environment_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Track and manage defect"""
        try:
            logger.info(f"Tracking defect: {severity.value} - {defect_description[:50]}...")
            
            # Generate defect ID
            defect_id = hashlib.sha256(
                f"{defect_description}_{datetime.now().isoformat()}".encode()
            ).hexdigest()[:12]
            
            # Defect classification
            defect_classification = await self._classify_defect(
                defect_description, severity, affected_components
            )
            
            # Impact assessment
            impact_assessment = await self._assess_defect_impact(
                severity, affected_components
            )
            
            # Assignment criteria
            assignment_criteria = await self._determine_assignment_criteria(
                defect_classification, impact_assessment
            )
            
            # Resolution planning
            resolution_planning = await self._plan_defect_resolution(
                defect_classification, severity
            )
            
            defect_data = {
                "defect_id": defect_id,
                "defect_description": defect_description,
                "severity": severity.value,
                "affected_components": affected_components,
                "reproduction_steps": reproduction_steps,
                "expected_behavior": expected_behavior,
                "actual_behavior": actual_behavior,
                "environment_details": environment_details,
                "status": "new",
                "created_date": datetime.now().isoformat(),
                "defect_classification": defect_classification,
                "impact_assessment": impact_assessment,
                "assignment_criteria": assignment_criteria,
                "resolution_planning": resolution_planning,
                "defect_lifecycle": {
                    "status_history": [{"status": "new", "timestamp": datetime.now().isoformat()}],
                    "assignments": [],
                    "comments": [],
                    "attachments": []
                }
            }
            
            # Store defect data
            await self.redis.setex(
                f"defect:{defect_id}",
                7776000,  # 90 days
                json.dumps(defect_data, default=str)
            )
            
            logger.info(f"Defect {defect_id} tracked successfully")
            return defect_data
            
        except Exception as e:
            logger.error(f"Error tracking defect: {e}")
            raise
    
    async def perform_root_cause_analysis(
        self,
        defect_id: str,
        analysis_scope: List[str],
        investigation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform root cause analysis for defect"""
        try:
            logger.info(f"Performing root cause analysis for defect: {defect_id}")
            
            # Get defect data
            defect_data = await self.redis.get(f"defect:{defect_id}")
            if not defect_data:
                raise ValueError(f"Defect {defect_id} not found")
            
            # Root cause investigation
            root_cause_investigation = await self._investigate_root_cause(
                investigation_data, analysis_scope
            )
            
            # Contributing factors analysis
            contributing_factors = await self._analyze_contributing_factors(
                root_cause_investigation
            )
            
            # Corrective actions
            corrective_actions = await self._define_corrective_actions(
                root_cause_investigation, contributing_factors
            )
            
            # Preventive measures
            preventive_measures = await self._recommend_preventive_measures(
                root_cause_investigation
            )
            
            root_cause_analysis = {
                "analysis_id": hashlib.sha256(
                    f"{defect_id}_{datetime.now().isoformat()}".encode()
                ).hexdigest()[:12],
                "defect_id": defect_id,
                "analysis_date": datetime.now().isoformat(),
                "analysis_scope": analysis_scope,
                "investigation_data": investigation_data,
                "root_cause_investigation": root_cause_investigation,
                "contributing_factors": contributing_factors,
                "corrective_actions": corrective_actions,
                "preventive_measures": preventive_measures,
                "analysis_confidence": await self._assess_analysis_confidence(
                    root_cause_investigation
                )
            }
            
            # Store root cause analysis
            await self.redis.setex(
                f"root_cause_analysis:{root_cause_analysis['analysis_id']}",
                7776000,  # 90 days
                json.dumps(root_cause_analysis, default=str)
            )
            
            logger.info(f"Root cause analysis {root_cause_analysis['analysis_id']} completed successfully")
            return root_cause_analysis
            
        except Exception as e:
            logger.error(f"Error performing root cause analysis: {e}")
            raise

class QualityMetricsAgent:
    """Quality metrics and performance tracking specialist"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.quality_dashboards = {}
        self.metrics_tracking = {}
        self.quality_reports = {}
        
    async def generate_quality_dashboard(
        self,
        project_id: str,
        dashboard_scope: Dict[str, Any],
        metrics_requirements: List[str],
        reporting_period: Dict[str, str]
    ) -> Dict[str, Any]:
        """Generate comprehensive quality dashboard"""
        try:
            logger.info(f"Generating quality dashboard for project: {project_id}")
            
            # Generate dashboard ID
            dashboard_id = hashlib.sha256(
                f"{project_id}_{dashboard_scope}_{datetime.now().isoformat()}".encode()
            ).hexdigest()[:12]
            
            # Quality metrics calculation
            quality_metrics = await self._calculate_quality_metrics(
                project_id, metrics_requirements, reporting_period
            )
            
            # Trend analysis
            trend_analysis = await self._analyze_quality_trends(
                quality_metrics, reporting_period
            )
            
            # Benchmark comparison
            benchmark_comparison = await self._compare_to_benchmarks(
                quality_metrics, dashboard_scope
            )
            
            # Quality insights
            quality_insights = await self._generate_quality_insights(
                quality_metrics, trend_analysis
            )
            
            # Recommendations
            quality_recommendations = await self._generate_quality_recommendations(
                quality_insights, benchmark_comparison
            )
            
            quality_dashboard = {
                "dashboard_id": dashboard_id,
                "project_id": project_id,
                "dashboard_scope": dashboard_scope,
                "metrics_requirements": metrics_requirements,
                "reporting_period": reporting_period,
                "generated_date": datetime.now().isoformat(),
                "quality_metrics": quality_metrics,
                "trend_analysis": trend_analysis,
                "benchmark_comparison": benchmark_comparison,
                "quality_insights": quality_insights,
                "quality_recommendations": quality_recommendations,
                "dashboard_summary": await self._generate_dashboard_summary(
                    quality_metrics, quality_insights
                )
            }
            
            # Store quality dashboard
            await self.redis.setex(
                f"quality_dashboard:{dashboard_id}",
                7776000,  # 90 days
                json.dumps(quality_dashboard, default=str)
            )
            
            logger.info(f"Quality dashboard {dashboard_id} generated successfully")
            return quality_dashboard
            
        except Exception as e:
            logger.error(f"Error generating quality dashboard: {e}")
            raise

class DynamicMessageProcessor:
    """Dynamic message processing for agent communication"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.message_history = deque(maxlen=10000)
        self.rate_limiter = TokenBucketRateLimiter()
        
    async def send_message(
        self,
        sender: str,
        receiver: str,
        content: Dict[str, Any],
        performative: str = "INFORM",
        priority: str = "P2_MEDIUM",
        requires_response: bool = False
    ) -> Dict[str, Any]:
        """Send message with dynamic communication patterns"""
        try:
            # Message deduplication
            message_hash = hashlib.sha256(
                json.dumps(content, sort_keys=True).encode()
            ).hexdigest()
            
            if not await self._is_new_message(message_hash):
                return {"status": "duplicate", "message_id": message_hash}
            
            # Rate limiting check
            rate_limit_result = await self.rate_limiter.check_rate_limit(
                f"{sender}:{receiver}", priority
            )
            
            if not rate_limit_result["allowed"]:
                await self._queue_message_for_retry(content, rate_limit_result["retry_after"])
                return {"status": "rate_limited", "retry_after": rate_limit_result["retry_after"]}
            
            # Create message envelope
            envelope = {
                "message_id": hashlib.sha256(
                    f"{datetime.now().isoformat()}_{sender}_{receiver}".encode()
                ).hexdigest()[:16],
                "timestamp": datetime.now().isoformat(),
                "sender": sender,
                "receiver": receiver,
                "performative": performative,
                "priority": priority,
                "requires_response": requires_response,
                "envelope_version": "1.0",
                "content_hash": message_hash
            }
            
            # Dual payload design (Envelope JSON + Content NL/JSON)
            full_message = {
                "envelope": envelope,
                "content": content,
                "metadata": {
                    "sent_via": "quality_assurance_team",
                    "communication_type": "agent_to_agent",
                    "protocol_version": "1.0"
                }
            }
            
            # Store message history
            self.message_history.append(full_message)
            
            # Log communication
            await self._log_communication(full_message)
            
            # Route message through NOTI hub (simulated)
            routing_result = await self._route_message(full_message)
            
            return {
                "status": "sent",
                "message_id": envelope["message_id"],
                "routing_result": routing_result,
                "delivered_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _is_new_message(self, message_hash: str) -> bool:
        """Check if message is new (deduplication)"""
        key = f"message_dedup:{message_hash}"
        if await self.redis.exists(key):
            return False
        
        await self.redis.setex(key, 3600, "1")
        return True
    
    async def _queue_message_for_retry(self, content: Dict[str, Any], retry_after: int):
        """Queue message for retry when rate limited"""
        retry_key = f"retry_queue:{datetime.now().timestamp() + retry_after}"
        await self.redis.setex(retry_key, retry_after, json.dumps(content))
    
    async def _route_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Route message through NOTI hub"""
        return {
            "routed_to": message["envelope"]["receiver"],
            "delivery_status": "delivered",
            "routing_timestamp": datetime.now().isoformat()
        }
    
    async def _log_communication(self, message: Dict[str, Any]):
        """Log communication for audit purposes"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "sender": message["envelope"]["sender"],
            "receiver": message["envelope"]["receiver"],
            "performative": message["envelope"]["performative"],
            "priority": message["envelope"]["priority"]
        }
        
        await self.redis.lpush("communication_logs", json.dumps(log_entry))

class TokenBucketRateLimiter:
    """Token bucket rate limiter for back-pressure mechanisms"""
    
    def __init__(self):
        self.buckets = {}
        
    async def check_rate_limit(
        self, 
        key: str, 
        priority: str, 
        tokens_per_minute: Dict[str, int] = None
    ) -> Dict[str, Any]:
        """Check rate limit based on priority"""
        if tokens_per_minute is None:
            tokens_per_minute = {
                "P0_CRITICAL": 1000,
                "P1_HIGH": 500,
                "P2_MEDIUM": 200,
                "P3_LOW": 50
            }
        
        bucket_key = f"bucket:{key}"
        current_time = datetime.now()
        
        if bucket_key not in self.buckets:
            self.buckets[bucket_key] = {
                "tokens": tokens_per_minute[priority],
                "last_refill": current_time
            }
        
        bucket = self.buckets[bucket_key]
        
        time_elapsed = (current_time - bucket["last_refill"]).total_seconds()
        tokens_to_add = int(time_elapsed / 60 * tokens_per_minute[priority])
        
        if tokens_to_add > 0:
            bucket["tokens"] = min(
                tokens_per_minute[priority],
                bucket["tokens"] + tokens_to_add
            )
            bucket["last_refill"] = current_time
        
        if bucket["tokens"] > 0:
            bucket["tokens"] -= 1
            return {
                "allowed": True,
                "remaining_tokens": bucket["tokens"]
            }
        else:
            return {
                "allowed": False,
                "retry_after": 60,
                "remaining_tokens": 0
            }

# FastAPI Models
class TestPlanRequest(BaseModel):
    project_name: str
    test_objectives: List[str]
    test_scope: Dict[str, Any]
    test_types: List[str]
    quality_standards: List[str]
    resource_requirements: Dict[str, Any]
    timeline: Dict[str, str]

class DefectTrackingRequest(BaseModel):
    defect_description: str
    severity: str
    affected_components: List[str]
    reproduction_steps: List[str]
    expected_behavior: str
    actual_behavior: str
    environment_details: Dict[str, Any]

class QualityDashboardRequest(BaseModel):
    project_id: str
    dashboard_scope: Dict[str, Any]
    metrics_requirements: List[str]
    reporting_period: Dict[str, str]

# FastAPI Application
app = FastAPI(
    title="HAAS+ Quality Assurance Team",
    description="Comprehensive quality assurance and testing management team",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
redis_client = None
test_planning_agent = None
defect_management_agent = None
quality_metrics_agent = None
message_processor = None

@app.on_event("startup")
async def startup_event():
    """Initialize the quality assurance team"""
    global redis_client, test_planning_agent, defect_management_agent
    global quality_metrics_agent, message_processor
    
    try:
        redis_client = redis.from_url(
            "redis://localhost:6379",
            encoding="utf-8",
            decode_responses=True
        )
        
        await redis_client.ping()
        logger.info("Redis connection established")
        
        test_planning_agent = TestPlanningAgent(redis_client)
        defect_management_agent = DefectManagementAgent(redis_client)
        quality_metrics_agent = QualityMetricsAgent(redis_client)
        message_processor = DynamicMessageProcessor(redis_client)
        
        logger.info("Quality Assurance Team initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing Quality Assurance Team: {e}")
        raise

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        await redis_client.ping()
        redis_status = "healthy"
    except:
        redis_status = "unhealthy"
    
    return {
        "service": "quality_assurance_team",
        "status": "healthy" if redis_status == "healthy" else "degraded",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "redis": redis_status,
            "test_planning": "active",
            "defect_management": "active",
            "quality_metrics": "active"
        }
    }

@app.post("/api/v1/create_test_plan")
async def create_test_plan(request: TestPlanRequest):
    """Create comprehensive test plan"""
    try:
        # Convert test type and quality standard strings to enums
        test_types = [TestType(test_type) for test_type in request.test_types]
        quality_standards = [QualityStandard(standard) for standard in request.quality_standards]
        
        result = await test_planning_agent.create_test_plan(
            request.project_name,
            request.test_objectives,
            request.test_scope,
            test_types,
            quality_standards,
            request.resource_requirements,
            request.timeline
        )
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Error creating test plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/manage_test_execution")
async def manage_test_execution(
    plan_id: str,
    execution_schedule: List[Dict[str, Any]],
    test_results: List[Dict[str, Any]],
    defect_reports: List[Dict[str, Any]]
):
    """Manage test execution process"""
    try:
        result = await test_planning_agent.manage_test_execution(
            plan_id, execution_schedule, test_results, defect_reports
        )
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Error managing test execution: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/track_defect")
async def track_defect(request: DefectTrackingRequest):
    """Track and manage defect"""
    try:
        severity = DefectSeverity(request.severity)
        result = await defect_management_agent.track_defect(
            request.defect_description,
            severity,
            request.affected_components,
            request.reproduction_steps,
            request.expected_behavior,
            request.actual_behavior,
            request.environment_details
        )
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Error tracking defect: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/perform_root_cause_analysis")
async def perform_root_cause_analysis(
    defect_id: str,
    analysis_scope: List[str],
    investigation_data: Dict[str, Any]
):
    """Perform root cause analysis for defect"""
    try:
        result = await defect_management_agent.perform_root_cause_analysis(
            defect_id, analysis_scope, investigation_data
        )
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Error performing root cause analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/generate_quality_dashboard")
async def generate_quality_dashboard(request: QualityDashboardRequest):
    """Generate comprehensive quality dashboard"""
    try:
        result = await quality_metrics_agent.generate_quality_dashboard(
            request.project_id,
            request.dashboard_scope,
            request.metrics_requirements,
            request.reporting_period
        )
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Error generating quality dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/send_message")
async def send_message(
    sender: str,
    receiver: str,
    content: Dict[str, Any],
    performative: str = "INFORM",
    priority: str = "P2_MEDIUM"
):
    """Send message with dynamic communication patterns"""
    try:
        result = await message_processor.send_message(
            sender, receiver, content, performative, priority
        )
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8025,
        reload=True,
        log_level="info"
    )