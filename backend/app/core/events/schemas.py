from typing import Optional, Dict, Any
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

class RealtimeEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    workflow_id: Optional[str] = None
    task_id: Optional[str] = None
    agent_name: Optional[str] = None
    organization_id: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: Optional[str] = None
    progress: Optional[int] = None
    message: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    tool_name: Optional[str] = None
    token_usage: Optional[int] = None
    latency_ms: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
