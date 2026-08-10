from typing import Optional, Any, Dict, List
from app.auth.models import UserModel, UserRole
from app.governance.models import RiskLevel, ApprovalStatus, ApprovalRequestModel
from app.execution.models import ActionModel, AutonomyMode, PolicyDecision, ActionStatus
from app.execution.action_registry import ActionRegistry, ActionDefinition

class PolicyEngine:
    """
    Deterministic Security Policy Engine for Autonomous AI Execution.
    Evaluates role permissions, organization multi-tenancy, risk level rules,
    governance approval state, self-approval prevention, and action allowlists.
    """

    @classmethod
    def evaluate_action(
        self,
        action: ActionModel,
        user: UserModel,
        approval: Optional[ApprovalRequestModel] = None,
        client_org_id: Optional[str] = None
    ) -> PolicyDecision:
        # 1. Allowlist Action Registration Check
        action_def = ActionRegistry.get(action.action_type)
        if not action_def:
            return PolicyDecision.DENY

        # 2. Multi-Tenant Security Scope Check
        if action.organization_id != user.organization_id:
            return PolicyDecision.DENY

        if client_org_id and client_org_id != user.organization_id:
            return PolicyDecision.DENY

        # 3. RBAC Role Check
        role_hierarchy = {
            UserRole.VIEWER: 1,
            UserRole.EMPLOYEE: 2,
            UserRole.MANAGER: 3,
            UserRole.ORG_ADMIN: 4,
            UserRole.SUPER_ADMIN: 5
        }
        user_rank = role_hierarchy.get(user.role, 0)
        required_rank = role_hierarchy.get(action_def.required_role, 2)

        if user_rank < required_rank:
            return PolicyDecision.DENY

        # 4. Self-Approval Prevention Check
        if approval:
            if approval.requested_by == approval.reviewed_by:
                return PolicyDecision.DENY
            if approval.organization_id != user.organization_id:
                return PolicyDecision.DENY

        # 5. Risk & Autonomy Evaluation Rules
        # Rule A: HIGH or CRITICAL Risk Actions ALWAYS require explicit Governance Approval
        if action.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            if not approval or approval.status != ApprovalStatus.APPROVED:
                return PolicyDecision.REQUIRE_APPROVAL

        # Rule B: MEDIUM Risk Actions require Governance Approval unless already approved
        if action.risk_level == RiskLevel.MEDIUM:
            if not approval or approval.status != ApprovalStatus.APPROVED:
                return PolicyDecision.REQUIRE_APPROVAL

        # Rule C: Autonomy Mode = APPROVAL_REQUIRED always requires approval
        if action.autonomy_mode == AutonomyMode.APPROVAL_REQUIRED:
            if not approval or approval.status != ApprovalStatus.APPROVED:
                return PolicyDecision.REQUIRE_APPROVAL

        # Rule D: LOW Risk Actions with AUTONOMOUS mode on allowlisted tools execute automatically
        if action.risk_level == RiskLevel.LOW and action.autonomy_mode == AutonomyMode.AUTONOMOUS:
            return PolicyDecision.ALLOW

        # Rule E: If valid Governance Approval exists and is APPROVED
        if approval and approval.status == ApprovalStatus.APPROVED:
            return PolicyDecision.ALLOW

        # Rule F: Default for ASSISTED / MANUAL actions with LOW risk
        if action.risk_level == RiskLevel.LOW and user_rank >= 2:
            return PolicyDecision.ALLOW

        return PolicyDecision.REQUIRE_APPROVAL
