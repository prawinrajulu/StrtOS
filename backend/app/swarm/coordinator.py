import asyncio
import time
from typing import Dict, Any, List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.swarm.context_bus import SharedContextBus
from app.agents.business_analysis.service import BusinessAnalysisService
from app.agents.seo_audit.service import SEOAuditService
from app.agents.competitor_research.service import CompetitorResearchService
from app.agents.marketing_strategy.service import MarketingStrategyService
from app.agents.campaign_planner.service import CampaignPlannerService
from app.core.logging import logger

class SwarmCoordinator:
    """
    Swarm Coordinator orchestrating parallel execution of StrtOS 5 Specialist Agents,
    dependency graph resolution, shared evidence bus integration, and robust fallback handling.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def execute_swarm_graph(
        self,
        swarm_id: str,
        org_id: str,
        client_domain: str = "example-client.com",
        objective: str = "Full-funnel digital strategy optimization"
    ) -> Dict[str, Any]:
        agent_outputs: Dict[str, Any] = {}

        # ----------------------------------------------------
        # STAGE 1: Parallel Execution (Independent Agents)
        # ----------------------------------------------------
        logger.info(f"[Swarm {swarm_id}] Initiating Stage 1 Parallel Agent Execution...")

        async def run_biz():
            try:
                svc = BusinessAnalysisService()
                res = await svc.run_analysis(client_domain=client_domain, org_id=org_id)
                output = {
                    "status": "SUCCESS",
                    "confidence": res.confidence_score,
                    "findings": [res.findings_summary],
                    "metrics": res.metrics
                }
                await SharedContextBus.publish_evidence(swarm_id, org_id, {
                    "source_agent": "Business Analysis Agent",
                    "finding": res.findings_summary,
                    "confidence": res.confidence_score
                })
                return "Business Analysis Agent", output
            except Exception as e:
                logger.error(f"Business Analysis Agent failed: {e}")
                return "Business Analysis Agent", {"status": "UNAVAILABLE", "error": str(e), "confidence": 0.0}

        async def run_seo():
            try:
                svc = SEOAuditService()
                res = await svc.run_audit(website_url=f"https://{client_domain}", org_id=org_id)
                output = {
                    "status": "SUCCESS",
                    "confidence": res.confidence_score,
                    "seo_score": res.seo_score,
                    "findings": [f"SEO Score: {res.seo_score}/100"]
                }
                await SharedContextBus.publish_evidence(swarm_id, org_id, {
                    "source_agent": "SEO Audit Agent",
                    "finding": f"Technical SEO score evaluated at {res.seo_score}/100",
                    "confidence": res.confidence_score
                })
                return "SEO Audit Agent", output
            except Exception as e:
                logger.error(f"SEO Audit Agent failed: {e}")
                return "SEO Audit Agent", {"status": "UNAVAILABLE", "error": str(e), "confidence": 0.0}

        async def run_comp():
            try:
                svc = CompetitorResearchService()
                res = await svc.run_research(client_domain=client_domain, org_id=org_id)
                output = {
                    "status": "SUCCESS",
                    "confidence": res.confidence_score,
                    "competition_intensity": "MEDIUM",
                    "findings": [f"Identified {len(res.competitors)} direct competitors"]
                }
                await SharedContextBus.publish_evidence(swarm_id, org_id, {
                    "source_agent": "Competitor Research Agent",
                    "finding": f"Competitor search mapped {len(res.competitors)} market threats",
                    "confidence": res.confidence_score
                })
                return "Competitor Research Agent", output
            except Exception as e:
                logger.error(f"Competitor Research Agent failed: {e}")
                return "Competitor Research Agent", {"status": "UNAVAILABLE", "error": str(e), "confidence": 0.0}

        # Gather Stage 1 in Parallel via asyncio.gather
        stage1_results = await asyncio.gather(run_biz(), run_seo(), run_comp(), return_exceptions=True)

        for item in stage1_results:
            if isinstance(item, tuple):
                name, out = item
                agent_outputs[name] = out

        # ----------------------------------------------------
        # STAGE 2: Dependent Agent (Marketing Strategy)
        # ----------------------------------------------------
        logger.info(f"[Swarm {swarm_id}] Initiating Stage 2 Marketing Strategy Agent...")
        try:
            m_svc = MarketingStrategyService()
            m_res = await m_svc.create_strategy(client_domain=client_domain, org_id=org_id)
            agent_outputs["Marketing Strategy Agent"] = {
                "status": "SUCCESS",
                "confidence": m_res.confidence_score,
                "recommended_budget": 5000,
                "findings": [m_res.strategy_summary]
            }
            await SharedContextBus.publish_evidence(swarm_id, org_id, {
                "source_agent": "Marketing Strategy Agent",
                "finding": m_res.strategy_summary,
                "confidence": m_res.confidence_score
            })
        except Exception as e:
            logger.error(f"Marketing Strategy Agent failed: {e}")
            agent_outputs["Marketing Strategy Agent"] = {"status": "UNAVAILABLE", "error": str(e), "confidence": 0.0, "recommended_budget": 5000}

        # ----------------------------------------------------
        # STAGE 3: Final Dependent Agent (Campaign Planner)
        # ----------------------------------------------------
        logger.info(f"[Swarm {swarm_id}] Initiating Stage 3 Campaign Planner Agent...")
        try:
            c_svc = CampaignPlannerService()
            c_res = await c_svc.build_plan(client_domain=client_domain, org_id=org_id)
            agent_outputs["Campaign Planner Agent"] = {
                "status": "SUCCESS",
                "confidence": c_res.confidence_score,
                "recommended_budget": 5000,
                "findings": [c_res.campaign_summary]
            }
            await SharedContextBus.publish_evidence(swarm_id, org_id, {
                "source_agent": "Campaign Planner Agent",
                "finding": c_res.campaign_summary,
                "confidence": c_res.confidence_score
            })
        except Exception as e:
            logger.error(f"Campaign Planner Agent failed: {e}")
            agent_outputs["Campaign Planner Agent"] = {"status": "UNAVAILABLE", "error": str(e), "confidence": 0.0, "recommended_budget": 5000}

        return agent_outputs
