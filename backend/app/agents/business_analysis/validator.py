from app.agents.business_analysis.schemas import BusinessAnalysisInput
from app.core.exceptions import ValidationException

class BusinessAnalysisValidator:
    """Validation pipeline for verifying input directives and business models."""
    def validate_input(self, data: BusinessAnalysisInput) -> bool:
        if not data.business_name or len(data.business_name.strip()) < 2:
            raise ValidationException("Invalid business_name: Must be at least 2 characters.")
        if not data.industry or len(data.industry.strip()) < 2:
            raise ValidationException("Invalid industry: Must specify a valid industry sector.")
        return True

    def validate_result_schema(self, result_dict: dict) -> bool:
        required_keys = [
            "business_name", "industry", "business_summary", "industry_analysis",
            "swot", "digital_maturity_score", "business_maturity_score",
            "target_audience", "customer_personas", "growth_opportunities",
            "business_risks", "recommendations", "confidence_score"
        ]
        for key in required_keys:
            if key not in result_dict:
                raise ValidationException(f"Missing required field in Business Analysis Result: {key}")
        return True
