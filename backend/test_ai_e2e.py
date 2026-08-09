import asyncio
import uuid
from app.core.database import AsyncSessionLocal
from app.auth.service import AuthService
from app.auth.schemas import UserRegisterRequest
from app.clients.service import ClientService
from app.clients.schemas import ClientCreateRequest
from app.workflows.service import WorkflowService
from app.workflows.schemas import WorkflowCreateRequest
from app.reports.service import ReportService
from app.dashboard.service import DashboardService

async def test_full_ai_e2e_suite():
    async with AsyncSessionLocal() as db:
        print("\n=======================================================")
        print("STARTING PRODUCTION REAL AI & TOOL EXECUTION E2E SUITE")
        print("=======================================================")

        # 1. Register Org A
        print("\n[1/6] Registering Enterprise Org A...")
        auth_service = AuthService(db)
        uid_a = str(uuid.uuid4())[:8]
        email_a = f"ai-e2e-a-{uid_a}@strtos.io"
        reg_a = await auth_service.register_organization(UserRegisterRequest(
            organization_name=f"AI-Real-Org-A-{uid_a}", full_name="Admin AI", email=email_a, password="Password123!"
        ))
        org_a_id = reg_a.organization_id

        # 2. Create Client & Workflow
        print("\n[2/6] Creating Client & Workflow for Org A...")
        client_service = ClientService(db)
        client = await client_service.create_client(ClientCreateRequest(
            name="Aether Systems", industry="Enterprise AI", website_url="https://aethersys.io"
        ), org_id=org_a_id, creator_id=reg_a.id)

        wf_service = WorkflowService(db)
        wf = await wf_service.create_workflow(WorkflowCreateRequest(
            client_id=client.id, title="Aether Enterprise AI Expansion", directive="Scale B2B AI SaaS adoption."
        ), org_id=org_a_id, creator_id=reg_a.id)

        # 3. Execute Real AI & Tool Execution Pipeline
        print("\n[3/6] Starting Real AI & Tool Execution Pipeline...")
        started_wf = await wf_service.start_workflow(wf.id, org_id=org_a_id)
        assert started_wf.status == "COMPLETED"

        # 4. Verify Persistent Tasks
        print("\n[4/6] Verifying Persistent Task Execution Records...")
        tasks = await wf_service.get_tasks(wf.id, org_id=org_a_id)
        print("Completed Tasks Count:", len(tasks))
        assert len(tasks) >= 4

        # 5. Verify Persisted Report Metadata & Scores
        print("\n[5/6] Verifying Synthesized Executive Report & Scores...")
        rep_service = ReportService(db)
        rep = await rep_service.get_by_workflow(wf.id, org_id=org_a_id)
        print(f"Generated Executive Report Title: {rep.title}")
        print(f"Overall Strategic Score: {rep.overall_score}/100, Confidence: {rep.confidence_score}%")
        assert rep.overall_score > 0
        assert len(rep.agent_results or {}) >= 1

        # 6. Verify Dashboard Metrics
        print("\n[6/6] Verifying Executive Dashboard Metrics Aggregation...")
        dash_service = DashboardService(db)
        dash = await dash_service.get_overview(org_a_id)
        assert dash.clients.total_clients == 1
        assert dash.workflows.total_workflows == 1

        print("\n=======================================================")
        print("ALL PRODUCTION AI & REAL TOOL E2E SUITE TESTS PASSED!")
        print("=======================================================")

if __name__ == "__main__":
    asyncio.run(test_full_ai_e2e_suite())
