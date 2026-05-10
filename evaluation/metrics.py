"""Metrics and evaluation for WorkflowSmith."""
import json
from datetime import datetime
from typing import List, Dict, Any
from src.utils.config import Config
from src.utils.logging import get_logger

logger = get_logger("evaluator")

class EvaluationFramework:
    """Calculates research metrics for the repair system."""
    
    def __init__(self):
        self.metrics_log = []

    def record_repair_session(self, scenario: str, result_state: Dict[str, Any]) -> None:
        """Process a finished repair state and calculate metrics."""
        start_time = result_state.get("start_time")
        end_time = datetime.now()
        
        duration = (end_time - start_time).total_seconds() if start_time else 0
        
        metrics = {
            "scenario": scenario,
            "outcome": result_state.get("termination_reason"),
            "mttr_seconds": duration,
            "iterations": result_state.get("iteration_count"),
            "patches_proposed": len(result_state.get("patches", [])),
            "verifications": len(result_state.get("verification_history", [])),
            "success": (result_state.get("termination_reason") == "REPAIR_SUCCESSFUL")
        }
        
        self.metrics_log.append(metrics)
        logger.info(f"Recorded metrics for {scenario}: {json.dumps(metrics, indent=2, default=str)}")

    def generate_report(self, output_path: str = "logs/evaluation_report.json") -> Dict[str, Any]:
        """Aggregate metrics into a final report."""
        if not self.metrics_log:
            return {}
            
        total_sessions = len(self.metrics_log)
        successful_repairs = sum(1 for m in self.metrics_log if m["success"])
        avg_mttr = sum(m.get("mttr_seconds") or 0 for m in self.metrics_log) / total_sessions
        avg_iterations = sum(m.get("iterations") or 0 for m in self.metrics_log) / total_sessions
        
        report = {
            "summary": {
                "total_runs": total_sessions,
                "success_rate": (successful_repairs / total_sessions) * 100,
                "avg_mttr": avg_mttr,
                "avg_iterations": avg_iterations
            },
            "raw_metrics": self.metrics_log
        }
        
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2, default=str)
            
        return report
