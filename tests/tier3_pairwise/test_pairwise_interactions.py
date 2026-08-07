"""
Tier 3 Pairwise Tests: Cross-feature integration interactions.
Testing interactions between Engine, Web Inspector, Knowledge Graph, HitL, Gemini Judge, agy Runner, and Rule B-01 Guardrail.
"""

import pytest


def test_pairwise_sequential_engine_web_inspector_kg_hitl(initialized_db):
    """
    Pairwise Interaction 1:
    SequentialThinking Engine stage -> Web Inspector model validation ->
    Knowledge Graph optical compatibility check -> HitL user approval prompt.
    """
    try:
        from src.engine.sequential_thinking import SequentialThinkingEngine
        from src.validator.web_inspector import EvidentWebInspector
        from src.db.knowledge_graph import KnowledgeGraph
        from src.cli.hitl import HitLHandler
    except ImportError as e:
        pytest.fail(f"Pairwise components missing: {e}")

    engine = SequentialThinkingEngine(db_path=initialized_db)
    inspector = EvidentWebInspector(db_path=initialized_db, offline_mode=True)
    kg = KnowledgeGraph(db_path=initialized_db)
    hitl = HitLHandler()

    # 1. Engine generates choices for 'objectives' stage
    result = engine.step(stage="objectives", current_config={"frame": "IX73"})
    choices = result.choices if hasattr(result, 'choices') else result.get('choices')
    assert len(choices) > 0
    selected_option = choices[0]

    model_name = selected_option.model_name if hasattr(selected_option, 'model_name') else selected_option.get('model_name')

    # 2. Web Inspector verifies model number authenticity
    model_ver = inspector.verify_model_number(model_name)
    verified = model_ver.verified if hasattr(model_ver, 'verified') else model_ver.get('verified')
    assert verified is True

    # 3. Knowledge Graph verifies optical compatibility against frame
    comp_frame = {"id": "IX73", "category": "frame", "thread_type": "RMS", "optical_standard": "UIS2"}
    comp_obj = {
        "id": selected_option.id if hasattr(selected_option, 'id') else selected_option.get('id'),
        "category": "objective",
        "thread_type": selected_option.english_specs.get('thread', 'M25') if hasattr(selected_option, 'english_specs') else 'M25',
        "optical_standard": "UIS2"
    }
    compat_res = kg.check_optical_compatibility(comp_frame, comp_obj)
    assert compat_res is not None

    # 4. HitL Handler presents choice card and collects explicit user confirmation
    user_inputs = iter(["y"])
    approved = hitl.request_approval(selected_option, user_input_func=lambda: next(user_inputs))
    assert approved is True


def test_pairwise_gemini_judge_fallback_during_cli_workflow(mock_gemini_env):
    """
    Pairwise Interaction 2:
    Interactive CLI evaluation triggering Gemini Judge ->
    Gemini Judge hitting rate limit -> Graceful fallback to zero-cloud Local agy Runner
    without interrupting CLI step completion.
    """
    try:
        from src.judge.gemini_judge import GeminiJudge
        from src.core.agy_runner import LocalAgyRunner
    except ImportError as e:
        pytest.fail(f"Judge / Runner components missing: {e}")

    # Initialize Gemini judge with 0 rate limit to force immediate fallback
    judge = GeminiJudge(daily_req_limit=0)
    runner = LocalAgyRunner()

    current_config = {"frame": "IX73", "light_source": "LED-ILL", "objective": "UPLSAPO60XO"}
    criteria = {"zero_hallucination": True, "accuracy": True}

    # Evaluate config
    verdict = judge.evaluate_configuration(current_config, criteria=criteria)
    source = verdict.source if hasattr(verdict, 'source') else verdict.get('source')

    assert source == 'agy_fallback', "Must fall back to agy_fallback when judge limit is reached"

    # Verify local runner produces zero cloud cost fallback output
    agy_res = runner.run_prompt(f"Evaluate config: {current_config}")
    cloud_cost = agy_res.cloud_cost if hasattr(agy_res, 'cloud_cost') else agy_res.get('cloud_cost')
    assert cloud_cost == 0.0


def test_pairwise_web_inspector_network_fail_to_db_cache(initialized_db):
    """
    Pairwise Interaction 3:
    Web Inspector online validation failing (network error / offline) ->
    Automatic fallback to local SQLite Knowledge Graph cache during assembly step.
    """
    try:
        from src.validator.web_inspector import EvidentWebInspector
    except ImportError as e:
        pytest.fail(f"Web Inspector missing: {e}")

    # Force inspector into offline mode with knowledge DB
    inspector = EvidentWebInspector(db_path=initialized_db, offline_mode=True)

    # Attempt to validate model URL when network is down
    url = "https://www.evident-scientific.com/en/microscopes/inverted/ix73/"
    res = inspector.validate_url(url)
    
    valid = res.valid if hasattr(res, 'valid') else res.get('valid')
    cached = res.cached if hasattr(res, 'cached') else res.get('cached')

    assert valid is True
    assert cached is True, "Offline validation must set cached flag to True"


def test_pairwise_rule_b01_guardrail_before_sequential_step():
    """
    Pairwise Interaction 4:
    SequentialThinking step encountering legacy configuration rule ->
    Rule B-01 Guardrail intercepting step and requiring user prompt approval
    BEFORE adopting legacy rule logic into active assembly configuration.
    """
    try:
        from src.engine.sequential_thinking import SequentialThinkingEngine
        from src.guardrails.rule_b01 import RuleB01Guardrail
    except ImportError as e:
        pytest.fail(f"Engine / Guardrail components missing: {e}")

    guardrail = RuleB01Guardrail()
    
    # Intercept legacy law from legacy_reference/MIGRATION_MAP.md
    concept = "LEGACY_LAW_01_CAMERA_MAGNIFICATION"
    req = guardrail.check_legacy_adoption(concept, {"rule": "Auto-calculate tube lens factor from legacy DB"})

    # User declines legacy adoption -> Engine must use clean-slate default rule
    user_declines = req.render_prompt_and_wait(user_input_func=lambda: "n")
    assert user_declines is False, "User decline must block legacy adoption"
