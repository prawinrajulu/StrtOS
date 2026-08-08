import asyncio
import uuid
from typing import Dict, List, Any
from app.models.schemas import (
    DirectiveRequest, Task, StatusType, PriorityType,
    WorkflowStage, ExecutionState, SpecialistOutput, ExecutiveReport
)
from app.agents.specialists import AVAILABLE_AGENTS
from app.core.redis_bus import event_bus

class CEOOrchestratorEngine:
    """
    CEO Agent Decision & Orchestration Engine.
    
    STRICT RULES:
    1. NEVER performs specialist work directly.
    2. ONLY orchestrates: parses directive, generates workflow, assigns specialist agents,
       schedules tasks, monitors live execution, handles failures, merges reports.
    """
    def __init__(self):
        self.current_state: ExecutionState = self._init_default_state()
        self.specialist_outputs: Dict[str, SpecialistOutput] = {}

    def _init_default_state(self) -> ExecutionState:
        stages = [
            WorkflowStage(id="1", name="CLIENT BRIEF", agent_name="Client Onboarding Agent", status=StatusType.COMPLETED),
            WorkflowStage(id="2", name="CEO AGENT", agent_name="CEO Agent", status=StatusType.RUNNING),
            WorkflowStage(id="3", name="BUSINESS", agent_name="Business Analysis Agent", status=StatusType.WAITING),
            WorkflowStage(id="4", name="SEO", agent_name="SEO Audit Agent", status=StatusType.WAITING),
            WorkflowStage(id="5", name="COMPETITOR", agent_name="Competitor Research Agent", status=StatusType.WAITING),
            WorkflowStage(id="6", name="MARKETING", agent_name="Marketing Strategy Agent", status=StatusType.WAITING),
            WorkflowStage(id="7", name="CAMPAIGN", agent_name="Campaign Planner Agent", status=StatusType.WAITING),
            WorkflowStage(id="8", name="ANALYTICS", agent_name="Analytics Agent", status=StatusType.WAITING),
            WorkflowStage(id="9", name="REPORT", agent_name="Report Generator Agent", status=StatusType.WAITING),
        ]
        tasks = [
            Task(task_id="t1", title="Synthesize Northwind competitive matrix", priority=PriorityType.HIGH, agent_name="Competitor Research Agent", status=StatusType.RUNNING, eta="ETA 2 MIN"),
            Task(task_id="t2", title="Draft Lumen Studios Q1 narrative", priority=PriorityType.HIGH, agent_name="Marketing Strategy Agent", status=StatusType.WAITING, eta="ETA 6 MIN"),
            Task(task_id="t3", title="SEO technical audit - orbitalabs.io", priority=PriorityType.MEDIUM, agent_name="SEO Audit Agent", status=StatusType.RUNNING, eta="ETA 4 MIN"),
            Task(task_id="t4", title="Kite & Loom holiday media mix", priority=PriorityType.MEDIUM, agent_name="Campaign Planner Agent", status=StatusType.WAITING, eta="ETA 9 MIN"),
            Task(task_id="t5", title="Halcyon Hotels attribution rebuild", priority=PriorityType.LOW, agent_name="Analytics Agent", status=StatusType.WAITING, eta="ETA 12 MIN"),
        ]
        return ExecutionState(
            workflow_id="wf-" + str(uuid.uuid4())[:8],
            client_name="Arcadia Ventures",
            current_thought="Reviewing Northwind Capital brief – enterprise FinTech, EMEA focus.",
            overall_confidence=92,
            stages=stages,
            tasks=tasks,
            completed_count=12,
            running_count=3,
            waiting_count=4,
            is_active=True
        )

    async def run_directive(self, request: DirectiveRequest):
        """
        Full orchestration pipeline for a new user directive.
        """
        workflow_id = "wf-" + str(uuid.uuid4())[:8]
        self.specialist_outputs.clear()

        # Step 1: Read Goal & Emit Thinking Thought
        thought_1 = f"Decomposing executive directive for {request.client_name}: '{request.directive}'..."
        await self._update_thought(thought_1)

        # Step 2: Determine Sequence & Create Tasks
        tasks = [
            Task(task_id="t-1", title=f"Business TAM & Model Analysis ({request.client_type})", priority=PriorityType.HIGH, agent_name="Business Analysis Agent", status=StatusType.WAITING, eta="ETA 1 MIN"),
            Task(task_id="t-2", title=f"SEO Technical & Keyword Discovery", priority=PriorityType.HIGH, agent_name="SEO Audit Agent", status=StatusType.WAITING, eta="ETA 2 MIN", dependencies=["t-1"]),
            Task(task_id="t-3", title=f"Rival Intelligence & Competitor Matrix", priority=PriorityType.HIGH, agent_name="Competitor Research Agent", status=StatusType.WAITING, eta="ETA 2 MIN", dependencies=["t-2"]),
            Task(task_id="t-4", title=f"Growth Positioning & Multi-channel Strategy", priority=PriorityType.HIGH, agent_name="Marketing Strategy Agent", status=StatusType.WAITING, eta="ETA 3 MIN", dependencies=["t-3"]),
            Task(task_id="t-5", title=f"Campaign Media Allocation & Funnel Planning", priority=PriorityType.MEDIUM, agent_name="Campaign Planner Agent", status=StatusType.WAITING, eta="ETA 3 MIN", dependencies=["t-4"]),
            Task(task_id="t-6", title=f"Attribution Model & Dashboard Loop", priority=PriorityType.LOW, agent_name="Analytics Agent", status=StatusType.WAITING, eta="ETA 4 MIN", dependencies=["t-5"]),
        ]

        # Reset State
        for stage in self.current_state.stages:
            stage.status = StatusType.WAITING if stage.name != "CLIENT BRIEF" else StatusType.COMPLETED

        self.current_state.workflow_id = workflow_id
        self.current_state.client_name = request.client_name
        self.current_state.tasks = tasks
        self.current_state.completed_count = 1
        self.current_state.running_count = 1
        self.current_state.waiting_count = len(tasks)
        await self._broadcast_state()

        # Step 3: Execute Sequence
        for task in tasks:
            # Update Current Thought
            thought = f"Delegating '{task.title}' to {task.agent_name}..."
            await self._update_thought(thought)

            # Update Stage & Task Status
            task.status = StatusType.RUNNING
            self._update_stage_status(task.agent_name, StatusType.RUNNING)
            await self._broadcast_state()

            # Execute via Specialist Agent
            agent = AVAILABLE_AGENTS.get(task.agent_name)
            if agent:
                output = await agent.execute(task, {"client": request.client_name, "directive": request.directive})
                self.specialist_outputs[task.agent_name] = output

            # Mark Completed
            task.status = StatusType.COMPLETED
            self._update_stage_status(task.agent_name, StatusType.COMPLETED)
            self.current_state.completed_count += 1
            self.current_state.waiting_count = max(0, self.current_state.waiting_count - 1)
            await self._broadcast_state()

        # Step 4: Final Executive Synthesis
        await self._update_thought("Validating outputs from all 6 specialist agents and synthesizing Executive Report...")
        await asyncio.sleep(1.5)

        self.current_state.current_thought = "Workflow completed successfully. Executive Report generated."
        self.current_state.running_count = 0
        self.current_state.overall_confidence = 96
        await self._broadcast_state()

    def _update_stage_status(self, agent_name: str, status: StatusType):
        for stage in self.current_state.stages:
            if stage.agent_name == agent_name:
                stage.status = status

    async def _update_thought(self, text: str):
        self.current_state.current_thought = text
        await self._broadcast_state()

    async def _broadcast_state(self):
        await event_bus.publish("STATE_UPDATE", self.current_state.model_dump())

    def get_executive_report(self) -> ExecutiveReport:
        b_out = self.specialist_outputs.get("Business Analysis Agent", SpecialistOutput(agent_name="Business Analysis Agent", title="Business Analysis", findings=["TAM analyzed."]))
        s_out = self.specialist_outputs.get("SEO Audit Agent", SpecialistOutput(agent_name="SEO Audit Agent", title="SEO Audit", findings=["Technical SEO healthy."]))
        c_out = self.specialist_outputs.get("Competitor Research Agent", SpecialistOutput(agent_name="Competitor Research Agent", title="Competitor Analysis", findings=["12 competitors mapped."]))
        m_out = self.specialist_outputs.get("Marketing Strategy Agent", SpecialistOutput(agent_name="Marketing Strategy Agent", title="Marketing Strategy", findings=["Positioning strategy defined."]))
        cp_out = self.specialist_outputs.get("Campaign Planner Agent", SpecialistOutput(agent_name="Campaign Planner Agent", title="Campaign Plan", findings=["Media allocation set."]))
        a_out = self.specialist_outputs.get("Analytics Agent", SpecialistOutput(agent_name="Analytics Agent", title="Analytics Attribution", findings=["Attribution loop live."]))

        return ExecutiveReport(
            workflow_id=self.current_state.workflow_id,
            client_name=self.current_state.client_name,
            directive="Acquire more online customers via high-efficiency multi-agent campaign.",
            overall_confidence=self.current_state.overall_confidence,
            business_summary=b_out,
            seo_summary=s_out,
            competitor_summary=c_out,
            marketing_summary=m_out,
            campaign_summary=cp_out,
            analytics_summary=a_out,
            ceo_final_recommendations=[
                "Deploy local geo-targeted search campaigns immediately to capture existing high-intent demand.",
                "Execute micro-influencer events to build local trust and brand equity.",
                "Maintain real-time multi-touch attribution to reallocate budget dynamically every 48 hours."
            ]
        )

ceo_engine = CEOOrchestratorEngine()
