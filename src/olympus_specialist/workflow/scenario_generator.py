"""
Parallel Evaluation Scenario Generator Subagent.
Runs continuously in parallel with main agent execution to generate,
mutate, and evaluate benchmark scenarios without blocking main flow.
"""

import os
import json
import time
import random
from pathlib import Path
from typing import Dict, Any, List

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATASET_PATH = PROJECT_ROOT / "evals" / "datasets" / "golden_scenarios.json"

STANDS = ["BX53M", "IX73", "GX53", "SZX16"]
MODES = ["Brightfield", "Darkfield", "Fluorescence", "Polarized"]
OBJECTIVES = ["MPLFLN-BD", "UPLAPO", "LMPLFLN", "PLN-BD"]


class ScenarioGeneratorSubagent:
    """
    Independent Parallel Subagent continuously crafting evaluation scenarios
    as Prompts-as-Code and Specs-as-Code.
    """

    def __init__(self, dataset_path: Path = DATASET_PATH):
        self.dataset_path = dataset_path
        self.generated_count = 0

    def generate_synthetic_scenario(self) -> Dict[str, Any]:
        """Generates a structured test scenario with optical constraints."""
        stand = random.choice(STANDS)
        mode = random.choice(MODES)
        objective = random.choice(OBJECTIVES)
        self.generated_count += 1

        scenario_id = f"scenario_auto_{int(time.time())}_{self.generated_count:03d}"
        return {
            "scenario_id": scenario_id,
            "description": f"Automated scenario for {stand} with {objective} under {mode}",
            "user_request": f"Configure {stand} microscope for {mode} imaging using {objective} series.",
            "expected_stand": stand,
            "expected_observation_mode": mode,
            "expected_objective": objective,
            "min_score_threshold": 0.80,
            "provenance_domain": "evidentscientific.com",
            "is_auto_generated": True,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }

    def append_scenario_to_dataset(self, scenario: Dict[str, Any]) -> bool:
        """Appends generated scenario to the golden dataset file."""
        if not self.dataset_path.exists():
            data = {"scenarios": []}
        else:
            with open(self.dataset_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except Exception:
                    data = {"scenarios": []}

        if "scenarios" not in data:
            data["scenarios"] = []

        data["scenarios"].append(scenario)

        with open(self.dataset_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        return True


if __name__ == "__main__":
    generator = ScenarioGeneratorSubagent()
    new_scenario = generator.generate_synthetic_scenario()
    print("Parallel Scenario Generator Created:", new_scenario["scenario_id"])
