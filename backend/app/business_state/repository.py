from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from app.business_state.models import (
    BusinessStateSnapshotModel, BusinessMetricSnapshotModel,
    BusinessSignalModel, BusinessChangeModel, BusinessAlertModel,
    SnapshotType, AlertStatus, AlertSeverity
)

class BusinessStateRepository:
    """Tenant-isolated repository for all Business State entities."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ---------------------------------------------------------------------------
    # SNAPSHOTS & METRICS
    # ---------------------------------------------------------------------------
    async def create_snapshot(self, snapshot: BusinessStateSnapshotModel) -> BusinessStateSnapshotModel:
        self.session.add(snapshot)
        await self.session.commit()
        return await self.get_snapshot_by_id(snapshot.id, snapshot.organization_id)

    async def get_snapshot_by_id(self, snapshot_id: str, org_id: str) -> Optional[BusinessStateSnapshotModel]:
        stmt = (
            select(BusinessStateSnapshotModel)
            .options(selectinload(BusinessStateSnapshotModel.metrics))
            .where(
                BusinessStateSnapshotModel.id == snapshot_id,
                BusinessStateSnapshotModel.organization_id == org_id
            )
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def get_latest_snapshot(self, org_id: str, snapshot_type: Optional[SnapshotType] = None) -> Optional[BusinessStateSnapshotModel]:
        stmt = (
            select(BusinessStateSnapshotModel)
            .options(selectinload(BusinessStateSnapshotModel.metrics))
            .where(BusinessStateSnapshotModel.organization_id == org_id)
        )
        if snapshot_type:
            stmt = stmt.where(BusinessStateSnapshotModel.snapshot_type == snapshot_type)
        stmt = stmt.order_by(BusinessStateSnapshotModel.created_at.desc())
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_snapshots(self, org_id: str, limit: int = 10) -> List[BusinessStateSnapshotModel]:
        stmt = (
            select(BusinessStateSnapshotModel)
            .options(selectinload(BusinessStateSnapshotModel.metrics))
            .where(BusinessStateSnapshotModel.organization_id == org_id)
            .order_by(BusinessStateSnapshotModel.created_at.desc())
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    # ---------------------------------------------------------------------------
    # SIGNALS & CHANGES
    # ---------------------------------------------------------------------------
    async def create_signal(self, signal: BusinessSignalModel) -> BusinessSignalModel:
        self.session.add(signal)
        await self.session.commit()
        await self.session.refresh(signal)
        return signal

    async def list_signals(self, org_id: str, limit: int = 20) -> List[BusinessSignalModel]:
        stmt = (
            select(BusinessSignalModel)
            .where(BusinessSignalModel.organization_id == org_id)
            .order_by(BusinessSignalModel.created_at.desc())
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def create_change(self, change: BusinessChangeModel) -> BusinessChangeModel:
        self.session.add(change)
        await self.session.commit()
        await self.session.refresh(change)
        return change

    async def list_changes(self, org_id: str, limit: int = 20) -> List[BusinessChangeModel]:
        stmt = (
            select(BusinessChangeModel)
            .where(BusinessChangeModel.organization_id == org_id)
            .order_by(BusinessChangeModel.created_at.desc())
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    # ---------------------------------------------------------------------------
    # ALERTS
    # ---------------------------------------------------------------------------
    async def create_alert(self, alert: BusinessAlertModel) -> BusinessAlertModel:
        self.session.add(alert)
        await self.session.commit()
        await self.session.refresh(alert)
        return alert

    async def get_alert_by_id(self, alert_id: str, org_id: str) -> Optional[BusinessAlertModel]:
        stmt = select(BusinessAlertModel).where(
            BusinessAlertModel.id == alert_id,
            BusinessAlertModel.organization_id == org_id
        )
        res = await self.session.execute(stmt)
        return res.scalars().first()

    async def list_alerts(self, org_id: str, status: Optional[AlertStatus] = None) -> List[BusinessAlertModel]:
        stmt = select(BusinessAlertModel).where(BusinessAlertModel.organization_id == org_id)
        if status:
            stmt = stmt.where(BusinessAlertModel.status == status)
        stmt = stmt.order_by(BusinessAlertModel.created_at.desc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def update_alert_status(self, alert_id: str, org_id: str, new_status: AlertStatus) -> Optional[BusinessAlertModel]:
        alert = await self.get_alert_by_id(alert_id, org_id)
        if not alert:
            return None
        alert.status = new_status
        await self.session.commit()
        await self.session.refresh(alert)
        return alert
