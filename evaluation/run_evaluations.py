import os
import sys
import pandas as pd
from typing import Dict, Any

# Add the project root to the PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.main import WorkflowSmith
from src.evaluation.metrics import EvaluationFramework

def main():
    print("Initializing WorkflowSmith for Batch Evaluation...")
    smith = WorkflowSmith()
    evaluator = EvaluationFramework()
    
    # Create sample data
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)
    sample_csv = os.path.join(data_dir, "users.csv")
    
    def generate_dense_data(n=10000):
        import random
        from datetime import datetime, timedelta
        
        data = {
            "id": range(1, n + 1),
            "timestamp": [(datetime.now() - timedelta(minutes=random.randint(0, 10000))).isoformat() for _ in range(n)],
            "user_id": [random.randint(1000, 9999) for _ in range(n)],
            "action": [random.choice(["login", "logout", "purchase", "view", "click"]) for _ in range(n)],
            "status": [random.choice(["success", "failure", "pending"]) for _ in range(n)],
            "duration": [random.uniform(0.1, 10.0) for _ in range(n)],
            "ip_address": [f"192.168.1.{random.randint(1, 255)}" for _ in range(n)],
            "region": [random.choice(["US", "EU", "APAC", "LATAM"]) for _ in range(n)],
            "device": [random.choice(["mobile", "desktop", "tablet"]) for _ in range(n)],
            "browser": [random.choice(["chrome", "safari", "firefox", "edge"]) for _ in range(n)],
            "os": [random.choice(["macOS", "Windows", "Linux", "iOS", "Android"]) for _ in range(n)],
            "priority": [random.randint(1, 5) for _ in range(n)],
            "category": [random.choice(["electronics", "clothing", "home", "beauty"]) for _ in range(n)],
            "tags": [random.choice(["sale", "new", "top_rated", "none"]) for _ in range(n)],
            "metadata": [f"ref_{random.randint(100, 999)}" for _ in range(n)],
            "last_login": [(datetime.now() - timedelta(days=random.randint(0, 30))).isoformat() for _ in range(n)],
            "subscription": [random.choice(["free", "pro", "enterprise"]) for _ in range(n)],
            "is_active": [random.choice([True, False]) for _ in range(n)],
            "total_spend": [random.uniform(0.0, 5000.0) for _ in range(n)],
            "referral": [random.choice(["social", "email", "ads", "organic"]) for _ in range(n)]
        }
        return pd.DataFrame(data)

    generate_dense_data().to_csv(sample_csv, index=False)
    
    scenarios = ["schema_drift", "data_corruption", "logic_bug"]
    
    for scenario in scenarios:
        print(f"\nEvaluating scenario: {scenario}")
        
        # Reset the sample data for each run
        generate_dense_data().to_csv(sample_csv, index=False)
        
        try:
            result_state = smith.run_repair(scenario, sample_csv)
            evaluator.record_repair_session(scenario, result_state)
            print(f"Scenario {scenario} outcome: {result_state.get('termination_reason', 'UNKNOWN')}")
        except Exception as e:
            print(f"Error evaluating scenario {scenario}: {e}")
            evaluator.record_repair_session(scenario, {"termination_reason": f"ERROR: {str(e)}"})
            
    print("\nGenerating comprehensive report...")
    os.makedirs("logs", exist_ok=True)
    report = evaluator.generate_report("logs/evaluation_report.json")
    print(f"Evaluation complete. Reports saved to logs/evaluation_report.json")
    print(f"Summary: {report.get('summary', {})}")

if __name__ == "__main__":
    main()
