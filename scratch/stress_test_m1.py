"""
Empirical Stress Test Suite for Milestone M1 (SequentialThinking Engine & CLI)
"""

import os
import sys
import json
import tempfile
import sqlite3
from typing import Any

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.engine.sequential_thinking import (
    SequentialThinkingEngine,
    AssemblyStage,
    AssemblyState,
    OptionCard,
    StageResult,
    InvalidStageError,
    EngineError,
    IncompatibleComponentError,
    normalize_stage,
)
from src.cli.main import run_cli, parse_args
from src.cli.formatter import RichFormatter, render_step_progress, render_bilingual_card
from src.cli.hitl import HITLHandler, HITLDecision, HITLResponse


def print_section(title: str):
    print("\n" + "=" * 80)
    print(f" STRESS TEST SECTION: {title}")
    print("=" * 80)


test_results = []

def record_result(name: str, passed: bool, details: str):
    status = "PASS" if passed else "FAIL"
    test_results.append((name, status, details))
    print(f"[{status}] {name}: {details}")


# ==============================================================================
# SECTION 1: INVALID STAGE TRANSITIONS & INPUTS
# ==============================================================================
def test_invalid_stage_transitions():
    print_section("1. Invalid Stage Transitions & Stage Normalization Inputs")

    # 1.1 Invalid string inputs to normalize_stage
    invalid_inputs = ["invalid_stage", "STAGE_99", "", "   ", "objective_invalid"]
    for inp in invalid_inputs:
        try:
            normalize_stage(inp)
            record_result(f"normalize_stage('{inp}')", False, "Expected InvalidStageError, but succeeded.")
        except InvalidStageError as e:
            record_result(f"normalize_stage('{inp}')", True, f"Caught expected InvalidStageError: {e}")
        except Exception as e:
            record_result(f"normalize_stage('{inp}')", False, f"Unexpected exception type: {type(e).__name__}: {e}")

    # 1.2 Non-string types to normalize_stage
    non_str_inputs = [None, 123, 45.6, [], {}]
    for inp in non_str_inputs:
        try:
            normalize_stage(inp)
            record_result(f"normalize_stage({inp})", False, "Expected InvalidStageError, but succeeded.")
        except InvalidStageError as e:
            record_result(f"normalize_stage({inp})", True, f"Caught expected InvalidStageError: {e}")
        except Exception as e:
            record_result(f"normalize_stage({inp})", False, f"Unexpected exception type: {type(e).__name__}: {e}")

    # 1.3 Out-of-order stage transitions in engine
    engine = SequentialThinkingEngine()
    try:
        # Step directly to stage 5 (SOFTWARE) without stage 1-4
        res = engine.step("software")
        if res.stage == "software":
            record_result("engine.step('software') out of order", False, 
                          "VULNERABILITY: Engine allowed stepping directly into SOFTWARE out-of-order without validating prerequisite stages!")
        else:
            record_result("engine.step('software') out of order", True, f"Handled out-of-order stage: {res}")
    except Exception as e:
        record_result("engine.step('software') out of order", True, f"Exception raised on out-of-order step: {e}")

    # 1.4 Selecting option for out-of-order stage
    try:
        res = engine.select_option("software", "cellSens-Dim")
        record_result("engine.select_option('software') without frame", False,
                      f"VULNERABILITY: Engine allowed option selection for SOFTWARE without prior stages selected! Selected stages: {list(engine.state.selected_components.keys())}")
    except Exception as e:
        record_result("engine.select_option('software') without frame", True, f"Exception raised: {e}")


# ==============================================================================
# SECTION 2: NON-EXISTENT OPTION IDS & HARDENING
# ==============================================================================
def test_non_existent_option_ids():
    print_section("2. Non-existent Option IDs & Incompatible Components")

    engine = SequentialThinkingEngine()

    # 2.1 Non-existent option ID for valid stage
    non_existent_ids = ["NON_EXISTENT_FRAME_999", "", "   ", "IX73_FAKE"]
    for opt_id in non_existent_ids:
        try:
            engine.select_option(AssemblyStage.FRAME, opt_id)
            record_result(f"engine.select_option(FRAME, '{opt_id}')", False, "Expected EngineError, but selection succeeded.")
        except EngineError as e:
            record_result(f"engine.select_option(FRAME, '{opt_id}')", True, f"Caught expected EngineError: {e}")
        except Exception as e:
            record_result(f"engine.select_option(FRAME, '{opt_id}')", False, f"Unexpected exception: {type(e).__name__}: {e}")

    # 2.2 Incompatible component status validation
    incompatible_card = OptionCard(
        id="NON_UIS2_FRAME",
        stage=AssemblyStage.FRAME,
        model_name="Old DIN Frame",
        arabic_description="إطار قديم",
        english_specs={"optical_standard": "DIN_160mm"},
    )
    is_compat, reason = engine.validate_component_compatibility(incompatible_card)
    if not is_compat and "UIS2" in (reason or ""):
        record_result("validate_component_compatibility(non-UIS2)", True, f"Correctly flagged incompatibility: {reason}")
    else:
        record_result("validate_component_compatibility(non-UIS2)", False, f"Failed to flag non-UIS2: compat={is_compat}, reason={reason}")

    # 2.3 Attempt to select incompatible card directly added to catalog
    engine.catalog[AssemblyStage.FRAME].append(incompatible_card)
    try:
        engine.select_option(AssemblyStage.FRAME, "NON_UIS2_FRAME")
        record_result("select_option(incompatible)", False, "Allowed selection of incompatible component!")
    except IncompatibleComponentError as e:
        record_result("select_option(incompatible)", True, f"Caught expected IncompatibleComponentError: {e}")
    except Exception as e:
        record_result("select_option(incompatible)", False, f"Unexpected exception: {type(e).__name__}: {e}")


# ==============================================================================
# SECTION 3: EMPTY CATALOG CONFIGURATIONS
# ==============================================================================
def test_empty_catalog_configs():
    print_section("3. Empty Catalog Configurations")

    # 3.1 Completely empty catalog dictionary
    empty_engine = SequentialThinkingEngine(initial_catalog={})
    try:
        res = empty_engine.step(AssemblyStage.FRAME)
        if len(res.choices) == 0:
            record_result("empty_engine.step(FRAME)", True, "Returned empty choices list without crashing.")
        else:
            record_result("empty_engine.step(FRAME)", False, f"BUG: initial_catalog={{}} was overridden by default catalog! choices len = {len(res.choices)}")
    except Exception as e:
        record_result("empty_engine.step(FRAME)", False, f"Engine crashed on empty catalog step: {e}")

    # 3.2 Select option on empty catalog (when catalog is actually empty)
    real_empty_engine = SequentialThinkingEngine(initial_catalog={AssemblyStage.FRAME: []})
    # Note: initial_catalog={AssemblyStage.FRAME: []} evaluates to truthy!
    try:
        real_empty_engine.select_option(AssemblyStage.FRAME, "IX73")
        record_result("real_empty_engine.select_option(FRAME, 'IX73')", False, "Expected EngineError, but selection succeeded.")
    except EngineError as e:
        record_result("real_empty_engine.select_option(FRAME, 'IX73')", True, f"Caught expected EngineError: {e}")
    except Exception as e:
        record_result("real_empty_engine.select_option(FRAME, 'IX73')", False, f"Unexpected exception: {type(e).__name__}: {e}")

    # 3.3 Non-interactive CLI with empty catalog choices (CRASH TEST)
    hitl = HITLHandler(non_interactive=True)
    empty_stage_res = StageResult(stage="frame", stage_index=1, choices=[])
    try:
        resp = hitl.prompt_stage_approval(empty_stage_res)
        record_result("hitl.prompt_stage_approval(empty_choices)", True, f"Handled empty choices in non-interactive: {resp}")
    except IndexError as e:
        record_result("hitl.prompt_stage_approval(empty_choices)", False, f"CRASH: IndexError when stage_result choices is empty in prompt_stage_approval: {e}")

    try:
        opt = hitl.prompt_option_selection([])
        record_result("hitl.prompt_option_selection([])", True, f"Handled empty choices in prompt_option_selection: {opt}")
    except IndexError as e:
        record_result("hitl.prompt_option_selection([])", False, f"CRASH: IndexError when choices list is empty in prompt_option_selection: {e}")


# ==============================================================================
# SECTION 4: MALFORMED JSON EXPORTS & NON-SERIALIZABLE OBJECTS
# ==============================================================================
def test_malformed_json_and_exports():
    print_section("4. Malformed JSON Exports & DB Edge Cases")

    # 4.1 Export JSON to invalid file paths
    invalid_paths = [
        ("/nonexistent_directory_xyz/export.json", "nonexistent directory"),
        ("", "empty string file path"),
        ("/tmp", "directory path instead of file path"),
    ]
    for p, desc in invalid_paths:
        code = run_cli(["--non-interactive", "--export-json", p])
        if p == "" and code == 0:
            record_result(f"run_cli export to '{p}' ({desc})", False, "BUG: export_json='' evaluates to False, skipping file write and silently returning 0 exit code!")
        elif code != 0:
            record_result(f"run_cli export to '{p}' ({desc})", True, f"Returned non-zero exit code: {code}")
        else:
            record_result(f"run_cli export to '{p}' ({desc})", False, f"Returned 0 exit code despite failure!")

    # 4.2 Export JSON with non-serializable objects in english_specs
    engine = SequentialThinkingEngine()
    card_with_set = OptionCard(
        id="CUSTOM_FRAME",
        stage=AssemblyStage.FRAME,
        model_name="Custom Set Frame",
        arabic_description="إطار تجريبي",
        english_specs={"tags": {"laser", "fluorescence"}},  # Python set is not JSON serializable!
    )
    engine.state.add_selection(AssemblyStage.FRAME, card_with_set)
    summary = engine.state.get_summary()
    try:
        json.dumps(summary)
        record_result("json.dumps(state_with_set)", True, "Dumps succeeded.")
    except TypeError as e:
        record_result("json.dumps(state_with_set)", False, f"CRASH: json.dumps raises TypeError on non-serializable specs (set): {e}")

    # 4.3 Malformed DB path handling
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        corrupt_db_path = f.name
        f.write(b"NOT A SQLITE DATABASE CORRUPT HEADER")

    engine = SequentialThinkingEngine(db_path=corrupt_db_path)
    if len(engine.catalog[AssemblyStage.FRAME]) > 0:
        record_result("engine(corrupt_db_path)", True, "Gracefully fell back to default catalog on corrupt DB.")
    else:
        record_result("engine(corrupt_db_path)", False, "Catalog empty after corrupt DB fallback!")

    try:
        os.remove(corrupt_db_path)
    except OSError:
        pass


# ==============================================================================
# SECTION 5: RAPID UNDO/REDO CYCLES & STATE CONSISTENCY
# ==============================================================================
def test_rapid_undo_redo_cycles():
    print_section("5. Rapid Undo/Redo Cycles & State Order Inconsistency")

    engine = SequentialThinkingEngine()

    # 5.1 Undo on empty state
    undone = engine.state.undo_last_stage()
    if undone is None:
        record_result("undo_last_stage on empty state", True, "Returned None cleanly.")
    else:
        record_result("undo_last_stage on empty state", False, f"Returned unexpected value: {undone}")

    # 5.2 Rapid multi-cycle select & undo
    engine.reset()
    card_frame = engine.catalog[AssemblyStage.FRAME][0]
    card_light = engine.catalog[AssemblyStage.LIGHT_SOURCE][0]

    engine.state.add_selection(AssemblyStage.FRAME, card_frame)
    engine.state.add_selection(AssemblyStage.LIGHT_SOURCE, card_light)

    u1 = engine.state.undo_last_stage()
    if u1 == AssemblyStage.LIGHT_SOURCE:
        record_result("undo 1 (LIGHT_SOURCE)", True, f"Undone stage: {u1}")
    else:
        record_result("undo 1 (LIGHT_SOURCE)", False, f"Expected LIGHT_SOURCE, got: {u1}")

    engine.state.add_selection(AssemblyStage.LIGHT_SOURCE, card_light)
    u2 = engine.state.undo_last_stage()
    if u2 == AssemblyStage.LIGHT_SOURCE:
        record_result("undo 2 (LIGHT_SOURCE)", True, f"Undone stage: {u2}")
    else:
        record_result("undo 2 (LIGHT_SOURCE)", False, f"Expected LIGHT_SOURCE, got: {u2}")

    u3 = engine.state.undo_last_stage()
    if u3 == AssemblyStage.FRAME:
        record_result("undo 3 (FRAME)", True, f"Undone stage: {u3}")
    else:
        record_result("undo 3 (FRAME)", False, f"Expected FRAME, got: {u3}")

    u4 = engine.state.undo_last_stage()
    if u4 is None:
        record_result("undo 4 (empty)", True, "Returned None.")
    else:
        record_result("undo 4 (empty)", False, f"Expected None, got: {u4}")

    # 5.3 OUT-OF-ORDER RE-SELECTION BUG TEST
    engine.reset()
    card_frame_2 = engine.catalog[AssemblyStage.FRAME][1]
    engine.state.add_selection(AssemblyStage.FRAME, card_frame)
    engine.state.add_selection(AssemblyStage.LIGHT_SOURCE, card_light)
    # Re-select FRAME (updating stage 1)
    engine.state.add_selection(AssemblyStage.FRAME, card_frame_2)

    undone_stage = engine.state.undo_last_stage()
    if undone_stage == AssemblyStage.FRAME:
        record_result("undo after re-selecting FRAME", True, "Popped FRAME (the component modified).")
    else:
        record_result("undo after re-selecting FRAME", False, 
                      f"BUG DETECTED: Popped '{undone_stage}' instead of 'FRAME' because dict key insertion order was not updated on re-selection!")


# ==============================================================================
# SECTION 6: CLI NON-INTERACTIVE EXECUTION & EDGE CASES
# ==============================================================================
def test_cli_non_interactive_and_edge_cases():
    print_section("6. CLI Non-Interactive Execution & Edge Case Arguments")

    # 6.1 Standard non-interactive run
    code = run_cli(["--non-interactive"])
    if code == 0:
        record_result("run_cli(['--non-interactive'])", True, "Successfully ran 5-stage assembly non-interactively with exit code 0.")
    else:
        record_result("run_cli(['--non-interactive'])", False, f"Failed with exit code: {code}")

    # 6.2 Non-interactive with valid JSON export
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        export_file = f.name

    code = run_cli(["--non-interactive", "--export-json", export_file])
    if code == 0 and os.path.exists(export_file) and os.path.getsize(export_file) > 0:
        with open(export_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("is_complete") is True and len(data.get("components", {})) == 5:
            record_result("run_cli with valid JSON export", True, f"JSON exported successfully with 5 components.")
        else:
            record_result("run_cli with valid JSON export", False, f"Export content invalid: {data}")
    else:
        record_result("run_cli with valid JSON export", False, f"Export failed, code={code}, exists={os.path.exists(export_file)}")

    try:
        os.remove(export_file)
    except OSError:
        pass

    # 6.3 Combined --interactive and --non-interactive flags
    code = run_cli(["--interactive", "--non-interactive"])
    if code == 0:
        record_result("run_cli(['--interactive', '--non-interactive'])", True, "Handled dual flags without crashing, non-interactive took precedence.")
    else:
        record_result("run_cli(['--interactive', '--non-interactive'])", False, f"Failed with code: {code}")

    # 6.4 Invalid command line flag
    code = run_cli(["--invalid-flag-xyz"])
    if code == 2:
        record_result("run_cli(['--invalid-flag-xyz'])", True, "Argparse correctly returned exit code 2 on unknown argument.")
    else:
        record_result("run_cli(['--invalid-flag-xyz'])", False, f"Unexpected exit code on invalid flag: {code}")

    # 6.5 Unhandled Engine Exception in run_cli (Incompatible First Option)
    custom_engine = SequentialThinkingEngine(initial_catalog={
        AssemblyStage.FRAME: [
            OptionCard(
                id="INCOMPAT_0",
                stage=AssemblyStage.FRAME,
                model_name="Incompatible Frame 0",
                arabic_description="إطار غير متوافق",
                english_specs={"optical_standard": "NON_UIS2_STANDARD"},
            )
        ]
    })

    # Test run_cli behavior when choice 0 is incompatible in non-interactive mode
    # Let's run a small test function to see if run_cli crashes with unhandled exception
    try:
        # Simulate run_cli with custom engine in non-interactive mode
        stage = AssemblyStage.FRAME
        stage_res = custom_engine.step(stage=stage)
        chosen_card = stage_res.choices[0]
        # In run_cli line 106: engine.select_option(stage, chosen_card.id)
        custom_engine.select_option(stage, chosen_card.id)
        record_result("run_cli handling of incompatible choice 0", False, "Allowed selection of incompatible choice 0!")
    except IncompatibleComponentError as e:
        record_result("run_cli handling of incompatible choice 0", True, f"Handled IncompatibleComponentError: {e}")
    except Exception as e:
        record_result("run_cli handling of incompatible choice 0", False, f"Exception: {e}")


def main():
    print("=" * 80)
    print(" STARTING EMPIRICAL STRESS TEST SUITE FOR M1")
    print("=" * 80)

    test_invalid_stage_transitions()
    test_non_existent_option_ids()
    test_empty_catalog_configs()
    test_malformed_json_and_exports()
    test_rapid_undo_redo_cycles()
    test_cli_non_interactive_and_edge_cases()

    print("\n" + "=" * 80)
    print(" SUMMARY OF EMPIRICAL STRESS TEST RESULTS")
    print("=" * 80)
    passed_count = sum(1 for _, status, _ in test_results if status == "PASS")
    failed_count = sum(1 for _, status, _ in test_results if status == "FAIL")

    for name, status, details in test_results:
        print(f"[{status}] {name}")
        print(f"       -> {details}")

    print("-" * 80)
    print(f"Total Tests: {len(test_results)} | Passed: {passed_count} | Vulnerabilities/Bugs Found: {failed_count}")
    print("=" * 80)


if __name__ == "__main__":
    main()
