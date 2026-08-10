from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.swarm.models import SwarmStatus, SwarmMessageType
from app.governance.models import RiskLevel

class SwarmSessionCreate(BaseModel):
    client_id: Optional[str] = None
    workflow_id: Optional[str] = None
    prediction_id: Optional[str] = None
    objective: str = Field(..., min_length=5, max_length=500)
    strategy: Optional[str] = None
    extra_metadata: Optional[Dict[str, Any]] = None

class SwarmSessionResponse(BaseModel):
    id: str
    organization_id: str
    client_id: Optional[str] = None
    workflow_id: Optional[str] = None
    prediction_id: Optional[str] = None
    status: SwarmStatus
    objective: str
    strategy: Optional[str] = None
    participating_agents: List[str]
    active_agents: List[str]
    completed_agents: List[str]
    failed_agents: List[str]
    consensus_score: float
    confidence_score: float
    conflict_count: int
    debate_rounds: int
    synthesis_output: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    extra_metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

class SwarmSessionListResponse(BaseModel):
    sessions: List[SwarmSessionResponse]
    total: int
    page: int
    page_size: int

class SwarmMessageResponse(BaseModel):
    id: str
    swarm_id: str
    organization_id: str
    source_agent: str
    target_agent: Optional[str] = None
    message_type: SwarmMessageType
    content: str
    evidence_refs: List[Dict[str, Any]]
    confidence: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SwarmConflictResponse(BaseModel):
    id: str
    swarm_id: str
    organization_id: str
    subject: str
    agent_a: str
    agent_b: str
    claim_a: str
    claim_b: str
    evidence_a: List[Dict[str, Any]]
    evidence_b: List[Dict[str, Any]]
    severity: RiskLevel
    resolution: Optional[str] = None
    resolved_by: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SwarmDebateResponse(BaseModel):
    id: str
    swarm_id: str
    organization_id: str
    round_number: int
    claim: str
    challenge: str
    supporting_evidence: List[Dict[str, Any]]
    counter_evidence: List[Dict[str, Any]]
    resolution: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
