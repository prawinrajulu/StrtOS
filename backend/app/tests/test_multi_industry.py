import asyncio
from app.agents.ceo.orchestrator import ceo_orchestrator
from app.agents.ceo.graph.state import WorkflowStatus, TaskStatus

async def test_multi_industry_ai_execution():
    scenarios = [
        ("Fine-Dining Italian Restaurant", "Bella Italia"),
        ("Modern Interior Design Studio", "LuxeInteriors"),
        ("Comprehensive Dental Clinic", "ApexDental"),
        ("24/7 Fitness & Gym Center", "PulseGym"),
        ("Boutique Luxury Hotel", "GrandView Hotel")
    ]

    for business_type, client_name in scenarios:
        directive = f"Full acquisition strategy for {business_type}"
        state = await ceo_orchestrator.execute_directive(directive, client_name)
        
        # Wait until current workflow finishes execution
        while not ceo_orchestrator.active_workflows[state.workflow_id].is_completed:
            await asyncio.sleep(0.2)
        
        active_state = ceo_orchestrator.active_workflows[state.workflow_id]
        assert active_state.status == WorkflowStatus.COMPLETED
        assert len(active_state.agent_outputs) == 5
        print(f"Verified Real AI Pipeline Execution for scenario: {business_type}")
