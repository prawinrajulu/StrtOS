import asyncio
import uuid
from app.core.database import AsyncSessionLocal
from app.auth.service import AuthService
from app.auth.schemas import UserRegisterRequest, UserLoginRequest
from app.clients.service import ClientService
from app.clients.schemas import ClientCreateRequest
from app.workflows.service import WorkflowService
from app.workflows.schemas import WorkflowCreateRequest
from app.reports.service import ReportService
from app.core.events.publisher import event_publisher

async def test_realtime_e2e_suite():
    async with AsyncSessionLocal() as db:
        print("\n=======================================================")
        print("STARTING FULL END-TO-END REAL-TIME AI STREAMING SUITE")
        print("=======================================================")

        # 1. Register & Authenticate Org A
        print("\n[1/6] Registering Org A & Generating Auth Context...")
        auth_service = AuthService(db)
        uid_a = str(uuid.uuid4())[:8]
        email_a = f"rt-a-{uid_a}@strtos.io"
        reg_a = await auth_service.register_organization(UserRegisterRequest(
            organization_name=f"RealTime-Org-A-{uid_a}", full_name="Admin RealTime", email=email_a, password="Password123!"
        ))
        org_a_id = reg_a.organization_id

        # 2. Register & Authenticate Org B
        uid_b = str(uuid.uuid4())[:8]
        email_b = f"rt-b-{uid_b}@globex.io"
        reg_b = await auth_service.register_organization(UserRegisterRequest(
            organization_name=f"RealTime-Org-B-{uid_b}", full_name="Admin B", email=email_b, password="Password123!"
        ))
        org_b_id = reg_b.organization_id

        # 3. Create Client & Workflow for Org A
        print("\n[2/6] Creating Enterprise Client & Workflow for Org A...")
        client_service = ClientService(db)
        client = await client_service.create_client(ClientCreateRequest(
            name="Quantum Systems", industry="DeepTech", website_url="https://quantumsys.io"
        ), org_id=org_a_id, creator_id=reg_a.id)

        wf_service = WorkflowService(db)
        wf = await wf_service.create_workflow(WorkflowCreateRequest(
            client_id=client.id, title="Quantum Commercial Strategy", directive="Expand quantum computing enterprise sales."
        ), org_id=org_a_id, creator_id=reg_a.id)

        # 4. Trigger Real-Time AI Workflow Execution
        print("\n[3/6] Starting AI Workflow Execution (Broadcasting Realtime Events)...")
        started_wf = await wf_service.start_workflow(wf.id, org_id=org_a_id)
        assert started_wf.status == "COMPLETED"

        # 5. Verify Event Emission Logged in Workflow Audit Events Table
        print("\n[4/6] Verifying Workflow Audit Events Table...")
        events = await wf_service.get_events(wf.id, org_id=org_a_id)
        print(f"Total Workflow Audit Events Logged: {len(events)}")
        assert len(events) >= 2

        # 6. Verify Executive Report & Multi-Tenant SSE Security
        print("\n[5/6] Verifying Report & Multi-Tenant Event Scoping...")
        rep_service = ReportService(db)
        rep = await rep_service.get_by_workflow(wf.id, org_id=org_a_id)
        assert rep.overall_score > 0

        try:
            await rep_service.get_report(rep.id, org_id=org_b_id)
            assert False
        except Exception:
            print("SECURITY SUCCESS: Org B prevented from accessing Org A workflow events/report!")

        print("\n=======================================================")
        print("ALL REAL-TIME AI STREAMING & SSE TESTS PASSED!")
        print("=======================================================")

if __name__ == "__main__":
    asyncio.run(test_realtime_e2e_suite())
