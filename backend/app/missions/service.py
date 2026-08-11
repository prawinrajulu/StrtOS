import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.missions.models import (
    MissionModel, MissionSuccessCriterionModel, MissionPlanVersionModel,
    MissionStepModel, MissionCheckpointModel, MissionStatus, MissionStepStatus,
    MissionCheckpointDecision
)
from app.missions.schemas import (
    MissionCreate, MissionResponse, MissionEvaluationResponse, MissionReplanRequest,
    MissionCheckpointResponse
)
from app.missions.repository import MissionRepository
from app.missions.planner import MissionPlanningEngine, DependencyGraphEngine
from app.missions.engine import (
    MissionAutonomyEngine, MissionCheckpointEngine, MissionAdaptationEngine,
    MissionEvaluationEngine
)
from app.core.events.publisher import event_publisher

class MissionService:
    """Core Service orchestrating Autonomous Strategic Mission Execution."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = MissionRepository(session)
        self.planner = MissionPlanningEngine()
        self.dag_engine = DependencyGraphEngine()
        self.autonomy_engine = MissionAutonomyEngine()
        self.checkpoint_engine = MissionCheckpointEngine()
        self.adaptation_engine = MissionAdaptationEngine()
        self.eval_engine = MissionEvaluationEngine()

    async def create_mission(self, payload: MissionCreate, org_id: str) -> MissionResponse:
        mission = MissionModel(
            organization_id=org_id,
            objective_id=payload.objective_id,
            title=payload.title,
            summary=payload.summary or f"Autonomous Mission execution for '{payload.title}'.",
            status=MissionStatus.READY,
            current_version="v1.0.0",
            progress_percentage=0.0,
            risk_score=20.0,
            confidence_score=90.0
        )

        for c_in in payload.criteria:
            mission.criteria.append(
                MissionSuccessCriterionModel(
                    organization_id=org_id,
                    metric_name=c_in.metric_name,
                    baseline_value=c_in.baseline_value,
                    target_value=c_in.target_value,
                    unit=c_in.unit,
                    status="PROGRESSING"
                )
            )

        # Generate default steps
        default_steps = self.planner.create_default_steps(org_id)
        for idx, s_in in enumerate(default_steps, start=1):
            mission.steps.append(
                MissionStepModel(
                    organization_id=org_id,
                    step_order=idx,
                    title=s_in["title"],
                    action_type=s_in["action_type"],
                    status=MissionStepStatus.PENDING if idx > 1 else MissionStepStatus.READY,
                    dependencies_json=s_in["dependencies_json"],
                    risk_level=s_in["risk_level"],
                    autonomy_level=s_in["autonomy_level"]
                )
            )

        mission.plans.append(
            MissionPlanVersionModel(
                organization_id=org_id,
                version="v1.0.0",
                adaptation_reason="Initial Mission Plan generation.",
                delta_percentage=0.0
            )
        )

        saved = await self.repo.create_mission(mission)

        await event_publisher.publish(
            event_type="mission.created",
            organization_id=org_id,
            message=f"Mission '{saved.title}' created successfully.",
            metadata={"mission_id": saved.id, "version": saved.current_version}
        )

        return MissionResponse.model_validate(saved)

    async def get_mission(self, mission_id: str, org_id: str) -> MissionResponse:
        m = await self.repo.get_mission_by_id(mission_id, org_id)
        if not m:
            raise KeyError(f"Mission '{mission_id}' not found.")
        return MissionResponse.model_validate(m)

    async def list_missions(self, org_id: str, status: Optional[MissionStatus] = None) -> List[MissionResponse]:
        missions = await self.repo.list_missions(org_id, status=status)
        return [MissionResponse.model_validate(m) for m in missions]

    async def start_mission(self, mission_id: str, org_id: str) -> MissionResponse:
        m = await self.repo.update_mission_status(mission_id, org_id, MissionStatus.ACTIVE)
        if not m:
            raise KeyError(f"Mission '{mission_id}' not found.")

        await event_publisher.publish(
            event_type="mission.started",
            organization_id=org_id,
            message=f"Mission '{m.title}' activated.",
            metadata={"mission_id": mission_id}
        )
        return MissionResponse.model_validate(m)

    async def replan_mission(self, mission_id: str, payload: MissionReplanRequest, org_id: str) -> MissionResponse:
        m = await self.repo.get_mission_by_id(mission_id, org_id)
        if not m:
            raise KeyError(f"Mission '{mission_id}' not found.")

        new_ver, bounded_delta = self.adaptation_engine.apply_bounded_adaptation(
            m.current_version, payload.adaptation_delta_percentage
        )

        m.current_version = new_ver
        await self.repo.add_plan_version(
            MissionPlanVersionModel(
                organization_id=org_id,
                mission_id=mission_id,
                version=new_ver,
                parent_version=m.current_version,
                adaptation_reason=payload.reason,
                delta_percentage=bounded_delta
            )
        )

        await event_publisher.publish(
            event_type="mission.replanning",
            organization_id=org_id,
            message=f"Mission '{m.title}' replanned to version {new_ver} (Delta: {bounded_delta}%).",
            metadata={"mission_id": mission_id, "new_version": new_ver}
        )

        updated_m = await self.repo.get_mission_by_id(mission_id, org_id)
        return MissionResponse.model_validate(updated_m)

    async def evaluate_mission(self, mission_id: str, org_id: str) -> MissionEvaluationResponse:
        m = await self.repo.get_mission_by_id(mission_id, org_id)
        if not m:
            raise KeyError(f"Mission '{mission_id}' not found.")
        return self.eval_engine.evaluate_mission(m)
