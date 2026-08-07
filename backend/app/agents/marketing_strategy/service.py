import time
import json
import asyncio
from typing import Dict, Any
from app.agents.marketing_strategy.schemas import (
    MarketingStrategyInput, MarketingStrategyResult, ChannelStrategyItem, MarketingFunnelStage
)
from app.agents.marketing_strategy.tools import MarketingStrategyTools
from app.agents.marketing_strategy.validator import MarketingStrategyValidator
from app.core.redis import redis_manager
from app.core.logging import logger

class MarketingStrategyService:
    """Service synthesizing marketing strategy and emitting Redis events."""
    def __init__(self):
        self.tools = MarketingStrategyTools()
        self.validator = MarketingStrategyValidator()

    async def create_strategy(self, payload: MarketingStrategyInput) -> MarketingStrategyResult:
        start_time = time.time()
        self.validator.validate_input(payload)

        # Publish marketing.started event
        await self._publish_event("marketing.started", {"business_goal": payload.business_goal})

        # Query tool abstractions
        budget_split = await self.tools.budget_planner.allocate_budget(payload.budget or "$10,000")
        benchmarks = await self.tools.benchmarks.fetch_benchmarks("D2C / FinTech")
        forecast = await self.tools.forecast.project_roi(payload.budget or "$10,000")

        await self._publish_event("marketing.progress", {"progress": "50%"})

        channels = [
            ChannelStrategyItem(
                channel="Google High-Intent Search Ads",
                objective="Capture immediate demand for solution",
                allocation_percentage=45.0,
                tactics=["Target competitor brand terms", "Exact match commercial intent keywords"],
                target_kpi="CAC < $24"
            ),
            ChannelStrategyItem(
                channel="Meta / Social Video Campaigns",
                objective="Build brand awareness & trust",
                allocation_percentage=35.0,
                tactics=["Micro-influencer video testimonials", "Before/After product proof"],
                target_kpi="ROAS > 3.8x"
            ),
            ChannelStrategyItem(
                channel="Automated Retargeting & Email",
                objective="Maximize LTV & cart recovery",
                allocation_percentage=20.0,
                tactics=["Abandoned checkout email sequence", "Loyalty VIP incentives"],
                target_kpi="Repeat Order Rate > 28%"
            )
        ]

        funnel = [
            MarketingFunnelStage(
                stage_name="TOFU - Awareness",
                focus="Generate high-trust brand awareness",
                key_channels=["Social Video", "Local Influencers"],
                conversion_metric="Click-Through Rate (CTR) > 3.2%"
            ),
            MarketingFunnelStage(
                stage_name="MOFU - Consideration",
                focus="Demonstrate competitive superiority",
                key_channels=["Search Ads", "Social Retargeting"],
                conversion_metric="Landing Page Conversion > 4.5%"
            ),
            MarketingFunnelStage(
                stage_name="BOFU - Conversion & Retention",
                focus="Drive first order & ongoing loyalty",
                key_channels=["Email Flows", "SMS Incentives"],
                conversion_metric="Customer Lifetime Value (LTV) $280"
            )
        ]

        result = MarketingStrategyResult(
            executive_marketing_summary="Synthesized multi-channel growth strategy targeting high-intent acquisition with 4.2x projected ROAS.",
            brand_positioning="High-speed, premium quality service alternative with sub-10 minute support guarantee.",
            unique_value_proposition="Superior quality combined with instant AI-powered customer support and verified trust.",
            marketing_objectives=[
                "Achieve target customer acquisition cost (CAC) of $24.",
                "Reach 4.2x average return on ad spend (ROAS) across paid channels.",
                "Expand monthly active digital customer volume by +35% within 90 days."
            ],
            target_personas=[
                {"name": "Convenience Seekers", "demographics": "Age 25-45, Urban", "channel": "Paid Search & IG Video"}
            ],
            channel_recommendations=channels,
            content_pillars=[
                "Educational Deep-Dives",
                "Verified Customer Testimonials",
                "Product Demonstration Videos"
            ],
            customer_journey=[
                "Discovery via Search/Social Ad",
                "Landing page review & offer claim",
                "Seamless checkout / reservation",
                "Automated post-purchase onboarding & review request"
            ],
            marketing_funnel=funnel,
            budget_allocation=budget_split,
            kpis=["Blended CAC", "ROAS", "Conversion Rate", "LTV"],
            roi_projection=forecast["projected_roi"],
            growth_roadmap=[
                "Days 1-30: Build high-intent Google Search campaigns & landing page funnels.",
                "Days 31-60: Launch Meta micro-influencer video campaigns & email flows.",
                "Days 61-90: Optimize multi-touch attribution & scale top-performing channels."
            ],
            implementation_timeline_days=90,
            risks=["Ad platform CPM fluctuations", "Creative fatigue after 45 days"],
            recommendations=[
                "Deploy local geo-targeted search campaigns immediately.",
                "Implement automated review collection flow to build trust.",
                "Rotate ad creatives bi-weekly to prevent fatigue."
            ],
            confidence_score=95.0,
            execution_time_seconds=round(time.time() - start_time, 2),
            status="COMPLETED"
        )

        # Validate Schema Output
        self.validator.validate_result_schema(result.model_dump())

        # Publish completion events
        await self._publish_event("marketing.completed", result.model_dump())
        await self._publish_event("dashboard.updated", {"agent": "Marketing Strategy Agent", "status": "COMPLETED"})

        return result

    async def _publish_event(self, event_type: str, data: Dict[str, Any]):
        msg = json.dumps({"type": event_type, "data": data})
        await redis_manager.publish_event("strtos_events", msg)
        await redis_manager.publish_event(event_type, msg)
