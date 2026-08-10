from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.governance.models import ApprovalRequestModel, ApprovalStatus, RiskLevel, DecisionType
from app.governance.schemas import (
    ApprovalRequestCreate, ApprovalRequestUpdate, ApprovalActionRequest,
    ApprovalResponse, ApprovalListResponse, RiskAssessmentResponse
)
from app.governance.repository import GovernanceRepository
from app.governance.risk_engine import calculate_decision_risk
from app.auth.models import UserModel, UserRole, AuditLogModel
from app.core.events.publisher import event_publisher
from app.core.logging import logger

class GovernanceService:
    """Core Service managing StrtOS Governance Approval Requests, Risk Assessment, and RBAC Enforcement."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = GovernanceRepository(session)

    async def create_approval_request(
        self,
        payload: ApprovalRequestCreate,
        org_id: str,
        creator_id: str
    ) -> ApprovalResponse:
        # Calculate Risk Score & Risk Level deterministically
        risk_res = calculate_decision_risk(
            ai_confidence_score=payload.ai_confidence_score,
            evidence_count=payload.evidence_count,
            decision_type=payload.decision_type,
            is_reversible=payload.is_reversible,
            has_unavailable_evidence=payload.has_unavailable_evidence
        )

        approval = ApprovalRequestModel(
            organization_id=org_id,
            workflow_id=payload.workflow_id,
            client_id=payload.client_id,
            report_id=payload.report_id,
            requested_by=creator_id,
            title=payload.title.strip(),
            description=payload.description,
            decision_type=payload.decision_type,
            risk_level=risk_res["risk_level"],
            risk_score=risk_res["risk_score"],
            status=ApprovalStatus.PENDING_APPROVAL,
            requested_action=payload.requested_action,
            ai_recommendation=payload.ai_recommendation,
            ai_confidence_score=payload.ai_confidence_score,
            evidence_count=payload.evidence_count,
            provider=payload.provider,
            model=payload.model,
            extra_metadata=payload.extra_metadata or {}
        )

        created = await self.repo.create(approval)

        # Audit Log
        audit = AuditLogModel(
            organization_id=org_id,
            user_id=creator_id,
            action="APPROVAL_REQUEST_CREATED",
            details={
                "approval_id": created.id,
                "workflow_id": created.workflow_id,
                "risk_level": created.risk_level.value,
                "risk_score": created.risk_score
            }
        )
        self.session.add(audit)

        await self.session.commit()
        await self.session.refresh(created)

        # Real-time SSE event publishing
        await event_publisher.publish(
            event_type="approval.created",
            workflow_id=created.workflow_id,
            organization_id=org_id,
            status=created.status.value,
            provider=created.provider,
            model=created.model,
            metadata={"approval_id": created.id, "risk_level": created.risk_level.value}
        )
        await event_publisher.publish(
            event_type="approval.pending",
            workflow_id=created.workflow_id,
            organization_id=org_id,
            status=created.status.value,
            metadata={"approval_id": created.id, "requested_by": creator_id}
        )

        return ApprovalResponse.model_validate(created)

    async def get_approval_request(self, approval_id: str, org_id: str) -> ApprovalResponse:
        approval = await self.repo.get_by_id_and_org(approval_id, org_id)
        if not approval:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval request not found.")
        return ApprovalResponse.model_validate(approval)

    async def list_approval_requests(
        self,
        org_id: str,
        page: int = 1,
        page_size: int = 20,
        status_filter: Optional[str] = None,
        risk_level: Optional[str] = None,
        workflow_id: Optional[str] = None,
        client_id: Optional[str] = None,
        search: Optional[str] = None
    ) -> ApprovalListResponse:
        skip = (page - 1) * page_size
        approvals, total = await self.repo.list_by_org(
            org_id=org_id,
            skip=skip,
            limit=page_size,
            status=status_filter,
            risk_level=risk_level,
            workflow_id=workflow_id,
            client_id=client_id,
            search=search
        )
        dtos = [ApprovalResponse.model_validate(a) for a in approvals]
        return ApprovalListResponse(approvals=dtos, total=total, page=page, page_size=page_size)

    async def approve_request(
        self,
        approval_id: str,
        payload: ApprovalActionRequest,
        org_id: str,
        reviewer_user: UserModel
    ) -> ApprovalResponse:
        approval = await self.repo.get_by_id_and_org(approval_id, org_id)
        if not approval:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval request not found.")

        # State Machine Validation
        if approval.status != ApprovalStatus.PENDING_APPROVAL:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot approve request in '{approval.status.value}' state. Must be PENDING_APPROVAL."
            )

        # RBAC Role Check
        if reviewer_user.role not in [UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN, UserRole.MANAGER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User role is not authorized to approve governance requests."
            )

        # Self-Approval Check: Requestor cannot approve own request
        if approval.requested_by == reviewer_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Self-approval forbidden. Requestor cannot approve their own governance request."
            )

        approval.status = ApprovalStatus.APPROVED
        approval.reviewed_by = reviewer_user.id
        approval.reviewed_at = datetime.now(timezone.utc)
        approval.reviewer_comment = payload.comment or "Approved by governance reviewer."

        updated = await self.repo.update(approval)

        # Audit Log
        audit = AuditLogModel(
            organization_id=org_id,
            user_id=reviewer_user.id,
            action="APPROVAL_APPROVED",
            details={"approval_id": updated.id, "workflow_id": updated.workflow_id}
        )
        self.session.add(audit)

        await self.session.commit()
        await self.session.refresh(updated)

        # Real-time Event
        await event_publisher.publish(
            event_type="approval.approved",
            workflow_id=updated.workflow_id,
            organization_id=org_id,
            status=updated.status.value,
            metadata={"approval_id": updated.id, "reviewed_by": reviewer_user.id}
        )

        return ApprovalResponse.model_validate(updated)

    async def reject_request(
        self,
        approval_id: str,
        payload: ApprovalActionRequest,
        org_id: str,
        reviewer_user: UserModel
    ) -> ApprovalResponse:
        approval = await self.repo.get_by_id_and_org(approval_id, org_id)
        if not approval:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval request not found.")

        # State Machine Validation
        if approval.status != ApprovalStatus.PENDING_APPROVAL:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot reject request in '{approval.status.value}' state. Must be PENDING_APPROVAL."
            )

        # RBAC Role Check
        if reviewer_user.role not in [UserRole.SUPER_ADMIN, UserRole.ORG_ADMIN, UserRole.MANAGER]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User role is not authorized to reject governance requests."
            )

        approval.status = ApprovalStatus.REJECTED
        approval.reviewed_by = reviewer_user.id
        approval.reviewed_at = datetime.now(timezone.utc)
        approval.rejection_reason = payload.rejection_reason or payload.comment or "Rejected by governance reviewer."

        updated = await self.repo.update(approval)

        # Audit Log
        audit = AuditLogModel(
            organization_id=org_id,
            user_id=reviewer_user.id,
            action="APPROVAL_REJECTED",
            details={"approval_id": updated.id, "workflow_id": updated.workflow_id, "reason": updated.rejection_reason}
        )
        self.session.add(audit)

        await self.session.commit()
        await self.session.refresh(updated)

        # Real-time Event
        await event_publisher.publish(
            event_type="approval.rejected",
            workflow_id=updated.workflow_id,
            organization_id=org_id,
            status=updated.status.value,
            metadata={"approval_id": updated.id, "reviewed_by": reviewer_user.id, "reason": updated.rejection_reason}
        )

        return ApprovalResponse.model_validate(updated)

    async def request_changes(
        self,
        approval_id: str,
        payload: ApprovalActionRequest,
        org_id: str,
        reviewer_user: UserModel
    ) -> ApprovalResponse:
        approval = await self.repo.get_by_id_and_org(approval_id, org_id)
        if not approval:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval request not found.")

        if approval.status != ApprovalStatus.PENDING_APPROVAL:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot request changes for request in '{approval.status.value}' state."
            )

        approval.status = ApprovalStatus.CHANGES_REQUESTED
        approval.reviewed_by = reviewer_user.id
        approval.reviewed_at = datetime.now(timezone.utc)
        approval.reviewer_comment = payload.comment or "Changes requested by governance reviewer."

        updated = await self.repo.update(approval)
        await self.session.commit()
        await self.session.refresh(updated)

        await event_publisher.publish(
            event_type="approval.changes_requested",
            workflow_id=updated.workflow_id,
            organization_id=org_id,
            status=updated.status.value,
            metadata={"approval_id": updated.id, "comment": updated.reviewer_comment}
        )

        return ApprovalResponse.model_validate(updated)

    async def cancel_request(
        self,
        approval_id: str,
        org_id: str,
        user_id: str
    ) -> ApprovalResponse:
        approval = await self.repo.get_by_id_and_org(approval_id, org_id)
        if not approval:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval request not found.")

        if approval.status not in [ApprovalStatus.PENDING_APPROVAL, ApprovalStatus.DRAFT, ApprovalStatus.CHANGES_REQUESTED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel request in '{approval.status.value}' terminal state."
            )

        approval.status = ApprovalStatus.CANCELLED
        updated = await self.repo.update(approval)
        await self.session.commit()
        await self.session.refresh(updated)

        await event_publisher.publish(
            event_type="approval.cancelled",
            workflow_id=updated.workflow_id,
            organization_id=org_id,
            status=updated.status.value,
            metadata={"approval_id": updated.id}
        )

        return ApprovalResponse.model_validate(updated)
