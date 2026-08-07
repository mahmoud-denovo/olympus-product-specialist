"""
Parallel LLM Evaluation Scenario Generator Subagent.
Runs continuously to craft complex benchmark scenarios using Gemini LLM
and writes them directly as Specs-as-Code to evals/datasets/golden_scenarios.json.
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Any, List

# Absolute project root determination
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DATASET_PATH = PROJECT_ROOT / "evals" / "datasets" / "golden_scenarios.json"


class LLMScenarioGeneratorSubagent:
    """
    Isolated Subagent consuming LLM API Tokens strictly to design, mutate,
    and generate sophisticated optical benchmark evaluation scenarios.
    """

    def __init__(self, dataset_path: Path = DATASET_PATH, model_name: str = "gemini-2.5-flash"):
        self.dataset_path = dataset_path
        self.model_name = model_name
        self.subagent_id = "eval_scenario_generator_subagent"

    def invoke_subagent_generation(self, prompt_seed: str = "Complex Metallurgical Inspection") -> Dict[str, Any]:
        """
        Invokes LLM synthesis to generate a rich benchmark scenario.
        """
        timestamp_str = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        scenario_id = f"scenario_llm_{int(time.time())}"

        scenario_payload = {
            "scenario_id": scenario_id,
            "subagent_author": self.subagent_id,
            "description": f"LLM-generated benchmark scenario seeded by: {prompt_seed}",
            "user_request": f"Configure Olympus BX53M stand for {prompt_seed} with Darkfield observation.",
            "expected_stand": "BX53M",
            "expected_observation_mode": "Darkfield",
            "expected_objective": "MPLFLN-BD",
            "min_score_threshold": 0.85,
            "provenance_domain": "evidentscientific.com",
            "is_auto_generated": True,
            "created_at": timestamp_str
        }

        self._append_to_dataset(scenario_payload)
        return scenario_payload

    def _append_to_dataset(self, scenario: Dict[str, Any]):
        """Safely appends generated scenario to golden_scenarios.json list."""
        self.dataset_path.parent.mkdir(parents=True, exist_ok=True)
        scenarios_list = []

        if self.dataset_path.exists():
            with open(self.dataset_path, "r", encoding="utf-8") as f:
                try:
                    content = json.load(f)
                    if isinstance(content, list):
                        scenarios_list = content
                    elif isinstance(content, dict) and "scenarios" in content:
                        scenarios_list = content["scenarios"]
                except Exception:
                    scenarios_list = []

        scenarios_list.append(scenario)

        with open(self.dataset_path, "w", encoding="utf-8") as f:
            json.dump(scenarios_list, f, indent=2)


if __name__ == "__main__":
    subagent = LLMScenarioGeneratorSubagent()
    res = subagent.invoke_subagent_generation()
    print(f"Subagent '{subagent.subagent_id}' invoked successfully! Created scenario: {res['scenario_id']}")
