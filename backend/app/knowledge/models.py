import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, JSON, Enum as SQLEnum, ForeignKey
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class NodeTypeEnum(str, enum.Enum):
    CLIENT = "CLIENT"
    INDUSTRY = "INDUSTRY"
    EVIDENCE = "EVIDENCE"
    MEMORY = "MEMORY"
    AGENT = "AGENT"
    DECISION = "DECISION"
    PREDICTION = "PREDICTION"
    ACTION = "ACTION"
    POLICY = "POLICY"
    POLICY_VERSION = "POLICY_VERSION"
    OUTCOME = "OUTCOME"
    METRIC = "METRIC"
    LESSON = "LESSON"
    APPROVAL = "APPROVAL"
    WORKFLOW = "WORKFLOW"
    SWARM_SESSION = "SWARM_SESSION"

class RelationTypeEnum(str, enum.Enum):
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    INFLUENCED = "INFLUENCED"
    CAUSED = "CAUSED"
    CONTRIBUTED_TO = "CONTRIBUTED_TO"
    LED_TO = "LED_TO"
    PRODUCED = "PRODUCED"
    VALIDATES = "VALIDATES"
    INVALIDATES = "INVALIDATES"
    IMPROVED = "IMPROVED"
    REGRESSED = "REGRESSED"
    GOVERNED = "GOVERNED"
    APPROVED_BY = "APPROVED_BY"
    REJECTED_BY = "REJECTED_BY"
    LEARNED_FROM = "LEARNED_FROM"
    INFLUENCES = "INFLUENCES"

class CausalStatusEnum(str, enum.Enum):
    OBSERVED = "OBSERVED"
    HYPOTHESIS = "HYPOTHESIS"
    SUPPORTED = "SUPPORTED"
    VALIDATED = "VALIDATED"
    CONTRADICTED = "CONTRADICTED"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"

class KnowledgeNodeModel(Base):
    """
    Represents an entity node in the StrtOS Causal Knowledge Graph.
    """
    __tablename__ = "knowledge_nodes"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    node_type = Column(SQLEnum(NodeTypeEnum), nullable=False, index=True)
    entity_id = Column(String, nullable=False, index=True)
    label = Column(String, nullable=False)
    confidence = Column(Float, default=85.0)
    node_metadata = Column("metadata", JSON, nullable=True, default=dict)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class KnowledgeRelationModel(Base):
    """
    Directed relationship link between two Knowledge Nodes.
    """
    __tablename__ = "knowledge_relations"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    source_node_id = Column(String, ForeignKey("knowledge_nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    target_node_id = Column(String, ForeignKey("knowledge_nodes.id", ondelete="CASCADE"), nullable=False, index=True)

    relation_type = Column(SQLEnum(RelationTypeEnum), nullable=False, index=True)
    causal_status = Column(SQLEnum(CausalStatusEnum), default=CausalStatusEnum.OBSERVED, nullable=False, index=True)
    confidence = Column(Float, default=80.0)
    weight = Column(Float, default=1.0)
    evidence_summary = Column(JSON, nullable=True)
    relation_metadata = Column("metadata", JSON, nullable=True, default=dict)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

class CausalObservationModel(Base):
    """
    Auditable observation record supporting or contradicting causal relationships.
    """
    __tablename__ = "causal_observations"

    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    relation_id = Column(String, ForeignKey("knowledge_relations.id", ondelete="CASCADE"), nullable=False, index=True)

    supporting_observations = Column(JSON, nullable=True, default=list)
    contradicting_observations = Column(JSON, nullable=True, default=list)
    causal_score = Column(Float, default=80.0)
    status = Column(SQLEnum(CausalStatusEnum), default=CausalStatusEnum.HYPOTHESIS, nullable=False, index=True)
    explanation = Column(Text, nullable=False)

    observed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
