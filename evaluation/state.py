"""Global state management for the LangGraph workflow."""
from typing import Annotated, Dict, List, Optional, TypedDict, Any
from datetime import datetime

from src.orchestration.messages import (
    FailureDetected,
    DiagnosisComplete,
    PatchProposal,
    VerificationResult,
    PipelineStatus,
    AgentType,
    FailureType
)

def merge_list(left: list, right: list) -> list:
    """Helper to merge lists in state updates."""
    return left + right

class WorkflowState(TypedDict):
    """The global state shared across all agents in the repair workflow."""
    
    # Pipeline health info
    pipeline_status: PipelineStatus
    
    # Failure information (from Detector)
    failure_context: Optional[FailureDetected]
    
    # Diagnosis (from Debugger)
    diagnosis: Optional[DiagnosisComplete]
    
    # Patches (from Fixer)
    patches: Annotated[List[PatchProposal], merge_list]
    selected_patch_id: Optional[str]
    
    # Verification history (from Verifier)
    verification_history: Annotated[List[VerificationResult], merge_list]
    
    # Progress tracking
    iteration_count: int
    max_iterations: int
    start_time: datetime
    
    # Agent coordination
    next_step: AgentType
    history: Annotated[List[Dict[str, Any]], merge_list]
    
    # Memory context
    similar_past_failures: List[Dict[str, Any]]
    
    # Error tracking
    system_errors: List[str]
    is_terminal: bool
    termination_reason: Optional[str]

from src.utils.config import Config

def create_initial_state(max_iterations: int = Config.MAX_REPAIR_ITERATIONS) -> WorkflowState:
    """Initialize a fresh workflow state."""
    return {
        "pipeline_status": PipelineStatus(is_healthy=True),
        "failure_context": None,
        "diagnosis": None,
        "patches": [],
        "selected_patch_id": None,
        "verification_history": [],
        "iteration_count": 0,
        "max_iterations": max_iterations,
        "start_time": datetime.now(),
        "next_step": AgentType.PLANNER,
        "history": [],
        "similar_past_failures": [],
        "system_errors": [],
        "is_terminal": False,
        "termination_reason": None
    }
