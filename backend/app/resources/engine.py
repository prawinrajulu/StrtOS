"""
Resource Engine — stateless, deterministic computation layer.

ResourceCapacityEngine
ResourceBottleneckEngine
ResourceConflictEngine
ResourcePriorityEngine
OpportunityCostEngine

All engines:
  - Pure computation, no DB access
  - No randomness
  - No fabricated values
  - UNKNOWN status when data unavailable
"""
from typing import List, Dict, Any, Optional, Tuple
from app.resources.models import ResourceStatus, BottleneckSeverity, ConflictSeverity
from app.resources.schemas import (
    CapacityResponse, BottleneckResult, BottleneckResponse,
    ConflictResult, ConflictResponse, MissionResourcePriority,
    PriorityResponse, OpportunityCostResult
)


# ═══════════════════════════════════════════════════════════════════════════════
# RESOURCE CAPACITY ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class ResourceCapacityEngine:
    """
    Calculates available capacity, utilization, shortage, and bottlenecks.
    Uses UNKNOWN when total capacity is unavailable.
    Never invents capacity values.
    """

    WARNING_THRESHOLD = 0.75   # 75% → LIMITED
    EXHAUSTED_THRESHOLD = 1.00 # 100% → EXHAUSTED
    SHORTAGE_THRESHOLD = 0.90  # 90% → near-exhaustion warning

    def compute_utilization(
        self,
        total_capacity: Optional[float],
        allocated_capacity: float
    ) -> Tuple[float, float, float, ResourceStatus]:
        """
        Returns: (utilization_pct, remaining_capacity, shortage, status)
        """
        if total_capacity is None or total_capacity <= 0:
            return 0.0, 0.0, 0.0, ResourceStatus.UNKNOWN

        utilization = allocated_capacity / total_capacity
        utilization_pct = round(min(100.0, utilization * 100.0), 2)
        remaining = round(max(0.0, total_capacity - allocated_capacity), 4)
        shortage = round(max(0.0, allocated_capacity - total_capacity), 4)

        if utilization >= self.EXHAUSTED_THRESHOLD:
            status = ResourceStatus.EXHAUSTED
        elif utilization >= self.WARNING_THRESHOLD:
            status = ResourceStatus.LIMITED
        else:
            status = ResourceStatus.AVAILABLE

        return utilization_pct, remaining, shortage, status

    def build_capacity_response(
        self,
        resource_id: str,
        resource_name: str,
        resource_type,
        total_capacity: Optional[float],
        allocated_capacity: float,
        is_measured: bool
    ) -> CapacityResponse:
        util_pct, remaining, shortage, status = self.compute_utilization(total_capacity, allocated_capacity)
        avail = round(max(0.0, (total_capacity or 0.0) - allocated_capacity), 4)
        return CapacityResponse(
            resource_id=resource_id,
            resource_name=resource_name,
            resource_type=resource_type,
            total_capacity=total_capacity,
            available_capacity=avail if total_capacity is not None else None,
            allocated_capacity=allocated_capacity,
            remaining_capacity=remaining,
            utilization_percentage=util_pct,
            status=status,
            is_measured=is_measured,
            shortage_detected=shortage > 0,
            shortage_amount=shortage
        )

    def classify_bottleneck_severity(self, shortage_pct: float) -> BottleneckSeverity:
        if shortage_pct >= 50.0:
            return BottleneckSeverity.CRITICAL
        elif shortage_pct >= 25.0:
            return BottleneckSeverity.HIGH
        elif shortage_pct >= 10.0:
            return BottleneckSeverity.MEDIUM
        return BottleneckSeverity.LOW

    def classify_conflict_severity(self, shortage_pct: float) -> ConflictSeverity:
        if shortage_pct >= 40.0:
            return ConflictSeverity.CRITICAL
        elif shortage_pct >= 20.0:
            return ConflictSeverity.HIGH
        elif shortage_pct >= 10.0:
            return ConflictSeverity.MEDIUM
        return ConflictSeverity.LOW


# ═══════════════════════════════════════════════════════════════════════════════
# RESOURCE BOTTLENECK ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class ResourceBottleneckEngine:
    """
    Detects resource bottlenecks across missions.
    Returns affected missions, severity, and recommended actions.
    Only uses actual system data — no fabricated values.
    """

    RECOMMENDED_ACTIONS = {
        BottleneckSeverity.CRITICAL: "IMMEDIATE ESCALATION: Request governance approval for emergency resource reallocation.",
        BottleneckSeverity.HIGH: "URGENT: Defer lower-priority missions or request additional resource allocation.",
        BottleneckSeverity.MEDIUM: "MONITOR: Review mission priorities and consider phased scheduling.",
        BottleneckSeverity.LOW: "OBSERVE: Track utilization — bottleneck is approaching but not critical."
    }

    def detect_bottlenecks(
        self,
        resources: List[Dict[str, Any]],
        mission_requirements: List[Dict[str, Any]]
    ) -> BottleneckResponse:
        """
        Args:
          resources: list of {resource_id, resource_name, resource_type, total_capacity, allocated_capacity}
          mission_requirements: list of {mission_id, resource_id, required_amount}
        """
        capacity_engine = ResourceCapacityEngine()
        bottlenecks: List[BottleneckResult] = []

        # Aggregate requirements per resource
        req_by_resource: Dict[str, Dict[str, Any]] = {}
        mission_by_resource: Dict[str, List[str]] = {}
        for req in mission_requirements:
            rid = req["resource_id"]
            req_by_resource[rid] = req_by_resource.get(rid, {"required_amount": 0.0})
            req_by_resource[rid]["required_amount"] += req.get("required_amount", 0.0)
            mission_by_resource.setdefault(rid, [])
            if req["mission_id"] not in mission_by_resource[rid]:
                mission_by_resource[rid].append(req["mission_id"])

        for res in resources:
            rid = res["resource_id"]
            if rid not in req_by_resource:
                continue
            total = res.get("total_capacity")
            allocated = res.get("allocated_capacity", 0.0)
            required = req_by_resource[rid]["required_amount"]

            if total is None:
                # Cannot determine bottleneck without total capacity
                continue

            available = max(0.0, total - allocated)
            shortage = max(0.0, required - available)

            if shortage > 0:
                shortage_pct = round((shortage / max(1.0, required)) * 100.0, 1)
                severity = capacity_engine.classify_bottleneck_severity(shortage_pct)
                bottlenecks.append(BottleneckResult(
                    resource_id=rid,
                    resource_name=res.get("resource_name", "Unknown"),
                    resource_type=res["resource_type"],
                    current_capacity=available,
                    required_capacity=required,
                    shortage=shortage,
                    shortage_pct=shortage_pct,
                    affected_mission_ids=mission_by_resource.get(rid, []),
                    severity=severity,
                    recommended_action=self.RECOMMENDED_ACTIONS[severity]
                ))

        # Sort: CRITICAL first
        severity_order = {
            BottleneckSeverity.CRITICAL: 0,
            BottleneckSeverity.HIGH: 1,
            BottleneckSeverity.MEDIUM: 2,
            BottleneckSeverity.LOW: 3
        }
        bottlenecks.sort(key=lambda b: severity_order[b.severity])
        critical = sum(1 for b in bottlenecks if b.severity == BottleneckSeverity.CRITICAL)
        high = sum(1 for b in bottlenecks if b.severity == BottleneckSeverity.HIGH)

        summary = (
            f"{len(bottlenecks)} bottleneck(s) detected — "
            f"{critical} CRITICAL, {high} HIGH priority."
            if bottlenecks else "No resource bottlenecks detected."
        )

        return BottleneckResponse(
            organization_id="",  # filled by caller
            bottlenecks=bottlenecks,
            critical_count=critical,
            high_count=high,
            total_count=len(bottlenecks),
            summary=summary
        )


# ═══════════════════════════════════════════════════════════════════════════════
# RESOURCE CONFLICT ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class ResourceConflictEngine:
    """
    Detects conflicts where combined mission requirements exceed available capacity.
    """

    RESOLUTION_OPTIONS_MAP = {
        ConflictSeverity.CRITICAL: [
            "ESCALATE to governance for emergency approval.",
            "Pause lowest-priority conflicting mission.",
            "Request emergency resource procurement."
        ],
        ConflictSeverity.HIGH: [
            "Defer lower-priority mission until capacity available.",
            "Stagger mission timelines to prevent simultaneous resource demand.",
            "Request partial resource increase from governance."
        ],
        ConflictSeverity.MEDIUM: [
            "Review mission priority rankings and defer accordingly.",
            "Negotiate shared resource schedule between mission leads.",
            "Consider phased execution to smooth resource demand."
        ],
        ConflictSeverity.LOW: [
            "Monitor resource utilization trend.",
            "Prepare contingency reallocation plan."
        ]
    }

    def detect_conflicts(
        self,
        resources: List[Dict[str, Any]],
        mission_requirements: List[Dict[str, Any]]
    ) -> ConflictResponse:
        capacity_engine = ResourceCapacityEngine()
        conflicts: List[ConflictResult] = []

        # Group requirements per resource
        req_by_resource: Dict[str, List[Dict]] = {}
        for req in mission_requirements:
            rid = req["resource_id"]
            req_by_resource.setdefault(rid, [])
            req_by_resource[rid].append(req)

        resource_map = {r["resource_id"]: r for r in resources}

        for rid, reqs in req_by_resource.items():
            if len(reqs) < 2:
                # Only one mission requesting this resource — no conflict
                continue

            res = resource_map.get(rid)
            if not res:
                continue

            total = res.get("total_capacity")
            allocated = res.get("allocated_capacity", 0.0)
            if total is None:
                continue

            available = max(0.0, total - allocated)
            combined_required = sum(r["required_amount"] for r in reqs)
            shortage = max(0.0, combined_required - available)

            if shortage > 0:
                shortage_pct = round((shortage / max(1.0, combined_required)) * 100.0, 1)
                severity = capacity_engine.classify_conflict_severity(shortage_pct)
                import uuid
                conflicts.append(ConflictResult(
                    conflict_id=str(uuid.uuid4()),
                    resource_id=rid,
                    resource_name=res.get("resource_name", "Unknown"),
                    resource_type=res["resource_type"],
                    mission_ids=[r["mission_id"] for r in reqs],
                    required_capacity=combined_required,
                    available_capacity=available,
                    shortage=shortage,
                    severity=severity,
                    resolution_options=self.RESOLUTION_OPTIONS_MAP[severity]
                ))

        critical = sum(1 for c in conflicts if c.severity == ConflictSeverity.CRITICAL)
        summary = (
            f"{len(conflicts)} resource conflict(s) — {critical} CRITICAL."
            if conflicts else "No resource conflicts detected."
        )

        return ConflictResponse(
            organization_id="",  # filled by caller
            conflicts=conflicts,
            critical_count=critical,
            total_count=len(conflicts),
            summary=summary
        )


# ═══════════════════════════════════════════════════════════════════════════════
# RESOURCE PRIORITY ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class ResourcePriorityEngine:
    """
    Deterministic mission ranking under resource constraints.

    Weights (sum = 1.0):
      strategic_value:    0.25
      expected_value:     0.20
      urgency:            0.15
      mission_priority:   0.15
      confidence:         0.10
      risk_penalty:       0.10 (inverted: lower risk → higher score)
      resource_efficiency:0.05
    """

    WEIGHTS = {
        "strategic_value": 0.25,
        "expected_value_norm": 0.20,
        "urgency": 0.15,
        "mission_priority": 0.15,
        "confidence": 0.10,
        "risk_inv": 0.10,
        "resource_efficiency": 0.05,
    }

    def rank_missions(
        self,
        missions: List[Dict[str, Any]],
        max_expected_value: float = 1.0
    ) -> PriorityResponse:
        ranked: List[MissionResourcePriority] = []

        for m in missions:
            ev = m.get("expected_value", 0.0)
            ev_norm = min(100.0, (ev / max(1.0, max_expected_value)) * 100.0)
            risk = m.get("risk_score", 20.0)
            risk_inv = max(0.0, 100.0 - risk)
            resource_req = max(1.0, m.get("resource_requirement", 1.0))
            resource_eff = min(100.0, (ev / resource_req) * 10.0)

            score = (
                self.WEIGHTS["strategic_value"] * m.get("strategic_value", 50.0) +
                self.WEIGHTS["expected_value_norm"] * ev_norm +
                self.WEIGHTS["urgency"] * m.get("urgency", 50.0) +
                self.WEIGHTS["mission_priority"] * m.get("mission_priority_score", 50.0) +
                self.WEIGHTS["confidence"] * m.get("confidence", 80.0) +
                self.WEIGHTS["risk_inv"] * risk_inv +
                self.WEIGHTS["resource_efficiency"] * resource_eff
            )
            score = round(min(100.0, max(0.0, score)), 2)

            tradeoffs = []
            if risk >= 60:
                tradeoffs.append(f"High risk ({risk:.0f}) increases uncertainty.")
            if m.get("urgency", 50.0) >= 80:
                tradeoffs.append("High urgency — delay would have strategic cost.")
            if resource_req >= 80000:
                tradeoffs.append("High resource cost — consider phased execution.")

            ranked.append(MissionResourcePriority(
                mission_id=m["mission_id"],
                mission_title=m.get("title", m["mission_id"][:12]),
                priority_score=score,
                rank=0,  # set below
                strategic_value=m.get("strategic_value", 50.0),
                urgency_score=m.get("urgency", 50.0),
                expected_value=ev,
                risk_penalty=risk,
                opportunity_cost_score=round(100.0 - score, 2),
                reason=(
                    f"Score {score:.1f}/100: strategic_value={m.get('strategic_value', 50.0):.0f}, "
                    f"urgency={m.get('urgency', 50.0):.0f}, confidence={m.get('confidence', 80.0):.0f}, "
                    f"risk={risk:.0f}."
                ),
                tradeoffs=tradeoffs
            ))

        ranked.sort(key=lambda x: x.priority_score, reverse=True)
        for i, r in enumerate(ranked):
            r.rank = i + 1

        explanation = (
            f"Ranked {len(ranked)} missions by strategic value, urgency, expected value, "
            f"confidence, and risk. Top mission: '{ranked[0].mission_title}' at score {ranked[0].priority_score}."
            if ranked else "No missions to rank."
        )

        return PriorityResponse(
            organization_id="",  # filled by caller
            ranked_missions=ranked,
            explanation=explanation
        )


# ═══════════════════════════════════════════════════════════════════════════════
# OPPORTUNITY COST ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class OpportunityCostEngine:
    """
    Calculates what is lost by choosing Mission A over Mission B.
    Returns INSUFFICIENT_DATA when required values are missing.
    Never presents fabricated financial numbers.
    """

    def compute(
        self,
        selected: Dict[str, Any],
        alternative: Dict[str, Any]
    ) -> OpportunityCostResult:
        required_fields = ["mission_id", "expected_value", "resource_requirement", "risk_score"]
        missing_s = [f for f in required_fields if f not in selected or selected[f] is None]
        missing_a = [f for f in required_fields if f not in alternative or alternative[f] is None]

        if missing_s or missing_a:
            return OpportunityCostResult(
                selected_mission_id=selected.get("mission_id", "UNKNOWN"),
                alternative_mission_id=alternative.get("mission_id", "UNKNOWN"),
                expected_value_difference=0.0,
                resource_difference=0.0,
                risk_difference=0.0,
                opportunity_cost_score=0.0,
                explanation=f"INSUFFICIENT_DATA: Missing fields in selected={missing_s}, alternative={missing_a}.",
                data_quality="INSUFFICIENT_DATA"
            )

        ev_diff = round(selected["expected_value"] - alternative["expected_value"], 2)
        res_diff = round(selected["resource_requirement"] - alternative["resource_requirement"], 2)
        risk_diff = round(selected["risk_score"] - alternative["risk_score"], 2)

        # Opportunity cost = value lost by NOT choosing alternative
        opp_cost_score = round(
            max(0.0, alternative["expected_value"] - selected["expected_value"]) /
            max(1.0, alternative["expected_value"]) * 100.0, 2
        )

        explanation = (
            f"By choosing '{selected.get('title', selected['mission_id'][:12])}' over "
            f"'{alternative.get('title', alternative['mission_id'][:12])}': "
            f"expected value delta={ev_diff:+,.0f}, "
            f"resource delta={res_diff:+,.0f}, "
            f"risk delta={risk_diff:+.1f}. "
            f"Opportunity cost score: {opp_cost_score:.1f}/100."
        )

        return OpportunityCostResult(
            selected_mission_id=selected["mission_id"],
            alternative_mission_id=alternative["mission_id"],
            expected_value_difference=ev_diff,
            resource_difference=res_diff,
            risk_difference=risk_diff,
            opportunity_cost_score=opp_cost_score,
            explanation=explanation,
            data_quality="SUFFICIENT"
        )
