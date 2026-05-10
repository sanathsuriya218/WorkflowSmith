"""Detector Agent for monitoring and failure classification."""
from typing import Dict, Any, List
from src.agents.base import BaseAgent
from src.orchestration.state import WorkflowState
from src.orchestration.messages import AgentType, FailureDetected, FailureType
from pydantic import BaseModel, Field

class ScannedMetrics(BaseModel):
    """Internal schema for scanning results."""
    anomalies: List[str]
    error_patterns: List[str]
    suggested_failure_type: FailureType
    severity: int
    hypothesis: str
    reasoning: str

class DetectorAgent(BaseAgent):
    """Monitors logs and data to classify failures."""
    
    def __init__(self):
        super().__init__(AgentType.DETECTOR)

    def run(self, state: WorkflowState) -> Dict[str, Any]:
        """Classify the failure based on the pipeline status and error messages."""
        self.logger.info("Scanning for pipeline failures...")
        
        status = state["pipeline_status"]
        if status.is_healthy:
            return {"next_step": AgentType.PLANNER}

        # Context for the LLM
        error_msg = status.error_summary or "Unknown error"
        completed_stages = status.stages_completed
        
        prompt = """
        You are a Data Pipeline Failure Detector. 
        Analyze the following pipeline error and classify it.
        
        Error Message: {error_msg}
        Completed Stages: {completed_stages}
        
        Classification Rules:
        - SCHEMA: Column mismatches, type changes, missing fields.
        - DATA: Null violations, range errors (e.g. negative age), statistical anomalies.
        - LOGIC: Incorrect results, join issues, calculation errors.
        - TEST: Assertion failures in tests.
        
        Provide your reasoning and initial hypothesis.
        """
        
        result = self._call_llm(
            prompt,
            {"error_msg": error_msg, "completed_stages": completed_stages},
            ScannedMetrics
        )
        
        failure_info = FailureDetected(
            sender=self.agent_type,
            reasoning=result.reasoning,
            failure_type=result.suggested_failure_type,
            affected_stage=state["pipeline_status"].stages_failed[0] if state["pipeline_status"].stages_failed else "unknown",
            severity=result.severity,
            error_message=error_msg,
            hypothesis=result.hypothesis,
            data={"anomalies": result.anomalies, "patterns": result.error_patterns}
        )
        
        self.log_decision(
            reasoning=result.reasoning,
            action="classify_failure",
            data=failure_info.model_dump()
        )
        
        return {
            "failure_context": failure_info,
            "next_step": AgentType.PLANNER
        }
