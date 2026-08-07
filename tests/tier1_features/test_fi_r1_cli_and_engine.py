"""
Tier 1 Feature Tests: FI-R1.1, FI-R1.2, FI-R1.3
Testing Interactive CLI & SequentialThinking HitL Engine interfaces.
"""

import pytest


def test_fi_r1_1_cli_rich_ui_and_logging(capsys):
    """
    FI-R1.1: Verify terminal CLI executes with rich UI and step-by-step logging.
    Tests main CLI entrypoint formatting and step progression logs.
    """
    try:
        from src.cli.formatter import render_step_progress, render_option_cards
        from src.cli.main import run_cli
    except ImportError as e:
        pytest.fail(f"FI-R1.1 Implementation missing: {e}")

    # Test rich step progress rendering
    log_output = render_step_progress(stage="frame", current_step=1, total_steps=5)
    assert "frame" in log_output.lower() or "الإطار" in log_output or "Step 1/5" in log_output

    # Test main CLI argument parsing or runner execution
    exit_code = run_cli(["--help"])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "olympus" in captured.out.lower() or "microscopy" in captured.out.lower()


def test_fi_r1_2_sequential_thinking_5_stages(initialized_db):
    """
    FI-R1.2: Verify native SequentialThinking protocol engine executes all 5 assembly stages:
    Frame, Light Source, Objectives, Camera Adapter, Software.
    """
    try:
        from src.engine.sequential_thinking import SequentialThinkingEngine
    except ImportError as e:
        pytest.fail(f"FI-R1.2 Implementation missing: {e}")

    engine = SequentialThinkingEngine(db_path=initialized_db)
    
    stages = ["frame", "light_source", "objectives", "camera_adapter", "software"]
    current_config = {}

    for stage in stages:
        result = engine.step(stage=stage, current_config=current_config)
        assert result is not None
        # Handle dict or object
        stage_name = result.stage if hasattr(result, 'stage') else result.get('stage')
        choices = result.choices if hasattr(result, 'choices') else result.get('choices')
        requires_hitl = result.requires_hitl if hasattr(result, 'requires_hitl') else result.get('requires_hitl')

        assert stage_name == stage
        assert isinstance(choices, list)
        assert len(choices) > 0
        assert requires_hitl is True, f"Stage {stage} must require HitL approval"
        
        # Select first available option for next stage testing
        first_card = choices[0]
        card_id = first_card.id if hasattr(first_card, 'id') else first_card.get('id')
        current_config[stage] = card_id

    assert len(current_config) == 5
    assert "frame" in current_config
    assert "software" in current_config


def test_fi_r1_3_bilingual_presentation_and_hitl(monkeypatch):
    """
    FI-R1.3: Verify bilingual card presentation (Arabic prose + English technical terms)
    and interactive prompt for explicit Human-in-the-Loop approval.
    """
    try:
        from src.cli.formatter import render_bilingual_card
        from src.cli.hitl import HitLHandler
    except ImportError as e:
        pytest.fail(f"FI-R1.3 Implementation missing: {e}")

    sample_card = {
        "id": "UPLSAPO60XO",
        "model_name": "UPLSAPO 60XO",
        "arabic_description": "عدسة شيئية عالية الدقة مغمورة بالزيت لتطبيقات الفلورة",
        "english_specs": {"mag": "60X", "na": 1.42, "thread": "M25"},
        "price_tier": "Premium",
        "optical_compatibility_status": True
    }

    # Verify bilingual card formatting
    card_text = render_bilingual_card(sample_card)
    assert "UPLSAPO 60XO" in card_text
    assert "عدسة شيئية" in card_text  # Arabic prose
    assert "60X" in card_text or "1.42" in card_text  # English technical specs

    # Test HitL Handler with simulated user approval ('y' or 'نعم')
    handler = HitLHandler()
    
    # Simulate user entering 'y'
    user_inputs = iter(["y"])
    approved = handler.request_approval(sample_card, user_input_func=lambda: next(user_inputs))
    assert approved is True

    # Simulate user rejecting with 'n'
    user_inputs_rej = iter(["n"])
    rejected = handler.request_approval(sample_card, user_input_func=lambda: next(user_inputs_rej))
    assert rejected is False
