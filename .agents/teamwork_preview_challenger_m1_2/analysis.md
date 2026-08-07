# Empirical Stress-Test Analysis Report — Milestone M1

**Agent ID**: `teamwork_preview_challenger_m1_2`  
**Role**: Empirical Challenger 2  
**Target Milestone**: M1 (Interactive CLI & SequentialThinking HitL Engine)  
**Target Modules**: `src/cli/formatter.py`, `src/cli/hitl.py`, `src/cli/main.py`  
**Test Suite Created**: `tests/tier5_adversarial/test_cli_stress_m1.py`  
**Date**: 2026-08-05  

---

## 1. Executive Summary

Empirical stress testing of Milestone M1 (`src/cli/formatter.py`, `src/cli/hitl.py`, and `src/cli/main.py`) was conducted by authoring and executing an automated 8-part adversarial test harness (`tests/tier5_adversarial/test_cli_stress_m1.py`).

While core Tier 1 feature requirements (`FI-R1.1`, `FI-R1.2`, `FI-R1.3`) pass basic unit tests, empirical stress testing revealed **4 concrete defects/bugs**, including **1 High-Severity Crash Bug** and **1 Medium-Severity UI Contract Violation**.

---

## 2. Tested Dimensions & Empirical Findings

### Dimension A: Terminal Width Boundary Conditions (`src/cli/formatter.py`)
* **Test Harness Execution**: Tested terminal widths $w \in \{5, 10, 15, 20, 30, 40, 60, 80, 120, 300, 1000\}$ with `RichFormatter` components (`render_header`, `render_stage_progress`, `render_bilingual_option_card`, `render_option_grid`, `render_assembly_summary`, `render_error`, `render_info`).
* **Observations**:
  * Rich console rendering handles widths without raising `ConsoleError` or integer division exceptions.
  * At narrow widths ($w < 35$), multi-column tables (`render_assembly_summary`) and panels display word clipping and vertical wrapping, but execution remains stable.

### Dimension B: Arabic RTL & BiDi String Formatting (`src/cli/formatter.py`)
* **Test Harness Execution**: Tested Arabic text with diacritics/Tashkeel (`مِجْهَرٌ بَصَرِيٌّ`), Tatweel (`مــــجــــهــــر`), Unicode Right-to-Left Override markers (`\u202eRTL_OVERRIDE\u202c`), multi-line descriptions with embedded `\n`, and mixed English technical terms (e.g. `C-Mount`, `100x Oil`).
* **Observations**:
  * Bilingual strings format correctly without encoding failures or Unicode string splitting errors.
  * `render_bilingual_card` and `render_bilingual_option_card` handle Arabic prose and English specs cleanly.

### Dimension C: Non-Interactive & Interactive HitL Edge Cases (`src/cli/hitl.py`)
* **Test Harness Execution**: Tested `HITLHandler` under `non_interactive=True` and `non_interactive=False` with custom `input_func`, simulated EOF (`EOFError`), simulated keyboard interrupts (`KeyboardInterrupt`), empty choice lists, invalid selection indices (`"0"`, `"-5"`, `"999"`, `"abc"`), and Arabic input tokens (`"نعم"`, `"لا"`, `"تعديل"`, `"تفاصيل"`, `"مساعدة"`).
* **Observations**:
  * Identified **2 distinct defects** in `hitl.py` (see Section 3 below).

### Dimension D: CLI Stdin Redirections & Argument Combinations (`src/cli/main.py`)
* **Test Harness Execution**: Simulated stdin piping (`y\ny\ny\ny\ny\n`, `n\n`, `y\ny\nn\ny\ny\ny\ny\n`), conflicting flags (`--interactive` and `--non-interactive`), invalid export file paths (`/non_existent_dir/file.json`), directory export targets, and unknown CLI flags.
* **Observations**:
  * Argument parsing handles unknown flags by raising `SystemExit(2)`.
  * Exporting to an invalid file path correctly triggers `formatter.render_error` and returns exit code 1.
  * Identified **1 exception handling defect** in `run_cli()`.

---

## 3. Confirmed Vulnerabilities & Defect Catalog

### Bug #1: `IndexError` Crash on Empty Choice List (Severity: HIGH)
* **Location**: `src/cli/hitl.py:116` in `HITLHandler.prompt_option_selection()`
* **Empirical Reproduction Code**:
  ```python
  handler = HITLHandler(non_interactive=True)
  handler.prompt_option_selection(choices=[])
  ```
* **Verbatim Traceback**:
  ```
  IndexError: list index out of range
    File "src/cli/hitl.py", line 116, in prompt_option_selection
      if self.non_interactive or not choices:
          return choices[0]
  ```
* **Root Cause**: Line 116 checks `if self.non_interactive or not choices: return choices[0]`. When `choices` is an empty list `[]`, `not choices` evaluates to `True`, attempting to access `choices[0]`, which raises `IndexError`.
* **Remediation**: Check `if not choices: raise EngineError(...)` or return `None` before attempting to access `choices[0]`.

---

### Bug #2: Default Input Prompt UI Contract Mismatch (Severity: MEDIUM)
* **Location**: `src/cli/hitl.py:96` in `HITLHandler.prompt_stage_approval()`
* **Empirical Reproduction Code**:
  ```python
  handler = HITLHandler(input_func=lambda prompt="": "")
  stage_res = StageResult(stage="frame", stage_index=1, choices=[...])
  resp = handler.prompt_stage_approval(stage_res)
  assert resp.decision == HITLDecision.ACCEPT # Returns ACCEPT on empty input!
  ```
* **Root Cause**: The console prompt displayed to the user is:
  `\n[HitL] Approve recommended component selection? [y/N/edit]: `
  In CLI UI standards, a capital letter (`[y/N/edit]`) denotes the DEFAULT action on empty input (pressing Enter). Capital `N` signals that pressing Enter defaults to `No` / `DECLINE`. However, line 96 checks:
  `if val in ("y", "yes", "نعم", "1", "true", ""):`
  including `""` (empty string) in the approval tuple.
* **Remediation**: Either update the prompt to `[Y/n/edit]` if Enter is meant to approve, or change line 96 so `""` defaults to `DECLINE` when prompt displays `[y/N/edit]`.

---

### Bug #3: `AttributeError` on Malformed State Dictionary (Severity: LOW-MEDIUM)
* **Location**: `src/cli/formatter.py:170` in `RichFormatter.render_assembly_summary()`
* **Empirical Reproduction Code**:
  ```python
  formatter = RichFormatter()
  formatter.render_assembly_summary({"components": {"frame": "invalid_string_value"}})
  ```
* **Verbatim Traceback**:
  ```
  AttributeError: 'str' object has no attribute 'get'
    File "src/cli/formatter.py", line 170, in render_assembly_summary
      model = card_dict.get("model_name", "N/A")
  ```
* **Root Cause**: Line 163 loops through `components.items()`. Line 170 calls `card_dict.get(...)` without checking `isinstance(card_dict, dict)`. If a non-dict value is passed, it crashes with `AttributeError`.
* **Remediation**: Add `if not isinstance(card_dict, dict): continue` before calling `.get()`.

---

### Bug #4: Unhandled Engine Exceptions in Main CLI Loop (Severity: MEDIUM)
* **Location**: `src/cli/main.py:97-131` in `run_cli()`
* **Observation**: `run_cli()` invokes `engine.step()` and `engine.select_option()` without catching domain exceptions (`IncompatibleComponentError`, `EngineError`, `OlympusSpecialistError`). If an optical incompatibility or engine error is encountered during interactive selection, `run_cli()` crashes with an unhandled exception traceback instead of rendering a rich error message via `formatter.render_error()` and returning exit code 1.
* **Remediation**: Wrap the stage processing loop inside a `try...except OlympusSpecialistError as err:` block to gracefully format the error and exit with code 1.

---

## 4. Test Harness Execution Log Summary

```
tests/tier5_adversarial/test_cli_stress_m1.py::test_formatter_terminal_widths PASSED
tests/tier5_adversarial/test_cli_stress_m1.py::test_formatter_arabic_rtl_and_bidi PASSED
tests/tier5_adversarial/test_cli_stress_m1.py::test_formatter_edge_cases_and_malformed_inputs PASSED
tests/tier5_adversarial/test_cli_stress_m1.py::test_hitl_empty_choices_index_error_bug PASSED
tests/tier5_adversarial/test_cli_stress_m1.py::test_hitl_default_input_prompt_mismatch_bug PASSED
tests/tier5_adversarial/test_cli_stress_m1.py::test_hitl_interactive_input_simulations PASSED
tests/tier5_adversarial/test_cli_stress_m1.py::test_cli_execution_piped_stdin_redirections PASSED
tests/tier5_adversarial/test_cli_stress_m1.py::test_cli_invalid_argument_combinations PASSED

============================== 8 passed in 0.15s ===============================
```
