"""Planner Agent for global coordination and orchestration."""
from typing import Dict, Any, List, Optional
from src.agents.base import BaseAgent
from src.orchestration.state import WorkflowState
from src.orchestration.messages import AgentType, PlanningDecision, VerificationStatus
from pydantic import BaseModel, Field

class ExecutionPlan(BaseModel):
    """Schema for planner output."""
    next_agent: AgentType
    goal: str
    should_terminate: bool
    termination_reason: Optional[str]
    reasoning: str

class PlannerAgent(BaseAgent):
    """Orchestrates the repair workflow process."""
    
    def __init__(self):
        super().__init__(AgentType.PLANNER)

    def run(self, state: WorkflowState) -> Dict[str, Any]:
        """Decide the next step in the repair journey."""
        self.logger.info("Evaluating state for next planning decision...")
        
        # Check for iteration limit
        if state["iteration_count"] >= state["max_iterations"]:
            return {
                "is_terminal": True,
                "termination_reason": "MAX_ITERATIONS_REACHED",
                "next_step": AgentType.PLANNER
            }

        # Simplified logic for LLM
        history_summary = [
            f"Agent: {h.get('sender', 'unknown')}, Action: {h.get('action', 'none')}" 
            for h in state["history"]
        ]
        
        prompt = """
        You are the WorkflowSmith Planner. You coordinate a multi-agent repair system.
        
        Current Progress:
        - Iteration: {iteration}
        - Health: {health}
        - Failure Detected: {failure}
        - Diagnosis: {diagnosis}
        - Verification History: {verifications}
        
        Agent Capabilities:
        - DETECTOR: Classifies the failure.
        - DEBUGGER: Deep root-cause analysis.
        - FIXER: Generates patches.
        - VERIFIER: Validates patches.
        
        Workflow Rules:
        1. If pipeline is unhealthy and no failure classified -> Call DETECTOR.
        2. If failure classified but no diagnosis -> Call DEBUGGER.
        3. If diagnosis but no patch -> Call FIXER.
        4. If patch but not verified -> Call VERIFIER.
        5. If VERIFIER rejected the patch -> Call DEBUGGER or FIXER for retry.
        6. If VERIFIER approved -> TERMINATE (SUCCESS).
        7. If max iterations reached -> TERMINATE (FAILURE).
        
        Choose the next agent and state the goal.
        """
        
        last_verification = state["verification_history"][-1].status if state["verification_history"] else "NONE"
        
        result = self._call_llm(
            prompt,
            {
                "iteration": state["iteration_count"],
                "health": "UNHEALTHY" if not state["pipeline_status"].is_healthy else "HEALTHY",
                "failure": state["failure_context"].failure_type if state["failure_context"] else "NONE",
                "diagnosis": "DONE" if state["diagnosis"] else "NONE",
                "verifications": last_verification
            },
            ExecutionPlan
        )

        # Handle termination
        if result.should_terminate or last_verification == VerificationStatus.APPROVED:
            return {
                "is_terminal": True,
                "termination_reason": result.termination_reason or "REPAIR_SUCCESSFUL",
                "next_step": AgentType.PLANNER,
                "iteration_count": state["iteration_count"]
            }

        decision = PlanningDecision(
            sender=self.agent_type,
            reasoning=result.reasoning,
            next_agent=result.next_agent,
            goal=result.goal,
            iteration_count=state["iteration_count"] + 1
        )
        
        self.log_decision(
            reasoning=result.reasoning,
            action="plan_next_step",
            data=decision.model_dump()
        )
        
        return {
            "next_step": result.next_agent,
            "iteration_count": state["iteration_count"] + 1
        }
