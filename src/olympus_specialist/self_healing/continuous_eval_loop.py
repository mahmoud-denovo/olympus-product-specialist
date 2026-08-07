import sys
import time
import logging
from pathlib import Path
from typing import Dict, Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from olympus_specialist.workflow.scenario_generator import ScenarioGeneratorAgent
from olympus_specialist.self_healing.remediation import SelfHealingEngine
from olympus_specialist.workflow.eaer_pipeline import EAERPipeline
from evals.reporters.eval_reporter import GoogleADKEvalReporter

logger = logging.getLogger(__name__)

class ContinuousEvalLifecycle:
    """
    Continuous Evaluation & Autonomous Self-Healing Lifecycle Engine.
    Runs long-running autonomous evaluation loops (e.g., 60-minute background cycles),
    generating new edge-case scenarios, amplifying the golden dataset, repairing failures,
    and updating Google ADK formal evaluation reports.
    """
    def __init__(self):
        self.scenario_generator = ScenarioGeneratorAgent()
        self.self_healing = SelfHealingEngine()
        self.pipeline = EAERPipeline()
        self.reporter = GoogleADKEvalReporter()

    def run_continuous_cycle(self, duration_seconds: int = 3600, max_iterations: int = 5) -> Dict[str, Any]:
        """
        Executes an autonomous continuous evaluation & dataset amplification loop.
        """
        start_time = time.time()
        iteration = 0
        cycle_history = []

        logger.info(f"Starting Continuous Eval Lifecycle: Target Duration={duration_seconds}s, Max Iterations={max_iterations}")

        while (time.time() - start_time) < duration_seconds and iteration < max_iterations:
            iteration += 1
            iteration_start = time.time()

            # 1. Run formal Google ADK Evaluation Reporter across current scenarios
            eval_summary = self.reporter.run_eval_suite()

            # 2. Check for low-scoring scenarios or missing slots
            low_score_scenarios = [
                r for r in eval_summary.get("results", []) if not r.get("passed", False)
            ]

            # 3. Generate and amplify new seed scenario from Evident sources
            new_seed = {
                "id": f"scenario_auto_{iteration:03d}",
                "user_query": f"Automated defect inspection query iteration {iteration}",
                "application": "metallurgical",
                "observation_mode": "Darkfield",
                "stand_id": "BX53M",
                "objective_series": "MPLFLN-BD",
                "source_url": "https://evidentscientific.com/en/products/upright/bx53m/"
            }
            amplified = self.scenario_generator.amplify_seed_case(new_seed)

            # 4. Perform self-healing remediation if low score detected
            remediation_info = None
            if low_score_scenarios:
                remediation_info = self.self_healing.diagnose_and_repair(
                    session_id=f"eval_loop_{iteration}",
                    step_index=iteration,
                    error=ValueError("Evaluation score below pass threshold"),
                    missing_slots=["stand_id", "observation_mode"]
                )

            cycle_history.append({
                "iteration": iteration,
                "duration_ms": round((time.time() - iteration_start) * 1000, 2),
                "pass_rate_pct": eval_summary.get("pass_rate_pct"),
                "avg_score": eval_summary.get("average_score"),
                "amplified_scenario_id": amplified.get("id"),
                "remediation_triggered": bool(remediation_info)
            })

            # Sleep briefly per iteration
            time.sleep(0.1)

        total_elapsed = round(time.time() - start_time, 2)
        final_summary = self.reporter.run_eval_suite()

        return {
            "status": "COMPLETED",
            "total_iterations": iteration,
            "total_elapsed_seconds": total_elapsed,
            "final_pass_rate_pct": final_summary.get("pass_rate_pct"),
            "final_avg_score": final_summary.get("average_score"),
            "cycle_history": cycle_history
        }

if __name__ == "__main__":
    lifecycle = ContinuousEvalLifecycle()
    result = lifecycle.run_continuous_cycle(duration_seconds=5, max_iterations=3)
    print("Continuous Lifecycle Execution Result:", result)
