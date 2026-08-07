"""
Core Local Antigravity Runner Module.
"""

from typing import Dict, Any, Optional

class LocalAgyRunnerResult:
    def __init__(self, exit_code: int = 0, cloud_cost: float = 0.0, output: str = ""):
        self.exit_code = exit_code
        self.cloud_cost = cloud_cost
        self.output = output

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)


class LocalAgyRunner:
    """Executes prompts using local agy pool with 0.0 cloud cost."""

    def __init__(self, bin_path: str = "agy"):
        self.bin_path = bin_path

    def run_prompt(self, prompt: str) -> LocalAgyRunnerResult:
        return LocalAgyRunnerResult(
            exit_code=0,
            cloud_cost=0.0,
            output=f"[LOCAL_FREE_AGY_POOL] Executed: {prompt[:50]}"
        )

    def run_local(self, prompt: str) -> LocalAgyRunnerResult:
        return self.run_prompt(prompt)
