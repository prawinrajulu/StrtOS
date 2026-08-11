import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from app.knowledge.models import KnowledgeNodeModel, NodeTypeEnum

def test_graph_node_structure():
    n1 = KnowledgeNodeModel(organization_id="org_A", node_type=NodeTypeEnum.EVIDENCE, entity_id="ev_01", label="Firecrawl Finding")
    n2 = KnowledgeNodeModel(organization_id="org_A", node_type=NodeTypeEnum.DECISION, entity_id="dec_01", label="Pricing Strategy")

    assert n1.node_type != n2.node_type
    assert n1.entity_id == "ev_01"
