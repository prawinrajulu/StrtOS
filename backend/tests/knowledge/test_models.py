import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from app.knowledge.models import KnowledgeNodeModel, KnowledgeRelationModel, NodeTypeEnum, RelationTypeEnum, CausalStatusEnum

def test_knowledge_node_model_instantiation():
    node = KnowledgeNodeModel(
        organization_id="org_kn_101",
        node_type=NodeTypeEnum.DECISION,
        entity_id="dec_901",
        label="Strategic SaaS Pricing Strategy",
        confidence=90.0
    )
    assert node.organization_id == "org_kn_101"
    assert node.node_type == NodeTypeEnum.DECISION
    assert node.entity_id == "dec_901"
    assert node.confidence == 90.0

def test_knowledge_relation_model_instantiation():
    rel = KnowledgeRelationModel(
        organization_id="org_kn_101",
        source_node_id="node_src",
        target_node_id="node_tgt",
        relation_type=RelationTypeEnum.SUPPORTS,
        causal_status=CausalStatusEnum.VALIDATED,
        confidence=92.0
    )
    assert rel.relation_type == RelationTypeEnum.SUPPORTS
    assert rel.causal_status == CausalStatusEnum.VALIDATED
