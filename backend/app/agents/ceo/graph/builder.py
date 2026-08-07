from langgraph.graph import StateGraph, END
from app.agents.ceo.graph.state import WorkflowState
from app.agents.ceo.orchestrator import ceo_orchestrator

async def analyze_intent_node(state: WorkflowState) -> WorkflowState:
    intent = await ceo_orchestrator.intent_engine.analyze_intent(state.directive)
    state.intent = intent
    state.current_thought = f"Analyzed intent: {intent.primary_goal} for {intent.business_type}"
    return state

async def evaluate_decision_node(state: WorkflowState) -> WorkflowState:
    if state.intent:
        decision = await ceo_orchestrator.decision_engine.evaluate_decision(state.intent)
        state.decision = decision
        state.current_thought = f"Generated execution plan with {len(decision.required_agents)} specialist agents."
    return state

async def generate_workflow_node(state: WorkflowState) -> WorkflowState:
    if state.decision:
        state.stages = await ceo_orchestrator.workflow_planner.generate_stages(state.decision)
        state.tasks = await ceo_orchestrator.task_planner.create_task_queue(state.decision)
        state.current_thought = "Workflow graph and task queue generated successfully."
    return state

def build_ceo_graph():
    """
    LangGraph Builder for CEO Agent Workflow State Machine.
    Supports sequential and parallel node transitions with state persistence.
    """
    builder = StateGraph(WorkflowState)
    builder.add_node("analyze_intent", analyze_intent_node)
    builder.add_node("evaluate_decision", evaluate_decision_node)
    builder.add_node("generate_workflow", generate_workflow_node)

    builder.set_entry_point("analyze_intent")
    builder.add_edge("analyze_intent", "evaluate_decision")
    builder.add_edge("evaluate_decision", "generate_workflow")
    builder.add_edge("generate_workflow", END)

    return builder
