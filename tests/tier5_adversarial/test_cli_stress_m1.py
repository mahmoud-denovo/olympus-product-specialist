"""
Tier 5 Adversarial Stress Test Suite for Milestone M1 (src/cli/formatter.py, src/cli/hitl.py, src/cli/main.py)
"""

import io
import json
import os
import sys
import pytest
from rich.console import Console
from rich.panel import Panel

from src.cli.formatter import (
    RichFormatter,
    render_step_progress,
    render_bilingual_card,
    render_option_cards,
)
from src.cli.hitl import HITLHandler, HITLDecision, HITLResponse
from src.cli.main import parse_args, run_cli
from src.engine.sequential_thinking import (
    AssemblyStage,
    OptionCard,
    StageResult,
    AssemblyState,
    SequentialThinkingEngine,
    EngineError,
    IncompatibleComponentError,
)


def test_formatter_terminal_widths():
    """
    Empirical test: Render RichFormatter components under various extreme terminal widths.
    Check for exceptions, visual crashes, formatting breaks, or integer division errors.
    """
    sample_card = OptionCard(
        id="IX73_STRESS",
        stage=AssemblyStage.FRAME,
        model_name="Olympus IX73 Inverted Frame",
        arabic_description="هيكل مجهر مقلوب متقدم للدراسات البيولوجية الحية وعلم الخلايا",
        english_specs={"magnification_range": "10x-100x", "ports": 4, "light_path": "100:0 / 20:80 / 0:100"},
        price_tier="Premium",
        optical_compatibility_status=True,
        recommended=True
    )

    widths = [5, 10, 15, 20, 30, 40, 60, 80, 120, 300, 1000]
    
    for w in widths:
        buffer = io.StringIO()
        console = Console(file=buffer, width=w, force_terminal=True, color_system=None)
        formatter = RichFormatter(console=console)

        # Test render_header
        formatter.render_header()
        
        # Test render_stage_progress
        formatter.render_stage_progress(AssemblyStage.FRAME, 1, 5)

        # Test render_bilingual_option_card
        card_panel = formatter.render_bilingual_option_card(sample_card, index=1, is_selected=True)
        console.print(card_panel)

        # Test render_option_grid
        formatter.render_option_grid([sample_card])

        # Test render_assembly_summary
        state = AssemblyState()
        state.selected_components[AssemblyStage.FRAME] = sample_card
        formatter.render_assembly_summary(state)

        # Test render_error and render_info
        formatter.render_error("Test Error Title", "Detailed error message body under width constraint")
        formatter.render_info("Test Info Title", "Detailed info message body under width constraint")

        output = buffer.getvalue()
        assert len(output) > 0, f"No output produced for terminal width {w}"


def test_formatter_arabic_rtl_and_bidi():
    """
    Empirical test: Render Arabic RTL, Tashkeel, Tatweel, BiDi mixed text, special control characters.
    """
    complex_arabic_card = {
        "id": "ARABIC_BIDI_01",
        "stage": "frame",
        "model_name": "Olympus IX73 (مجهر ضوئي 100x)",
        "arabic_description": "مِجْهَرٌ بَصَرِيٌّ مَقْلُوبٌ مــــعــــدٌّ لِلْبُحُوثِ\nملاحظة: يدعم C-Mount & BFP (Back Focal Plane) \u202eRTL_OVERRIDE\u202c 100% متوافق",
        "english_specs": {"mag": "100X", "resolution_nm": 200, "adapter": "C-Mount 0.5x"},
        "price_tier": "Standard / قياسي",
        "optical_compatibility_status": False,
        "incompatibility_reason": "عدم تطابق القلاووظ (Thread mismatch RMS vs M25)",
        "recommended": False
    }

    buffer = io.StringIO()
    console = Console(file=buffer, width=80, force_terminal=True)
    formatter = RichFormatter(console=console)

    # Test render_bilingual_card function
    text_repr = render_bilingual_card(complex_arabic_card)
    assert "مِجْهَرٌ" in text_repr
    assert "C-Mount" in text_repr

    # Test RichFormatter render_bilingual_option_card
    panel = formatter.render_bilingual_option_card(complex_arabic_card, index=1)
    console.print(panel)
    output = buffer.getvalue()
    
    assert "Incompatible" in output or "غير متوافق" in output or "Thread mismatch" in output
    assert "مِجْهَرٌ" in output or "مجهر" in output or "مــــعــــدٌّ" in output or "RTL_OVERRIDE" in output


def test_formatter_edge_cases_and_malformed_inputs():
    """
    Empirical test: Feed malformed, empty, None, or unexpected types into RichFormatter methods.
    """
    buffer = io.StringIO()
    console = Console(file=buffer, width=80)
    formatter = RichFormatter(console=console)

    # 1. Stage progress with unknown/invalid stage input
    formatter.render_stage_progress(current_stage="NON_EXISTENT_STAGE", stage_idx=99, total_stages=5)
    output = buffer.getvalue()
    assert "NON_EXISTENT_STAGE" in output

    # 2. Card with empty dict, missing fields, or non-dict specs
    empty_card = {}
    card_panel = formatter.render_bilingual_option_card(empty_card, index=1)
    console.print(card_panel)

    malformed_specs_card = {
        "model_name": "Test Specs Model",
        "arabic_description": "وصف",
        "english_specs": "Plain string spec instead of dict",
        "price_tier": None,
        "optical_compatibility_status": True
    }
    formatter.render_bilingual_option_card(malformed_specs_card, index=2)

    # 3. render_assembly_summary with dict having valid stage entries
    dict_state = {
        "components": {
            "frame": {"model_name": "IX73", "arabic_description": "هيكل", "english_specs": {"type": "Inverted"}},
        }
    }
    formatter.render_assembly_summary(dict_state)

    # 4. render_step_progress with invalid input
    step_str = render_step_progress(stage=12345, current_step=-1, total_steps=0)
    assert "12345" in step_str


def test_hitl_empty_choices_index_error_bug():
    """
    Empirical test: Verify prompt_option_selection handles empty choices list without raising IndexError.
    """
    handler = HITLHandler(non_interactive=True)
    assert handler.prompt_option_selection(choices=[]) is None


def test_hitl_default_input_prompt_mismatch_bug():
    """
    Empirical test: Verify UI prompt convention in prompt_stage_approval.
    The prompt text displays '[y/N/edit]' indicating capital 'N' (Decline) is the default on empty input (Enter).
    Verify prompt_stage_approval maps empty input ('') to DECLINE.
    """
    console = Console(file=io.StringIO())
    
    # Simulate user pressing Enter (empty input '')
    handler = HITLHandler(console=console, input_func=lambda prompt="": "")
    stage_res = StageResult(
        stage="frame",
        stage_index=1,
        choices=[OptionCard(id="IX73", stage="frame", model_name="IX73", arabic_description="", english_specs={})],
        prompt_ar="",
        prompt_en="",
        requires_hitl=True
    )
    
    resp = handler.prompt_stage_approval(stage_res)
    assert resp.decision == HITLDecision.DECLINE


def test_hitl_interactive_input_simulations():
    """
    Empirical test: HITLHandler under interactive mode with various simulated inputs.
    """
    console = Console(file=io.StringIO())

    # Helper to simulate input queue
    def make_input_func(inputs_list):
        it = iter(inputs_list)
        return lambda prompt="": next(it)

    # 1. prompt_stage_approval with Arabic inputs
    handler_ar = HITLHandler(console=console, input_func=make_input_func(["نعم", "تعديل", "تفاصيل", "مساعدة", "لا"]))
    
    stage_res = StageResult(
        stage="frame",
        stage_index=1,
        choices=[OptionCard(id="IX73", stage="frame", model_name="IX73", arabic_description="", english_specs={})],
        prompt_ar="",
        prompt_en="",
        requires_hitl=True
    )

    resp_yes = handler_ar.prompt_stage_approval(stage_res)
    assert resp_yes.decision == HITLDecision.ACCEPT
    assert resp_yes.selected_option_id == "IX73"

    resp_edit = handler_ar.prompt_stage_approval(stage_res)
    assert resp_edit.decision == HITLDecision.EDIT

    resp_details = handler_ar.prompt_stage_approval(stage_res)
    assert resp_details.decision == HITLDecision.DETAILS

    resp_help = handler_ar.prompt_stage_approval(stage_res)
    assert resp_help.decision == HITLDecision.HELP

    resp_no = handler_ar.prompt_stage_approval(stage_res)
    assert resp_no.decision == HITLDecision.DECLINE

    # 2. EOFError and KeyboardInterrupt handling in input_func
    def eof_input(prompt=""):
        raise EOFError("Simulated EOF")

    def ki_input(prompt=""):
        raise KeyboardInterrupt("Simulated Ctrl+C")

    handler_eof = HITLHandler(console=console, input_func=eof_input)
    assert handler_eof.request_approval(OptionCard(id="IX73", stage="frame", model_name="IX73", arabic_description="", english_specs={})) is False
    assert handler_eof.prompt_stage_approval(stage_res).decision == HITLDecision.DECLINE

    handler_ki = HITLHandler(console=console, input_func=ki_input)
    assert handler_ki.request_approval(OptionCard(id="IX73", stage="frame", model_name="IX73", arabic_description="", english_specs={})) is False
    assert handler_ki.prompt_stage_approval(stage_res).decision == HITLDecision.DECLINE

    # 3. Option selection bounds: invalid numbers, string text, negative indices
    choices = [
        OptionCard(id="OPT1", stage="frame", model_name="Option 1", arabic_description="", english_specs={}),
        OptionCard(id="OPT2", stage="frame", model_name="Option 2", arabic_description="", english_specs={}),
    ]
    
    handler_sel = HITLHandler(console=console, input_func=make_input_func(["0", "99", "-5", "abc", "2"]))
    assert handler_sel.prompt_option_selection(choices).id == "OPT1"  # 0 out of bounds -> fallback to default [0]
    assert handler_sel.prompt_option_selection(choices).id == "OPT1"  # 99 out of bounds -> fallback [0]
    assert handler_sel.prompt_option_selection(choices).id == "OPT1"  # -5 invalid -> fallback [0]
    assert handler_sel.prompt_option_selection(choices).id == "OPT1"  # string invalid -> fallback [0]
    assert handler_sel.prompt_option_selection(choices).id == "OPT2"  # 2 is valid -> choices[1]


def test_cli_execution_piped_stdin_redirections(monkeypatch):
    """
    Empirical test: Execute run_cli() under simulated piped stdin redirections.
    """
    # 1. Full automated approval via piped stdin "y\ny\ny\ny\ny\n"
    stdin_data = "y\ny\ny\ny\ny\n"
    monkeypatch.setattr("sys.stdin", io.StringIO(stdin_data))
    
    res_code = run_cli([])
    assert res_code == 0

    # 2. Early abort at step 1 via piped stdin "n\n"
    monkeypatch.setattr("sys.stdin", io.StringIO("n\n"))
    res_code_abort = run_cli([])
    assert res_code_abort == 1

    # 3. Step back / undo via piped stdin "y\ny\nn\ny\ny\ny\ny\n"
    monkeypatch.setattr("sys.stdin", io.StringIO("y\ny\nn\ny\ny\ny\ny\n"))
    res_code_undo = run_cli([])
    assert res_code_undo == 0


def test_cli_invalid_argument_combinations(tmp_path):
    """
    Empirical test: Test CLI argument parsing and error handling for invalid/conflicting flags.
    """
    # 1. Both --interactive and --non-interactive specified
    parsed = parse_args(["--interactive", "--non-interactive"])
    assert parsed.non_interactive is True

    # 2. Export JSON to non-existent directory
    invalid_json_path = "/non_existent_directory_9999/assembly.json"
    res_code_exp_fail = run_cli(["--non-interactive", "--export-json", invalid_json_path])
    assert res_code_exp_fail == 1

    # 3. Export JSON to a directory path instead of a file
    dir_json_path = str(tmp_path)
    res_code_dir_fail = run_cli(["--non-interactive", "--export-json", dir_json_path])
    assert res_code_dir_fail == 1

    # 4. Export JSON to valid file path
    valid_json_path = str(tmp_path / "valid_assembly.json")
    res_code_exp_success = run_cli(["--non-interactive", "--export-json", valid_json_path])
    assert res_code_exp_success == 0
    assert os.path.exists(valid_json_path)
    with open(valid_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert "components" in data or isinstance(data, dict)

    # 5. Invalid flag passed to CLI
    with pytest.raises(SystemExit) as exc_info:
        parse_args(["--invalid-unknown-flag"])
    assert exc_info.value.code == 2
