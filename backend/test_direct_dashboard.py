import asyncio
import uuid
from app.core.database import AsyncSessionLocal
from app.dashboard.service import DashboardService
from app.workflows.service import WorkflowService
from app.workflows.schemas import WorkflowCreateRequest
from app.clients.service import ClientService
from app.clients.schemas import ClientCreateRequest
from app.auth.service import AuthService
from app.auth.schemas import UserRegisterRequest

async def test_direct_dashboard():
    async with AsyncSessionLocal() as db:
        print("\n--- STEP 1: REGISTER ORG A & B ---")
        auth_service = AuthService(db)
        uid_a = str(uuid.uuid4())[:8]
        reg_a = await auth_service.register_organization(UserRegisterRequest(
            organization_name=f"Dash-Direct-Org-{uid_a}", full_name="Admin A", email=f"dash-direct-{uid_a}@acme.com", password="Password123!"
        ))
        org_a_id = reg_a.organization_id
        user_a_id = reg_a.id

        uid_b = str(uuid.uuid4())[:8]
        reg_b = await auth_service.register_organization(UserRegisterRequest(
            organization_name=f"Dash-Direct-Org-{uid_b}", full_name="Admin B", email=f"dash-direct-{uid_b}@globex.com", password="Password123!"
        ))
        org_b_id = reg_b.organization_id

        dash_service = DashboardService(db)

        print("\n--- STEP 2: CHECK EMPTY DASHBOARD FOR ORG A ---")
        overview_init = await dash_service.get_overview(org_a_id)
        print("Org A Initial Clients:", overview_init.clients.total_clients)
        print("Org A Initial Workflows:", overview_init.workflows.total_workflows)
        assert overview_init.clients.total_clients == 0

        print("\n--- STEP 3: CREATE CLIENT & EXECUTE WORKFLOW FOR ORG A ---")
        client_service = ClientService(db)
        client = await client_service.create_client(ClientCreateRequest(
            name="OmniHealth", industry="HealthTech", website_url="https://omnihealth.io"
        ), org_id=org_a_id, creator_id=user_a_id)

        wf_service = WorkflowService(db)
        wf = await wf_service.create_workflow(WorkflowCreateRequest(
            client_id=client.id, title="OmniHealth Q4 Strategy"
        ), org_id=org_a_id, creator_id=user_a_id)

        await wf_service.start_workflow(wf.id, org_id=org_a_id)

        print("\n--- STEP 4: FETCH UPDATED DASHBOARD FOR ORG A ---")
        overview_updated = await dash_service.get_overview(org_a_id)
        print("Org A Updated Clients:", overview_updated.clients.total_clients)
        print("Org A Updated Workflows:", overview_updated.workflows.total_workflows)
        print("Org A Updated Reports:", overview_updated.reports.total_reports)
        print("Org A Agent Performance Count:", len(overview_updated.agent_performance))
        print("Org A Insights Count:", len(overview_updated.insights))
        assert overview_updated.clients.total_clients == 1
        assert overview_updated.workflows.total_workflows == 1
        assert overview_updated.reports.total_reports == 1

        print("\n--- STEP 5: MULTI-TENANT DASHBOARD ISOLATION CHECK (ORG B) ---")
        overview_b = await dash_service.get_overview(org_b_id)
        print("Org B Total Clients (Must be 0):", overview_b.clients.total_clients)
        print("Org B Total Workflows (Must be 0):", overview_b.workflows.total_workflows)
        assert overview_b.clients.total_clients == 0
        assert overview_b.workflows.total_workflows == 0

        print("\n=======================================================")
        print("DIRECT DASHBOARD SERVICE VERIFICATION PASSED SUCCESSFULLY!")
        print("=======================================================")

if __name__ == "__main__":
    asyncio.run(test_direct_dashboard())
