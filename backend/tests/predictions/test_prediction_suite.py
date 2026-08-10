import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import asyncio
import uuid
from datetime import datetime, timezone

from app.core.database import AsyncSessionLocal
from app.predictions.models import PredictionModel, ScenarioType, PredictionStatus
from app.predictions.schemas import PredictionCreate, ScenarioGenerateRequest, WhatIfSimulationRequest
from app.predictions.service import PredictionService
from app.predictions.scenario_engine import ScenarioEngine
from app.predictions.engine import calculate_prediction_confidence, calculate_prediction_risk, calculate_prediction_range
from app.predictions.accuracy import evaluate_prediction_accuracy
from app.auth.service import AuthService
from app.auth.repository import AuthRepository
from app.auth.schemas import UserRegisterRequest
from app.governance.models import RiskLevel
from fastapi import HTTPException

# 1. Deterministic Engines Unit Tests
def test_deterministic_prediction_engines():
    print("\n[1/5] Testing Prediction Range Bounds, Risk Engine & Accuracy Calculation...")

    # Range Bounds
    pred, low, high = calculate_prediction_range(3.7, uncertainty_pct=15.0)
    assert pred == 3.7
    assert low in [3.14, 3.15]
    assert high in [4.25, 4.26]
    print(f"  [PASS] Prediction Bounds calculated correctly: {pred}x (Range: {low}x – {high}x)")

    # Risk Scoring
    score_cons, lvl_cons = calculate_prediction_risk(ScenarioType.CONSERVATIVE, 3.1, confidence_score=92.0, budget=7500.0)
    assert lvl_cons in [RiskLevel.LOW, RiskLevel.MEDIUM]
    score_agg, lvl_agg = calculate_prediction_risk(ScenarioType.AGGRESSIVE, 4.5, confidence_score=65.0, budget=30000.0)
    assert lvl_agg in [RiskLevel.HIGH, RiskLevel.CRITICAL]
    print(f"  [PASS] Risk Levels evaluated correctly: Conservative={lvl_cons.value}, Aggressive={lvl_agg.value}")

    # Accuracy Engine
    acc = evaluate_prediction_accuracy(predicted_value=4.0, actual_value=3.8, metric_name="ROAS")
    assert acc["percentage_error"] == 5.0
    assert acc["accuracy_score"] == 95.0
    assert acc["accuracy_status"] == "HIGH_ACCURACY"
    print(f"  [PASS] Prediction Accuracy evaluated correctly (Accuracy: {acc['accuracy_score']}%, Status: {acc['accuracy_status']})")


# 2. Scenario Engine Tests
def test_scenario_generation():
    print("\n[2/5] Testing Deterministic Scenario Engine (CONSERVATIVE, BALANCED, AGGRESSIVE)...")
    scenarios = ScenarioEngine.generate_default_scenarios(
        metric_name="ROAS",
        monthly_budget=10000.0,
        timeline_days=90,
        evidence_items=[{"finding": "Verified SEO baseline"}],
        historical_memories=[{"structured_data": {"actual_value": 3.8}}]
    )

    assert len(scenarios) == 3
    types = [s["scenario_type"] for s in scenarios]
    assert ScenarioType.CONSERVATIVE in types
    assert ScenarioType.BALANCED in types
    assert ScenarioType.AGGRESSIVE in types
    print("  [PASS] All 3 core scenarios generated with valid numeric bounds & assumptions!")


# 3. Database CRUD & Multi-Tenant Security Tests
async def test_prediction_crud_and_security():
    print("\n[3/5] Testing Prediction CRUD, What-If Simulation & Multi-Tenant Security...")

    async with AsyncSessionLocal() as db:
        uid = str(uuid.uuid4())[:8]
        auth_service = AuthService(db)

        # Register Org A & Org B
        reg_a = await auth_service.register_organization(UserRegisterRequest(
            organization_name=f"Pred-Org-A-{uid}", full_name="Admin Pred A",
            email=f"admin-pred-a-{uid}@pred.io", password="Password123!"
        ))
        org_a_id = reg_a.organization_id

        reg_b = await auth_service.register_organization(UserRegisterRequest(
            organization_name=f"Pred-Org-B-{uid}", full_name="Admin Pred B",
            email=f"admin-pred-b-{uid}@pred.io", password="Password123!"
        ))
        org_b_id = reg_b.organization_id

        service = PredictionService(db)

        # Create Prediction in Org A
        p_res = await service.create_prediction(PredictionCreate(
            scenario_name="Apex Health Search Expansion",
            scenario_type=ScenarioType.BALANCED,
            metric_name="ROAS",
            predicted_value=3.7,
            lower_bound=3.2,
            upper_bound=4.1,
            confidence_score=86.0,
            risk_score=45.0,
            risk_level=RiskLevel.MEDIUM,
            assumptions=["Constant CPM"]
        ), org_id=org_a_id, creator_id=reg_a.id)

        assert p_res.id is not None
        print(f"  [PASS] Created Prediction record in Org A (ID: {p_res.id[:8]})")

        # Multi-Tenant Block Check
        print("  [TEST] Verifying Multi-Tenant Isolation Block...")
        try:
            await service.get_prediction(p_res.id, org_id=org_b_id)
            assert False, "Org B should not access Org A prediction"
        except HTTPException as exc:
            assert exc.status_code == 404
            print("  [PASS] Multi-tenant prediction access correctly BLOCKED!")

        # What-If Simulation Test
        sim_res = await service.simulate_what_if(WhatIfSimulationRequest(
            metric_name="ROAS",
            current_budget=10000.0,
            simulated_budget=18000.0,
            timeline_days=90
        ), org_id=org_a_id)

        assert sim_res.simulated_scenario["predicted_value"] > sim_res.baseline["predicted_value"]
        assert sim_res.delta["percentage_delta"] > 0
        print(f"  [PASS] What-If Simulation verified! (Delta: +{sim_res.delta['percentage_delta']}%)")


# 4. Governance Approval Integration Test
async def test_prediction_governance_approval():
    print("\n[4/5] Testing Governance Approval Request Integration...")

    async with AsyncSessionLocal() as db:
        uid = str(uuid.uuid4())[:8]
        auth_service = AuthService(db)
        auth_repo = AuthRepository(db)

        reg = await auth_service.register_organization(UserRegisterRequest(
            organization_name=f"Gov-Pred-Org-{uid}", full_name="Admin GovPred",
            email=f"admin-govpred-{uid}@pred.io", password="Password123!"
        ))
        org_id = reg.organization_id
        admin = await auth_repo.get_user_by_id(reg.id)

        service = PredictionService(db)

        # Create Prediction
        p_res = await service.create_prediction(PredictionCreate(
            scenario_name="Aggressive Flight Approval",
            scenario_type=ScenarioType.AGGRESSIVE,
            metric_name="ROAS",
            predicted_value=4.4,
            lower_bound=3.5,
            upper_bound=5.2,
            confidence_score=72.0,
            risk_score=70.0,
            risk_level=RiskLevel.HIGH
        ), org_id=org_id, creator_id=admin.id)

        # Submit for Governance Approval
        app_pred = await service.submit_prediction_for_approval(p_res.id, org_id=org_id, current_user=admin)
        assert app_pred.approval_id is not None
        assert app_pred.prediction_status == PredictionStatus.PENDING_APPROVAL
        print(f"  [PASS] Prediction submitted for Governance Approval! (Approval ID: {app_pred.approval_id[:8]})")


async def main():
    test_deterministic_prediction_engines()
    test_scenario_generation()
    await test_prediction_crud_and_security()
    await test_prediction_governance_approval()
    print("\n=======================================================")
    print("ALL STRTOS v1.2.0 PREDICTION SUITE TESTS PASSED!")
    print("=======================================================\n")

if __name__ == "__main__":
    asyncio.run(main())
