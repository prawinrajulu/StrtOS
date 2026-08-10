import asyncio
import time
import json
from datetime import datetime, timezone, timedelta
from pydantic import ValidationError

from app.core.evidence.models import EvidenceItem
from app.core.confidence.engine import calculate_confidence
from app.agents.base_agent import SpecialistAgentBase
from app.agents.business_analysis.service import BusinessAnalysisService
from app.agents.business_analysis.schemas import BusinessAnalysisInput
from app.agents.seo_audit.service import SEOAuditService
from app.agents.seo_audit.schemas import SEOAuditInput
from app.agents.competitor_research.service import CompetitorResearchService
from app.agents.competitor_research.schemas import CompetitorResearchInput
from app.agents.marketing_strategy.service import MarketingStrategyService
from app.agents.marketing_strategy.schemas import MarketingStrategyInput
from app.agents.campaign_planner.service import CampaignPlannerService
from app.agents.campaign_planner.schemas import CampaignPlanningInput

# 1. EvidenceItem Model Unit Tests
def test_evidence_item_valid():
    item = EvidenceItem(
        finding="Page load LCP is 1.1s",
        source="Google PageSpeed",
        source_type="api",
        url="https://example.com",
        evidence={"lcp": "1.1s"},
        confidence=95.0
    )
    assert item.finding == "Page load LCP is 1.1s"
    assert item.source_type == "api"
    assert item.confidence == 95.0
    assert str(item.url) == "https://example.com"
    assert item.timestamp is not None
    print("[PASS] test_evidence_item_valid")

def test_evidence_item_invalid_confidence():
    try:
        EvidenceItem(
            finding="Test invalid confidence",
            source="Test",
            source_type="api",
            confidence=150.0  # Invalid > 100
        )
        assert False, "Should have raised ValidationError for confidence > 100"
    except ValidationError:
        print("[PASS] test_evidence_item_invalid_confidence")

def test_evidence_item_invalid_source_type():
    try:
        EvidenceItem(
            finding="Test invalid source type",
            source="Test",
            source_type="unknown_source",  # Invalid source_type
            confidence=80.0
        )
        assert False, "Should have raised ValidationError for invalid source_type"
    except ValidationError:
        print("[PASS] test_evidence_item_invalid_source_type")


# 2. Confidence Engine Unit Tests
def test_confidence_engine():
    # Test empty evidence
    score_empty = calculate_confidence([], llm_status="SUCCESS")
    assert score_empty == 40.0

    # Test single API evidence
    ev_api = EvidenceItem(finding="API metric", source="PageSpeed API", source_type="api", confidence=100.0)
    score_api = calculate_confidence([ev_api], llm_status="SUCCESS")
    assert score_api > 80.0

    # Test website evidence
    ev_web = EvidenceItem(finding="Web content", source="Firecrawl", source_type="website", confidence=90.0)
    score_web = calculate_confidence([ev_web], llm_status="SUCCESS")
    assert score_web > 70.0

    # Test corroborating sources boost
    ev_api_sub = EvidenceItem(finding="API metric", source="PageSpeed API", source_type="api", confidence=75.0)
    ev_web_sub = EvidenceItem(finding="Web content", source="Firecrawl", source_type="website", confidence=75.0)
    ev_search_sub = EvidenceItem(finding="Search result", source="Tavily", source_type="search", confidence=75.0)

    single_score = calculate_confidence([ev_api_sub], llm_status="SUCCESS")
    score_corrob = calculate_confidence([ev_api_sub, ev_web_sub, ev_search_sub], llm_status="SUCCESS")
    assert score_corrob > single_score

    # Test unavailable tool penalty
    ev_unavail = EvidenceItem(finding="Tool failed", source="Firecrawl", source_type="unavailable", confidence=0.0)
    score_unavail = calculate_confidence([ev_unavail], llm_status="SUCCESS", has_unavailable_tools=True)
    assert score_unavail < 50.0

    # Test stale evidence penalty (>30 days old)
    old_time = (datetime.now(timezone.utc) - timedelta(days=40)).isoformat()
    ev_stale = EvidenceItem(finding="Old metric", source="API", source_type="api", confidence=100.0, timestamp=old_time)
    score_stale = calculate_confidence([ev_stale], llm_status="SUCCESS")
    assert score_stale < score_api

    print("[PASS] test_confidence_engine")


# 3. Specialist Agent Execution Tests
async def test_specialist_agents_execution():
    print("\nExecuting Specialist Agent Intelligence Integration Tests...")

    # Business Analysis Agent
    ba_service = BusinessAnalysisService()
    ba_input = BusinessAnalysisInput(
        business_name="Northwind Capital",
        industry="FinTech",
        website="https://example.com",
        business_goal="Scale ARR from $2M to $5M"
    )
    ba_res = await ba_service.run_analysis(ba_input)
    assert ba_res.business_name == "Northwind Capital"
    assert len(ba_res.evidence) >= 1
    assert ba_res.confidence_score > 0.0
    assert ba_res.status in ["COMPLETED", "DEGRADED"]
    print(f"  [PASS] Business Analysis Agent - Status: {ba_res.status}, Confidence: {ba_res.confidence_score}%")

    # SEO Audit Agent
    seo_service = SEOAuditService()
    seo_input = SEOAuditInput(website_url="https://example.com")
    seo_res = await seo_service.run_audit(seo_input)
    assert seo_res.website_url == "https://example.com"
    assert len(seo_res.evidence) >= 1
    assert seo_res.confidence_score > 0.0
    print(f"  [PASS] SEO Audit Agent - Status: {seo_res.status}, Performance Score: {seo_res.performance_score}")

    # Competitor Research Agent
    comp_service = CompetitorResearchService()
    comp_input = CompetitorResearchInput(business_name="Northwind Capital", industry="FinTech")
    comp_res = await comp_service.run_research(comp_input)
    assert comp_res.business_name == "Northwind Capital"
    assert len(comp_res.direct_competitors) >= 1
    assert comp_res.confidence_score > 0.0
    print(f"  [PASS] Competitor Research Agent - Status: {comp_res.status}, Competitors Discovered: {len(comp_res.direct_competitors)}")

    # Marketing Strategy Agent
    mkt_service = MarketingStrategyService()
    mkt_input = MarketingStrategyInput(
        business_analysis_result=ba_res.model_dump(),
        seo_audit_result=seo_res.model_dump(),
        competitor_research_result=comp_res.model_dump(),
        business_goal="Acquire 5,000 enterprise users"
    )
    mkt_res = await mkt_service.create_strategy(mkt_input)
    assert len(mkt_res.channel_recommendations) >= 1
    assert mkt_res.confidence_score > 0.0
    print(f"  [PASS] Marketing Strategy Agent - Status: {mkt_res.status}, Channels: {len(mkt_res.channel_recommendations)}")

    # Campaign Planner Agent
    camp_service = CampaignPlannerService()
    camp_input = CampaignPlanningInput(
        marketing_strategy_result=mkt_res.model_dump(),
        business_analysis_result=ba_res.model_dump(),
        seo_audit_result=seo_res.model_dump(),
        competitor_research_result=comp_res.model_dump(),
        business_goal="Acquire 5,000 enterprise users",
        timeline="90 Days"
    )
    camp_res = await camp_service.build_plan(camp_input)
    assert len(camp_res.creative_requirements) >= 1
    assert len(camp_res.weekly_roadmap) >= 1
    assert camp_res.confidence_score > 0.0
    print(f"  [PASS] Campaign Planner Agent - Status: {camp_res.status}, Deliverables: {len(camp_res.creative_requirements)}")


async def main():
    test_evidence_item_valid()
    test_evidence_item_invalid_confidence()
    test_evidence_item_invalid_source_type()
    test_confidence_engine()
    await test_specialist_agents_execution()
    print("\n=======================================================")
    print("ALL PHASE 8 v0.9.0 AI INTELLIGENCE UNIT TESTS PASSED!")
    print("=======================================================\n")

if __name__ == "__main__":
    asyncio.run(main())
