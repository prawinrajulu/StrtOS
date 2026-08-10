from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.execution.models import ActionModel, ActionStatus, PolicyDecision, AutonomyMode
from app.execution.schemas import (
    ActionCreate, ActionResponse, ActionListResponse, ActionEvaluateResponse,
    OutcomeMeasurementRequest, ClosedLoopOptimizationResponse
)
from app.execution.repository import ActionRepository
from app.execution.action_registry import ActionRegistry
from app.execution.policy_engine import PolicyEngine
from app.execution.executor import ActionExecutor
from app.execution.measurement import ClosedLoopOptimizationEngine
from app.governance.service import GovernanceService
from app.governance.schemas import ApprovalRequestCreate
from app.governance.models import DecisionType, ApprovalRequestModel
from app.core.events.publisher import event_publisher
from app.core.logging import logger

class ExecutionService:
    """
    High-level Execution Service managing Action proposals, Security Policy evaluation,
    Governance Integration, Tool Execution, Retries, and SSE Event Broadcasting.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ActionRepository(session)

    async def create_action(
        self,
        payload: ActionCreate,
        org_id: str,
        current_user: Any
    ) -> ActionResponse:
        # 1. Idempotency Check
        if payload.idempotency_key:
            existing = await self.repo.get_by_idempotency_key(payload.idempotency_key, org_id)
            if existing:
                logger.info(f"Idempotency hit for key '{payload.idempotency_key}'. Returning existing action {existing.id}.")
                return ActionResponse.model_validate(existing)

        # 2. Check Action Registry Allowlist
        if not ActionRegistry.is_registered(payload.action_type):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Action type '{payload.action_type}' is not registered in Action Registry."
            )

        # 3. Instantiate Action Model
        action = ActionModel(
            organization_id=org_id,
            client_id=payload.client_id,
            workflow_id=payload.workflow_id,
            prediction_id=payload.prediction_id,
            approval_id=payload.approval_id,
            created_by=current_user.id,
            action_type=payload.action_type,
            name=payload.name.strip(),
            description=payload.description,
            risk_level=payload.risk_level,
            autonomy_mode=payload.autonomy_mode,
            input_payload=payload.input_payload or {},
            idempotency_key=payload.idempotency_key,
            max_retries=payload.max_retries,
            status=ActionStatus.DRAFT,
            extra_metadata=payload.extra_metadata or {}
        )

        # 4. Evaluate Policy
        decision = PolicyEngine.evaluate_action(action, current_user)
        action.policy_decision = decision

        if decision == PolicyDecision.ALLOW:
            action.status = ActionStatus.APPROVED
        elif decision == PolicyDecision.REQUIRE_APPROVAL:
            action.status = ActionStatus.PENDING_APPROVAL
        else:
            action.status = ActionStatus.FAILED
            action.error_message = "Denied by Security Policy Engine."

        created = await self.repo.create(action)
        await self.session.commit()
        await self.session.refresh(created)

        # SSE Event
        await event_publisher.publish(
            event_type="action.created",
            workflow_id=created.workflow_id,
            organization_id=org_id,
            status=created.status.value,
            metadata={"action_id": created.id, "policy_decision": decision.value}
        )

        return ActionResponse.model_validate(created)

    async def get_action(self, action_id: str, org_id: str) -> ActionResponse:
        act = await self.repo.get_by_id_and_org(action_id, org_id)
        if not act:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action record not found.")
        return ActionResponse.model_validate(act)

    async def list_actions(
        self,
        org_id: str,
        page: int = 1,
        page_size: int = 20,
        client_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        prediction_id: Optional[str] = None,
        status_filter: Optional[ActionStatus] = None,
        action_type: Optional[str] = None,
        search: Optional[str] = None
    ) -> ActionListResponse:
        skip = (page - 1) * page_size
        actions, total = await self.repo.list_by_org(
            org_id=org_id,
            client_id=client_id,
            workflow_id=workflow_id,
            prediction_id=prediction_id,
            status_filter=status_filter,
            action_type=action_type,
            search=search,
            skip=skip,
            limit=page_size
        )
        dtos = [ActionResponse.model_validate(a) for a in actions]
        return ActionListResponse(actions=dtos, total=total, page=page, page_size=page_size)

    async def evaluate_action_policy(self, action_id: str, org_id: str, current_user: Any) -> ActionEvaluateResponse:
        act = await self.repo.get_by_id_and_org(action_id, org_id)
        if not act:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action not found.")

        approval = None
        if act.approval_id:
            gov_service = GovernanceService(self.session)
            try:
                approval_dto = await gov_service.get_approval_request(act.approval_id, org_id)
                from app.governance.models import ApprovalRequestModel
                stmt = await self.session.execute(
                    f"SELECT * FROM approval_requests WHERE id = '{act.approval_id}'"
                )
                approval = stmt.scalars().first()
            except Exception:
                approval = None

        decision = PolicyEngine.evaluate_action(act, current_user, approval=approval)
        act.policy_decision = decision
        await self.repo.update(act)
        await self.session.commit()

        return ActionEvaluateResponse(
            action_id=act.id,
            action_type=act.action_type,
            policy_decision=decision,
            required_approval=(decision == PolicyDecision.REQUIRE_APPROVAL),
            allowed_execution=(decision == PolicyDecision.ALLOW),
            explanation=f"Policy decision '{decision.value}' evaluated for risk level '{act.risk_level.value}'."
        )

    async def submit_action_for_approval(
        self,
        action_id: str,
        org_id: str,
        current_user: Any
    ) -> ActionResponse:
        act = await self.repo.get_by_id_and_org(action_id, org_id)
        if not act:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action not found.")

        if act.approval_id:
            return ActionResponse.model_validate(act)

        # Create Governance Approval Request
        gov_service = GovernanceService(self.session)
        approval_req = await gov_service.create_approval_request(
            payload=ApprovalRequestCreate(
                workflow_id=act.workflow_id,
                client_id=act.client_id,
                title=f"Action Approval Required: {act.name}",
                description=f"Authorize execution of action '{act.action_type}' for {act.name}.",
                decision_type=DecisionType.WORKFLOW_EXECUTION,
                requested_action=f"Execute {act.action_type}",
                ai_recommendation=f"Execute {act.action_type} under {act.autonomy_mode.value} policy.",
                ai_confidence_score=90.0
            ),
            org_id=org_id,
            creator_id=current_user.id
        )

        act.approval_id = approval_req.id
        act.status = ActionStatus.PENDING_APPROVAL
        act.policy_decision = PolicyDecision.REQUIRE_APPROVAL
        updated = await self.repo.update(act)
        await self.session.commit()

        await event_publisher.publish(
            event_type="action.approval.pending",
            workflow_id=updated.workflow_id,
            organization_id=org_id,
            status="PENDING_APPROVAL",
            metadata={"action_id": updated.id, "approval_id": approval_req.id}
        )

        return ActionResponse.model_validate(updated)

    async def execute_action(
        self,
        action_id: str,
        org_id: str,
        current_user: Any
    ) -> ActionResponse:
        act = await self.repo.get_by_id_and_org(action_id, org_id)
        if not act:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action not found.")

        if act.status == ActionStatus.COMPLETED:
            return ActionResponse.model_validate(act)

        # Evaluate policy & governance approval
        approval = None
        if act.approval_id:
            from app.governance.models import ApprovalRequestModel
            from sqlalchemy import select
            stmt = select(ApprovalRequestModel).where(ApprovalRequestModel.id == act.approval_id)
            res = await self.session.execute(stmt)
            approval = res.scalars().first()

        decision = PolicyEngine.evaluate_action(act, current_user, approval=approval)
        act.policy_decision = decision

        if decision == PolicyDecision.DENY:
            act.status = ActionStatus.FAILED
            act.error_message = "Execution denied by Security Policy Engine."
            await self.repo.update(act)
            await self.session.commit()
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Execution denied by Security Policy Engine.")

        if decision == PolicyDecision.REQUIRE_APPROVAL:
            act.status = ActionStatus.PENDING_APPROVAL
            await self.repo.update(act)
            await self.session.commit()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Action requires explicit Governance Approval before execution.")

        # Transition to RUNNING
        ActionExecutor.validate_transition(act.status, ActionStatus.RUNNING)
        act.status = ActionStatus.RUNNING
        act.started_at = datetime.now(timezone.utc)
        await self.repo.update(act)
        await self.session.commit()

        await event_publisher.publish(
            event_type="action.started",
            workflow_id=act.workflow_id,
            organization_id=org_id,
            status="RUNNING",
            metadata={"action_id": act.id}
        )

        # Execute handler via ActionExecutor
        exec_status, output, error_msg = await ActionExecutor.execute_action_handler(act, current_user, approval=approval)

        act.status = exec_status
        act.output_payload = output
        act.error_message = error_msg
        act.completed_at = datetime.now(timezone.utc)
        updated = await self.repo.update(act)
        await self.session.commit()

        event_name = "action.completed" if exec_status == ActionStatus.COMPLETED else "action.failed"
        await event_publisher.publish(
            event_type=event_name,
            workflow_id=updated.workflow_id,
            organization_id=org_id,
            status=updated.status.value,
            metadata={"action_id": updated.id}
        )

        return ActionResponse.model_validate(updated)

    async def cancel_action(self, action_id: str, org_id: str, current_user: Any) -> ActionResponse:
        act = await self.repo.get_by_id_and_org(action_id, org_id)
        if not act:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action not found.")

        ActionExecutor.validate_transition(act.status, ActionStatus.CANCELLED)
        act.status = ActionStatus.CANCELLED
        updated = await self.repo.update(act)
        await self.session.commit()
        return ActionResponse.model_validate(updated)

    async def retry_action(self, action_id: str, org_id: str, current_user: Any) -> ActionResponse:
        act = await self.repo.get_by_id_and_org(action_id, org_id)
        if not act:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action not found.")

        if act.retry_count >= act.max_retries:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Maximum retries exceeded.")

        act.retry_count += 1
        act.status = ActionStatus.APPROVED
        await self.repo.update(act)
        await self.session.commit()

        return await self.execute_action(action_id, org_id, current_user)

    async def measure_action_outcome(
        self,
        action_id: str,
        payload: OutcomeMeasurementRequest,
        org_id: str
    ) -> ClosedLoopOptimizationResponse:
        act = await self.repo.get_by_id_and_org(action_id, org_id)
        if not act:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action not found.")

        result_dict = await ClosedLoopOptimizationEngine.process_closed_loop_measurement(
            action=act,
            actual_metric_value=payload.actual_metric_value,
            session=self.session
        )

        return ClosedLoopOptimizationResponse.model_validate(result_dict)
