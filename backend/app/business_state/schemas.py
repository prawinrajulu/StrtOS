from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from app.business_state.models import SnapshotType, AlertSeverity, AlertStatus, MetricDirection

class MetricSnapshotCreate(BaseModel):
    metric_name: str
    category: str = "General"
    value: float
    unit: str = "USD"
    confidence_score: float = 95.0
    source: str = "SystemTelemetry"

class MetricSnapshotResponse(BaseModel):
    id: str
    organization_id: str
    snapshot_id: str
    metric_name: str
    category: str
    value: float
    unit: str
    confidence_score: float
    source: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class StateSnapshotCreate(BaseModel):
    snapshot_type: SnapshotType = SnapshotType.CURRENT
    metrics: List[MetricSnapshotCreate] = []
    summary: Optional[str] = None

class StateSnapshotResponse(BaseModel):
    id: str
    organization_id: str
    snapshot_type: SnapshotType
    health_score: float
    health_status: str
    summary: Optional[str] = None
    created_at: datetime
    metrics: List[MetricSnapshotResponse] = []
    model_config = ConfigDict(from_attributes=True)

class SignalResponse(BaseModel):
    id: str
    organization_id: str
    metric_name: str
    previous_value: float
    current_value: float
    delta: float
    percentage_change: float
    direction: MetricDirection
    confidence: float
    evidence_ref: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ChangeResponse(BaseModel):
    id: str
    organization_id: str
    metric_name: str
    severity: AlertSeverity
    title: str
    description: Optional[str] = None
    previous_value: float
    current_value: float
    percentage_change: float
    confidence: float
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AlertResponse(BaseModel):
    id: str
    organization_id: str
    alert_type: str
    severity: AlertSeverity
    status: AlertStatus
    title: str
    message: str
    affected_objective_id: Optional[str] = None
    confidence_score: float
    recommended_action: Optional[str] = None
    governance_required: bool
    metadata_json: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class OpportunityResponse(BaseModel):
    title: str
    category: str
    expected_value: float
    confidence_score: float
    evidence: str
    recommended_action: str

class ThreatResponse(BaseModel):
    title: str
    severity: AlertSeverity
    confidence_score: float
    evidence: str
    potential_impact: str
    recommended_action: str

class BusinessHealthResponse(BaseModel):
    health_score: float
    health_status: str
    component_scores: Dict[str, float]
    recommendation: str

class BusinessExplanationResponse(BaseModel):
    alert_id: str
    why_detected: str
    what_changed: str
    evidence_summary: str
    causation_vs_correlation: str
    affected_objective: str
    expected_impact: str
    governance_required: bool
