import time
import json
from app.llm.providers.base_provider import BaseLLMProvider, LLMRequest, LLMResponse

class MockLLMProvider(BaseLLMProvider):
    """Deterministic Mock LLM Provider for unit and integration testing."""

    def __init__(self, model_name: str = "mock-model"):
        super().__init__(model_name)

    async def generate(self, request: LLMRequest) -> LLMResponse:
        start_time = time.time()
        
        # Deterministic JSON response payload tailored for specialist agents
        mock_payload = {
            "business_summary": "Mock Business Summary for deterministic automated testing.",
            "industry_analysis": "Mock Industry Analysis grounded in evidence.",
            "swot": {
                "strengths": ["Strong brand core", "High efficiency"],
                "weaknesses": ["Limited budget"],
                "opportunities": ["Digital expansion"],
                "threats": ["Market competition"]
            },
            "digital_maturity_score": 78,
            "business_maturity_score": 82,
            "target_audience": "Beauty Consumers",
            "customer_personas": [
                {
                    "name": "Convenience Seekers",
                    "demographics": "Age 25-45, Digital Natives",
                    "pain_points": ["Long waiting times"],
                    "buying_motivations": ["Speed of service"]
                },
                {
                    "name": "Quality Aficionados",
                    "demographics": "Age 30-50, High Income",
                    "pain_points": ["Lack of premium options"],
                    "buying_motivations": ["High quality"]
                }
            ],
            "growth_opportunities": ["Online direct acquisition"],
            "business_risks": ["Channel dependence"],
            "recommendations": ["Optimize digital flow"],
            "seo_score": 85,
            "technical_issues": [],
            "content_gaps": [],
            "backlink_opportunities": [],
            "competitor_analysis": [],
            "market_position": "Strong",
            "campaign_ideas": []
        }

        return LLMResponse(
            content=json.dumps(mock_payload),
            provider="Mock",
            model=self.model_name,
            status="SUCCESS",
            prompt_tokens=100,
            completion_tokens=200,
            total_tokens=300,
            estimated_cost_usd=0.0,
            latency_seconds=round(time.time() - start_time, 2)
        )
