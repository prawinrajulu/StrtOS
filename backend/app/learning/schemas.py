from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.learning.models import ReliabilityClass, PolicyStatus, AdaptationStatus

class AgentPerformanceResponse(BaseModel):
    id: str
    organization_id: str
    client_id: Optional[str] = None
    agent_name: str
    agent_version: str
    total_executions: int
    successful_executions: int
    degraded_executions: int
    failed_executions: int
    average_confidence: float
    average_latency_ms: float
    average_token_usage: int
    prediction_accuracy: float
    outcome_success_rate: float
    human_approval_rate: float
    human_rejection_rate: float
    swarm_consensus_rate: float
    tool_success_rate: float
    evidence_quality_score: float
    current_reliability_score: float
    reliability_class: ReliabilityClass
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ToolReliabilityResponse(BaseModel):
    id: str
    organization_id: str
    tool_name: str
    success_count: int
    failure_count: int
    timeout_count: int
    average_latency_ms: float
    availability_rate: float
    evidence_quality: float
    reliability_score: float
    last_successful_execution: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class LLMProviderPerformanceResponse(BaseModel):
    id: str
    organization_id: str
    provider: str
    model: str
    agent_name: Optional[str] = None
    average_latency_ms: float
    average_token_usage: int
    estimated_cost: float
    success_count: int
    failure_count: int
    retry_count: int
    fallback_count: int
    structured_output_success_rate: float
    confidence_score: float

    model_config = ConfigDict(from_attributes=True)

class AgentPolicyResponse(BaseModel):
    id: str
    organization_id: str
    agent_name: str
    policy_version: str
    configuration: Dict[str, Any]
    reason: str
    evidence_count: int
    confidence: float
    status: PolicyStatus
    created_by: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AgentAdaptationResponse(BaseModel):
    id: str
    organization_id: str
    agent_name: str
    title: str
    description: str
    previous_performance: Optional[Dict[str, Any]] = None
    expected_improvement: Optional[Dict[str, Any]] = None
    adaptation_delta: float
    status: AdaptationStatus
    approval_id: Optional[str] = None
    policy_id: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class LearningOverviewResponse(BaseModel):
    overall_system_reliability: float
    prediction_accuracy_avg: float
    total_adaptations_applied: int
    active_policies_count: int
    agent_performance: List[AgentPerformanceResponse]
    tool_reliability: List[ToolReliabilityResponse]
    provider_performance: List[LLMProviderPerformanceResponse]

class PolicyActivateResponse(BaseModel):
    policy_id: str
    agent_name: str
    policy_version: str
    status: PolicyStatus
    message: str

class PolicyRollbackResponse(BaseModel):
    agent_name: str
    rolled_back_policy_id: str
    activated_policy_id: str
    reason: str
