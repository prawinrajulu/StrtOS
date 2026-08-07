from app.agents.campaign_planner.schemas import CampaignPlanningInput
from app.core.exceptions import ValidationException

class CampaignPlannerValidator:
    """Validation pipeline verifying strategy inputs and campaign plan output schemas."""
    def validate_input(self, data: CampaignPlanningInput) -> bool:
        if not data.marketing_strategy_result:
            raise ValidationException("Invalid Campaign Planning Input: Missing marketing_strategy_result.")
        return True

    def validate_result_schema(self, result_dict: dict) -> bool:
        required_keys = [
            "campaign_summary", "campaign_timeline", "execution_plan",
            "channel_allocation", "creative_requirements", "budget_allocation",
            "weekly_roadmap", "kpis", "launch_checklist", "optimization_plan",
            "confidence_score"
        ]
        for key in required_keys:
            if key not in result_dict:
                raise ValidationException(f"Missing required field in Campaign Planning Result: {key}")
        return True
