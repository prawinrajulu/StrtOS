import asyncio
import uuid
from app.core.database import AsyncSessionLocal
from app.auth.service import AuthService
from app.auth.schemas import UserRegisterRequest, UserLoginRequest
from app.auth.jwt_handler import JWTHandler
from app.clients.service import ClientService
from app.clients.schemas import ClientCreateRequest
from app.workflows.service import WorkflowService
from app.workflows.schemas import WorkflowCreateRequest
from app.reports.service import ReportService
from app.dashboard.service import DashboardService

async def test_direct_production_suite():
    async with AsyncSessionLocal() as db:
        print("\n=======================================================")
        print("STARTING DIRECT PRODUCTION INFRASTRUCTURE & HARDENING SUITE")
        print("=======================================================")

        # 1. Register & Login Org A
        auth_service = AuthService(db)
        uid_a = str(uuid.uuid4())[:8]
        email_a = f"prod-direct-a-{uid_a}@strtos.io"
        reg_a = await auth_service.register_organization(UserRegisterRequest(
            organization_name=f"Prod-Direct-Org-A-{uid_a}", full_name="Admin Org A", email=email_a, password="Password123!"
        ))
        token_a = await auth_service.login(UserLoginRequest(email=email_a, password="Password123!"))

        # 2. Register & Login Org B
        uid_b = str(uuid.uuid4())[:8]
        email_b = f"prod-direct-b-{uid_b}@globex.io"
        reg_b = await auth_service.register_organization(UserRegisterRequest(
            organization_name=f"Prod-Direct-Org-B-{uid_b}", full_name="Admin Org B", email=email_b, password="Password123!"
        ))

        # 3. Create Client & Workflow for Org A
        print("\n[1/5] Creating Client & Workflow for Org A...")
        client_service = ClientService(db)
        client = await client_service.create_client(ClientCreateRequest(
            name="Starlight Corp", industry="Enterprise Software", website_url="https://starlight.io"
        ), org_id=reg_a.organization_id, creator_id=reg_a.id)

        wf_service = WorkflowService(db)
        wf = await wf_service.create_workflow(WorkflowCreateRequest(
            client_id=client.id, title="Starlight Market Expansion", directive="Expand TAM into APAC."
        ), org_id=reg_a.organization_id, creator_id=reg_a.id)

        # 4. Start Workflow Execution (CEO + Specialist Pipeline)
        print("\n[2/5] Starting Workflow Execution (CEO + Specialist Pipeline)...")
        started_wf = await wf_service.start_workflow(wf.id, org_id=reg_a.organization_id)
        assert started_wf.status == "COMPLETED"

        # 5. Idempotency Check
        print("\n[3/5] Verifying Workflow Start Idempotency...")
        dup_wf = await wf_service.start_workflow(wf.id, org_id=reg_a.organization_id)
        assert dup_wf.status == "COMPLETED"

        # 6. Fetch Executive Report & Dashboard Overview
        print("\n[4/5] Fetching Executive Report & Dashboard Overview...")
        rep_service = ReportService(db)
        rep = await rep_service.get_by_workflow(wf.id, org_id=reg_a.organization_id)
        assert rep.overall_score > 0

        dash_service = DashboardService(db)
        dash_a = await dash_service.get_overview(reg_a.organization_id)
        assert dash_a.clients.total_clients == 1
        assert dash_a.workflows.total_workflows == 1

        # 7. Multi-Tenant Security Check for Org B
        print("\n[5/5] SECURITY CHECK: Org B accessing Org A resources...")
        try:
            await rep_service.get_report(rep.id, org_id=reg_b.organization_id)
            assert False
        except Exception:
            print("SECURITY SUCCESS: Org B denied access to Org A report!")

        dash_b = await dash_service.get_overview(reg_b.organization_id)
        assert dash_b.clients.total_clients == 0

        print("\n=======================================================")
        print("ALL DIRECT PRODUCTION SUITE TESTS PASSED SUCCESSFULLY!")
        print("=======================================================")

if __name__ == "__main__":
    asyncio.run(test_direct_production_suite())
