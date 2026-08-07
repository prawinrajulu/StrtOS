from app.agents.competitor_research.schemas import CompetitorResearchInput
from app.core.exceptions import ValidationException

class CompetitorResearchValidator:
    """Validation pipeline for verifying input directives and competitor output models."""
    def validate_input(self, data: CompetitorResearchInput) -> bool:
        if not data.business_name or len(data.business_name.strip()) < 2:
            raise ValidationException("Invalid business_name: Must be at least 2 characters.")
        if not data.industry or len(data.industry.strip()) < 2:
            raise ValidationException("Invalid industry: Must specify a valid industry sector.")
        return True

    def validate_result_schema(self, result_dict: dict) -> bool:
        required_keys = [
            "business_name", "industry", "direct_competitors", "indirect_competitors",
            "market_position_summary", "pricing_comparison_summary", "strength_matrix",
            "weakness_matrix", "market_gaps", "competitive_opportunities",
            "recommendations", "confidence_score"
        ]
        for key in required_keys:
            if key not in result_dict:
                raise ValidationException(f"Missing required field in Competitor Research Result: {key}")
        return True
