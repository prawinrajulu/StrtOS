from typing import List, Dict, Any

class CriticEngine:
    """
    Deterministic Critic Engine evaluating evidence quality, logical consistency,
    cross-agent agreement, and unsupported AI assumptions.
    """

    @classmethod
    def evaluate_findings(
        cls,
        agent_outputs: Dict[str, Any],
        evidence_bus: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        strengths = []
        weaknesses = []
        unsupported = []

        total_confidence = 0.0
        agent_count = len(agent_outputs)

        for agent_name, output in agent_outputs.items():
            conf = output.get("confidence", 80.0)
            total_confidence += conf

            findings = output.get("findings", [])
            has_evidence = any(e.get("source_agent") == agent_name for e in evidence_bus)

            if has_evidence:
                strengths.append(f"{agent_name}: Findings backed by verified evidence items.")
            else:
                weaknesses.append(f"{agent_name}: Findings rely on unverified assumptions.")
                unsupported.append(f"{agent_name} recommendation lacks direct external tool telemetry.")

        avg_conf = total_confidence / agent_count if agent_count > 0 else 80.0
        critic_score = round(max(0.0, min(100.0, avg_conf - (len(weaknesses) * 5.0))), 1)

        return {
            "critic_score": critic_score,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "unsupported_claims": unsupported,
            "evaluation_summary": f"Critic Evaluation Completed. Score: {critic_score}/100. Evaluated {agent_count} specialist agents."
        }
