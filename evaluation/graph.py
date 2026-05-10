"""LangGraph orchestration logic for WorkflowSmith."""
from typing import Dict, Any
from langgraph.graph import StateGraph, END

from src.orchestration.state import WorkflowState
from src.orchestration.messages import AgentType
from src.agents.planner import PlannerAgent
from src.agents.detector import DetectorAgent
from src.agents.debugger import DebuggerAgent
from src.agents.fixer import FixerAgent
from src.agents.verifier import VerifierAgent
from src.utils.logging import get_logger

logger = get_logger("workflow_graph")

def create_repair_graph() -> StateGraph:
    """Create the LangGraph for the repair workflow."""
    
    # Initialize agents
    planner = PlannerAgent()
    detector = DetectorAgent()
    debugger = DebuggerAgent()
    fixer = FixerAgent()
    verifier = VerifierAgent()

    # Define the nodes (agent bridges)
    def call_planner(state: WorkflowState) -> Dict[str, Any]:
        return planner.run(state)

    def call_detector(state: WorkflowState) -> Dict[str, Any]:
        return detector.run(state)

    def call_debugger(state: WorkflowState) -> Dict[str, Any]:
        return debugger.run(state)

    def call_fixer(state: WorkflowState) -> Dict[str, Any]:
        return fixer.run(state)

    def call_verifier(state: WorkflowState) -> Dict[str, Any]:
        return verifier.run(state)

    # Build the graph
    workflow = StateGraph(WorkflowState)

    # Add nodes
    workflow.add_node("planner", call_planner)
    workflow.add_node("detector", call_detector)
    workflow.add_node("debugger", call_debugger)
    workflow.add_node("fixer", call_fixer)
    workflow.add_node("verifier", call_verifier)

    # Set entry point
    workflow.set_entry_point("planner")

    # Define conditional edges based on planner's decision
    def router(state: WorkflowState) -> str:
        if state["is_terminal"]:
            return "end"
        
        mapping = {
            AgentType.PLANNER: "planner",
            AgentType.DETECTOR: "detector",
            AgentType.DEBUGGER: "debugger",
            AgentType.FIXER: "fixer",
            AgentType.VERIFIER: "verifier"
        }
        return mapping.get(state["next_step"], "planner")

    workflow.add_conditional_edges(
        "planner",
        router,
        {
            "planner": "planner",
            "detector": "detector",
            "debugger": "debugger",
            "fixer": "fixer",
            "verifier": "verifier",
            "end": END
        }
    )

    # All other agents go back into the planner to decide next move
    workflow.add_edge("detector", "planner")
    workflow.add_edge("debugger", "planner")
    workflow.add_edge("fixer", "planner")
    workflow.add_edge("verifier", "planner")

    return workflow.compile()
