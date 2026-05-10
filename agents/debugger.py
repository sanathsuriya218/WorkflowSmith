"""Debugger Agent for root-cause analysis and diagnosis."""
from typing import Dict, Any, List
from src.agents.base import BaseAgent
from src.orchestration.state import WorkflowState
from src.orchestration.messages import AgentType, DiagnosisComplete
from pydantic import BaseModel, Field

class DiagnosisOutput(BaseModel):
    """Schema for debugger output."""
    root_cause: str
    affected_locations: List[str]
    data_evidence: Dict[str, Any]
    repair_strategies: List[str]
    confidence: float
    reasoning: str

class DebuggerAgent(BaseAgent):
    """Diagnoses the root cause of failures."""
    
    def __init__(self):
        super().__init__(AgentType.DEBUGGER)

    def run(self, state: WorkflowState) -> Dict[str, Any]:
        """Perform deep analysis of the detected failure."""
        failure = state["failure_context"]
        if not failure:
            return {"next_step": AgentType.PLANNER}

        self.logger.info(f"Diagnosing root cause for {failure.failure_type} failure...")
        
        prompt = """
        You are a Senior Data Engineer and Debugger.
        Perform root-cause analysis for the following pipeline failure:
        
        Failure Type: {failure_type}
        Error Message: {error_msg}
        Hypothesis: {hypothesis}
        Affected Stage: {stage}
        
        Task:
        1. Identify the most likely root cause.
        2. Point to suspected code or schema locations.
        3. Suggest repair strategies.
        
        Be precise and evidence-based.
        """
        
        result = self._call_llm(
            prompt,
            {
                "failure_type": failure.failure_type,
                "error_msg": failure.error_message,
                "hypothesis": failure.hypothesis,
                "stage": failure.affected_stage
            },
            DiagnosisOutput
        )
        
        diagnosis = DiagnosisComplete(
            sender=self.agent_type,
            reasoning=result.reasoning,
            root_cause=result.root_cause,
            affected_locations=result.affected_locations,
            data_evidence=result.data_evidence,
            repair_strategies=result.repair_strategies,
            confidence=result.confidence
        )
        
        self.log_decision(
            reasoning=result.reasoning,
            action="diagnose_failure",
            data=diagnosis.model_dump()
        )
        
        return {
            "diagnosis": diagnosis,
            "next_step": AgentType.PLANNER
        }
