"""Fixer Agent for generating code and schema patches."""
import uuid
from typing import Dict, Any, List
from src.agents.base import BaseAgent
from src.orchestration.state import WorkflowState
from src.orchestration.messages import AgentType, PatchesProposed, PatchProposal
from pydantic import BaseModel, Field

class PatchOutput(BaseModel):
    """Schema for fixer output."""
    explanation: str
    target_file: str
    diff: str
    confidence: float
    risk_level: int
    reasoning: str

class FixerAgent(BaseAgent):
    """Generates fixes for diagnosed failures."""
    
    def __init__(self):
        super().__init__(AgentType.FIXER)

    def run(self, state: WorkflowState) -> Dict[str, Any]:
        """Generate a repair patch based on the diagnosis."""
        diagnosis = state["diagnosis"]
        if not diagnosis:
            return {"next_step": AgentType.PLANNER}

        self.logger.info("Generating repair patches...")
        
        prompt = """
        You are an AI Software Engineer. Generate a minimal, auditable code patch for the following diagnosis:
        
        Root Cause: {root_cause}
        Repair Strategies: {strategies}
        Affected Locations: {locations}
        
        Task:
        - Provide a unified diff format patch.
        - Explain why this fix works.
        - Assess risk (1-5).
        
        The code you target is usually in `src/pipeline/etl.py` or `src/pipeline/schema.py`.
        For schema drift, provide the Python code to update the schema metadata or migration logic.
        """
        
        result = self._call_llm(
            prompt,
            {
                "root_cause": diagnosis.root_cause,
                "strategies": diagnosis.repair_strategies,
                "locations": diagnosis.affected_locations
            },
            PatchOutput
        )
        
        patch_proposal = PatchProposal(
            patch_id=str(uuid.uuid4())[:8],
            target_file=result.target_file,
            diff=result.diff,
            explanation=result.explanation,
            confidence=result.confidence,
            risk_level=result.risk_level
        )
        
        patches_msg = PatchesProposed(
            sender=self.agent_type,
            reasoning=result.reasoning,
            patches=[patch_proposal]
        )
        
        self.log_decision(
            reasoning=result.reasoning,
            action="propose_patch",
            data=patches_msg.model_dump()
        )
        
        return {
            "patches": [patch_proposal],
            "next_step": AgentType.PLANNER
        }
