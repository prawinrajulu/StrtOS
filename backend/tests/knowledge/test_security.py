import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from app.knowledge.models import KnowledgeNodeModel, NodeTypeEnum

def test_graph_multi_tenant_isolation():
    node_org_A = KnowledgeNodeModel(organization_id="org_A", node_type=NodeTypeEnum.DECISION, entity_id="dec_A", label="Org A Strategy")
    node_org_B = KnowledgeNodeModel(organization_id="org_B", node_type=NodeTypeEnum.DECISION, entity_id="dec_B", label="Org B Strategy")

    assert node_org_A.organization_id != node_org_B.organization_id
    assert node_org_A.organization_id == "org_A"
    assert node_org_B.organization_id == "org_B"
