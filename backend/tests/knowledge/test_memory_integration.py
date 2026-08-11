import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from app.memory.schemas import MemoryRecordCreate
from app.memory.models import MemoryType, OutcomeStatus

def test_causal_memory_record_creation():
    mem = MemoryRecordCreate(
        title="Causal Lesson: High Elasticity",
        content="Validated causal relationship between pricing adjustment and user retention drop.",
        memory_type=MemoryType.LESSON,
        outcome_status=OutcomeStatus.SUCCESS,
        confidence_score=92.0
    )
    assert mem.title == "Causal Lesson: High Elasticity"
    assert mem.confidence_score == 92.0
