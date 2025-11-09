"""
HAAS+ Multi-Agent System - Sales Team
====================================

Comprehensive sales automation and customer acquisition team for enterprise-level sales operations.
Implements lead management, customer relationship management, sales analytics, and pipeline optimization.

Team Structure:
- Lead Generation: Prospect identification, list building, lead scoring
- Sales Development: Qualification, nurturing, and lead conversion
- Account Management: Customer relationship management, upselling, retention
- Sales Analytics: Performance tracking, forecasting, pipeline analysis
- Sales Operations: Process optimization, sales enablement, territory management
- Customer Success: Onboarding, expansion, retention, advocacy
- Sales Training: Coaching, skill development, performance improvement
- Revenue Operations: Revenue optimization, pricing strategy, deal management

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
import re
from urllib.parse import quote, unquote

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LeadStatus(Enum):
    """Lead status progression"""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    INTERESTED = "interested"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"
    NURTURING = "nurturing"

class DealStage(Enum):
    """Sales deal stages"""
    PROSPECTING = "prospecting"
    QUALIFICATION = "qualification"
    NEEDS_ANALYSIS = "needs_analysis"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSING = "closing"
    WON = "won"
    LOST = "lost"

class LeadSource(Enum):
    """Lead source types"""
    WEBSITE = "website"
    REFERRAL = "referral"
    COLD_OUTREACH = "cold_outreach"
    EVENT = "event"
    PARTNER = "partner"
    SOCIAL_MEDIA = "social_media"
    CONTENT_MARKETING = "content_marketing"
    PAID_ADS = "paid_ads"
    EMAIL = "email"
    PHONE = "phone"

class Priority(Enum):
    """Priority levels"""
    P0_CRITICAL = "p0_critical"
    P1_HIGH = "p1_high"
    P2_MEDIUM = "p2_medium"
    P3_LOW = "p3_low"

@dataclass
class SalesMetrics:
    """Sales performance metrics"""
    team_id: str
    leads_generated: int = 0
    qualified_leads: int = 0
    deals_created: int = 0
    deals_closed: int = 0
    revenue_generated: float = 0.0
    conversion_rate: float = 0.0
    average_deal_size: float = 0.0
    sales_cycle_length: float = 0.0
    pipeline_value: float = 0.0
    win_rate: float = 0.0

class LeadGenerationAgent:
    """Lead generation and prospecting specialist"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.prospect_database = {}
        self.lead_scoring_models = {}
        
    async def generate_leads(
        self,
        target_criteria: Dict[str, Any],
        lead_volume: int,
        lead_sources: List[str],
        geography: List[str] = None,
        industry: List[str] = None,
        company_size: str = "all"
    ) -> Dict[str, Any]:
        """Generate leads based on target criteria"""
        try:
            logger.info(f"Generating {lead_volume} leads for target criteria")
            
            # Prospect identification
            prospects = await self._identify_prospects(
                target_criteria, lead_volume, geography, industry, company_size
            )
            
            # Lead scoring
            scored_leads = await self._score_leads(prospects, target_criteria)
            
            # Lead enrichment
            enriched_leads = await self._enrich_lead_data(scored_leads)
            
            # Lead source attribution
            source_attribution = await self._attribute_lead_sources(
                enriched_leads, lead_sources
            )
            
            # Lead generation report
            generation_report = {
                "generation_id": hashlib.sha256(
                    f"{datetime.now().isoformat()}_{lead_volume}".encode()
                ).hexdigest()[:12],
                "generation_date": datetime.now().isoformat(),
                "target_criteria": target_criteria,
                "lead_volume": lead_volume,
                "lead_sources": lead_sources,
                "geography": geography or [],
                "industry": industry or [],
                "company_size": company_size,
                "prospects_identified": len(prospects),
                "leads_generated": len(enriched_leads),
                "leads": enriched_leads,
                "source_attribution": source_attribution,
                "quality_metrics": await self._calculate_lead_quality_metrics(enriched_leads),
                "next_actions": await self._generate_next_actions(enriched_leads)
            }
            
            # Cache generation data
            await self.redis.setex(
                f"lead_generation:{generation_report['generation_id']}",
                604800,  # 7 days
                json.dumps(generation_report, default=str)
            )
            
            logger.info(f"Generated {len(enriched_leads)} leads successfully")
            return generation_report
            
        except Exception as e:
            logger.error(f"Error generating leads: {e}")
            raise
    
    async def qualify_leads(
        self,
        lead_ids: List[str],
        qualification_criteria: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Qualify leads based on BANT or similar criteria"""
        try:
            logger.info(f"Qualifying {len(lead_ids)} leads")
            
            # Get lead data
            leads_data = await self._get_lead_data(lead_ids)
            
            # Apply qualification criteria
            qualified_leads = await self._apply_qualification_criteria(
                leads_data, qualification_criteria
            )
            
            # Calculate qualification scores
            qualification_scores = await self._calculate_qualification_scores(
                leads_data, qualification_criteria
            )
            
            # Classify leads
            lead_classification = await self._classify_leads(
                leads_data, qualification_scores
            )
            
            qualification_result = {
                "qualification_date": datetime.now().isoformat(),
                "total_leads": len(lead_ids),
                "qualified_leads": len(qualified_leads["hot"]),
                "warm_leads": len(qualified_leads["warm"]),
                "cold_leads": len(qualified_leads["cold"]),
                "unqualified": len(qualified_leads["unqualified"]),
                "qualification_scores": qualification_scores,
                "lead_classification": lead_classification,
                "qualified_leads": qualified_leads,
                "recommendations": await self._generate_qualification_recommendations(lead_classification)
            }
            
            return qualification_result
            
        except Exception as e:
            logger.error(f"Error qualifying leads: {e}")
            raise
    
    async def _identify_prospects(
        self,
        target_criteria: Dict[str, Any],
        lead_volume: int,
        geography: List[str],
        industry: List[str],
        company_size: str
    ) -> List[Dict[str, Any]]:
        """Identify potential prospects"""
        prospects = []
        
        # Simulate prospect identification
        for i in range(lead_volume):
            prospect = {
                "prospect_id": f"PROS_{i+1:06d}",
                "company_name": f"Company_{i+1}",
                "industry": np.random.choice(industry) if industry else "Technology",
                "geography": np.random.choice(geography) if geography else "US",
                "company_size": company_size,
                "estimated_revenue": np.random.uniform(1000000, 100000000),
                "employee_count": np.random.randint(10, 10000),
                "website": f"https://company{i+1}.com",
                "linkedin_url": f"https://linkedin.com/company/company{i+1}",
                "contact_email": f"contact@company{i+1}.com",
                "decision_maker": f"Decision Maker {i+1}",
                "title": np.random.choice([
                    "CEO", "CTO", "VP Sales", "VP Marketing", "Director IT", "Manager"
                ]),
                "contact_phone": f"+1-555-{i+1:04d}",
                "fit_score": np.random.uniform(0.3, 1.0),
                "priority": np.random.choice(["High", "Medium", "Low"]),
                "last_activity": datetime.now().isoformat(),
                "source": np.random.choice([
                    "LinkedIn", "Website", "Referral", "Event", "Cold Outreach"
                ])
            }
            prospects.append(prospect)
        
        return prospects
    
    async def _score_leads(
        self, 
        prospects: List[Dict[str, Any]], 
        target_criteria: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Score leads based on fit and engagement potential"""
        scored_leads = []
        
        for prospect in prospects:
            # Calculate fit score
            fit_score = 0.0
            
            # Industry match
            if prospect["industry"] in target_criteria.get("industries", []):
                fit_score += 0.3
            
            # Company size match
            if prospect["employee_count"] >= target_criteria.get("min_employees", 0):
                fit_score += 0.2
            
            # Revenue match
            if prospect["estimated_revenue"] >= target_criteria.get("min_revenue", 0):
                fit_score += 0.2
            
            # Geographic match
            if prospect["geography"] in target_criteria.get("geographies", []):
                fit_score += 0.15
            
            # Priority indicator
            if prospect["priority"] == "High":
                fit_score += 0.15
            
            prospect["lead_score"] = fit_score
            scored_leads.append(prospect)
        
        # Sort by score
        scored_leads.sort(key=lambda x: x["lead_score"], reverse=True)
        
        return scored_leads

class SalesDevelopmentAgent:
    """Sales development and lead nurturing specialist"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.sales_sequences = {}
        self.outreach_templates = {}
        
    async def create_sales_sequence(
        self,
        sequence_name: str,
        sequence_type: str,
        target_segment: Dict[str, Any],
        steps: List[Dict[str, Any]],
        personalization_rules: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create sales outreach sequence"""
        try:
            logger.info(f"Creating sales sequence: {sequence_name}")
            
            # Generate sequence ID
            sequence_id = hashlib.sha256(
                f"{sequence_name}_{datetime.now().isoformat()}".encode()
            ).hexdigest()[:12]
            
            # Sequence strategy
            strategy = await self._define_sequence_strategy(sequence_type, target_segment)
            
            # Step configuration
            configured_steps = await self._configure_sequence_steps(steps)
            
            # Personalization setup
            personalization = await self._setup_personalization_rules(
                personalization_rules or {}, target_segment
            )
            
            # Success metrics
            success_metrics = await self._define_success_metrics(sequence_type)
            
            sequence_data = {
                "sequence_id": sequence_id,
                "sequence_name": sequence_name,
                "sequence_type": sequence_type,
                "target_segment": target_segment,
                "steps": configured_steps,
                "strategy": strategy,
                "personalization": personalization,
                "success_metrics": success_metrics,
                "created_date": datetime.now().isoformat(),
                "status": "active",
                "performance": {
                    "sent": 0,
                    "opens": 0,
                    "replies": 0,
                    "meetings": 0,
                    "conversions": 0
                }
            }
            
            # Store sequence
            self.sales_sequences[sequence_id] = sequence_data
            
            # Cache sequence
            await self.redis.setex(
                f"sales_sequence:{sequence_id}",
                2592000,  # 30 days
                json.dumps(sequence_data, default=str)
            )
            
            logger.info(f"Sales sequence {sequence_id} created successfully")
            return sequence_data
            
        except Exception as e:
            logger.error(f"Error creating sales sequence: {e}")
            raise
    
    async def execute_outreach(
        self,
        sequence_id: str,
        lead_ids: List[str],
        execution_type: str = "automated"
    ) -> Dict[str, Any]:
        """Execute sales outreach to leads"""
        try:
            logger.info(f"Executing outreach for sequence {sequence_id} to {len(lead_ids)} leads")
            
            # Get sequence data
            sequence = self.sales_sequences.get(sequence_id)
            if not sequence:
                raise ValueError(f"Sequence {sequence_id} not found")
            
            # Get lead data
            leads_data = await self._get_lead_data(lead_ids)
            
            # Personalize outreach
            personalized_messages = await self._personalize_outreach(
                sequence, leads_data
            )
            
            # Execute outreach steps
            execution_results = await self._execute_outreach_steps(
                sequence, personalized_messages, execution_type
            )
            
            # Track performance
            performance_tracking = await self._track_outreach_performance(
                execution_results, sequence
            )
            
            outreach_result = {
                "execution_id": hashlib.sha256(
                    f"{sequence_id}_{datetime.now().isoformat()}".encode()
                ).hexdigest()[:12],
                "sequence_id": sequence_id,
                "execution_date": datetime.now().isoformat(),
                "execution_type": execution_type,
                "leads_contacted": len(lead_ids),
                "personalized_messages": personalized_messages,
                "execution_results": execution_results,
                "performance_tracking": performance_tracking,
                "next_actions": await self._generate_outreach_next_actions(execution_results)
            }
            
            return outreach_result
            
        except Exception as e:
            logger.error(f"Error executing outreach: {e}")
            raise
    
    async def _configure_sequence_steps(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Configure individual sequence steps"""
        configured_steps = []
        
        for i, step in enumerate(steps):
            configured_step = {
                "step_number": i + 1,
                "step_type": step.get("type", "email"),  # email, call, linkedin
                "delay_days": step.get("delay_days", 2),
                "subject": step.get("subject", ""),
                "template": step.get("template", ""),
                "conditions": step.get("conditions", []),
                "follow_up_rules": step.get("follow_up_rules", {}),
                "success_criteria": step.get("success_criteria", {})
            }
            configured_steps.append(configured_step)
        
        return configured_steps

class AccountManagementAgent:
    """Account management and customer relationship specialist"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.account_portfolios = {}
        self.customer_journeys = {}
        
    async def manage_account(
        self,
        account_id: str,
        account_data: Dict[str, Any],
        management_strategy: str = "relationship_focused"
    ) -> Dict[str, Any]:
        """Manage customer account"""
        try:
            logger.info(f"Managing account: {account_id}")
            
            # Account analysis
            account_analysis = await self._analyze_account_health(account_data)
            
            # Relationship mapping
            relationship_map = await self._create_relationship_map(account_data)
            
            # Opportunity identification
            opportunities = await self._identify_upsell_opportunities(account_data)
            
            # Risk assessment
            risk_assessment = await self._assess_account_risks(account_data)
            
            # Account plan
            account_plan = await self._create_account_plan(
                account_data, management_strategy, opportunities, risk_assessment
            )
            
            # Key account activities
            key_activities = await self._plan_key_account_activities(account_data)
            
            account_management = {
                "account_id": account_id,
                "management_date": datetime.now().isoformat(),
                "management_strategy": management_strategy,
                "account_analysis": account_analysis,
                "relationship_map": relationship_map,
                "opportunities": opportunities,
                "risk_assessment": risk_assessment,
                "account_plan": account_plan,
                "key_activities": key_activities,
                "next_review_date": (datetime.now() + timedelta(days=30)).isoformat()
            }
            
            # Store account management data
            await self.redis.setex(
                f"account_management:{account_id}",
                2592000,  # 30 days
                json.dumps(account_management, default=str)
            )
            
            logger.info(f"Account {account_id} management plan created successfully")
            return account_management
            
        except Exception as e:
            logger.error(f"Error managing account: {e}")
            raise
    
    async def track_customer_journey(
        self,
        customer_id: str,
        journey_stages: List[str],
        current_stage: str
    ) -> Dict[str, Any]:
        """Track customer journey progression"""
        try:
            logger.info(f"Tracking customer journey for: {customer_id}")
            
            # Journey stage analysis
            stage_analysis = await self._analyze_journey_stages(journey_stages, current_stage)
            
            # Progress tracking
            progress_tracking = await self._track_journey_progress(customer_id, current_stage)
            
            # Next steps identification
            next_steps = await self._identify_journey_next_steps(current_stage, stage_analysis)
            
            # Journey optimization
            optimization_opportunities = await self._identify_journey_optimization(current_stage)
            
            journey_data = {
                "customer_id": customer_id,
                "tracking_date": datetime.now().isoformat(),
                "journey_stages": journey_stages,
                "current_stage": current_stage,
                "stage_analysis": stage_analysis,
                "progress_tracking": progress_tracking,
                "next_steps": next_steps,
                "optimization_opportunities": optimization_opportunities,
                "stage_completion_probability": await self._calculate_stage_completion_probability(current_stage)
            }
            
            # Store journey data
            await self.redis.setex(
                f"customer_journey:{customer_id}",
                2592000,  # 30 days
                json.dumps(journey_data, default=str)
            )
            
            return journey_data
            
        except Exception as e:
            logger.error(f"Error tracking customer journey: {e}")
            raise

class SalesAnalyticsAgent:
    """Sales analytics and performance tracking specialist"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.analytics_dashboards = {}
        self.forecasting_models = {}
        
    async def analyze_sales_performance(
        self,
        time_period: str,
        sales_team: str = "all",
        metrics: List[str] = None
    ) -> Dict[str, Any]:
        """Analyze sales performance across various dimensions"""
        try:
            logger.info(f"Analyzing sales performance for period: {time_period}")
            
            # Fetch performance data
            performance_data = await self._fetch_sales_performance_data(
                time_period, sales_team
            )
            
            # Calculate key metrics
            if metrics is None:
                metrics = [
                    "revenue", "leads", "conversions", "pipeline", 
                    "win_rate", "avg_deal_size", "sales_cycle"
                ]
            
            calculated_metrics = await self._calculate_sales_metrics(
                performance_data, metrics
            )
            
            # Performance trends
            trend_analysis = await self._analyze_performance_trends(
                calculated_metrics, time_period
            )
            
            # Benchmark comparison
            benchmarks = await self._compare_to_benchmarks(calculated_metrics)
            
            # Performance insights
            insights = await self._generate_performance_insights(calculated_metrics, trend_analysis)
            
            # Recommendations
            recommendations = await self._generate_performance_recommendations(
                calculated_metrics, insights
            )
            
            performance_analysis = {
                "analysis_date": datetime.now().isoformat(),
                "time_period": time_period,
                "sales_team": sales_team,
                "metrics_analyzed": metrics,
                "performance_data": performance_data,
                "calculated_metrics": calculated_metrics,
                "trend_analysis": trend_analysis,
                "benchmarks": benchmarks,
                "insights": insights,
                "recommendations": recommendations,
                "performance_summary": await self._generate_performance_summary(calculated_metrics)
            }
            
            return performance_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing sales performance: {e}")
            raise
    
    async def forecast_sales(
        self,
        forecast_period: str,
        forecast_type: str = "pipeline_based",
        factors: List[str] = None
    ) -> Dict[str, Any]:
        """Generate sales forecasts"""
        try:
            logger.info(f"Generating sales forecast for: {forecast_period}")
            
            # Historical data analysis
            historical_data = await self._analyze_historical_sales_data(forecast_period)
            
            # Forecast methodology
            methodology = await self._select_forecast_methodology(forecast_type)
            
            # Forecast calculation
            forecast_results = await self._calculate_forecast(
                historical_data, methodology, factors or []
            )
            
            # Confidence intervals
            confidence_intervals = await self._calculate_confidence_intervals(forecast_results)
            
            # Scenario planning
            scenarios = await self._create_forecast_scenarios(forecast_results)
            
            forecast_analysis = {
                "forecast_id": hashlib.sha256(
                    f"{forecast_period}_{forecast_type}_{datetime.now().isoformat()}".encode()
                ).hexdigest()[:12],
                "forecast_date": datetime.now().isoformat(),
                "forecast_period": forecast_period,
                "forecast_type": forecast_type,
                "factors_considered": factors or [],
                "methodology": methodology,
                "historical_data": historical_data,
                "forecast_results": forecast_results,
                "confidence_intervals": confidence_intervals,
                "scenarios": scenarios,
                "accuracy_expectations": await self._calculate_forecast_accuracy_expectations(forecast_type)
            }
            
            return forecast_analysis
            
        except Exception as e:
            logger.error(f"Error forecasting sales: {e}")
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
                    "sent_via": "sales_team",
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
class LeadGenerationRequest(BaseModel):
    target_criteria: Dict[str, Any]
    lead_volume: int
    lead_sources: List[str]
    geography: List[str] = None
    industry: List[str] = None
    company_size: str = "all"

class LeadQualificationRequest(BaseModel):
    lead_ids: List[str]
    qualification_criteria: Dict[str, Any]

class SalesSequenceRequest(BaseModel):
    sequence_name: str
    sequence_type: str
    target_segment: Dict[str, Any]
    steps: List[Dict[str, Any]]
    personalization_rules: Dict[str, Any] = None

class AccountManagementRequest(BaseModel):
    account_id: str
    account_data: Dict[str, Any]
    management_strategy: str = "relationship_focused"

class SalesPerformanceRequest(BaseModel):
    time_period: str
    sales_team: str = "all"
    metrics: List[str] = None

# FastAPI Application
app = FastAPI(
    title="HAAS+ Sales Team",
    description="Comprehensive sales automation and customer acquisition team",
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
lead_generation_agent = None
sales_development_agent = None
account_management_agent = None
sales_analytics_agent = None
message_processor = None

@app.on_event("startup")
async def startup_event():
    """Initialize the sales team"""
    global redis_client, lead_generation_agent, sales_development_agent
    global account_management_agent, sales_analytics_agent, message_processor
    
    try:
        redis_client = redis.from_url(
            "redis://localhost:6379",
            encoding="utf-8",
            decode_responses=True
        )
        
        await redis_client.ping()
        logger.info("Redis connection established")
        
        lead_generation_agent = LeadGenerationAgent(redis_client)
        sales_development_agent = SalesDevelopmentAgent(redis_client)
        account_management_agent = AccountManagementAgent(redis_client)
        sales_analytics_agent = SalesAnalyticsAgent(redis_client)
        message_processor = DynamicMessageProcessor(redis_client)
        
        logger.info("Sales Team initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing Sales Team: {e}")
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
        "service": "sales_team",
        "status": "healthy" if redis_status == "healthy" else "degraded",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "redis": redis_status,
            "lead_generation": "active",
            "sales_development": "active",
            "account_management": "active",
            "sales_analytics": "active"
        }
    }

@app.post("/api/v1/generate_leads")
async def generate_leads(request: LeadGenerationRequest):
    """Generate leads based on target criteria"""
    try:
        result = await lead_generation_agent.generate_leads(
            request.target_criteria,
            request.lead_volume,
            request.lead_sources,
            request.geography,
            request.industry,
            request.company_size
        )
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Error generating leads: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/qualify_leads")
async def qualify_leads(request: LeadQualificationRequest):
    """Qualify leads based on criteria"""
    try:
        result = await lead_generation_agent.qualify_leads(
            request.lead_ids,
            request.qualification_criteria
        )
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Error qualifying leads: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/create_sales_sequence")
async def create_sales_sequence(request: SalesSequenceRequest):
    """Create sales outreach sequence"""
    try:
        result = await sales_development_agent.create_sales_sequence(
            request.sequence_name,
            request.sequence_type,
            request.target_segment,
            request.steps,
            request.personalization_rules
        )
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Error creating sales sequence: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/execute_outreach")
async def execute_outreach(
    sequence_id: str,
    lead_ids: List[str],
    execution_type: str = "automated"
):
    """Execute sales outreach to leads"""
    try:
        result = await sales_development_agent.execute_outreach(
            sequence_id, lead_ids, execution_type
        )
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Error executing outreach: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/manage_account")
async def manage_account(request: AccountManagementRequest):
    """Manage customer account"""
    try:
        result = await account_management_agent.manage_account(
            request.account_id,
            request.account_data,
            request.management_strategy
        )
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Error managing account: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/track_customer_journey")
async def track_customer_journey(
    customer_id: str,
    journey_stages: List[str],
    current_stage: str
):
    """Track customer journey progression"""
    try:
        result = await account_management_agent.track_customer_journey(
            customer_id, journey_stages, current_stage
        )
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Error tracking customer journey: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/analyze_sales_performance")
async def analyze_sales_performance(request: SalesPerformanceRequest):
    """Analyze sales performance"""
    try:
        result = await sales_analytics_agent.analyze_sales_performance(
            request.time_period,
            request.sales_team,
            request.metrics
        )
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Error analyzing sales performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/forecast_sales")
async def forecast_sales(
    forecast_period: str,
    forecast_type: str = "pipeline_based",
    factors: List[str] = None
):
    """Generate sales forecasts"""
    try:
        result = await sales_analytics_agent.forecast_sales(
            forecast_period, forecast_type, factors
        )
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Error forecasting sales: {e}")
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
        port=8015,
        reload=True,
        log_level="info"
    )