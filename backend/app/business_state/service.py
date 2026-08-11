import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.business_state.models import (
    BusinessStateSnapshotModel, BusinessMetricSnapshotModel,
    BusinessSignalModel, BusinessChangeModel, BusinessAlertModel,
    SnapshotType, AlertStatus, AlertSeverity, MetricDirection
)
from app.business_state.schemas import (
    StateSnapshotCreate, StateSnapshotResponse, SignalResponse, ChangeResponse,
    AlertResponse, OpportunityResponse, ThreatResponse, BusinessHealthResponse,
    BusinessExplanationResponse
)
from app.business_state.repository import BusinessStateRepository
from app.business_state.engine import StrategicEarlyWarningEngine
from app.core.events.publisher import event_publisher

class BusinessStateService:
    """Core Service orchestrating Continuous Business State Intelligence & Early Warnings."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = BusinessStateRepository(session)
        self.engine = StrategicEarlyWarningEngine()

    # ---------------------------------------------------------------------------
    # SNAPSHOTS & METRIC PROCESSING
    # ---------------------------------------------------------------------------
    async def create_snapshot(self, payload: StateSnapshotCreate, org_id: str) -> StateSnapshotResponse:
        metrics_map = {m.metric_name: m.value for m in payload.metrics}
        health_resp = self.engine.health_engine.calculate_health(metrics_map)

        snapshot = BusinessStateSnapshotModel(
            organization_id=org_id,
            snapshot_type=payload.snapshot_type,
            health_score=health_resp.health_score,
            health_status=health_resp.health_status,
            summary=payload.summary or f"Business state snapshot ({payload.snapshot_type.value}) - Health: {health_resp.health_status}"
        )

        for m_in in payload.metrics:
            snapshot.metrics.append(
                BusinessMetricSnapshotModel(
                    organization_id=org_id,
                    metric_name=m_in.metric_name,
                    category=m_in.category,
                    value=m_in.value,
                    unit=m_in.unit,
                    confidence_score=m_in.confidence_score,
                    source=m_in.source
                )
            )

        # Fetch previous snapshot before adding new one
        prev_snapshot = await self.repo.get_latest_snapshot(org_id)

        saved = await self.repo.create_snapshot(snapshot)

        # Evaluate signals against previous snapshot
        if prev_snapshot and prev_snapshot.id != saved.id:
            prev_metrics = {m.metric_name: m.value for m in prev_snapshot.metrics}
            for m in saved.metrics:
                if m.metric_name in prev_metrics:
                    p_val = prev_metrics[m.metric_name]
                    delta, pct_change, direction = self.engine.baseline_engine.compare_metrics(p_val, m.value)
                    
                    # Create signal
                    sig = BusinessSignalModel(
                        organization_id=org_id,
                        metric_name=m.metric_name,
                        previous_value=p_val,
                        current_value=m.value,
                        delta=delta,
                        percentage_change=pct_change,
                        direction=direction,
                        confidence=m.confidence_score,
                        evidence_ref=f"Snapshot-{saved.id}"
                    )
                    await self.repo.create_signal(sig)

                    # Evaluate change severity & create alert if significant
                    if abs(pct_change) >= 5.0:
                        sev = self.engine.change_engine.evaluate_change_severity(m.metric_name, pct_change, direction)
                        chg = BusinessChangeModel(
                            organization_id=org_id,
                            metric_name=m.metric_name,
                            severity=sev,
                            title=f"Significant Change: {m.metric_name} ({pct_change}%)",
                            description=f"{m.metric_name} shifted from {p_val} to {m.value} ({direction.value}).",
                            previous_value=p_val,
                            current_value=m.value,
                            percentage_change=pct_change,
                            confidence=m.confidence_score
                        )
                        await self.repo.create_change(chg)

                        if sev in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
                            alert = BusinessAlertModel(
                                organization_id=org_id,
                                alert_type="METRIC_DEGRADATION" if direction == MetricDirection.DECREASE else "METRIC_SPIKE",
                                severity=sev,
                                status=AlertStatus.DETECTED,
                                title=f"Early Warning: {m.metric_name} {direction.value}",
                                message=f"{m.metric_name} changed by {pct_change}% ({p_val} -> {m.value}).",
                                confidence_score=m.confidence_score,
                                recommended_action=f"Investigate root cause of {m.metric_name} change.",
                                governance_required=(sev == AlertSeverity.CRITICAL)
                            )
                            await self.repo.create_alert(alert)

        await event_publisher.publish(
            event_type="business_state.updated",
            organization_id=org_id,
            message=f"Business state snapshot updated. Health: {health_resp.health_status} ({health_resp.health_score}).",
            metadata={"snapshot_id": saved.id, "health_score": health_resp.health_score}
        )

        return StateSnapshotResponse.model_validate(saved)

    async def get_latest_snapshot(self, org_id: str) -> Optional[StateSnapshotResponse]:
        snap = await self.repo.get_latest_snapshot(org_id)
        return StateSnapshotResponse.model_validate(snap) if snap else None

    async def list_snapshots(self, org_id: str) -> List[StateSnapshotResponse]:
        snaps = await self.repo.list_snapshots(org_id)
        return [StateSnapshotResponse.model_validate(s) for s in snaps]

    # ---------------------------------------------------------------------------
    # SIGNALS, CHANGES, OPPORTUNITIES & THREATS
    # ---------------------------------------------------------------------------
    async def list_signals(self, org_id: str) -> List[SignalResponse]:
        signals = await self.repo.list_signals(org_id)
        return [SignalResponse.model_validate(s) for s in signals]

    async def list_changes(self, org_id: str) -> List[ChangeResponse]:
        changes = await self.repo.list_changes(org_id)
        return [ChangeResponse.model_validate(c) for c in changes]

    async def list_opportunities(self, org_id: str) -> List[OpportunityResponse]:
        snap = await self.repo.get_latest_snapshot(org_id)
        metrics = {m.metric_name: m.value for m in snap.metrics} if snap else {}
        return self.engine.opportunity_engine.detect_opportunities(metrics)

    async def list_threats(self, org_id: str) -> List[ThreatResponse]:
        snap = await self.repo.get_latest_snapshot(org_id)
        metrics = {m.metric_name: m.value for m in snap.metrics} if snap else {}
        changes = await self.repo.list_changes(org_id)
        return self.engine.threat_engine.detect_threats(metrics, changes)

    # ---------------------------------------------------------------------------
    # ALERTS
    # ---------------------------------------------------------------------------
    async def list_alerts(self, org_id: str, status: Optional[AlertStatus] = None) -> List[AlertResponse]:
        alerts = await self.repo.list_alerts(org_id, status=status)
        return [AlertResponse.model_validate(a) for a in alerts]

    async def get_alert(self, alert_id: str, org_id: str) -> AlertResponse:
        alert = await self.repo.get_alert_by_id(alert_id, org_id)
        if not alert:
            raise KeyError(f"Business Alert '{alert_id}' not found.")
        return AlertResponse.model_validate(alert)

    async def update_alert_status(self, alert_id: str, org_id: str, new_status: AlertStatus) -> AlertResponse:
        updated = await self.repo.update_alert_status(alert_id, org_id, new_status)
        if not updated:
            raise KeyError(f"Business Alert '{alert_id}' not found.")

        await event_publisher.publish(
            event_type=f"early_warning.{new_status.value.lower()}",
            organization_id=org_id,
            message=f"Alert '{updated.title}' status updated to {new_status.value}.",
            metadata={"alert_id": alert_id, "status": new_status.value}
        )

        return AlertResponse.model_validate(updated)

    async def get_alert_explanation(self, alert_id: str, org_id: str) -> BusinessExplanationResponse:
        alert = await self.repo.get_alert_by_id(alert_id, org_id)
        if not alert:
            raise KeyError(f"Business Alert '{alert_id}' not found.")

        return BusinessExplanationResponse(
            alert_id=alert.id,
            why_detected=f"Alert '{alert.title}' detected by ChangeDetectionEngine based on variance threshold.",
            what_changed=alert.message,
            evidence_summary=f"Telemetry signals recorded with confidence {alert.confidence_score}%.",
            causation_vs_correlation="HYPOTHESIS: Change correlates with upstream ad network performance shifts.",
            affected_objective="Revenue Growth Objective",
            expected_impact=f"Severity {alert.severity.value} impact on Q1 milestone targets.",
            governance_required=alert.governance_required
        )
