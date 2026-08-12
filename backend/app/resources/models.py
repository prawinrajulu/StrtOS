import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, Integer, JSON, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


# ─────────────────────────── Enumerations ────────────────────────────────────

class ResourceType(str, enum.Enum):
    HUMAN = "HUMAN"
    AI_AGENT = "AI_AGENT"
    BUDGET = "BUDGET"
    TIME = "TIME"
    COMPUTE = "COMPUTE"
    TOOL = "TOOL"
    EXECUTION_CAPACITY = "EXECUTION_CAPACITY"
    MARKETING_CAPACITY = "MARKETING_CAPACITY"
    OPERATIONAL_CAPACITY = "OPERATIONAL_CAPACITY"


class ResourceStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    LIMITED = "LIMITED"
    EXHAUSTED = "EXHAUSTED"
    BLOCKED = "BLOCKED"
    DEGRADED = "DEGRADED"
    UNKNOWN = "UNKNOWN"


class AllocationPlanStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SIMULATED = "SIMULATED"
    PENDING_GOVERNANCE = "PENDING_GOVERNANCE"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    ROLLED_BACK = "ROLLED_BACK"
    DEGRADED = "DEGRADED"


class BottleneckSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ConflictSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ─────────────────────────── ORM Models ──────────────────────────────────────

class ResourceModel(Base):
    """Core resource entity with deterministic capacity tracking."""
    __tablename__ = "resources"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False, index=True)
    client_id = Column(String, nullable=True, index=True)
    name = Column(String, nullable=False)
    resource_type = Column(Enum(ResourceType), nullable=False, index=True)
    description = Column(Text, nullable=True)
    total_capacity = Column(Float, nullable=True)  # NULL = UNKNOWN
    available_capacity = Column(Float, nullable=True)
    allocated_capacity = Column(Float, nullable=False, default=0.0)
    utilization_percentage = Column(Float, nullable=False, default=0.0)
    unit = Column(String, nullable=False, default="UNITS")
    cost_per_unit = Column(Float, nullable=True)  # NULL = unknown cost
    status = Column(Enum(ResourceStatus), nullable=False, default=ResourceStatus.UNKNOWN, index=True)
    is_shared = Column(Boolean, default=False)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    capacities = relationship("ResourceCapacityModel", back_populates="resource", cascade="all, delete-orphan")
    allocations = relationship("ResourceAllocationModel", back_populates="resource", cascade="all, delete-orphan")
    constraints = relationship("ResourceConstraintModel", back_populates="resource", cascade="all, delete-orphan")
    conflicts = relationship("ResourceConflictModel", back_populates="resource", cascade="all, delete-orphan")
    utilizations = relationship("ResourceUtilizationModel", back_populates="resource", cascade="all, delete-orphan")


class ResourceCapacityModel(Base):
    """Time-series capacity snapshots for trend analysis."""
    __tablename__ = "resource_capacities"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, nullable=False, index=True)
    resource_id = Column(String, ForeignKey("resources.id"), nullable=False, index=True)
    total_capacity = Column(Float, nullable=True)
    available_capacity = Column(Float, nullable=True)
    allocated_capacity = Column(Float, nullable=False, default=0.0)
    utilization_percentage = Column(Float, nullable=False, default=0.0)
    is_measured = Column(Boolean, default=False)  # True=actual telemetry, False=estimated
    period_start = Column(DateTime(timezone=True), nullable=True)
    period_end = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    resource = relationship("ResourceModel", back_populates="capacities")


class ResourceAllocationModel(Base):
    """Immutable per-mission resource allocation record."""
    __tablename__ = "resource_allocations"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, nullable=False, index=True)
    resource_id = Column(String, ForeignKey("resources.id"), nullable=False, index=True)
    mission_id = Column(String, ForeignKey("missions.id"), nullable=True, index=True)
    plan_id = Column(String, nullable=True, index=True)
    plan_version = Column(String, nullable=False, default="v1.0.0")
    requested_amount = Column(Float, nullable=False)
    allocated_amount = Column(Float, nullable=False, default=0.0)
    priority_score = Column(Float, nullable=False, default=50.0)
    is_mandatory = Column(Boolean, default=True)
    allocation_reason = Column(Text, nullable=True)
    opportunity_cost_score = Column(Float, nullable=True)
    status = Column(String, nullable=False, default="PENDING")  # PENDING, ACTIVE, RELEASED, FAILED
    governance_approval_id = Column(String, nullable=True)
    allocated_at = Column(DateTime(timezone=True), nullable=True)
    released_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    resource = relationship("ResourceModel", back_populates="allocations")


class ResourceConstraintModel(Base):
    """Hard/soft constraints per resource."""
    __tablename__ = "resource_constraints"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, nullable=False, index=True)
    resource_id = Column(String, ForeignKey("resources.id"), nullable=False, index=True)
    constraint_type = Column(String, nullable=False)  # MAX_ALLOCATION, MIN_RESERVE, POLICY, GOVERNANCE
    limit_value = Column(Float, nullable=False)
    current_value = Column(Float, nullable=False, default=0.0)
    is_hard_constraint = Column(Boolean, default=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    resource = relationship("ResourceModel", back_populates="constraints")


class ResourceConflictModel(Base):
    """Detected resource conflicts between missions."""
    __tablename__ = "resource_conflicts"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, nullable=False, index=True)
    resource_id = Column(String, ForeignKey("resources.id"), nullable=False, index=True)
    mission_ids_json = Column(JSON, nullable=False, default=list)  # list of conflicting mission IDs
    required_capacity = Column(Float, nullable=False)
    available_capacity = Column(Float, nullable=False)
    shortage = Column(Float, nullable=False)
    severity = Column(Enum(ConflictSeverity), nullable=False, default=ConflictSeverity.MEDIUM)
    resolution_options_json = Column(JSON, nullable=True)
    is_resolved = Column(Boolean, default=False)
    detected_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    resource = relationship("ResourceModel", back_populates="conflicts")


class ResourceUtilizationModel(Base):
    """Running utilization snapshots for monitoring."""
    __tablename__ = "resource_utilizations"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, nullable=False, index=True)
    resource_id = Column(String, ForeignKey("resources.id"), nullable=False, index=True)
    utilization_percentage = Column(Float, nullable=False)
    allocated_capacity = Column(Float, nullable=False)
    available_capacity = Column(Float, nullable=True)
    status = Column(Enum(ResourceStatus), nullable=False, default=ResourceStatus.AVAILABLE)
    snapshot_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    resource = relationship("ResourceModel", back_populates="utilizations")


class ResourceAllocationPlanModel(Base):
    """Full allocation plan with lifecycle, governance, and versioning."""
    __tablename__ = "resource_allocation_plans"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, nullable=False, index=True)
    portfolio_id = Column(String, nullable=True, index=True)
    version = Column(String, nullable=False, default="v1.0.0")
    status = Column(Enum(AllocationPlanStatus), nullable=False, default=AllocationPlanStatus.DRAFT, index=True)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    resource_allocations_json = Column(JSON, nullable=True)  # per-mission allocation breakdown
    bottlenecks_json = Column(JSON, nullable=True)
    conflicts_json = Column(JSON, nullable=True)
    expected_value = Column(Float, nullable=False, default=0.0)
    risk_score = Column(Float, nullable=False, default=20.0)
    confidence_score = Column(Float, nullable=False, default=90.0)
    explanation = Column(Text, nullable=True)
    governance_approval_id = Column(String, nullable=True)
    approved_by = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    versions = relationship("ResourceAllocationPlanVersionModel", back_populates="plan", cascade="all, delete-orphan")


class ResourceAllocationPlanVersionModel(Base):
    """Immutable version history of allocation plans."""
    __tablename__ = "resource_allocation_plan_versions"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, nullable=False, index=True)
    plan_id = Column(String, ForeignKey("resource_allocation_plans.id"), nullable=False, index=True)
    version = Column(String, nullable=False)
    parent_version = Column(String, nullable=True)
    change_reason = Column(Text, nullable=True)
    snapshot_json = Column(JSON, nullable=True)  # full plan snapshot at this version
    risk_change = Column(Float, nullable=False, default=0.0)
    value_change = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    plan = relationship("ResourceAllocationPlanModel", back_populates="versions")
