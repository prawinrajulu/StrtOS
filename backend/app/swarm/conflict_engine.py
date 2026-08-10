from typing import List, Dict, Any
from app.governance.models import RiskLevel

class ConflictEngine:
    """
    Deterministic Conflict Detection Engine identifying contradictions across specialist agent outputs
    (e.g., budget allocations, market demand signals, positioning strategies).
    """

    @classmethod
    def detect_conflicts(
        cls,
        agent_outputs: Dict[str, Any],
        evidence_bus: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        conflicts = []

        # Example Conflict Check: Budget / Scale Discrepancies
        marketing_out = agent_outputs.get("Marketing Strategy Agent", {})
        campaign_out = agent_outputs.get("Campaign Planner Agent", {})

        m_budget = marketing_out.get("recommended_budget", 5000)
        c_budget = campaign_out.get("recommended_budget", 5000)

        if abs(m_budget - c_budget) > 2000:
            conflicts.append({
                "subject": "Flight Budget Allocation Discrepancy",
                "agent_a": "Marketing Strategy Agent",
                "agent_b": "Campaign Planner Agent",
                "claim_a": f"Recommended flight budget: ${m_budget}",
                "claim_b": f"Proposed media execution budget: ${c_budget}",
                "severity": RiskLevel.HIGH,
                "resolution": "Resolved via Consensus Engine: Capped flight budget to lower conservative bound."
            })

        # Example Conflict Check: SEO vs Competitor Positioning
        seo_out = agent_outputs.get("SEO Audit Agent", {})
        comp_out = agent_outputs.get("Competitor Research Agent", {})

        seo_score = seo_out.get("seo_score", 75)
        comp_intensity = comp_out.get("competition_intensity", "MEDIUM")

        if seo_score < 50 and comp_intensity == "HIGH":
            conflicts.append({
                "subject": "Organic Visibility vs High Market Competition Risk",
                "agent_a": "SEO Audit Agent",
                "agent_b": "Competitor Research Agent",
                "claim_a": f"SEO Score is critically low ({seo_score}/100)",
                "claim_b": f"Market competition intensity is {comp_intensity}",
                "severity": RiskLevel.MEDIUM,
                "resolution": "Resolved via Consensus Engine: Prioritize technical SEO remediations before scaling paid campaigns."
            })

        return conflicts
