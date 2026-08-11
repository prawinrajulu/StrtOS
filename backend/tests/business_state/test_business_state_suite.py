import pytest
from app.core.database import AsyncSessionLocal
from app.business_state.models import SnapshotType, AlertSeverity, AlertStatus, MetricDirection
from app.business_state.engine import StrategicEarlyWarningEngine
from app.business_state.service import BusinessStateService
from app.business_state.schemas import StateSnapshotCreate, MetricSnapshotCreate

@pytest.mark.asyncio
async def test_business_state_models_service_and_engines():
    async with AsyncSessionLocal() as session:
        service = BusinessStateService(session)
        org_id = "test-bs-org-1"

        # 1. Create Initial Snapshot (Baseline)
        snap1 = await service.create_snapshot(
            StateSnapshotCreate(
                snapshot_type=SnapshotType.BASELINE,
                metrics=[
                    MetricSnapshotCreate(metric_name="Revenue", category="Revenue", value=10000.0),
                    MetricSnapshotCreate(metric_name="Conversion Rate", category="Acquisition", value=4.0),
                    MetricSnapshotCreate(metric_name="SEO Score", category="SEO", value=90.0),
                    MetricSnapshotCreate(metric_name="Agent Reliability", category="Agent", value=95.0)
                ],
                summary="Initial baseline snapshot"
            ),
            org_id=org_id
        )
        assert snap1.health_status in ["EXCELLENT", "HEALTHY"]
        assert snap1.health_score >= 85.0

        # 2. Create Second Snapshot with Conversion Drop (Triggers Alert)
        snap2 = await service.create_snapshot(
            StateSnapshotCreate(
                snapshot_type=SnapshotType.CURRENT,
                metrics=[
                    MetricSnapshotCreate(metric_name="Revenue", category="Revenue", value=9500.0),
                    MetricSnapshotCreate(metric_name="Conversion Rate", category="Acquisition", value=2.0), # 50% drop!
                    MetricSnapshotCreate(metric_name="SEO Score", category="SEO", value=90.0),
                    MetricSnapshotCreate(metric_name="Agent Reliability", category="Agent", value=95.0)
                ],
                summary="Current snapshot with conversion shift"
            ),
            org_id=org_id
        )

        # 3. Verify Signals and Early Warning Alerts
        signals = await service.list_signals(org_id)
        assert len(signals) >= 1
        conv_signal = next(s for s in signals if s.metric_name == "Conversion Rate")
        assert conv_signal.direction == MetricDirection.DECREASE
        assert conv_signal.percentage_change == -50.0

        alerts = await service.list_alerts(org_id)
        assert len(alerts) >= 1
        critical_alert = alerts[0]
        assert critical_alert.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]

        # 4. Alert Lifecycle (Acknowledge -> Resolve)
        ack_alert = await service.update_alert_status(critical_alert.id, org_id, AlertStatus.ACKNOWLEDGED)
        assert ack_alert.status == AlertStatus.ACKNOWLEDGED

        res_alert = await service.update_alert_status(critical_alert.id, org_id, AlertStatus.RESOLVED)
        assert res_alert.status == AlertStatus.RESOLVED

        # 5. Opportunities & Threats Detection
        opps = await service.list_opportunities(org_id)
        assert len(opps) >= 1

        threats = await service.list_threats(org_id)
        assert len(threats) >= 1

        # 6. Alert Explanation
        exp = await service.get_alert_explanation(critical_alert.id, org_id)
        assert exp.alert_id == critical_alert.id

        # 7. Multi-Tenant Check
        try:
            await service.get_alert(critical_alert.id, org_id="unauthorized-org")
            assert False, "Should have failed multi-tenant check"
        except KeyError:
            pass
