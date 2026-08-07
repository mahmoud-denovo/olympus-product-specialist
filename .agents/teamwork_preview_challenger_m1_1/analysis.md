# Empirical Stress Testing Analysis — Milestone M1 (`src/engine/` & `src/cli/`)

**Target Subsystems**: `src/engine/sequential_thinking.py`, `src/cli/main.py`, `src/cli/formatter.py`, `src/cli/hitl.py`  
**Execution Environment**: Python 3.14.6, macOS (Darwin)  
**Assigned Metadata Directory**: `/Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/.agents/teamwork_preview_challenger_m1_1`  
**Verdict**: **`Verdict: REJECT`**

---

## 1. Executive Summary

As Challenger 1, an empirical stress testing suite (`scratch/stress_test_m1.py`) was constructed and executed against `src/engine/sequential_thinking.py` and `src/cli/`. The harness evaluated 38 test assertions covering invalid stage transitions, non-existent option IDs, empty catalog configurations, malformed JSON exports/paths, rapid undo/redo state cycles, and non-interactive CLI edge cases.

Out of 38 assertions tested, **30 passed** and **8 critical bugs / failure modes** were empirically reproduced. Key findings include state corruption during stage re-selection, out-of-order stage transition bypasses, unhandled CLI loop exceptions on incompatible choices, `IndexError` crashes on empty option sets, and silent export failures.

Because these failure modes directly break state machine integrity and CLI execution stability for Milestone M1, the milestone is **REJECTED**.

---

## 2. Empirical Test Harness Overview

A dedicated empirical stress harness was executed:
- **Test Harness Script**: `scratch/stress_test_m1.py`
- **Total Assertions**: 38
- **Passed Assertions**: 30
- **Failed Assertions / Confirmed Bugs**: 8

### Harness Output Summary:
```text
================================================================================
 SUMMARY OF EMPIRICAL STRESS TEST RESULTS
================================================================================
[PASS] normalize_stage('invalid_stage')
[PASS] normalize_stage('STAGE_99')
[PASS] normalize_stage('')
[PASS] normalize_stage('   ')
[PASS] normalize_stage('objective_invalid')
[PASS] normalize_stage(None)
[PASS] normalize_stage(123)
[PASS] normalize_stage(45.6)
[PASS] normalize_stage([])
[PASS] normalize_stage({})
[FAIL] engine.step('software') out of order
       -> VULNERABILITY: Engine allowed stepping directly into SOFTWARE out-of-order without validating prerequisite stages!
[FAIL] engine.select_option('software') without frame
       -> VULNERABILITY: Engine allowed option selection for SOFTWARE without prior stages selected! Selected stages: [<AssemblyStage.SOFTWARE: 'software'>]
[PASS] engine.select_option(FRAME, 'NON_EXISTENT_FRAME_999')
[PASS] engine.select_option(FRAME, '')
[PASS] engine.select_option(FRAME, '   ')
[PASS] engine.select_option(FRAME, 'IX73_FAKE')
[PASS] validate_component_compatibility(non-UIS2)
[PASS] select_option(incompatible)
[FAIL] empty_engine.step(FRAME)
       -> BUG: initial_catalog={} was overridden by default catalog! choices len = 3
[PASS] real_empty_engine.select_option(FRAME, 'IX73')
[PASS] hitl.prompt_stage_approval(empty_choices)
[FAIL] hitl.prompt_option_selection([])
       -> CRASH: IndexError when choices list is empty in prompt_option_selection: list index out of range
[PASS] run_cli export to '/nonexistent_directory_xyz/export.json' (nonexistent directory)
[FAIL] run_cli export to '' (empty string file path)
       -> BUG: export_json='' evaluates to False, skipping file write and silently returning 0 exit code!
[PASS] run_cli export to '/tmp' (directory path instead of file path)
[FAIL] json.dumps(state_with_set)
       -> CRASH: json.dumps raises TypeError on non-serializable specs (set): Object of type set is not JSON serializable
[PASS] engine(corrupt_db_path)
[PASS] undo_last_stage on empty state
[PASS] undo 1 (LIGHT_SOURCE)
[PASS] undo 2 (LIGHT_SOURCE)
[PASS] undo 3 (FRAME)
[PASS] undo 4 (empty)
[FAIL] undo after re-selecting FRAME
       -> BUG DETECTED: Popped 'light_source' instead of 'FRAME' because dict key insertion order was not updated on re-selection!
[PASS] run_cli(['--non-interactive'])
[PASS] run_cli with valid JSON export
[PASS] run_cli(['--interactive', '--non-interactive'])
[PASS] run_cli(['--invalid-flag-xyz'])
[FAIL] run_cli handling of incompatible choice 0
       -> CRASH/UNHANDLED EXCEPTION in CLI loop: run_cli does not catch IncompatibleComponentError: Component 'INCOMPAT_0' is incompatible: Optical standard 'NON_UIS2_STANDARD' is incompatible with Olympus UIS2 standard.
--------------------------------------------------------------------------------
Total Tests: 38 | Passed: 30 | Vulnerabilities/Bugs Found: 8
================================================================================
```

---

## 3. Detailed Breakdown of Confirmed Empirical Bugs

### Bug 1: State Machine Bypass (Out-of-Order Stage Transitions Allowed)
- **Location**: `src/engine/sequential_thinking.py:488` (`step()`) & `src/engine/sequential_thinking.py:499` (`select_option()`)
- **Observation**: Calling `engine.step("software")` or `engine.select_option("software", "cellSens-Dim")` on a brand new engine session succeeds without requiring stages 1 to 4 (`FRAME`, `LIGHT_SOURCE`, `OBJECTIVES`, `CAMERA_ADAPTER`).
- **Logic Chain**:
  1. `step()` calls `evaluate_stage_options(stage)` which directly sets `self.state.current_stage = norm_stage`.
  2. No check is performed to verify whether `norm_stage` follows the previous stage or if prior stages in `AssemblyStage` order are selected.
  3. `select_option()` checks component availability and compatibility, then invokes `self.state.add_selection(norm_stage, selected_card)`.
  4. `add_selection` inserts `norm_stage` into `self.selected_components` regardless of missing prerequisites.
- **Blast Radius**: High. Breaks the core 5-stage sequential assembly protocol contract. Users/API callers can jump to stage 5 or skip stages entirely, producing incomplete/invalid microscopy configurations.

---

### Bug 2: Dict Key Insertion Order Corruption on Stage Re-selection During Undo Cycles
- **Location**: `src/engine/sequential_thinking.py:179` (`add_selection()`) & `src/engine/sequential_thinking.py:186` (`undo_last_stage()`)
- **Observation**:
  1. User selects Stage 1 (`FRAME` -> `IX73`).
  2. User selects Stage 2 (`LIGHT_SOURCE` -> `LED-ILL`).
  3. User returns to Stage 1 and re-selects `FRAME` -> `BX53`.
  4. User triggers `undo_last_stage()`.
  5. **Expected**: Stage 1 (`FRAME`) is undone (the modified stage).
  6. **Actual**: Stage 2 (`LIGHT_SOURCE`) is undone instead!
- **Logic Chain**:
  1. In Python 3.7+, dictionary key order tracks initial key insertion.
  2. In `add_selection()`: `self.selected_components[stg] = option`. Updating an existing key `stg` changes its value but leaves its key position at index 0 (`FRAME`).
  3. In `undo_last_stage()`: `last_stage = list(self.selected_components.keys())[-1]`. Index `-1` returns `LIGHT_SOURCE` (index 1), not `FRAME` (index 0).
- **Blast Radius**: High. Causes silent state corruption during interactive edit/undo workflows in CLI.

---

### Bug 3: Falsy `initial_catalog={}` Overridden by Default Catalog
- **Location**: `src/engine/sequential_thinking.py:223`
- **Observation**: Instantiating `SequentialThinkingEngine(initial_catalog={})` results in `self.catalog` being populated with the full built-in default catalog instead of an empty catalog.
- **Logic Chain**:
  1. Code reads: `self.catalog = initial_catalog or self._load_default_catalog()`.
  2. In Python, an empty dictionary `{}` evaluates as boolean `False`.
  3. Expression evaluates `initial_catalog or self._load_default_catalog()`, replacing `{}` with `self._load_default_catalog()`.
- **Blast Radius**: Medium. Prevents passing custom empty catalogs or testing zero-catalog behavior.

---

### Bug 4: `HITLHandler.prompt_option_selection([])` Crashes with `IndexError`
- **Location**: `src/cli/hitl.py:115`
- **Observation**: Calling `hitl.prompt_option_selection([])` with an empty choices list raises an unhandled `IndexError: list index out of range`.
- **Logic Chain**:
  1. Line 115 checks: `if self.non_interactive or not choices: return choices[0]`.
  2. If `choices` is `[]`, `not choices` is `True`.
  3. Attempting `choices[0]` on empty list `[]` raises `IndexError`.
- **Blast Radius**: High. Causes immediate CLI process crash if a stage has no compatible options.

---

### Bug 5: Silent Success on Empty String Export Path (`--export-json ""`)
- **Location**: `src/cli/main.py:136`
- **Observation**: Running `run_cli(["--non-interactive", "--export-json", ""])` exits with code `0` (Success) without creating any export file.
- **Logic Chain**:
  1. `parsed_args.export_json` equals `""`.
  2. `if parsed_args.export_json:` evaluates to `False`.
  3. Export logic is completely bypassed; CLI returns exit code `0`.
- **Blast Radius**: Low-Medium. Misleads automated tooling into believing export succeeded.

---

### Bug 6: Unhandled `IncompatibleComponentError` in CLI Execution Loop
- **Location**: `src/cli/main.py:106` & `118`
- **Observation**: If choice 0 of a stage is optically incompatible, `engine.select_option()` raises `IncompatibleComponentError`, which is not caught by `run_cli()`, causing the CLI to crash with a traceback.
- **Logic Chain**:
  1. `run_cli()` calls `engine.select_option(stage, chosen_card.id)`.
  2. `select_option()` raises `IncompatibleComponentError` if `is_compat` is False.
  3. `run_cli()` lacks a `try...except EngineError` handler around component selection.
- **Blast Radius**: High. CLI crashes ungracefully when encountering incompatible components.

---

### Bug 7: Crash on Non-JSON-Serializable Specs (`json.dumps` TypeError)
- **Location**: `src/engine/sequential_thinking.py:108` & `src/cli/main.py:139`
- **Observation**: If `OptionCard.english_specs` contains non-primitive Python types (e.g. `set`, `datetime`), calling `json.dumps(engine.state.get_summary())` raises `TypeError: Object of type set is not JSON serializable`.
- **Logic Chain**:
  1. `OptionCard.to_dict()` includes `self.english_specs` directly.
  2. `json.dump()` attempts to serialize `english_specs` without type sanitization.
- **Blast Radius**: Medium. Prevents JSON exports when components contain set metadata.

---

### Bug 8: Immediate Stage State Mutation in `step()` Before HITL Confirmation
- **Location**: `src/engine/sequential_thinking.py:452`
- **Observation**: Calling `engine.step(stage)` immediately mutates `self.state.current_stage = norm_stage` before the user has reviewed or confirmed the stage option.
- **Logic Chain**:
  1. `evaluate_stage_options()` sets `self.state.current_stage = norm_stage` upon evaluation.
  2. If the user declines at the HITL prompt, `self.state.current_stage` remains set to the unconfirmed stage.
- **Blast Radius**: Low-Medium. Inconsistent state tracking between evaluated step vs committed step.

---

## 4. Unchallenged & Passing Areas

- **Stage Normalization (`normalize_stage`)**: Correctly handles case-insensitivity, whitespace, `objective` vs `objectives` aliases, and raises `InvalidStageError` for non-matching strings and non-string inputs (`None`, numbers, lists).
- **Non-Existent Option Selection**: `select_option()` correctly raises `EngineError` when passed non-existent option IDs.
- **UIS2 Optical Standard Validation**: `validate_component_compatibility()` correctly flags non-UIS2 standards (`DIN_160mm`) and blocks selection.
- **Corrupt SQLite DB Fallback**: `SequentialThinkingEngine` gracefully falls back to built-in default catalog when passed a corrupted database file path.
- **Argparse & Unknown Flags**: CLI correctly rejects unrecognized arguments with exit code `2`.
- **Dual Flag Handling**: Passing `--interactive` and `--non-interactive` simultaneously is handled cleanly, with `--non-interactive` taking precedence.

---

## 5. Mitigations & Fix Recommendations

1. **Enforce Sequential Stage Order**: In `SequentialThinkingEngine.step()` and `select_option()`, validate that `stage` matches `self.state.current_stage` or the immediate successor stage, and verify prerequisite stage selections exist in `self.state.selected_components`.
2. **Fix Dict Key Re-selection Order**: In `AssemblyState.add_selection()`, if `stg` already exists in `self.selected_components`, delete it first (`del self.selected_components[stg]`) before setting `self.selected_components[stg] = option` to move `stg` to the end of insertion order.
3. **Fix Catalog Default Guard**: Change `self.catalog = initial_catalog if initial_catalog is not None else self._load_default_catalog()`.
4. **Fix HITL Empty Choice Check**: In `hitl.py:115`, handle empty choices cleanly: `if not choices: return None` or raise a clean `CLIUIError`.
5. **Fix `--export-json` Flag Validation**: In `main.py`, check `if parsed_args.export_json is not None:` instead of `if parsed_args.export_json:`.
6. **Add Exception Handling in CLI Loop**: Wrap `engine.select_option()` calls in `run_cli()` with `try...except OlympusSpecialistError as e:` and display a rich error panel instead of crashing.
