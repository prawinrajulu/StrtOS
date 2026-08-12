"""
Resource Allocation Engine.

Deterministically allocates resources to missions based on priority scores.
No black-box unexplained allocation. Each allocation includes a full explanation.
Never silently exceeds capacity.
"""
from typing import List, Dict, Any, Tuple, Optional
from app.resources.models import ResourceStatus


ALLOCATION_SCORE_WEIGHTS = {
    "strategic_value": 0.25,
    "expected_value_norm": 0.20,
    "urgency": 0.15,
    "mission_priority": 0.15,
    "confidence": 0.10,
    "risk_inv": 0.10,
    "resource_efficiency": 0.05,
}


class AllocationPool:
    """Mutable in-memory resource pool for allocation computation (no DB)."""

    def __init__(self, resources: List[Dict[str, Any]]):
        self._total: Dict[str, float] = {}
        self._allocated: Dict[str, float] = {}
        self._names: Dict[str, str] = {}
        for r in resources:
            rid = r["resource_id"]
            self._total[rid] = float(r.get("total_capacity") or 0.0)
            self._allocated[rid] = float(r.get("allocated_capacity", 0.0))
            self._names[rid] = r.get("resource_name", rid)

    def available(self, resource_id: str) -> float:
        return max(0.0, self._total.get(resource_id, 0.0) - self._allocated.get(resource_id, 0.0))

    def total(self, resource_id: str) -> float:
        return self._total.get(resource_id, 0.0)

    def allocate(self, resource_id: str, amount: float) -> bool:
        """Returns True if allocation succeeded."""
        avail = self.available(resource_id)
        if amount > avail:
            return False
        self._allocated[resource_id] = self._allocated.get(resource_id, 0.0) + amount
        return True

    def snapshot(self) -> Dict[str, Dict[str, float]]:
        result = {}
        for rid in self._total:
            total = self._total[rid]
            alloc = self._allocated.get(rid, 0.0)
            result[rid] = {
                "resource_name": self._names.get(rid, rid),
                "total": total,
                "allocated": alloc,
                "remaining": max(0.0, total - alloc),
                "utilization_pct": round((alloc / max(1.0, total)) * 100.0, 1)
            }
        return result


class ResourceAllocationEngine:
    """
    Allocates resources to missions deterministically.

    Algorithm:
    1. Score each mission (deterministic priority score)
    2. Sort missions by score (highest first)
    3. For each mission, attempt to allocate its required resources from pool
    4. On failure: mark as RESOURCE_CONSTRAINED with explanation
    5. Return full allocation plan with per-mission explanation
    """

    def compute_allocation_score(self, mission: Dict[str, Any], max_ev: float = 1.0) -> float:
        ev = mission.get("expected_value", 0.0)
        ev_norm = min(100.0, (ev / max(1.0, max_ev)) * 100.0)
        risk_inv = max(0.0, 100.0 - mission.get("risk_score", 20.0))
        res_req = max(1.0, mission.get("resource_requirement", 1.0))
        res_eff = min(100.0, (ev / res_req) * 10.0)

        score = (
            ALLOCATION_SCORE_WEIGHTS["strategic_value"] * mission.get("strategic_value", 50.0) +
            ALLOCATION_SCORE_WEIGHTS["expected_value_norm"] * ev_norm +
            ALLOCATION_SCORE_WEIGHTS["urgency"] * mission.get("urgency", 50.0) +
            ALLOCATION_SCORE_WEIGHTS["mission_priority"] * mission.get("mission_priority_score", 50.0) +
            ALLOCATION_SCORE_WEIGHTS["confidence"] * mission.get("confidence", 80.0) +
            ALLOCATION_SCORE_WEIGHTS["risk_inv"] * risk_inv +
            ALLOCATION_SCORE_WEIGHTS["resource_efficiency"] * res_eff
        )
        return round(min(100.0, max(0.0, score)), 2)

    def allocate(
        self,
        missions: List[Dict[str, Any]],
        resources: List[Dict[str, Any]],
        requirements: List[Dict[str, Any]],  # [{mission_id, resource_id, required_amount, is_mandatory}]
        org_id: str
    ) -> Dict[str, Any]:
        """
        Returns full allocation plan as dict:
        {
          allocated: [{mission_id, resource_id, allocated, requested, success, reason, score}],
          constrained_missions: [mission_id, ...],
          pool_snapshot: {resource_id: {...}},
          total_expected_value: float,
          risk_score: float,
          confidence: float,
          explanation: str
        }
        """
        pool = AllocationPool(resources)
        max_ev = max((m.get("expected_value", 0.0) for m in missions), default=1.0)

        # Score and sort missions
        scored = sorted(
            [(m, self.compute_allocation_score(m, max_ev)) for m in missions],
            key=lambda x: x[1],
            reverse=True
        )

        # Index requirements
        req_by_mission: Dict[str, List[Dict]] = {}
        for req in requirements:
            req_by_mission.setdefault(req["mission_id"], []).append(req)

        allocated_records: List[Dict] = []
        constrained_missions: List[str] = []
        total_value = 0.0
        total_risk = 0.0

        for mission, score in scored:
            mid = mission["mission_id"]
            mission_reqs = req_by_mission.get(mid, [])
            mission_blocked = False

            for req in mission_reqs:
                rid = req["resource_id"]
                amount = req.get("required_amount", 0.0)
                mandatory = req.get("is_mandatory", True)
                avail_before = pool.available(rid)
                success = pool.allocate(rid, amount)

                reason = (
                    f"Allocated {amount:.2f} units from {pool._names.get(rid, rid)} "
                    f"(remaining: {pool.available(rid):.2f})."
                    if success else
                    f"RESOURCE_CONSTRAINED: requested {amount:.2f} but only "
                    f"{avail_before:.2f} available in {pool._names.get(rid, rid)}. "
                    f"{'Mandatory resource — mission BLOCKED.' if mandatory else 'Optional — mission continues.'}"
                )

                allocated_records.append({
                    "mission_id": mid,
                    "resource_id": rid,
                    "requested": amount,
                    "allocated": amount if success else 0.0,
                    "success": success,
                    "reason": reason,
                    "priority_score": score,
                    "is_mandatory": mandatory
                })

                if not success and mandatory:
                    mission_blocked = True

            if mission_blocked:
                constrained_missions.append(mid)
            else:
                total_value += mission.get("expected_value", 0.0) * (mission.get("confidence", 80.0) / 100.0)
                total_risk += mission.get("risk_score", 20.0)

        n_allocated = len(scored) - len(constrained_missions)
        avg_risk = round(total_risk / max(1, len(scored)), 1)
        confidence = round(min(95.0, 70.0 + n_allocated * 3.0 - avg_risk * 0.3), 1)

        explanation = (
            f"Allocated resources to {n_allocated}/{len(scored)} missions. "
            f"{len(constrained_missions)} mission(s) resource-constrained. "
            f"Expected portfolio value: {total_value:,.0f}. "
            f"Average risk: {avg_risk:.1f}."
        )

        return {
            "allocated": allocated_records,
            "constrained_missions": constrained_missions,
            "pool_snapshot": pool.snapshot(),
            "total_expected_value": round(total_value, 2),
            "risk_score": avg_risk,
            "confidence": confidence,
            "explanation": explanation
        }
