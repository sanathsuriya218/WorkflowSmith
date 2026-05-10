"""Message schemas for inter-agent communication."""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AgentType(str, Enum):
    """Types of agents in the system."""
    PLANNER = "planner"
    DETECTOR = "detector"
    DEBUGGER = "debugger"
    FIXER = "fixer"
    VERIFIER = "verifier"


class FailureType(str, Enum):
    """Categories of pipeline failures."""
    SCHEMA = "schema"
    DATA = "data"
    LOGIC = "logic"
    TEST = "test"
    UNKNOWN = "unknown"


class VerificationStatus(str, Enum):
    """Verification outcomes."""
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"


class AgentMessage(BaseModel):
    """Base message for inter-agent communication."""
    sender: AgentType
    timestamp: datetime = Field(default_factory=datetime.now)
    reasoning: str = Field(description="Required rationale for this message")
    data: Dict[str, Any] = Field(default_factory=dict)


class FailureDetected(AgentMessage):
    """Message indicating a failure has been detected."""
    failure_type: FailureType
    affected_stage: str
    severity: int = Field(ge=1, le=5, description="Severity level 1-5")
    error_message: str
    stack_trace: Optional[str] = None
    hypothesis: str = Field(description="Initial hypothesis about the failure")


class DiagnosisComplete(AgentMessage):
    """Message containing diagnosis results."""
    root_cause: str
    affected_locations: List[str] = Field(description="Code/schema locations")
    data_evidence: Dict[str, Any] = Field(default_factory=dict)
    repair_strategies: List[str] = Field(description="Suggested repair approaches")
    confidence: float = Field(ge=0.0, le=1.0)


class PatchProposal(BaseModel):
    """A proposed code patch."""
    patch_id: str
    target_file: str
    diff: str = Field(description="Unified diff format")
    explanation: str
    confidence: float = Field(ge=0.0, le=1.0)
    risk_level: int = Field(ge=1, le=5, description="Risk assessment 1-5")


class PatchesProposed(AgentMessage):
    """Message containing patch proposals."""
    patches: List[PatchProposal] = Field(description="Ranked by confidence (high to low)")
    retrieval_context: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Similar past failures used for guidance"
    )


class VerificationResult(AgentMessage):
    """Message containing verification results."""
    patch_id: str
    status: VerificationStatus
    tests_passed: int
    tests_failed: int
    test_details: List[Dict[str, Any]] = Field(default_factory=list)
    regression_detected: bool = False
    performance_impact: Optional[str] = None


class PlanningDecision(AgentMessage):
    """Message containing planner's decision on next action."""
    next_agent: AgentType
    goal: str
    constraints: Dict[str, Any] = Field(default_factory=dict)
    iteration_count: int
    should_terminate: bool = False
    termination_reason: Optional[str] = None


class PipelineStatus(BaseModel):
    """Current status of the data pipeline."""
    is_healthy: bool
    last_run_timestamp: Optional[datetime] = None
    stages_completed: List[str] = Field(default_factory=list)
    stages_failed: List[str] = Field(default_factory=list)
    error_summary: Optional[str] = None


class PastFailure(BaseModel):
    """Historical failure record from memory."""
    failure_id: str
    failure_type: FailureType
    error_signature: str
    patch_applied: str
    outcome: str  # "success" or "failure"
    timestamp: datetime
    similarity_score: float = Field(ge=0.0, le=1.0)
