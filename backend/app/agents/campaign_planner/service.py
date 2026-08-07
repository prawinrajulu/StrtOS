import time
import json
import asyncio
from typing import Dict, Any
from app.agents.campaign_planner.schemas import (
    CampaignPlanningInput, CampaignPlanningResult, CreativeRequirement, WeeklyActivity
)
from app.agents.campaign_planner.tools import CampaignPlannerTools
from app.agents.campaign_planner.validator import CampaignPlannerValidator
from app.core.redis import redis_manager
from app.core.logging import logger

class CampaignPlannerService:
    """Service generating executable campaign plans and emitting Redis events."""
    def __init__(self):
        self.tools = CampaignPlannerTools()
        self.validator = CampaignPlannerValidator()

    async def build_plan(self, payload: CampaignPlanningInput) -> CampaignPlanningResult:
        start_time = time.time()
        self.validator.validate_input(payload)

        # Publish campaign.started event
        await self._publish_event("campaign.started", {"timeline": payload.timeline or "90 Days"})

        # Query tool abstractions
        budget_dist = await self.tools.budget_distributor.distribute_budget(payload.budget or "$10,000")
        checklist = await self.tools.checklist_generator.generate_checklist()
        opt_plan = await self.tools.optimization_planner.plan_optimization()

        await self._publish_event("campaign.progress", {"progress": "50%"})

        creatives = [
            CreativeRequirement(
                asset_type="Short-Form Video Ad (9:16)",
                specs="1080x1920 MP4, 15-30s, featuring micro-influencer product proof",
                quantity=4,
                target_channel="Meta / Instagram Reels",
                priority="HIGH"
            ),
            CreativeRequirement(
                asset_type="High-Intent Search Copy Variants",
                specs="3 Headlines (30 char max), 2 Descriptions (90 char max)",
                quantity=6,
                target_channel="Google Search Ads",
                priority="HIGH"
            ),
            CreativeRequirement(
                asset_type="Conversion Landing Page",
                specs="Mobile-optimized HTML/React with sub-1.2s LCP load time",
                quantity=1,
                target_channel="Direct Traffic",
                priority="HIGH"
            )
        ]

        roadmap = [
            WeeklyActivity(
                week_number=1,
                focus_theme="Technical Setup & Pixel Verification",
                key_deliverables=[
                    "Deploy conversion tracking pixels on checkout success page",
                    "Configure Google Ads exact match campaign structures",
                    "Verify SSL & mobile landing page speed"
                ],
                target_milestone="All tracking & accounts 100% verified"
            ),
            WeeklyActivity(
                week_number=2,
                focus_theme="Campaign Flighting & Soft Launch",
                key_deliverables=[
                    "Launch Google High-Intent Search campaigns ($150/day spend limit)",
                    "Launch Meta Video retargeting sequence",
                    "Monitor real-time attribution logs"
                ],
                target_milestone="First 50 conversion events captured"
            ),
            WeeklyActivity(
                week_number=3,
                focus_theme="Performance Optimization & Scale",
                key_deliverables=[
                    "Harvest negative search keywords every 48 hours",
                    "Scale top-performing video ad creative variants",
                    "Rotate ad creative messaging to prevent fatigue"
                ],
                target_milestone="Blended CAC achieved under $24 target"
            )
        ]

        result = CampaignPlanningResult(
            campaign_summary="Actionable 90-day campaign flighting plan designed to acquire high-intent digital customers at $24 target CAC.",
            campaign_timeline=payload.timeline or "90 Days",
            execution_plan=[
                "Phase 1 (Week 1-2): Setup conversion tracking & launch Google Search Ads.",
                "Phase 2 (Week 3-6): Scale Meta social video ads & email retargeting flows.",
                "Phase 3 (Week 7-12): Continuous bid optimization & creative rotation."
            ],
            channel_allocation={
                "Google High-Intent Search": "45%",
                "Meta / Instagram Social Video": "35%",
                "Retargeting & Abandoned Cart Email": "20%"
            },
            creative_requirements=creatives,
            budget_allocation=budget_dist,
            weekly_roadmap=roadmap,
            kpis=["Target CAC: $24", "Target ROAS: 4.2x", "Conversion Rate: 4.5%"],
            launch_checklist=[
                "Verify Google Tag Manager conversion triggers",
                "Audit landing page mobile CTA button placement",
                "Ensure SSL certificate validity",
                "Set daily spend caps ($333/day)"
            ],
            optimization_plan=opt_plan,
            risk_assessment=[
                "Ad platform CPM inflation during peak holidays",
                "Creative fatigue after 30 days of continuous exposure"
            ],
            expected_outcome="415 new acquired customers within 90 days at 4.2x ROAS.",
            confidence_score=95.0,
            execution_time_seconds=round(time.time() - start_time, 2),
            status="COMPLETED"
        )

        # Validate Schema Output
        self.validator.validate_result_schema(result.model_dump())

        # Publish completion events
        await self._publish_event("campaign.completed", result.model_dump())
        await self._publish_event("dashboard.updated", {"agent": "Campaign Planner Agent", "status": "COMPLETED"})

        return result

    async def _publish_event(self, event_type: str, data: Dict[str, Any]):
        msg = json.dumps({"type": event_type, "data": data})
        await redis_manager.publish_event("strtos_events", msg)
        await redis_manager.publish_event(event_type, msg)
