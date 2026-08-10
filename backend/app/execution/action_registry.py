from typing import Dict, Any, Callable, Optional, List
from app.auth.models import UserRole
from app.governance.models import RiskLevel
from app.execution.models import AutonomyMode
from app.tools.registry import tool_registry

class ActionDefinition:
    def __init__(
        self,
        action_type: str,
        name: str,
        description: str,
        required_role: UserRole = UserRole.EMPLOYEE,
        minimum_risk_level: RiskLevel = RiskLevel.LOW,
        allowed_autonomy_modes: Optional[List[AutonomyMode]] = None,
        tool_name: Optional[str] = None
    ):
        self.action_type = action_type
        self.name = name
        self.description = description
        self.required_role = required_role
        self.minimum_risk_level = minimum_risk_level
        self.allowed_autonomy_modes = allowed_autonomy_modes or [
            AutonomyMode.MANUAL, AutonomyMode.ASSISTED, AutonomyMode.APPROVAL_REQUIRED
        ]
        self.tool_name = tool_name

class ActionRegistry:
    """
    Explicit Security Allowlist Registry for Autonomous Execution.
    Strictly forbids arbitrary shell, SQL, Python execution, or credentials access.
    """
    _registry: Dict[str, ActionDefinition] = {}

    @classmethod
    def register(cls, definition: ActionDefinition):
        cls._registry[definition.action_type] = definition

    @classmethod
    def get(cls, action_type: str) -> Optional[ActionDefinition]:
        return cls._registry.get(action_type)

    @classmethod
    def is_registered(cls, action_type: str) -> bool:
        return action_type in cls._registry

    @classmethod
    def list_actions(cls) -> List[Dict[str, Any]]:
        return [
            {
                "action_type": d.action_type,
                "name": d.name,
                "description": d.description,
                "required_role": d.required_role.value,
                "minimum_risk_level": d.minimum_risk_level.value,
                "tool_name": d.tool_name
            }
            for d in cls._registry.values()
        ]

# Register Explicit Safe Action Definitions
ActionRegistry.register(ActionDefinition(
    action_type="GENERATE_REPORT",
    name="Generate Executive Report",
    description="Synthesizes multi-agent analysis into formal executive client report",
    required_role=UserRole.EMPLOYEE,
    minimum_risk_level=RiskLevel.LOW,
    allowed_autonomy_modes=[AutonomyMode.MANUAL, AutonomyMode.ASSISTED, AutonomyMode.APPROVAL_REQUIRED, AutonomyMode.AUTONOMOUS]
))

ActionRegistry.register(ActionDefinition(
    action_type="RUN_WEBSITE_AUDIT",
    name="Execute Website Crawl & Audit",
    description="Crawls target website to extract DOM structure and metadata",
    required_role=UserRole.EMPLOYEE,
    minimum_risk_level=RiskLevel.LOW,
    allowed_autonomy_modes=[AutonomyMode.MANUAL, AutonomyMode.ASSISTED, AutonomyMode.APPROVAL_REQUIRED, AutonomyMode.AUTONOMOUS],
    tool_name="firecrawl"
))

ActionRegistry.register(ActionDefinition(
    action_type="RUN_SEO_AUDIT",
    name="Execute SEO Technical Audit",
    description="Performs keyword analysis, backlinks search, and technical SEO evaluation",
    required_role=UserRole.EMPLOYEE,
    minimum_risk_level=RiskLevel.LOW,
    allowed_autonomy_modes=[AutonomyMode.MANUAL, AutonomyMode.ASSISTED, AutonomyMode.APPROVAL_REQUIRED, AutonomyMode.AUTONOMOUS],
    tool_name="serper"
))

ActionRegistry.register(ActionDefinition(
    action_type="RUN_COMPETITOR_RESEARCH",
    name="Execute Competitor Market Search",
    description="Searches web for direct competitor positioning and pricing signals",
    required_role=UserRole.EMPLOYEE,
    minimum_risk_level=RiskLevel.LOW,
    allowed_autonomy_modes=[AutonomyMode.MANUAL, AutonomyMode.ASSISTED, AutonomyMode.APPROVAL_REQUIRED, AutonomyMode.AUTONOMOUS],
    tool_name="tavily"
))

ActionRegistry.register(ActionDefinition(
    action_type="RUN_PAGESPEED_ANALYSIS",
    name="Execute PageSpeed & Core Web Vitals Audit",
    description="Fetches performance telemetry and Core Web Vitals metrics",
    required_role=UserRole.EMPLOYEE,
    minimum_risk_level=RiskLevel.LOW,
    allowed_autonomy_modes=[AutonomyMode.MANUAL, AutonomyMode.ASSISTED, AutonomyMode.APPROVAL_REQUIRED, AutonomyMode.AUTONOMOUS],
    tool_name="pagespeed"
))

ActionRegistry.register(ActionDefinition(
    action_type="COLLECT_BUSINESS_DATA",
    name="Collect Google Business Listing Telemetry",
    description="Retrieves Google Maps listing signals and customer review data",
    required_role=UserRole.EMPLOYEE,
    minimum_risk_level=RiskLevel.LOW,
    allowed_autonomy_modes=[AutonomyMode.MANUAL, AutonomyMode.ASSISTED, AutonomyMode.APPROVAL_REQUIRED, AutonomyMode.AUTONOMOUS],
    tool_name="google_business"
))

ActionRegistry.register(ActionDefinition(
    action_type="REFRESH_CLIENT_ANALYSIS",
    name="Refresh Client Intelligence File",
    description="Re-runs specialist analysis for selected client workspace",
    required_role=UserRole.EMPLOYEE,
    minimum_risk_level=RiskLevel.MEDIUM,
    allowed_autonomy_modes=[AutonomyMode.MANUAL, AutonomyMode.ASSISTED, AutonomyMode.APPROVAL_REQUIRED]
))

ActionRegistry.register(ActionDefinition(
    action_type="CREATE_CAMPAIGN_DRAFT",
    name="Draft Campaign Flight Plan",
    description="Drafts promotional timeline and media budget allocation",
    required_role=UserRole.EMPLOYEE,
    minimum_risk_level=RiskLevel.MEDIUM,
    allowed_autonomy_modes=[AutonomyMode.MANUAL, AutonomyMode.ASSISTED, AutonomyMode.APPROVAL_REQUIRED]
))

ActionRegistry.register(ActionDefinition(
    action_type="GENERATE_MARKETING_PLAN",
    name="Generate Marketing Strategy Plan",
    description="Synthesizes digital maturity & brand positioning recommendations",
    required_role=UserRole.EMPLOYEE,
    minimum_risk_level=RiskLevel.MEDIUM,
    allowed_autonomy_modes=[AutonomyMode.MANUAL, AutonomyMode.ASSISTED, AutonomyMode.APPROVAL_REQUIRED]
))

ActionRegistry.register(ActionDefinition(
    action_type="RECORD_OUTCOME",
    name="Record Measured Outcome Data",
    description="Persists actual performance metrics into adaptive memory engine",
    required_role=UserRole.EMPLOYEE,
    minimum_risk_level=RiskLevel.LOW,
    allowed_autonomy_modes=[AutonomyMode.MANUAL, AutonomyMode.ASSISTED, AutonomyMode.APPROVAL_REQUIRED, AutonomyMode.AUTONOMOUS]
))
