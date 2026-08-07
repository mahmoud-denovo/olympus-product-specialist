"""
Tier 1 Feature Tests: FI-R2.1, FI-R2.2, FI-R2.3
Testing Zero-Cloud Local Core (agy) & Controlled Gemini LLM Judge.
"""

import os
import pytest


def test_fi_r2_1_zero_cloud_cost_agy_runner():
    """
    FI-R2.1: Verify local Antigravity CLI (agy) runner operates with zero cloud token cost.
    """
    try:
        from src.core.agy_runner import LocalAgyRunner
    except ImportError as e:
        pytest.fail(f"FI-R2.1 Implementation missing: {e}")

    runner = LocalAgyRunner()
    result = runner.run_prompt("Validate microscope assembly compatibility")
    
    # Handle dict or object
    output = result.output if hasattr(result, 'output') else result.get('output')
    exit_code = result.exit_code if hasattr(result, 'exit_code') else result.get('exit_code')
    cloud_cost = result.cloud_cost if hasattr(result, 'cloud_cost') else result.get('cloud_cost')

    assert exit_code == 0
    assert cloud_cost == 0.0, "Zero-cloud-cost runner must have 0.0 cloud cost"
    assert output is not None


def test_fi_r2_2_controlled_gemini_llm_judge(mock_gemini_env):
    """
    FI-R2.2: Verify controlled Gemini LLM Judge evaluates configuration accuracy,
    zero-hallucination checks, and tracks daily request limits & spending caps.
    """
    try:
        from src.judge.gemini_judge import GeminiJudge
    except ImportError as e:
        pytest.fail(f"FI-R2.2 Implementation missing: {e}")

    judge = GeminiJudge(daily_req_limit=50, daily_spending_cap=0.50)
    
    sample_config = {
        "frame": "IX73",
        "objective": "UPLSAPO60XO",
        "camera": "DP74"
    }
    criteria = {"zero_hallucination": True, "accuracy": True}

    verdict = judge.evaluate_configuration(sample_config, criteria=criteria)
    
    # Handle dict or object
    score = verdict.score if hasattr(verdict, 'score') else verdict.get('score')
    zero_hall = verdict.zero_hallucination_passed if hasattr(verdict, 'zero_hallucination_passed') else verdict.get('zero_hallucination_passed')
    source = verdict.source if hasattr(verdict, 'source') else verdict.get('source')
    cost = verdict.cost_charged if hasattr(verdict, 'cost_charged') else verdict.get('cost_charged')

    assert isinstance(score, (int, float))
    assert 0.0 <= score <= 1.0
    assert isinstance(zero_hall, bool)
    assert source in ['gemini', 'agy_fallback']
    assert cost <= 0.50


def test_fi_r2_3_graceful_fallback_to_agy(mock_no_gemini_env):
    """
    FI-R2.3: Verify graceful fallback mechanism to local agy pool when GEMINI_API_KEY
    is absent, rate-limited, or daily spending cap is reached.
    """
    try:
        from src.judge.gemini_judge import GeminiJudge
    except ImportError as e:
        pytest.fail(f"FI-R2.3 Implementation missing: {e}")

    # Case 1: No API key set
    judge_no_key = GeminiJudge()
    verdict = judge_no_key.evaluate_configuration({"frame": "IX73"}, criteria={"zero_hallucination": True})
    
    source = verdict.source if hasattr(verdict, 'source') else verdict.get('source')
    assert source == 'agy_fallback', "Must fallback to agy_fallback when GEMINI_API_KEY is absent"

    # Case 2: Spending cap reached
    judge_capped = GeminiJudge(daily_spending_cap=0.0)  # Immediately capped
    verdict_capped = judge_capped.evaluate_configuration({"frame": "IX73"}, criteria={"zero_hallucination": True})
    
    source_capped = verdict_capped.source if hasattr(verdict_capped, 'source') else verdict_capped.get('source')
    assert source_capped == 'agy_fallback', "Must fallback to agy_fallback when spending cap is reached"
