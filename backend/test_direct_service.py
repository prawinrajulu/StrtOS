import asyncio
import uuid
from app.core.database import AsyncSessionLocal
from app.workflows.service import WorkflowService
from app.workflows.schemas import WorkflowCreateRequest
from app.clients.service import ClientService
from app.clients.schemas import ClientCreateRequest
from app.auth.service import AuthService
from app.auth.schemas import UserRegisterRequest

async def test_direct_service():
    async with AsyncSessionLocal() as db:
        auth_service = AuthService(db)
        uid_a = str(uuid.uuid4())[:8]
        email_a = f"direct-wf-{uid_a}@acme.com"
        reg = await auth_service.register_organization(UserRegisterRequest(
            organization_name=f"Direct-Org-{uid_a}", full_name="Admin", email=email_a, password="Password123!"
        ))
        org_id = reg.organization_id
        user_id = reg.id

        client_service = ClientService(db)
        client = await client_service.create_client(ClientCreateRequest(
            name="Apex Direct", industry="SaaS", website_url="https://apex.io"
        ), org_id=org_id, creator_id=user_id)

        wf_service = WorkflowService(db)
        wf = await wf_service.create_workflow(WorkflowCreateRequest(
            client_id=client.id, title="Direct Scale Campaign", directive="Scale growth"
        ), org_id=org_id, creator_id=user_id)

        print(f"Created Workflow ID: {wf.id}, Status: {wf.status}")

        started_wf = await wf_service.start_workflow(wf.id, org_id=org_id)
        print(f"Started Workflow Status: {started_wf.status}, Progress: {started_wf.progress}%")

        tasks = await wf_service.get_tasks(wf.id, org_id=org_id)
        print(f"Persisted Tasks Count: {len(tasks)}")
        for t in tasks:
            print(f" - [{t.status}] {t.agent_name}: {t.title}")

        events = await wf_service.get_events(wf.id, org_id=org_id)
        print(f"Audit Events Count: {len(events)}")
        for e in events:
            print(f" - {e.event_type}")

        print("\nDIRECT SERVICE WORKFLOW TEST PASSED!")

if __name__ == "__main__":
    asyncio.run(test_direct_service())
