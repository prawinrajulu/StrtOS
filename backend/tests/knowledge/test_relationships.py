import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from app.knowledge.models import KnowledgeRelationModel, RelationTypeEnum, CausalStatusEnum

def test_relation_types_filtering():
    rel_supports = KnowledgeRelationModel(
        organization_id="org_A",
        source_node_id="n1",
        target_node_id="n2",
        relation_type=RelationTypeEnum.SUPPORTS,
        causal_status=CausalStatusEnum.VALIDATED
    )

    assert rel_supports.relation_type == RelationTypeEnum.SUPPORTS
    assert rel_supports.causal_status == CausalStatusEnum.VALIDATED
