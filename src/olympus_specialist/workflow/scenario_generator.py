import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List

DATASET_FILE = Path(__file__).resolve().parent.parent.parent.parent / "evals" / "datasets" / "golden_scenarios.json"

class ScenarioGeneratorAgent:
    """
    Scenario Generator Agent that amplifies seed cases from official Evident sources
    and dynamically enriches the golden evaluation dataset (evals/datasets/golden_scenarios.json).
    """
    def __init__(self):
        self.dataset_path = DATASET_FILE
        self.dataset_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.dataset_path.exists():
            with open(self.dataset_path, "w", encoding="utf-8") as f:
                json.dump([], f)

    def amplify_seed_case(self, seed: Dict[str, Any]) -> Dict[str, Any]:
        """Amplifies 1 or 2 seed parameters into a validated edge-case evaluation scenario."""
        seed_id = seed.get("id") or f"scenario_{hashlib.md5(str(seed).encode('utf-8')).hexdigest()[:8]}"
        amplified_scenario = {
            "id": seed_id,
            "input": seed.get("user_query", f"Need a system for {seed.get('application', 'industrial')} analysis."),
            "expected_slots": {
                "application": seed.get("application", "metallurgical"),
                "observation_mode": seed.get("observation_mode", "Darkfield"),
                "magnification": seed.get("magnification", 50)
            },
            "expected_stand": seed.get("stand_id", "BX53M"),
            "expected_objective": seed.get("objective_series", "MPLFLN-BD"),
            "source_provenance": seed.get("source_url", "https://evidentscientific.com/en/products/upright/bx53m/"),
            "is_amplified": True
        }
        
        # Append to golden scenarios dataset if not present
        with open(self.dataset_path, "r+", encoding="utf-8") as f:
            scenarios = json.load(f)
            if not any(s.get("id") == seed_id for s in scenarios):
                scenarios.append(amplified_scenario)
                f.seek(0)
                json.dump(scenarios, f, indent=2)
                f.truncate()

        return amplified_scenario

if __name__ == "__main__":
    agent = ScenarioGeneratorAgent()
    res = agent.amplify_seed_case({
        "id": "scenario_003_semiconductor_wafer",
        "user_query": "I need a microscope for semiconductor wafer defect inspection.",
        "application": "semiconductor",
        "observation_mode": "DIC",
        "stand_id": "GX53",
        "objective_series": "LMPLFLN-BD"
    })
    print("Amplified Scenario Output:", res)
