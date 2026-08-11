import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest
from app.policies.versioning import PolicyVersioningEngine
from app.policies.models import PolicyVersionModel, PolicyStatus

def test_rollback_status_transitions():
    v1 = PolicyVersionModel(version="1.0.0", status=PolicyStatus.SUPERSEDED)
    v2 = PolicyVersionModel(version="1.1.0", status=PolicyStatus.ACTIVE)

    # Rollback active v2 to v1
    PolicyVersioningEngine.retire_version(v2, PolicyStatus.ROLLED_BACK)
    PolicyVersioningEngine.activate_version(v1)

    assert v2.status == PolicyStatus.ROLLED_BACK
    assert v1.status == PolicyStatus.ACTIVE
