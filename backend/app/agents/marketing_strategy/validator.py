from app.agents.marketing_strategy.schemas import MarketingStrategyInput
from app.core.exceptions import ValidationException

class MarketingStrategyValidator:
    """Validation pipeline verifying upstream outputs and strategy models."""
    def validate_input(self, data: MarketingStrategyInput) -> bool:
        if not data.business_analysis_result:
            raise ValidationException("Invalid Marketing Strategy Input: Missing business_analysis_result.")
        if not data.seo_audit_result:
            raise ValidationException("Invalid Marketing Strategy Input: Missing seo_audit_result.")
        if not data.competitor_research_result:
            raise ValidationException("Invalid Marketing Strategy Input: Missing competitor_research_result.")
        return True

    def validate_result_schema(self, result_dict: dict) -> bool:
        required_keys = [
            "brand_positioning", "unique_value_proposition", "marketing_objectives",
            "channel_recommendations", "content_pillars", "customer_journey",
            "marketing_funnel", "budget_allocation", "kpis", "roi_projection",
            "growth_roadmap", "confidence_score"
        ]
        for key in required_keys:
            if key not in result_dict:
                raise ValidationException(f"Missing required field in Marketing Strategy Result: {key}")
        return True
