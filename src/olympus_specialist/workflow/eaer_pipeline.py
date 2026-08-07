"""
EAER (Extraction -> Amplification -> Evaluation -> Redo) Workflow Engine.

4-Stage Pipeline Architecture:
1. Stage 1: Extraction - Fetch raw Evident/Olympus specs, catalog nodes, and URL provenance.
2. Stage 2: Amplification - Synthesize optical specs and validate stand-to-optics compatibility.
3. Stage 3: Evaluation - $0-cost deterministic evaluation using LocalJudge against golden benchmarks.
4. Stage 4: Redo / Self-Healing - Trigger autonomous remediation if score < 0.80 or optical mismatch occurs.
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.olympus_specialist.logging.logger import log_step
from src.olympus_specialist.self_healing.remediation import SelfHealingEngine
from src.olympus_specialist.domain.compatibility.rules import validate_stand_optics
from src.validator.web_inspector import EvidentWebInspector
from evals.graders.local_judge import LocalJudge


class EAERPipeline:
    """
    4-Stage EAER (Extraction -> Amplification -> Evaluation -> Redo) Workflow Engine.
    Executes end-to-end extraction, optical synthesis, local $0-cost evaluation,
    and self-healing remediation loops for Olympus/Evident microscopy configurations.
    """

    def __init__(self):
        self.self_healing = SelfHealingEngine()
        self.local_judge = LocalJudge()
        self.web_inspector = EvidentWebInspector()

    def run_pipeline(
        self,
        session_id: str,
        user_request: str,
        stand_id: str,
        observation_mode: str,
        objective_series: str,
        scenario_id: Optional[str] = "scenario_001_metallurgical_darkfield"
    ) -> Dict[str, Any]:
        """
        Executes the 4-Stage EAER Pipeline.

        Args:
            session_id: Session identifier for correlation logging.
            user_request: Original user query or requirements text.
            stand_id: Microscope stand model (e.g., 'BX53M', 'IX73').
            observation_mode: Imaging technique (e.g., 'Darkfield', 'Fluorescence').
            objective_series: Objective lens series (e.g., 'MPLFLN-BD', 'UPLAPO').
            scenario_id: Benchmark scenario ID for LocalJudge evaluation.

        Returns:
            Dict containing pipeline status, optical configuration, evaluation scorecard, and remediation if triggered.
        """
        # Identify missing input slots
        missing_slots = []
        if not stand_id:
            missing_slots.append("stand_id")
        if not observation_mode:
            missing_slots.append("observation_mode")
        if not objective_series:
            missing_slots.append("objective_series")

        # Stage 1: Extraction (Fetch raw Evident specs / catalog nodes & provenance)
        source_url = (
            f"https://evidentscientific.com/en/products/upright/{stand_id.lower()}/"
            if stand_id
            else "https://evidentscientific.com/en/products/"
        )
        url_validation = self.web_inspector.validate_url(source_url)

        raw_extraction = {
            "stand_id": stand_id,
            "observation_mode": observation_mode,
            "objective_series": objective_series,
            "source_url": source_url,
            "url_whitelisted": url_validation.domain_whitelisted
        }
        log_step(
            session_id=session_id,
            step_index=1,
            action="EAER_EXTRACTION",
            status="SUCCESS",
            details={"user_request": user_request, "raw_extraction": raw_extraction}
        )

        # Stage 2: Amplification (Synthesize optical specs & compatibility)
        log_step(
            session_id=session_id,
            step_index=2,
            action="EAER_AMPLIFICATION",
            status="PROCESSING",
            details=raw_extraction
        )

        if missing_slots:
            compat_result = {
                "compatible": False,
                "reason": f"Missing required input parameters: {', '.join(missing_slots)}"
            }
        else:
            compat_result = validate_stand_optics(stand_id, observation_mode, objective_series)

        # Stage 3: Evaluation ($0-Cost Local Judge Audit)
        log_step(
            session_id=session_id,
            step_index=3,
            action="EAER_EVALUATION",
            status="AUDITING"
        )
        eval_scorecard = self.local_judge.evaluate_recommendation(
            scenario_id=scenario_id or "scenario_001_metallurgical_darkfield",
            generated_stand=stand_id,
            generated_objective=objective_series,
            sources=[source_url]
        )

        score = eval_scorecard.get("score", 0.0)
        is_compatible = compat_result.get("compatible", False)

        # Stage 4: Redo / Remediation (Self-healing loop if score < 0.80 or incompatible)
        if not is_compatible or score < 0.80 or not eval_scorecard.get("passed"):
            log_step(
                session_id=session_id,
                step_index=4,
                action="EAER_REDO_TRIGGERED",
                status="HEALING_REQUIRED",
                details={"scorecard": eval_scorecard, "compatibility": compat_result}
            )
            remediation = self.self_healing.diagnose_and_repair(
                session_id=session_id,
                step_index=4,
                error=ValueError(
                    compat_result.get("reason", f"Evaluation score threshold not met (Score: {score:.2f} < 0.80)")
                ),
                missing_slots=missing_slots
            )
            return {
                "status": "HEALING_REQUIRED",
                "remediation": remediation,
                "scorecard": eval_scorecard,
                "optical_configuration": compat_result
            }

        log_step(
            session_id=session_id,
            step_index=4,
            action="EAER_PIPELINE_COMPLETE",
            status="PASSED",
            details={"scorecard": eval_scorecard}
        )
        return {
            "status": "SUCCESS",
            "optical_configuration": compat_result,
            "provenance": source_url,
            "scorecard": eval_scorecard
        }


if __name__ == "__main__":
    pipeline = EAERPipeline()
    res = pipeline.run_pipeline(
        session_id="test_eaer_001",
        user_request="Metallurgical inspection 50x darkfield",
        stand_id="BX53M",
        observation_mode="Darkfield",
        objective_series="MPLFLN-BD"
    )
    print("EAER Pipeline Test Output:", res)
