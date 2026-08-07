from app.agents.seo_audit.schemas import SEOAuditInput
from app.core.exceptions import ValidationException

class SEOAuditValidator:
    """Validation pipeline for verifying input website URLs and SEO output schemas."""
    def validate_input(self, data: SEOAuditInput) -> bool:
        if not data.website_url or not data.website_url.strip():
            raise ValidationException("Invalid website_url: URL cannot be empty.")
        
        url_lower = data.website_url.lower().strip()
        if not (url_lower.startswith("http://") or url_lower.startswith("https://")):
            raise ValidationException("Invalid website_url: Must start with http:// or https://")
        return True

    def validate_result_schema(self, result_dict: dict) -> bool:
        required_keys = [
            "website_url", "overall_seo_score", "technical_seo_score",
            "on_page_seo_score", "performance_score", "accessibility_score",
            "core_web_vitals", "critical_issues", "warnings",
            "recommendations", "priority_fixes", "confidence_score"
        ]
        for key in required_keys:
            if key not in result_dict:
                raise ValidationException(f"Missing required field in SEO Audit Result: {key}")
        return True
