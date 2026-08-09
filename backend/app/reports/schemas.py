from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from enum import Enum

class ReportStatusEnum(str, Enum):
    DRAFT = "DRAFT"
    FINAL = "FINAL"
    ARCHIVED = "ARCHIVED"

class ReportCreateRequest(BaseModel):
    workflow_id: str
    client_id: Optional[str] = None
    title: str = Field(..., min_length=2, max_length=150)
    executive_summary: Optional[str] = None
    report_type: str = "EXECUTIVE_SUMMARY"
    overall_score: int = 92
    confidence_score: float = 95.0
    key_findings: Optional[List[Any]] = None
    recommendations: Optional[List[Any]] = None
    agent_results: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None

class ReportUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=150)
    executive_summary: Optional[str] = None
    status: Optional[ReportStatusEnum] = None
    overall_score: Optional[int] = None

class ReportResponse(BaseModel):
    id: str
    workflow_id: str
    organization_id: str
    client_id: Optional[str] = None
    created_by: Optional[str] = None
    title: str
    executive_summary: Optional[str] = None
    report_type: str = "EXECUTIVE_SUMMARY"
    status: str = "FINAL"
    overall_score: int = 92
    confidence_score: float = 95.0
    key_findings: Optional[List[Any]] = None
    recommendations: Optional[List[Any]] = None
    agent_results: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    summary_json: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ReportListResponse(BaseModel):
    reports: List[ReportResponse]
    total: int
    page: int
    page_size: int

class ReportSummaryResponse(BaseModel):
    id: str
    workflow_id: str
    client_id: Optional[str] = None
    title: str
    executive_summary: Optional[str] = None
    status: str
    overall_score: int
    confidence_score: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ReportMetricsResponse(BaseModel):
    total_reports: int
    average_score: float
    average_confidence: float
    completed_reports: int
