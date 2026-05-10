"""Verifier Agent for validating proposed patches."""
from typing import Dict, Any, List
from src.agents.base import BaseAgent
from src.orchestration.state import WorkflowState
from src.orchestration.messages import AgentType, VerificationResult, VerificationStatus
from pydantic import BaseModel, Field

class VerificationDecision(BaseModel):
    """Schema for verifier output."""
    status: VerificationStatus
    tests_passed: int
    tests_failed: int
    reasoning: str
    regression_detected: bool

class VerifierAgent(BaseAgent):
    """Validates patches against test suites and safety rules."""
    
    def __init__(self):
        super().__init__(AgentType.VERIFIER)

    def run(self, state: WorkflowState) -> Dict[str, Any]:
        """Verify the latest proposed patch."""
        if not state["patches"]:
            return {"next_step": AgentType.PLANNER}
            
        latest_patch = state["patches"][-1]
        self.logger.info(f"Verifying patch {latest_patch.patch_id}...")
        
        prompt = """
        You are a Quality Assurance Engineer and Security Auditor.
        Evaluate the following proposed patch:
        
        Patch Explanation: {explanation}
        Patch Diff: {diff}
        Confidence: {confidence}
        Risk Level: {risk}
        
        Task:
        1. Check for syntax errors or obvious logical flaws.
        2. Assess if this fix addresses the root cause: {root_cause}
        3. Decide if the patch is approved, rejected, or needs revision.
        
        Provide test pass/fail counts (simulated).
        """
        
        result = self._call_llm(
            prompt,
            {
                "explanation": latest_patch.explanation,
                "diff": latest_patch.diff,
                "confidence": latest_patch.confidence,
                "risk": latest_patch.risk_level,
                "root_cause": state["diagnosis"].root_cause if state["diagnosis"] else "Unknown"
            },
            VerificationDecision
        )
        
        verification = VerificationResult(
            sender=self.agent_type,
            reasoning=result.reasoning,
            patch_id=latest_patch.patch_id,
            status=result.status,
            tests_passed=result.tests_passed,
            tests_failed=result.tests_failed,
            regression_detected=result.regression_detected
        )
        
        self.log_decision(
            reasoning=result.reasoning,
            action="verify_patch",
            data=verification.model_dump()
        )
        
        return {
            "verification_history": [verification],
            "next_step": AgentType.PLANNER
        }
