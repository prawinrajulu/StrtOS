from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.knowledge.models import NodeTypeEnum, RelationTypeEnum, CausalStatusEnum

class KnowledgeNodeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    node_type: NodeTypeEnum
    entity_id: str
    label: str
    confidence: float
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, alias="node_metadata")
    created_at: datetime
    updated_at: datetime

class KnowledgeRelationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    source_node_id: str
    target_node_id: str
    relation_type: RelationTypeEnum
    causal_status: CausalStatusEnum
    confidence: float
    weight: float
    evidence_summary: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, alias="relation_metadata")
    created_at: datetime

class CausalObservationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    organization_id: str
    relation_id: str
    supporting_observations: List[Any]
    contradicting_observations: List[Any]
    causal_score: float
    status: CausalStatusEnum
    explanation: str
    observed_at: datetime

class DecisionChainResponse(BaseModel):
    decision_id: str
    label: str
    evidence_used: List[Dict[str, Any]]
    agents_involved: List[Dict[str, Any]]
    memories_used: List[Dict[str, Any]]
    prediction: Optional[Dict[str, Any]] = None
    policy_version: Optional[Dict[str, Any]] = None
    approval: Optional[Dict[str, Any]] = None
    action: Optional[Dict[str, Any]] = None
    outcome: Optional[Dict[str, Any]] = None
    lessons: List[Dict[str, Any]]
    causal_relationships: List[KnowledgeRelationResponse]
    confidence: float

class RootCauseContributor(BaseModel):
    contributor_name: str
    contributor_type: str
    contribution_score: float
    rank: int
    explanation: str

class OutcomeRootCauseResponse(BaseModel):
    outcome_id: str
    status: str
    primary_root_cause: str
    contributors: List[RootCauseContributor]
    supporting_observations: List[str]
    contradicting_observations: List[str]
    confidence: float

class AgentInfluenceResponse(BaseModel):
    agent_name: str
    total_contributions: int
    decision_influence_score: float
    outcome_correlation: float
    evidence_contribution_score: float
    historical_reliability: float
    causal_lessons_count: int

class KnowledgeOverviewResponse(BaseModel):
    total_nodes: int
    total_relations: int
    validated_causal_links: int
    causal_hypotheses: int
    contradictions_count: int
    average_causal_confidence: float
    nodes: List[KnowledgeNodeResponse]
    relations: List[KnowledgeRelationResponse]
