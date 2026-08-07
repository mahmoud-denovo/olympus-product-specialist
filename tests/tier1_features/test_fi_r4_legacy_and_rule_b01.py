"""
Tier 1 Feature Tests: FI-R4.1, FI-R4.2
Testing Legacy Reference Preservation & Rule B-01 Guardrail.
"""

from pathlib import Path
import pytest


def test_fi_r4_1_legacy_reference_migration_map_exists():
    """
    FI-R4.1: Verify legacy_reference/ directory exists and legacy_reference/MIGRATION_MAP.md
    is initialized with Rule B-01 explicitly documented.
    """
    migration_map_path = Path(__file__).parent.parent.parent / "legacy_reference" / "MIGRATION_MAP.md"
    assert migration_map_path.exists(), "legacy_reference/MIGRATION_MAP.md must exist"

    content = migration_map_path.read_text(encoding="utf-8")
    assert "Rule B-01" in content or "B-01" in content, "MIGRATION_MAP.md must explicitly document Rule B-01"
    assert "olympus-workspace-agent" in content, "MIGRATION_MAP.md must reference original legacy workspace agent"


def test_fi_r4_2_rule_b01_guardrail_approval_flow():
    """
    FI-R4.2: Verify Rule B-01 guardrail ensuring zero legacy code or decision is adopted
    without explicit prior user presentation and prompt approval.
    """
    try:
        from src.guardrails.rule_b01 import RuleB01Guardrail
    except ImportError as e:
        pytest.fail(f"FI-R4.2 Implementation missing: {e}")

    guardrail = RuleB01Guardrail()
    
    concept_id = "LEGACY_OPTICAL_CALC_RULE_42"
    details = {
        "legacy_source": "olympus-workspace-agent/calc.py",
        "description": "Legacy objective parfocality calculation formula"
    }

    # Generate approval request
    req = guardrail.check_legacy_adoption(concept_id, details)
    assert req is not None

    # Test 1: User approves legacy adoption ('y' / 'yes')
    approved = req.render_prompt_and_wait(user_input_func=lambda: "yes")
    assert approved is True

    # Test 2: User rejects legacy adoption ('n' / 'no')
    req2 = guardrail.check_legacy_adoption(concept_id, details)
    rejected = req2.render_prompt_and_wait(user_input_func=lambda: "no")
    assert rejected is False
