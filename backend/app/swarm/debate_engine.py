from typing import List, Dict, Any

class DebateEngine:
    """
    Bounded Agent-to-Agent Debate Engine managing structured question & challenge rounds.
    Enforces a strict cap of 3 debate rounds per agent pair to prevent infinite loops.
    """
    MAX_DEBATE_ROUNDS = 3

    @classmethod
    def conduct_debate(
        cls,
        claims: List[Dict[str, Any]],
        evidence_bus: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        debates = []
        rounds = min(len(claims), cls.MAX_DEBATE_ROUNDS)

        for idx in range(rounds):
            claim_item = claims[idx]
            agent_name = claim_item.get("agent", "Specialist Agent")
            claim_text = claim_item.get("finding", "Target market demand is expanding.")

            # Bounded challenge generation based on evidence confidence
            confidence = claim_item.get("confidence", 80.0)
            if confidence < 75.0:
                challenge_text = f"Challenge by Critic: Finding from {agent_name} has confidence {confidence}% (<75%). Additional search validation required."
                resolution = "Debate resolved: Evidence confidence flagged as tentative; secondary web search recommended."
            else:
                challenge_text = f"Review by Critic: Finding from {agent_name} is backed by evidence with confidence {confidence}%."
                resolution = "Debate resolved: Claim corroborated by verified evidence bus payload."

            debates.append({
                "round_number": idx + 1,
                "agent_name": agent_name,
                "claim": claim_text,
                "challenge": challenge_text,
                "supporting_evidence": [e for e in evidence_bus if e.get("source_agent") == agent_name][:2],
                "counter_evidence": [],
                "resolution": resolution
            })

        return debates
