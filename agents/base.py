"""Base agent abstraction for all WorkflowSmith agents."""
import abc
import time
import random
import os
from typing import Any, Dict, List, Optional, Type, TypeVar
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel

from src.utils.config import Config
from src.utils.logging import get_logger, StructuredLogger
from src.orchestration.state import WorkflowState
from src.orchestration.messages import AgentType, FailureType, VerificationStatus

T = TypeVar('T', bound=BaseModel)

# Mock classes for Presentation/Demo Mode
class MockChatGoogleGenerativeAI:
    def __init__(self, model: str):
        self.model = model
        self.agent_type: Optional[AgentType] = None

class MockChain:
    def __init__(self, llm: MockChatGoogleGenerativeAI, parser: PydanticOutputParser):
        self.llm = llm
        self.parser = parser

    def invoke(self, input_dict):
        schema = self.parser.pydantic_object
        defaults = {}
        agent_type = getattr(self.llm, "agent_type", None)
        iteration = input_dict.get("iteration", 0)
        failure = input_dict.get("failure", "NONE")
        diagnosis = input_dict.get("diagnosis", "NONE")
        verifications = input_dict.get("verifications", "NONE")
        
        time.sleep(random.uniform(2.0, 3.5))
        
        #Logic
        for name, field in schema.model_fields.items():
            if name == "next_agent" or name == "next_step":
                if failure == "NONE": defaults[name] = AgentType.DETECTOR
                elif diagnosis == "NONE": defaults[name] = AgentType.DEBUGGER
                elif iteration < 3: defaults[name] = AgentType.FIXER
                elif verifications == "NONE": defaults[name] = AgentType.VERIFIER
                else: defaults[name] = AgentType.PLANNER
            elif name == "should_terminate" or name == "is_terminal":
                defaults[name] = (iteration >= 4 or verifications == VerificationStatus.APPROVED)
            elif name == "termination_reason":
                defaults[name] = "REPAIR_SUCCESSFUL"
            elif name == "reasoning":
                if agent_type == AgentType.PLANNER:
                    defaults[name] = f"Analyzing research-specification state (10,465 rows). Repair Cycle {iteration}/10. Routing to {defaults.get('next_agent', 'Terminal')}."
                elif agent_type == AgentType.DETECTOR:
                    defaults[name] = f"Scanning 17-column schema. Detected {failure} patterns in 3.8% of 10,465 rows. Confidence 0.995."
                elif agent_type == AgentType.DEBUGGER:
                    defaults[name] = f"Deep-dive analysis of {failure}. Identified root cause in multi-column logic at row index 8,421."
                elif agent_type == AgentType.FIXER:
                    defaults[name] = f"Generating 10k-optimized repair patch for {failure}. Implementing vectorized validation logic for 17 columns."
                elif agent_type == AgentType.VERIFIER:
                    defaults[name] = "Executing research-grade regression tests. Verification successful for 10,465 records in 180ms."
            elif name == "root_cause":
                defaults[name] = f"Enterprise-level {failure} identified. Root cause: Multi-modal inconsistency in the 69k-row dataset."
            elif name == "status":
                defaults[name] = "approved"
            elif name == "suggested_failure_type" or name == "failure_type":
                defaults[name] = failure.lower() if failure and failure != "NONE" else "schema"
            elif "confidence" in name:
                defaults[name] = 0.98
            elif name == "diff":
                defaults[name] = f"--- a/etl.py\n+++ b/etl.py\n@@ -12,1 +12,1 @@\n-old_logic()\n+fixed_autonomous_logic_v1()"
            else:
                # Type-safe fallbacks
                import typing
                origin = typing.get_origin(field.annotation)
                if field.annotation == bool: defaults[name] = True
                elif field.annotation == int: defaults[name] = 1
                elif field.annotation == float: defaults[name] = 1.0
                elif field.annotation == str: defaults[name] = "Success"
                elif origin is list or field.annotation == list: defaults[name] = []
                elif origin is dict or field.annotation == dict: defaults[name] = {}
                else: defaults[name] = None
        
        return schema(**defaults)

class BaseAgent(abc.ABC):
    """Abstract base class for all reasoning-driven agents."""
    
    def __init__(self, agent_type: AgentType, model: str = Config.GEMINI_MODEL):
        self.agent_type = agent_type
        self.logger: StructuredLogger = get_logger(agent_type.value)
        
        if os.getenv("DEMO_MODE") == "true":
            self.llm = MockChatGoogleGenerativeAI(model=model)
            self.llm.agent_type = agent_type
        else:
            self.llm = ChatGoogleGenerativeAI(
                model=model,
                google_api_key=Config.GOOGLE_API_KEY,
                temperature=0
            )

    @abc.abstractmethod
    def run(self, state: WorkflowState) -> Dict[str, Any]:
        """Execute the agent's logic and return state updates."""
        pass

    def _call_llm(
        self, 
        prompt_template: str, 
        input_variables: Dict[str, Any], 
        output_schema: Type[T]
    ) -> T:
        """Helper to call LLM with structured output parsing."""
        parser = PydanticOutputParser(pydantic_object=output_schema)
        
        if isinstance(self.llm, MockChatGoogleGenerativeAI):
            chain = MockChain(self.llm, parser)
            return chain.invoke({**input_variables})
            
        prompt = ChatPromptTemplate.from_template(
            prompt_template + "\n\n{format_instructions}"
        )
        chain = prompt | self.llm | parser
        
        try:
            result = chain.invoke({
                **input_variables,
                "format_instructions": parser.get_format_instructions()
            })
            return result
        except Exception as e:
            self.logger.error(f"LLM call failed: {str(e)}")
            raise

    def log_decision(self, reasoning: str, action: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Log a structured decision for transparency."""
        self.logger.log_agent_action(
            agent=self.agent_type.value,
            action=action,
            reasoning=reasoning,
            output_data=data
        )
