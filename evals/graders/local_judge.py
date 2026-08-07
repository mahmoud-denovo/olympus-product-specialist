import json
from pathlib import Path
from typing import Dict, Any, List

DATASET_FILE = Path(__file__).resolve().parent.parent / "datasets" / "golden_scenarios.json"

class LocalJudge:
    """Zero-token deterministic local evaluator for agent recommendations."""

    def __init__(self):
        with open(DATASET_FILE, "r", encoding="utf-8") as f:
            self.scenarios = json.load(f)

    def evaluate_recommendation(
        self,
        scenario_id: str,
        generated_stand: str,
        generated_objective: str,
        sources: List[str]
    ) -> Dict[str, Any]:
        scenario = next((s for s in self.scenarios if s["id"] == scenario_id), None)
        if not scenario:
            return {"passed": False, "score": 0.0, "reason": "Scenario ID not found"}

        stand_match = (generated_stand == scenario["expected_stand"])
        obj_match = (generated_objective == scenario["expected_objective"])
        has_sources = len(sources) > 0 and any("evidentscientific.com" in src for src in sources)

        score = 0.0
        if stand_match: score += 0.4
        if obj_match: score += 0.4
        if has_sources: score += 0.2

        return {
            "scenario_id": scenario_id,
            "passed": score >= 0.8,
            "score": round(score, 2),
            "stand_match": stand_match,
            "objective_match": obj_match,
            "has_sources": has_sources
        }

if __name__ == "__main__":
    judge = LocalJudge()
    res = judge.evaluate_recommendation(
        scenario_id="scenario_001_metallurgical_darkfield",
        generated_stand="BX53M",
        generated_objective="MPLFLN-BD",
        sources=["https://evidentscientific.com/en/products/upright/bx53m/"]
    )
    print("Local Judge Test Scorecard:", json.dumps(res, indent=2))
