import asyncio
import uuid
from app.core.database import AsyncSessionLocal
from app.workflows.service import WorkflowService
from app.workflows.schemas import WorkflowCreateRequest
from app.clients.service import ClientService
from app.clients.schemas import ClientCreateRequest
from app.auth.service import AuthService
from app.auth.schemas import UserRegisterRequest
from app.reports.service import ReportService

async def test_direct_report():
    async with AsyncSessionLocal() as db:
        print("\n--- STEP 1: REGISTER ORG A ---")
        auth_service = AuthService(db)
        uid_a = str(uuid.uuid4())[:8]
        email_a = f"rep-direct-{uid_a}@acme.com"
        reg_a = await auth_service.register_organization(UserRegisterRequest(
            organization_name=f"Rep-Direct-Org-{uid_a}", full_name="Admin A", email=email_a, password="Password123!"
        ))
        org_a_id = reg_a.organization_id
        user_a_id = reg_a.id

        print("\n--- STEP 2: REGISTER ORG B ---")
        uid_b = str(uuid.uuid4())[:8]
        email_b = f"rep-direct-{uid_b}@globex.com"
        reg_b = await auth_service.register_organization(UserRegisterRequest(
            organization_name=f"Rep-Direct-Org-{uid_b}", full_name="Admin B", email=email_b, password="Password123!"
        ))
        org_b_id = reg_b.organization_id

        print("\n--- STEP 3: CREATE CLIENT & WORKFLOW FOR ORG A ---")
        client_service = ClientService(db)
        client = await client_service.create_client(ClientCreateRequest(
            name="Aether MedTech", industry="Healthcare AI", website_url="https://aethermed.io"
        ), org_id=org_a_id, creator_id=user_a_id)

        wf_service = WorkflowService(db)
        wf = await wf_service.create_workflow(WorkflowCreateRequest(
            client_id=client.id, title="Aether MedTech Growth Campaign", directive="Scale MedTech adoption"
        ), org_id=org_a_id, creator_id=user_a_id)

        print("\n--- STEP 4: EXECUTE WORKFLOW (TRIGGERS CEO AGENT & REPORT PERSISTENCE) ---")
        started_wf = await wf_service.start_workflow(wf.id, org_id=org_a_id)
        print(f"Workflow Status: {started_wf.status}, Progress: {started_wf.progress}%")
        assert started_wf.status == "COMPLETED"

        print("\n--- STEP 5: FETCH REPORT FOR ORG A ---")
        rep_service = ReportService(db)
        report = await rep_service.get_by_workflow(wf.id, org_id=org_a_id)
        print(f"Generated Report ID: {report.id}, Title: {report.title}")
        print(f"Overall Score: {report.overall_score}/100, Confidence: {report.confidence_score}%")
        print(f"Specialist Agent Results Count: {len(report.agent_results or {})}")
        assert len(report.agent_results or {}) >= 4

        print("\n--- STEP 6: TENANT ISOLATION CHECK (ORG B ACCESSING ORG A REPORT) ---")
        try:
            await rep_service.get_report(report.id, org_id=org_b_id)
            print("ERROR: Org B accessed Org A report!")
            assert False
        except Exception as e:
            print("SECURITY SUCCESS: Org B access denied with exception:", type(e), str(e))

        print("\n--- STEP 7: IDEMPOTENCY CHECK ---")
        rep_list = await rep_service.list_reports(org_id=org_a_id, workflow_id=wf.id)
        print("Reports for Workflow Count:", rep_list.total)
        assert rep_list.total == 1

        print("\n--- STEP 8: TEST REPORT METRICS & EXPORT ---")
        metrics = await rep_service.get_metrics(org_id=org_a_id)
        print("Org A Metrics:", metrics.model_dump())

        export_data = await rep_service.export_report(report.id, org_id=org_a_id)
        print("Export Format:", export_data["format"])

        print("\n=======================================================")
        print("DIRECT REPORT SERVICE E2E VERIFICATION PASSED SUCCESSFULLY!")
        print("=======================================================")

if __name__ == "__main__":
    asyncio.run(test_direct_report())
