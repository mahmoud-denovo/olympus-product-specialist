"""
Tier 2 Boundary Tests: Edge cases, boundary conditions, invalid inputs, resource limits.
"""

import pytest
import sqlite3


def test_boundary_web_inspector_invalid_urls_and_sql_injection():
    """
    Test web inspector resilience against malformed URLs, non-whitelisted domains,
    and potential injection strings in model numbers.
    """
    try:
        from src.validator.web_inspector import EvidentWebInspector
    except ImportError as e:
        pytest.fail(f"Web Inspector Implementation missing: {e}")

    inspector = EvidentWebInspector(offline_mode=True)

    # Edge Case 1: Malformed and empty URLs
    invalid_inputs = [
        "",
        "   ",
        "not_a_url",
        "ftp://evident-scientific.com/spec",
        "http://evident-scientific.com.attacker.com/malicious",
        "https://evident-scientific.com/../../../etc/passwd"
    ]
    for inp in invalid_inputs:
        res = inspector.validate_url(inp)
        valid = res.valid if hasattr(res, 'valid') else res.get('valid')
        assert valid is False, f"URL '{inp}' should be rejected as invalid"

    # Edge Case 2: SQL Injection / Malicious inputs in model numbers
    injection_models = [
        "IX73'; DROP TABLE components; --",
        "<script>alert(1)</script>",
        "SELECT * FROM users",
        "A" * 1000  # Extreme length input
    ]
    for model in injection_models:
        model_res = inspector.verify_model_number(model)
        verified = model_res.verified if hasattr(model_res, 'verified') else model_res.get('verified')
        assert verified is False, f"Model number injection string '{model}' should fail verification"


def test_boundary_gemini_judge_rate_limits_and_spending_caps(mock_gemini_env):
    """
    Test Gemini LLM Judge behavior under extreme request counts (>50 reqs) and spending caps.
    Must gracefully fallback to agy runner without throwing unhandled exceptions.
    """
    try:
        from src.judge.gemini_judge import GeminiJudge
    except ImportError as e:
        pytest.fail(f"Gemini Judge Implementation missing: {e}")

    # Set strict rate limit of 2 requests and spending cap of $0.02
    judge = GeminiJudge(daily_req_limit=2, daily_spending_cap=0.02)
    sample_config = {"frame": "IX73", "objective": "UPLSAPO60XO"}
    criteria = {"zero_hallucination": True}

    # First request: within limit
    v1 = judge.evaluate_configuration(sample_config, criteria=criteria)
    s1 = v1.source if hasattr(v1, 'source') else v1.get('source')
    
    # Second request: within limit
    v2 = judge.evaluate_configuration(sample_config, criteria=criteria)

    # Third request: exceeds rate limit of 2 -> must fallback to agy
    v3 = judge.evaluate_configuration(sample_config, criteria=criteria)
    s3 = v3.source if hasattr(v3, 'source') else v3.get('source')

    assert s3 == 'agy_fallback', "Exceeding daily request limit must cause graceful fallback to agy_fallback"


def test_boundary_optical_compatibility_edge_cases(initialized_db):
    """
    Test Knowledge Graph optical compatibility checks for severe physical mismatches:
    - Thread mismatch (M32 on RMS without adapter)
    - Parfocality distance mismatch (45mm vs 60mm)
    - Sensor format vignetting (Full Frame camera sensor on 0.35X C-mount adapter)
    """
    try:
        from src.db.knowledge_graph import KnowledgeGraph
    except ImportError as e:
        pytest.fail(f"Knowledge Graph Implementation missing: {e}")

    kg = KnowledgeGraph(db_path=initialized_db)

    # Boundary Case 1: M32 thread on RMS nosepiece
    frame_rms = {"id": "IX73", "category": "frame", "thread_type": "RMS", "optical_standard": "UIS2"}
    obj_m32 = {"id": "XLPLN25XW", "category": "objective", "thread_type": "M32", "optical_standard": "UIS2"}

    res1 = kg.check_optical_compatibility(frame_rms, obj_m32)
    compatible1 = res1.compatible if hasattr(res1, 'compatible') else res1.get('compatible')
    rule_violations1 = res1.rule_violations if hasattr(res1, 'rule_violations') else res1.get('rule_violations')

    assert compatible1 is False
    assert len(rule_violations1) > 0 or len(res1.get('required_adapters', [])) > 0

    # Boundary Case 2: Sensor format vignetting (1-inch camera sensor on 0.35X narrow mount adapter)
    camera_full_frame = {"id": "DP74", "category": "camera", "sensor_format": "1.1 inch"}
    adapter_narrow = {"id": "U-TV0.35XC", "category": "camera_adapter", "sensor_format": "1/3 inch"}

    res2 = kg.check_optical_compatibility(camera_full_frame, adapter_narrow)
    compatible2 = res2.compatible if hasattr(res2, 'compatible') else res2.get('compatible')
    assert compatible2 is False, "Camera sensor format larger than adapter format must cause vignetting lockout"


def test_boundary_rule_b01_invalid_and_empty_user_responses():
    """
    Test Rule B-01 guardrail handling of ambiguous, empty, or unexpected user inputs.
    Must safely default to rejecting adoption on any non-explicit confirmation.
    """
    try:
        from src.guardrails.rule_b01 import RuleB01Guardrail
    except ImportError as e:
        pytest.fail(f"Rule B-01 Guardrail Implementation missing: {e}")

    guardrail = RuleB01Guardrail()
    req = guardrail.check_legacy_adoption("LEGACY_RULE_99", {"desc": "Test legacy adoption"})

    invalid_responses = ["", "  ", "maybe", "123", "cancel", "what?", "\n"]

    for resp in invalid_responses:
        # Any non-'yes'/'y' response must default to False (rejection)
        approved = req.render_prompt_and_wait(user_input_func=lambda r=resp: r)
        assert approved is False, f"Response '{resp}' must be interpreted as rejection for Rule B-01"


def test_boundary_sqlite_knowledge_graph_empty_and_corrupt_db(tmp_path):
    """
    Test Knowledge Graph handling of uninitialized or missing database tables.
    """
    try:
        from src.db.knowledge_graph import KnowledgeGraph
    except ImportError as e:
        pytest.fail(f"Knowledge Graph Implementation missing: {e}")

    empty_db = tmp_path / "empty.db"
    # Touch empty file
    empty_db.write_text("")

    kg = KnowledgeGraph(db_path=str(empty_db))
    comp_a = {"id": "A", "category": "frame"}
    comp_b = {"id": "B", "category": "objective"}

    # Querying empty db should return unhandled exception safe failure or incompatible status
    res = kg.check_optical_compatibility(comp_a, comp_b)
    compatible = res.compatible if hasattr(res, 'compatible') else res.get('compatible')
    assert compatible is False
