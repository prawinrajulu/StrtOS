import hashlib
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.experiments.models import (
    ExperimentModel, ExperimentVariantModel, ExperimentMeasurementModel,
    ExperimentStatus, ExperimentResult, VariantType
)
from app.experiments.schemas import ExperimentCreate, ExperimentMeasurementCreate
from app.experiments.engine import ExperimentDesignEngine, ExperimentEvaluator
from app.learning.models import AgentPolicyModel, PolicyStatus

class ExperimentRepository:
    """
    Handles persistence and assignment querying for experiments.
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_experiment(self, org_id: str, payload: ExperimentCreate, created_by: str) -> ExperimentModel:
        exp = ExperimentModel(
            organization_id=org_id,
            client_id=payload.client_id,
            workflow_id=payload.workflow_id,
            prediction_id=payload.prediction_id,
            baseline_policy_id=payload.baseline_policy_id,
            variant_policy_id=payload.variant_policy_id,
            experiment_name=payload.experiment_name,
            objective=payload.objective,
            hypothesis=payload.hypothesis,
            metric_name=payload.metric_name,
            baseline_value=payload.baseline_value,
            target_value=payload.target_value,
            minimum_detectable_effect=payload.minimum_detectable_effect,
            confidence_threshold=payload.confidence_threshold,
            status=ExperimentStatus.DRAFT,
            created_by=created_by
        )
        self.session.add(exp)
        await self.session.commit()
        await self.session.refresh(exp)
        return exp

    async def create_variant(self, exp_id: str, org_id: str, variant_type: VariantType, name: str, policy_id: str, config: Dict[str, Any]) -> ExperimentVariantModel:
        var = ExperimentVariantModel(
            experiment_id=exp_id,
            organization_id=org_id,
            variant_type=variant_type,
            variant_name=name,
            policy_id=policy_id,
            configuration=config
        )
        self.session.add(var)
        await self.session.commit()
        await self.session.refresh(var)
        return var

    async def get_experiment(self, exp_id: str, org_id: str) -> Optional[ExperimentModel]:
        stmt = select(ExperimentModel).where(
            ExperimentModel.id == exp_id,
            ExperimentModel.organization_id == org_id
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_variants(self, exp_id: str, org_id: str) -> List[ExperimentVariantModel]:
        stmt = select(ExperimentVariantModel).where(
            ExperimentVariantModel.experiment_id == exp_id,
            ExperimentVariantModel.organization_id == org_id
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def list_experiments(self, org_id: str) -> List[ExperimentModel]:
        stmt = select(ExperimentModel).where(
            ExperimentModel.organization_id == org_id
        ).order_by(ExperimentModel.created_at.desc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def record_measurement(self, exp_id: str, variant_id: str, org_id: str, variant_type: VariantType, payload: ExperimentMeasurementCreate) -> ExperimentMeasurementModel:
        meas = ExperimentMeasurementModel(
            experiment_id=exp_id,
            variant_id=variant_id,
            organization_id=org_id,
            execution_id=payload.execution_id,
            variant_type=variant_type,
            kpi_value=payload.kpi_value,
            success=1 if payload.success else 0,
            confidence=payload.confidence,
            latency_ms=payload.latency_ms,
            cost=payload.cost,
            human_approved=1 if payload.human_approved else 0,
            prediction_error=payload.prediction_error,
            metadata_json=payload.metadata_json
        )
        self.session.add(meas)

        # Update variant aggregate stats
        stmt = select(ExperimentMeasurementModel).where(
            ExperimentMeasurementModel.variant_id == variant_id
        )
        res = await self.session.execute(stmt)
        all_meas = list(res.scalars().all())
        all_meas.append(meas)

        n = len(all_meas)
        succ = sum(1 for m in all_meas if m.success == 1)
        fail = n - succ
        avg_kpi = sum(m.kpi_value for m in all_meas) / n
        avg_lat = sum(m.latency_ms for m in all_meas) / n
        avg_cost = sum(m.cost for m in all_meas) / n
        avg_conf = sum(m.confidence for m in all_meas) / n

        await self.session.execute(
            update(ExperimentVariantModel)
            .where(ExperimentVariantModel.id == variant_id)
            .values(
                sample_size=n,
                success_count=succ,
                failure_count=fail,
                average_kpi=avg_kpi,
                average_latency_ms=avg_lat,
                average_cost=avg_cost,
                average_confidence=avg_conf
            )
        )
        await self.session.commit()
        await self.session.refresh(meas)
        return meas

    async def get_measurements(self, exp_id: str, org_id: str, variant_type: Optional[VariantType] = None) -> List[ExperimentMeasurementModel]:
        stmt = select(ExperimentMeasurementModel).where(
            ExperimentMeasurementModel.experiment_id == exp_id,
            ExperimentMeasurementModel.organization_id == org_id
        )
        if variant_type:
            stmt = stmt.where(ExperimentMeasurementModel.variant_type == variant_type)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    @staticmethod
    def assign_execution(org_id: str, client_id: Optional[str], exp_id: str, execution_id: str) -> VariantType:
        """
        Deterministic hash assignment of an execution into CONTROL or VARIANT_A.
        """
        key = f"{org_id}:{client_id or ''}:{exp_id}:{execution_id}".encode("utf-8")
        hash_val = int(hashlib.md5(key).hexdigest(), 16)
        return VariantType.CONTROL if (hash_val % 2 == 0) else VariantType.VARIANT_A
