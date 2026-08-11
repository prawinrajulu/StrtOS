import uuid
import pytest
from app.auth.service import AuthService
from app.auth.schemas import UserRegisterRequest
from app.learning.service import LearningService
from app.experiments.service import ExperimentService
from app.experiments.schemas import ExperimentCreate, ExperimentMeasurementCreate
from app.experiments.models import ExperimentStatus, ExperimentResult, VariantType
from app.experiments.engine import ExperimentDesignEngine, ExperimentEvaluator
from app.core.database import AsyncSessionLocal

def test_experiment_design_engine():
    res = ExperimentDesignEngine.design_experiment(
        baseline_policy_config={"max_budget": 1000, "confidence_min": 75},
        variant_policy_config={"max_budget": 1050, "confidence_min": 75},
        baseline_kpi=50.0,
        target_kpi=60.0,
        min_detectable_effect=20.0,
        available_sample_size=1000
    )
    assert res["is_feasible"] is True

@pytest.mark.asyncio
async def test_experiment_evaluator_stat_safety():
    # Inconclusive on low samples
    inc = ExperimentEvaluator.evaluate([10.0, 11.0], [12.0, 13.0], min_sample_size=5)
    assert inc["result"] == ExperimentResult.INCONCLUSIVE

    # Win evaluation with sufficient samples
    win = ExperimentEvaluator.evaluate([10.0, 10.2, 9.8, 10.1, 9.9], [15.0, 15.2, 14.8, 15.1, 14.9], min_sample_size=5)
    assert win["result"] == ExperimentResult.WIN
    assert win["winner"] == VariantType.VARIANT_A
    assert win["statistically_significant"] is True

@pytest.mark.asyncio
async def test_experiment_lifecycle_e2e():
    async with AsyncSessionLocal() as db:
        uid = str(uuid.uuid4())[:8]
        auth_service = AuthService(db)

        # 1. Register Org & User
        reg = await auth_service.register_organization(UserRegisterRequest(
            organization_name=f"Exp-Org-{uid}",
            full_name="Exp Admin",
            email=f"exp-admin-{uid}@exec.io",
            password="Password123!"
        ))
        org_id = reg.organization_id
        user_id = reg.id

        # 2. Setup Baseline & Variant Policies via AgentPolicyModel
        learning_service = LearningService(db)
        from app.learning.models import AgentPolicyModel
        ctrl_pol = await learning_service.repo.create_agent_policy(AgentPolicyModel(
            organization_id=org_id, agent_name="Business Analysis Agent", policy_version="1.0.0",
            configuration={"risk_threshold": "LOW", "max_budget": 1000}, reason="Baseline control", created_by="system"
        ))
        var_pol = await learning_service.repo.create_agent_policy(AgentPolicyModel(
            organization_id=org_id, agent_name="Business Analysis Agent", policy_version="1.1.0",
            configuration={"risk_threshold": "LOW", "max_budget": 1050}, reason="Variant proposal", created_by="system"
        ))

        # 3. Create Experiment
        exp_service = ExperimentService(db)
        exp_data = await exp_service.create_experiment(
            org_id,
            ExperimentCreate(
                experiment_name=f"Campaign Budget Test {uid}",
                objective="Test 5% budget increase impact on conversion",
                hypothesis="Increasing budget by 5% improves conversion by 10%",
                metric_name="conversion_rate",
                baseline_value=10.0,
                target_value=12.0,
                minimum_detectable_effect=5.0,
                confidence_threshold=95.0,
                baseline_policy_id=ctrl_pol.id,
                variant_policy_id=var_pol.id
            ),
            user_id
        )
        exp_id = exp_data["experiment"].id

        # 4. Design & Request Approval
        await exp_service.design_experiment(exp_id, org_id)
        await exp_service.request_approval(exp_id, org_id, user_id)

        # 5. Start Experiment
        await exp_service.start_experiment(exp_id, org_id, user_id)

        # 6. Record Measurements for CONTROL and VARIANT_A directly
        ctrl_var = exp_data["control_variant"]
        var_var = exp_data["variant"]

        for i in range(3):
            await exp_service.repo.record_measurement(
                exp_id, ctrl_var.id, org_id, VariantType.CONTROL,
                ExperimentMeasurementCreate(execution_id=f"exec-ctrl-{i}-{uid}", kpi_value=10.0 + (i * 0.1), success=True)
            )
            await exp_service.repo.record_measurement(
                exp_id, var_var.id, org_id, VariantType.VARIANT_A,
                ExperimentMeasurementCreate(execution_id=f"exec-var-{i}-{uid}", kpi_value=15.0 + (i * 0.1), success=True)
            )

        # 7. Evaluate Experiment
        eval_res = await exp_service.evaluate_experiment(exp_id, org_id)
        assert eval_res["result"] == ExperimentResult.WIN
        assert eval_res["winner"] == VariantType.VARIANT_A

        # 8. Propose Optimization
        opt_res = await exp_service.propose_optimization(exp_id, org_id, user_id)
        assert opt_res["status"] == "PENDING_GOVERNANCE_APPROVAL"
