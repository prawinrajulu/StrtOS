from typing import List, Dict, Any, Tuple
from app.governance.models import RiskLevel

class ConsensusEngine:
    """
    Deterministic Consensus Engine calculating evidence-backed consensus scores,
    overall confidence scores, supporting vs dissenting agents, and governance escalation thresholds.
    """

    @classmethod
    def calculate_consensus(
        cls,
        agent_outputs: Dict[str, Any],
        critic_score: float,
        conflicts: List[Dict[str, Any]],
        evidence_bus: List[Dict[str, Any]]
    ) -> Tuple[float, float, List[str], List[str], bool, str]:
        supporting_agents = []
        dissenting_agents = []

        total_confidence = 0.0
        agent_count = len(agent_outputs)

        for agent_name, output in agent_outputs.items():
            conf = output.get("confidence", 80.0)
            total_confidence += conf
            status = output.get("status", "SUCCESS")

            if status == "SUCCESS" and conf >= 70.0:
                supporting_agents.append(agent_name)
            else:
                dissenting_agents.append(agent_name)

        avg_confidence = total_confidence / agent_count if agent_count > 0 else 80.0

        # Consensus Score calculation
        base_consensus = (len(supporting_agents) / agent_count) * 100.0 if agent_count > 0 else 80.0
        conflict_penalty = len(conflicts) * 10.0
        consensus_score = round(max(0.0, min(100.0, base_consensus - conflict_penalty)), 1)
        overall_confidence = round(max(0.0, min(100.0, (avg_confidence * 0.6) + (critic_score * 0.4))), 1)

        # Governance Escalation Rules: Consensus < 60 OR any CRITICAL conflict triggers Human Review!
        has_critical_conflict = any(c.get("severity") == RiskLevel.CRITICAL for c in conflicts)
        requires_governance = (consensus_score < 60.0) or has_critical_conflict

        rationale = f"Consensus score {consensus_score}% with {len(supporting_agents)} supporting agents and {len(dissenting_agents)} dissenting agents. {len(conflicts)} cross-agent conflicts detected."

        return consensus_score, overall_confidence, supporting_agents, dissenting_agents, requires_governance, rationale
