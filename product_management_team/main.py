"""
HAAS+ Multi-Agent System - Product Management Team
=================================================

Comprehensive product management and development team for enterprise-level product operations.
Implements product strategy, roadmap planning, feature management, user research, and product analytics.

Team Structure:
- Product Strategy: Product vision, positioning, strategy development
- Product Planning: Roadmapping, feature prioritization, release planning
- User Research: User interviews, surveys, usability testing, persona development
- Product Analytics: Feature usage, user behavior, product metrics
- Product Operations: Process optimization, cross-functional coordination
- Go-to-Market: Launch strategy, market positioning, sales enablement
- Product Design: UX/UI design, user experience optimization
- Competitive Analysis: Market analysis, competitor intelligence

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

class ProductStatus(Enum):
    """Product lifecycle status"""
    CONCEPT = "concept"
    DEVELOPMENT = "development"
    BETA = "beta"
    LAUNCHED = "launched"
    GROWTH = "growth"
    MATURE = "mature"
    DECLINING = "declining"
    RETIRED = "retired"

class FeaturePriority(Enum):
    """Feature priority levels"""
    MUST_HAVE = "must_have"
    SHOULD_HAVE = "should_have"
    COULD_HAVE = "could_have"
    WONT_HAVE = "wont_have"

class UserSegment(Enum):
    """User segment types"""
    ENTERPRISE = "enterprise"
    SMB = "smb"
    INDIVIDUAL = "individual"
    DEVELOPERS = "developers"
    ADMINISTRATORS = "administrators"

class Priority(Enum):
    """Priority levels"""
    P0_CRITICAL = "p0_critical"
    P1_HIGH = "p1_high"
    P2_MEDIUM = "p2_medium"
    P3_LOW = "p3_low"

@dataclass
class ProductMetrics:
    """Key product performance metrics"""
    product_id: str
    active_users: int = 0
    monthly_recurring_revenue: float = 0.0
    churn_rate: float = 0.0
    net_promoter_score: float = 0.0
    feature_adoption: float = 0.0
    user_satisfaction: float = 0.0
    time_to_value: float = 0.0
    customer_acquisition_cost: float = 0.0
    lifetime_value: float = 0.0

class ProductStrategyAgent:
    """Product strategy and vision specialist"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.product_strategies = {}
        self.product_roadmaps = {}
        self.feature_backlogs = {}
        
    async def define_product_strategy(
        self,
        product_name: str,
        product_vision: str,
        target_audience: Dict[str, Any],
        value_proposition: str,
        competitive_advantages: List[str],
        strategic_goals: List[str]
    ) -> Dict[str, Any]:
        """Define comprehensive product strategy"""
        try:
            logger.info(f"Defining product strategy for: {product_name}")
            
            # Generate strategy ID
            strategy_id = hashlib.sha256(
                f"{product_name}_{product_vision}_{datetime.now().isoformat()}".encode()
            ).hexdigest()[:12]
            
            # Market analysis
            market_analysis = await self._conduct_market_analysis(target_audience)
            
            # Competitive positioning
            competitive_positioning = await self._define_competitive_positioning(
                competitive_advantages
            )
            
            # Product positioning
            product_positioning = await self._define_product_positioning(
                product_vision, value_proposition, target_audience
            )
            
            # Go-to-market strategy
            go_to_market_strategy = await self._develop_go_to_market_strategy(
                target_audience, competitive_positioning
            )
            
            # Success metrics
            success_metrics = await self._define_success_metrics(strategic_goals)
            
            # Risk assessment
            risk_assessment = await self._assess_product_risks(
                market_analysis, go_to_market_strategy
            )
            
            product_strategy_data = {
                "strategy_id": strategy_id,
                "product_name": product_name,
                "product_vision": product_vision,
                "target_audience": target_audience,
                "value_proposition": value_proposition,
                "competitive_advantages": competitive_advantages,
                "strategic_goals": strategic_goals,
                "status": "draft",
                "created_date": datetime.now().isoformat(),
                "market_analysis": market_analysis,
                "competitive_positioning": competitive_positioning,
                "product_positioning": product_positioning,
                "go_to_market_strategy": go_to_market_strategy,
                "success_metrics": success_metrics,
                "risk_assessment": risk_assessment,
                "implementation_roadmap": await self._create_implementation_roadmap(
                    strategic_goals
                )
            }
            
            # Store product strategy
            self.product_strategies[strategy_id] = product_strategy_data
            
            # Cache strategy data
            await self.redis.setex(
                f"product_strategy:{strategy_id}",
                31536000,  # 1 year
                json.dumps(product_strategy_data, default=str)
            )
            
            logger.info(f"Product strategy {strategy_id} defined successfully")
            return product_strategy_data
            
        except Exception as e:
            logger.error(f"Error defining product strategy: {e}")
            raise
    
    async def create_product_roadmap(
        self,
        strategy_id: str,
        roadmap_horizon: int,
        feature_priorities: List[Dict[str, Any]],
        resource_allocation: Dict[str, Any],
        milestone_definitions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create detailed product roadmap"""
        try:
            logger.info(f"Creating product roadmap for strategy: {strategy_id}")
            
            # Generate roadmap ID
            roadmap_id = hashlib.sha256(
                f"{strategy_id}_{roadmap_horizon}_{datetime.now().isoformat()}".encode()
            ).hexdigest()[:12]
            
            # Timeline planning
            timeline_planning = await self._create_timeline_planning(
                roadmap_horizon, milestone_definitions
            )
            
            # Feature prioritization
            prioritized_features = await self._prioritize_features(
                feature_priorities, resource_allocation
            )
            
            # Release planning
            release_planning = await self._plan_releases(
                prioritized_features, timeline_planning
            )
            
            # Resource allocation
            detailed_allocation = await self._allocate_resources(
                release_planning, resource_allocation
            )
            
            # Dependencies analysis
            dependencies_analysis = await self._analyze_dependencies(
                prioritized_features
            )
            
            # Risk mitigation
            risk_mitigation = await self._develop_risk_mitigation(
                dependencies_analysis, resource_allocation
            )
            
            product_roadmap_data = {
                "roadmap_id": roadmap_id,
                "strategy_id": strategy_id,
                "roadmap_horizon": roadmap_horizon,
                "feature_priorities": feature_priorities,
                "resource_allocation": resource_allocation,
                "milestone_definitions": milestone_definitions,
                "status": "planning",
                "created_date": datetime.now().isoformat(),
                "timeline_planning": timeline_planning,
                "prioritized_features": prioritized_features,
                "release_planning": release_planning,
                "detailed_allocation": detailed_allocation,
                "dependencies_analysis": dependencies_analysis,
                "risk_mitigation": risk_mitigation,
                "progress_tracking": {
                    "milestones_completed": 0,
                    "features_delivered": 0,
                    "overall_progress": 0.0
                }
            }
            
            # Store product roadmap
            await self.redis.setex(
                f"product_roadmap:{roadmap_id}",
                31536000,  # 1 year
                json.dumps(product_roadmap_data, default=str)
            )
            
            logger.info(f"Product roadmap {roadmap_id} created successfully")
            return product_roadmap_data
            
        except Exception as e:
            logger.error(f"Error creating product roadmap: {e}")
            raise

class UserResearchAgent:
    """User research and experience specialist"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.user_research_studies = {}
        self.user_personas = {}
        self.usability_tests = {}
        
    async def conduct_user_research(
        self,
        research_objectives: List[str],
        target_user_segments: List[UserSegment],
        research_methods: List[str],
        timeline: Dict[str, str]
    ) -> Dict[str, Any]:
        """Conduct comprehensive user research study"""
        try:
            logger.info(f"Conducting user research with objectives: {research_objectives}")
            
            # Generate research ID
            research_id = hashlib.sha256(
                f"{'_'.join(research_objectives)}_{datetime.now().isoformat()}".encode()
            ).hexdigest()[:12]
            
            # Research design
            research_design = await self._design_research_study(
                research_objectives, research_methods, target_user_segments
            )
            
            # Participant recruitment
            participant_recruitment = await self._plan_participant_recruitment(
                target_user_segments, research_design
            )
            
            # Research instruments
            research_instruments = await self._develop_research_instruments(
                research_methods, research_objectives
            )
            
            # Data collection plan
            data_collection_plan = await self._create_data_collection_plan(
                research_design, timeline
            )
            
            # Analysis framework
            analysis_framework = await self._define_analysis_framework(
                research_objectives, research_methods
            )
            
            user_research_data = {
                "research_id": research_id,
                "research_objectives": research_objectives,
                "target_user_segments": [segment.value for segment in target_user_segments],
                "research_methods": research_methods,
                "timeline": timeline,
                "status": "planning",
                "created_date": datetime.now().isoformat(),
                "research_design": research_design,
                "participant_recruitment": participant_recruitment,
                "research_instruments": research_instruments,
                "data_collection_plan": data_collection_plan,
                "analysis_framework": analysis_framework,
                "research_outputs": {
                    "key_findings": [],
                    "user_insights": [],
                    "recommendations": [],
                    "persona_updates": []
                }
            }
            
            # Store user research study
            self.user_research_studies[research_id] = user_research_data
            
            # Cache research data
            await self.redis.setex(
                f"user_research:{research_id}",
                7776000,  # 90 days
                json.dumps(user_research_data, default=str)
            )
            
            logger.info(f"User research study {research_id} created successfully")
            return user_research_data
            
        except Exception as e:
            logger.error(f"Error conducting user research: {e}")
            raise
    
    async def create_user_persona(
        self,
        persona_name: str,
        demographic_profile: Dict[str, Any],
        behavioral_patterns: Dict[str, Any],
        goals_and_motivations: List[str],
        pain_points: List[str],
        technology_aptitude: str
    ) -> Dict[str, Any]:
        """Create detailed user persona"""
        try:
            logger.info(f"Creating user persona: {persona_name}")
            
            # Generate persona ID
            persona_id = hashlib.sha256(
                f"{persona_name}_{demographic_profile}_{datetime.now().isoformat()}".encode()
            ).hexdigest()[:12]
            
            # Persona development
            persona_development = await self._develop_persona_details(
                demographic_profile, behavioral_patterns
            )
            
            # User journey mapping
            user_journey = await self._map_user_journey(
                goals_and_motivations, pain_points
            )
            
            # Technology usage patterns
            technology_patterns = await self._analyze_technology_patterns(
                technology_aptitude, demographic_profile
            )
            
            # Decision-making factors
            decision_factors = await self._identify_decision_factors(
                goals_and_motivations, pain_points
            )
            
            user_persona_data = {
                "persona_id": persona_id,
                "persona_name": persona_name,
                "demographic_profile": demographic_profile,
                "behavioral_patterns": behavioral_patterns,
                "goals_and_motivations": goals_and_motivations,
                "pain_points": pain_points,
                "technology_aptitude": technology_aptitude,
                "created_date": datetime.now().isoformat(),
                "persona_development": persona_development,
                "user_journey": user_journey,
                "technology_patterns": technology_patterns,
                "decision_factors": decision_factors,
                "persona_validation": await self._validate_persona(persona_development)
            }
            
            # Store user persona
            await self.redis.setex(
                f"user_persona:{persona_id}",
                31536000,  # 1 year
                json.dumps(user_persona_data, default=str)
            )
            
            logger.info(f"User persona {persona_id} created successfully")
            return user_persona_data
            
        except Exception as e:
            logger.error(f"Error creating user persona: {e}")
            raise

class ProductAnalyticsAgent:
    """Product analytics and metrics specialist"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.product_metrics = {}
        self.analytics_dashboards = {}
        self.user_behavior_analysis = {}
        
    async def analyze_product_performance(
        self,
        product_id: str,
        analysis_period: str,
        metrics_focus: List[str],
        user_segments: List[str] = None
    ) -> Dict[str, Any]:
        """Analyze comprehensive product performance"""
        try:
            logger.info(f"Analyzing product performance for: {product_id}")
            
            # Generate analysis ID
            analysis_id = hashlib.sha256(
                f"{product_id}_{analysis_period}_{datetime.now().isoformat()}".encode()
            ).hexdigest()[:12]
            
            # Core metrics analysis
            core_metrics = await self._analyze_core_metrics(
                product_id, analysis_period, metrics_focus
            )
            
            # User behavior analysis
            behavior_analysis = await self._analyze_user_behavior(
                product_id, analysis_period, user_segments
            )
            
            # Feature usage analysis
            feature_usage = await self._analyze_feature_usage(
                product_id, analysis_period
            )
            
            # User journey analysis
            journey_analysis = await self._analyze_user_journey(
                product_id, analysis_period
            )
            
            # Cohort analysis
            cohort_analysis = await self._perform_cohort_analysis(
                product_id, analysis_period
            )
            
            # Performance insights
            performance_insights = await self._generate_performance_insights(
                core_metrics, behavior_analysis, feature_usage
            )
            
            # Recommendations
            optimization_recommendations = await self._generate_optimization_recommendations(
                performance_insights, cohort_analysis
            )
            
            product_performance_data = {
                "analysis_id": analysis_id,
                "product_id": product_id,
                "analysis_period": analysis_period,
                "metrics_focus": metrics_focus,
                "user_segments": user_segments or [],
                "analysis_date": datetime.now().isoformat(),
                "core_metrics": core_metrics,
                "behavior_analysis": behavior_analysis,
                "feature_usage": feature_usage,
                "journey_analysis": journey_analysis,
                "cohort_analysis": cohort_analysis,
                "performance_insights": performance_insights,
                "optimization_recommendations": optimization_recommendations,
                "performance_summary": await self._generate_performance_summary(
                    core_metrics, performance_insights
                )
            }
            
            # Store performance analysis
            await self.redis.setex(
                f"product_performance:{analysis_id}",
                7776000,  # 90 days
                json.dumps(product_performance_data, default=str)
            )
            
            logger.info(f"Product performance analysis {analysis_id} completed successfully")
            return product_performance_data
            
        except Exception as e:
            logger.error(f"Error analyzing product performance: {e}")
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
                    "sent_via": "product_management_team",
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
class ProductStrategyRequest(BaseModel):
    product_name: str
    product_vision: str
    target_audience: Dict[str, Any]
    value_proposition: str
    competitive_advantages: List[str]
    strategic_goals: List[str]

class ProductRoadmapRequest(BaseModel):
    strategy_id: str
    roadmap_horizon: int
    feature_priorities: List[Dict[str, Any]]
    resource_allocation: Dict[str, Any]
    milestone_definitions: List[Dict[str, Any]]

class UserResearchRequest(BaseModel):
    research_objectives: List[str]
    target_user_segments: List[str]
    research_methods: List[str]
    timeline: Dict[str, str]

class UserPersonaRequest(BaseModel):
    persona_name: str
    demographic_profile: Dict[str, Any]
    behavioral_patterns: Dict[str, Any]
    goals_and_motivations: List[str]
    pain_points: List[str]
    technology_aptitude: str

# FastAPI Application
app = FastAPI(
    title="HAAS+ Product Management Team",
    description="Comprehensive product management and development team",
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
product_strategy_agent = None
user_research_agent = None
product_analytics_agent = None
message_processor = None

@app.on_event("startup")
async def startup_event():
    """Initialize the product management team"""
    global redis_client, product_strategy_agent, user_research_agent
    global product_analytics_agent, message_processor
    
    try:
        redis_client = redis.from_url(
            "redis://localhost:6379",
            encoding="utf-8",
            decode_responses=True
        )
        
        await redis_client.ping()
        logger.info("Redis connection established")
        
        product_strategy_agent = ProductStrategyAgent(redis_client)
        user_research_agent = UserResearchAgent(redis_client)
        product_analytics_agent = ProductAnalyticsAgent(redis_client)
        message_processor = DynamicMessageProcessor(redis_client)
        
        logger.info("Product Management Team initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing Product Management Team: {e}")
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
        "service": "product_management_team",
        "status": "healthy" if redis_status == "healthy" else "degraded",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "redis": redis_status,
            "product_strategy": "active",
            "user_research": "active",
            "product_analytics": "active"
        }
    }

@app.post("/api/v1/define_product_strategy")
async def define_product_strategy(request: ProductStrategyRequest):
    """Define comprehensive product strategy"""
    try:
        result = await product_strategy_agent.define_product_strategy(
            request.product_name,
            request.product_vision,
            request.target_audience,
            request.value_proposition,
            request.competitive_advantages,
            request.strategic_goals
        )
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Error defining product strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/create_product_roadmap")
async def create_product_roadmap(request: ProductRoadmapRequest):
    """Create detailed product roadmap"""
    try:
        result = await product_strategy_agent.create_product_roadmap(
            request.strategy_id,
            request.roadmap_horizon,
            request.feature_priorities,
            request.resource_allocation,
            request.milestone_definitions
        )
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Error creating product roadmap: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/conduct_user_research")
async def conduct_user_research(request: UserResearchRequest):
    """Conduct comprehensive user research study"""
    try:
        # Convert user segment strings to enums
        segments = [UserSegment(segment) for segment in request.target_user_segments]
        result = await user_research_agent.conduct_user_research(
            request.research_objectives,
            segments,
            request.research_methods,
            request.timeline
        )
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Error conducting user research: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/create_user_persona")
async def create_user_persona(request: UserPersonaRequest):
    """Create detailed user persona"""
    try:
        result = await user_research_agent.create_user_persona(
            request.persona_name,
            request.demographic_profile,
            request.behavioral_patterns,
            request.goals_and_motivations,
            request.pain_points,
            request.technology_aptitude
        )
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Error creating user persona: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/analyze_product_performance")
async def analyze_product_performance(
    product_id: str,
    analysis_period: str,
    metrics_focus: List[str],
    user_segments: List[str] = None
):
    """Analyze comprehensive product performance"""
    try:
        result = await product_analytics_agent.analyze_product_performance(
            product_id, analysis_period, metrics_focus, user_segments
        )
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Error analyzing product performance: {e}")
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
        port=8021,
        reload=True,
        log_level="info"
    )