# Milestone M1 Retry Analysis & Remediation Blueprint

## 1. Executive Summary & Overview

This document presents a comprehensive, evidence-backed root-cause analysis and exact refactoring blueprint for Worker M1 to remediate all 10 identified defects across the interactive CLI (`src/cli/`) and the SequentialThinking engine (`src/engine/`). 

Milestone M1 delivers the core 5-stage optical assembly state machine (`FRAME` -> `LIGHT_SOURCE` -> `OBJECTIVES` -> `CAMERA_ADAPTER` -> `SOFTWARE`) and bilingual Human-in-the-Loop (HitL) CLI interface for Evident/Olympus product assembly. While happy-path execution passes existing Tier 1 feature tests, empirical stress testing by Reviewer 2, Challenger 1, and Challenger 2 identified 10 critical bugs ranging from crash conditions and state corruption to UI convention mismatches.

All 10 defects have been verified against the current codebase in `src/engine/sequential_thinking.py`, `src/cli/formatter.py`, `src/cli/hitl.py`, and `src/cli/main.py`. Below is the detailed breakdown and actionable blueprint for Worker M1.

---

## 2. Comprehensive Root-Cause Analysis of the 10 Defects

### Defect 1: Unescaped Rich Markup Strings (`RichFormatter`)
- **Affected File**: `src/cli/formatter.py` (lines 86–194)
- **Root Cause**: `RichFormatter` interpolates dynamic string variables (e.g. error messages, titles, model names, Arabic descriptions, spec keys/values, incompatibility reasons) directly into Rich markup template strings without escaping square brackets (`[` and `]`).
- **Evidence**: Passing strings containing bracket patterns like `[Errno 2]: [/tmp/foo]` to `RichFormatter.render_error()` raises unhandled `rich.errors.MarkupError: closing tag '[/tmp/foo]' doesn't match any open tag`.
- **Blast Radius**: Application crashes whenever catalog data, file paths, or exception text contains bracketed content.

### Defect 2: HitL Menu Decisions (`DETAILS`, `HELP`) Stage Reversal
- **Affected File**: `src/cli/main.py` (lines 110–132)
- **Root Cause**: `HITLHandler` returns `HITLDecision.DETAILS` for `"details"` input and `HITLDecision.HELP` for `"help"` input. However, `main.py` only handles `HITLDecision.ACCEPT` and `HITLDecision.EDIT` in its decision `if/elif` chain. Any other decision falls into `else:`, which decrements `step_idx` and reverts to the previous stage.
- **Evidence**: Requesting details (`"details"`) or help (`"help"`) at the approval prompt causes `main.py` to revert the current stage and undo the previous selection.
- **Blast Radius**: High UX degradation; requesting information undoes user assembly progress.

### Defect 3: `IndexError` on Empty Choice List Handling in `HITLHandler`
- **Affected File**: `src/cli/hitl.py` (lines 81–85, 115–116)
- **Root Cause**: In `HITLHandler.prompt_option_selection()`, line 115 evaluates `if self.non_interactive or not choices: return choices[0]`. When `choices` is an empty list (`[]`), `not choices` evaluates to `True`, attempting `choices[0]` and raising `IndexError: list index out of range`. In `prompt_stage_approval()`, `choices[0]` is accessed without checking if `choices` is non-empty.
- **Evidence**: Executing `HITLHandler(non_interactive=True).prompt_option_selection([])` raises `IndexError: list index out of range`.
- **Blast Radius**: Process crash when evaluating empty catalog categories.

### Defect 4: HitL Default Prompt `[y/N/edit]` Response Mapping Mismatch
- **Affected File**: `src/cli/hitl.py` (lines 91, 96)
- **Root Cause**: Line 91 displays prompt `[HitL] Approve recommended component selection? [y/N/edit]:`. The capital letter `N` explicitly communicates that `No` (Decline) is the default choice when pressing Enter (`""`). However, line 96 checks `if val in ("y", "yes", "نعم", "1", "true", ""):`, mapping empty input (`""`) to `HITLDecision.ACCEPT`.
- **Evidence**: User pressing Enter on prompt `[y/N/edit]` yields `HITLDecision.ACCEPT` instead of `HITLDecision.DECLINE`.
- **Blast Radius**: Contract mismatch between UI prompt text and decision logic.

### Defect 5: Dict Insertion Order Corruption on Stage Re-selection in `AssemblyState`
- **Affected File**: `src/engine/sequential_thinking.py` (lines 179–194)
- **Root Cause**: `AssemblyState.add_selection(stage, option)` sets `self.selected_components[stg] = option`. In Python 3.7+, dictionary key updating does not alter existing key insertion position. When a user re-selects an earlier stage (e.g. stage 1), key position 0 is modified. When `undo_last_stage()` subsequently calls `list(self.selected_components.keys())[-1]`, it pops key position 1 (e.g. stage 2), undoing the wrong stage.
- **Evidence**: `add_selection(FRAME, card1)` -> `add_selection(LIGHT_SOURCE, card2)` -> `add_selection(FRAME, card1_alt)` -> `undo_last_stage()` pops `LIGHT_SOURCE` instead of `FRAME`.
- **Blast Radius**: Session history corruption during stage re-selections and rollbacks.

### Defect 6: Lack of Sequential Stage Guard in `SequentialThinkingEngine.step()`
- **Affected File**: `src/engine/sequential_thinking.py` (lines 488–503)
- **Root Cause**: Neither `step()` nor `select_option()` validates whether prerequisite stages have been completed before executing a target stage.
- **Evidence**: `engine.step("software")` or `engine.select_option("software", "cellSens-Dim")` succeeds on a fresh engine session without prior selection of `FRAME`, `LIGHT_SOURCE`, `OBJECTIVES`, or `CAMERA_ADAPTER`.
- **Blast Radius**: State machine order bypass; incomplete optical assembly sequences.

### Defect 7: Unhandled JSON Serialization Crash on Non-Primitive Spec Types
- **Affected File**: `src/engine/sequential_thinking.py` (lines 108–120, 196–207)
- **Root Cause**: `OptionCard.to_dict()` outputs `english_specs` directly. If `english_specs` contains non-primitive types (e.g. `set`, `Enum`, `datetime`, `uuid.UUID`), `json.dumps(engine.state.get_summary())` raises `TypeError: Object of type set is not JSON serializable`.
- **Evidence**: Creating card with `english_specs={"tags": {"laser"}}` causes `json.dumps()` to fail with `TypeError`.
- **Blast Radius**: Config export failure on complex catalog specs.

### Defect 8: Silent Export Skip on Empty String Path (`--export-json ""`)
- **Affected File**: `src/cli/main.py` (line 136)
- **Root Cause**: `if parsed_args.export_json:` evaluates to `False` when `parsed_args.export_json` is `""` (empty string), skipping export entirely and returning exit code `0`.
- **Evidence**: `run_cli(["--non-interactive", "--export-json", ""])` exits with code `0` without writing any export file.
- **Blast Radius**: Silent failure when user provides invalid or empty export path flags.

### Defect 9: Missing Domain Exception Catching in CLI Loop (`main.py`)
- **Affected File**: `src/cli/main.py` (lines 97–132)
- **Root Cause**: The main CLI stage execution loop in `main.py` does not catch `EngineError`, `IncompatibleComponentError`, or `OlympusSpecialistError`.
- **Evidence**: If an incompatible component or engine error occurs during `engine.select_option()`, the CLI crashes with a raw Python traceback instead of rendering a user-friendly Rich error panel.
- **Blast Radius**: Unhandled CLI crashes on engine exceptions.

### Defect 10: `AttributeError` on Non-Dict Component Items in `RichFormatter.render_assembly_summary()`
- **Affected File**: `src/cli/formatter.py` (lines 161–182)
- **Root Cause**: When `state` is a dict, `render_assembly_summary()` iterates over `components.items()`. Line 170 calls `card_dict.get("model_name", "N/A")`. If any component entry is a primitive string or non-dict object, calling `.get()` raises `AttributeError: 'str' object has no attribute 'get'`.
- **Evidence**: `render_assembly_summary({'components': {'frame': 'invalid'}})` crashes with `AttributeError`.
- **Blast Radius**: Summary table rendering crash on non-standard dictionary state.

---

## 3. Worker M1 Refactoring Blueprint & Code Specifications

Worker M1 must execute the exact code refactoring specified below across the 4 target files.

### 3.1 `src/engine/sequential_thinking.py` Refactoring

1. **Add `InvalidStageTransitionError`**:
   Ensure `InvalidStageTransitionError` is defined as a subclass of `InvalidStageError` (or alias).
   ```python
   class InvalidStageTransitionError(InvalidStageError):
       """Raised when an out-of-order stage transition is requested."""
   ```

2. **Add Recursive JSON Serializer Helper**:
   Add helper function `_make_json_serializable(obj)` to handle sets, enums, dates, uuids, dicts, and lists.
   ```python
   def _make_json_serializable(obj: Any) -> Any:
       """Recursively convert non-primitive types (sets, enums, dates) to JSON serializable objects."""
       if isinstance(obj, (set, tuple)):
           return [_make_json_serializable(item) for item in obj]
       if isinstance(obj, dict):
           return {str(k): _make_json_serializable(v) for k, v in obj.items()}
       if isinstance(obj, list):
           return [_make_json_serializable(item) for item in obj]
       if hasattr(obj, "value"):
           return obj.value
       if isinstance(obj, (datetime,)):
           return obj.isoformat()
       if isinstance(obj, uuid.UUID):
           return str(obj)
       return obj
   ```
   In `OptionCard.to_dict()`, apply `_make_json_serializable(self.english_specs)`:
   ```python
   def to_dict(self) -> dict[str, Any]:
       stage_val = self.stage.value if isinstance(self.stage, AssemblyStage) else str(self.stage)
       return {
           "id": self.id,
           "stage": stage_val,
           "model_name": self.model_name,
           "arabic_description": self.arabic_description,
           "english_specs": _make_json_serializable(self.english_specs),
           "price_tier": self.price_tier,
           "optical_compatibility_status": self.optical_compatibility_status,
           "incompatibility_reason": self.incompatibility_reason,
           "recommended": self.recommended,
       }
   ```
   In `AssemblyState.get_summary()`, wrap return payload with `_make_json_serializable(...)`.

3. **Fix Dict Insertion Order in `AssemblyState.add_selection()`**:
   ```python
   def add_selection(self, stage: AssemblyStage | str, option: OptionCard) -> None:
       stg = normalize_stage(stage)
       # Delete key first if already present so insertion order updates to latest position
       if stg in self.selected_components:
           del self.selected_components[stg]
       self.selected_components[stg] = option
       self.updated_at = datetime.now(timezone.utc)
       if len(self.selected_components) == 5:
           self.is_complete = True
   ```

4. **Enforce Sequential Stage Guard in `SequentialThinkingEngine.step()` and `select_option()`**:
   Define sequence order constant:
   ```python
   STAGE_ORDER = [
       AssemblyStage.FRAME,
       AssemblyStage.LIGHT_SOURCE,
       AssemblyStage.OBJECTIVES,
       AssemblyStage.CAMERA_ADAPTER,
       AssemblyStage.SOFTWARE,
   ]
   ```
   In `step()` and `select_option()`, validate that all previous stages in `STAGE_ORDER` exist in `self.state.selected_components`:
   ```python
   def _validate_stage_sequence(self, target_stage: AssemblyStage) -> None:
       target_idx = STAGE_ORDER.index(target_stage)
       for prev_stage in STAGE_ORDER[:target_idx]:
           if prev_stage not in self.state.selected_components:
               raise InvalidStageTransitionError(
                   f"Cannot transition to stage '{target_stage.value}' before completing required stage '{prev_stage.value}'."
               )
   ```
   Call `self._validate_stage_sequence(norm_stage)` in both `step()` and `select_option()`.

---

### 3.2 `src/cli/formatter.py` Refactoring

1. **Import `escape` from `rich.markup`**:
   ```python
   from rich.markup import escape
   ```

2. **Escape Dynamic Variables in Panel and Message Strings**:
   - In `render_stage_progress`:
     `progress_msg = f"[bold yellow]Step {stage_idx}/{total_stages}[/bold yellow] : [bold white]{escape(str(ar_title))}[/bold white] | [dim]{escape(str(en_title))}[/dim]"`
   - In `render_bilingual_option_card`:
     ```python
     escaped_model = escape(str(model_name))
     escaped_ar_desc = escape(str(ar_desc))
     escaped_tier = escape(str(price_tier))
     header = f"[bold cyan]Option #{index}: {escaped_model}[/bold cyan]"
     if recommended:
         header += " [bold green]★ RECOMMENDED / موصى به[/bold green]"

     tier_tag = f"[dim cyan][Tier: {escaped_tier}][/dim cyan]"
     ar_text = f"[bold white]التفاصيل بالعربية:[/bold white]\n[italic green]{escaped_ar_desc}[/italic green]"

     specs_items = []
     if isinstance(specs, dict):
         for k, v in specs.items():
             specs_items.append(f"  • [bold yellow]{escape(str(k))}:[/bold yellow] {escape(str(v))}")
         specs_formatted = "\n".join(specs_items)
     else:
         specs_formatted = f"  • {escape(str(specs))}"

     en_text = f"[bold white]English Technical Specifications:[/bold white]\n{specs_formatted}"

     if compat:
         status_tag = "[bold green]✓ Optical Compatibility Verified / متوافق بصرياً[/bold green]"
     else:
         incompat_msg = escape(str(incompat_reason)) if incompat_reason else 'Optical constraint violation'
         status_tag = f"[bold red]✗ Incompatible: {incompat_msg}[/bold red]"
     ```
   - In `render_error`:
     ```python
     content = f"[bold red]{escape(str(title))}[/bold red]\n{escape(str(message))}"
     ```
   - In `render_info`:
     ```python
     content = f"[bold cyan]{escape(str(title))}[/bold cyan]\n{escape(str(message))}"
     ```

3. **Harden `render_assembly_summary()` against Non-Dict Entries**:
   ```python
   def render_assembly_summary(self, state: AssemblyState | dict) -> Table:
       table = Table(title="[bold green]FINAL OPTICAL MICROSCOUNT ASSEMBLY SUMMARY / ملخص التجميع النهائي[/bold green]", box=ROUNDED, show_lines=True)
       table.add_column("Stage / المرحلة", style="bold yellow", justify="left")
       table.add_column("Model / الموديل", style="bold cyan", justify="left")
       table.add_column("Arabic Description / الوصف بالعربية", style="green", justify="left")
       table.add_column("Technical Specs / المواصفات الفنية", style="white", justify="left")
       table.add_column("Status / الحالة", style="bold green", justify="center")

       if isinstance(state, dict):
           components = state.get("components", {})
           for stage_key, card_data in components.items():
               try:
                   norm_stg = normalize_stage(stage_key)
                   stg_name = f"{norm_stg.display_name_ar}\n({norm_stg.display_name_en})"
               except Exception:
                   stg_name = str(stage_key)

               if isinstance(card_data, dict):
                   model = card_data.get("model_name", "N/A")
                   ar_desc = card_data.get("arabic_description", "N/A")
                   specs = card_data.get("english_specs", {})
                   specs_str = ", ".join(f"{k}:{v}" for k, v in specs.items()) if isinstance(specs, dict) else str(specs)
               else:
                   model = str(card_data)
                   ar_desc = "N/A"
                   specs_str = "N/A"
               table.add_row(escape(stg_name), escape(str(model)), escape(str(ar_desc)), escape(str(specs_str)), "✓ Approved")
       else:
           for stage, card in state.selected_components.items():
               stg_name = f"{stage.display_name_ar}\n({stage.display_name_en})"
               specs_str = ", ".join(f"{k}:{v}" for k, v in card.english_specs.items()) if isinstance(card.english_specs, dict) else str(card.english_specs)
               table.add_row(escape(stg_name), escape(str(card.model_name)), escape(str(card.arabic_description)), escape(str(specs_str)), "✓ Approved")

       self.console.print(table)
       return table
   ```

---

### 3.3 `src/cli/hitl.py` Refactoring

1. **Fix Empty Choice Handling in `prompt_option_selection()`**:
   ```python
   def prompt_option_selection(
       self,
       choices: list[OptionCard | dict],
       user_input_func: Callable[[], str] | None = None
   ) -> OptionCard | dict | None:
       if not choices:
           return None

       if self.non_interactive:
           return choices[0]

       if user_input_func is not None:
           raw = user_input_func()
       else:
           try:
               raw = self._input_func(f"\nSelect option index [1-{len(choices)}]: ")
           except (EOFError, KeyboardInterrupt):
               return choices[0]

       try:
           idx = int(raw.strip()) - 1
           if 0 <= idx < len(choices):
               return choices[idx]
       except ValueError:
           pass

       return choices[0]
   ```

2. **Fix Default Prompt Mapping (`[y/N/edit]`) in `prompt_stage_approval()`**:
   Empty input `""` must map to `HITLDecision.DECLINE`:
   ```python
   def prompt_stage_approval(
       self,
       stage_result: StageResult | dict,
       user_input_func: Callable[[], str] | None = None
   ) -> HITLResponse:
       choices = stage_result.choices if hasattr(stage_result, "choices") else stage_result.get("choices", [])
       first_id = choices[0].id if choices and hasattr(choices[0], "id") else (choices[0].get("id") if choices and isinstance(choices[0], dict) else None)

       if self.non_interactive:
           if not choices:
               return HITLResponse(decision=HITLDecision.DECLINE, selected_option_id=None, raw_input="n")
           return HITLResponse(decision=HITLDecision.ACCEPT, selected_option_id=first_id, raw_input="y")

       if user_input_func is not None:
           raw = user_input_func()
       else:
           try:
               raw = self._input_func("\n[HitL] Approve recommended component selection? [y/N/edit]: ")
           except (EOFError, KeyboardInterrupt):
               return HITLResponse(decision=HITLDecision.DECLINE, raw_input="n")

       val = raw.lower().strip()
       if val in ("y", "yes", "نعم", "1", "true"):
           return HITLResponse(decision=HITLDecision.ACCEPT, selected_option_id=first_id, raw_input=raw)
       elif val in ("edit", "e", "تعديل", "3"):
           return HITLResponse(decision=HITLDecision.EDIT, raw_input=raw)
       elif val in ("details", "d", "تفاصيل", "4"):
           return HITLResponse(decision=HITLDecision.DETAILS, raw_input=raw)
       elif val in ("help", "h", "مساعدة", "5"):
           return HITLResponse(decision=HITLDecision.HELP, raw_input=raw)
       elif val in ("n", "no", "لا", "0", "false", ""):  # Empty string maps to capital 'N' default
           return HITLResponse(decision=HITLDecision.DECLINE, raw_input=raw)
       else:
           return HITLResponse(decision=HITLDecision.DECLINE, raw_input=raw)
   ```

---

### 3.4 `src/cli/main.py` Refactoring

1. **Handle `HITLDecision.DETAILS` and `HITLDecision.HELP` Explicitly**:
   Do not decrement `step_idx` when user requests details or help:
   ```python
   elif response.decision == HITLDecision.DETAILS:
       formatter.render_info("Stage Details", f"Detailed specs for stage {stage.display_name_en}:")
       formatter.render_option_grid(stage_res.choices)
       # Keep step_idx unchanged to re-prompt user for approval on the current stage
   elif response.decision == HITLDecision.HELP:
       help_text = (
           "HitL Interactive Commands:\n"
           "  • y / yes: Accept the recommended option\n"
           "  • edit / e: Select a specific option card from the list\n"
           "  • details / d: Display detailed technical specifications\n"
           "  • help / h: View this help guide\n"
           "  • n / no (or Enter): Decline selection and revert to previous assembly stage"
       )
       formatter.render_info("HitL Help Guide", help_text)
       # Keep step_idx unchanged to re-prompt user for approval on the current stage
   elif response.decision == HITLDecision.DECLINE:
       if step_idx > 0:
           step_idx -= 1
           prev_stage = stages[step_idx]
           if prev_stage.value in current_config:
               del current_config[prev_stage.value]
           engine.state.undo_last_stage()
           formatter.render_info("Step Reverted", f"Reverted to stage: {stages[step_idx].display_name_en}")
       else:
           formatter.render_info("Session Aborted", "User cancelled assembly at initial stage.")
           return 1
   ```

2. **Handle Empty Path String for `--export-json`**:
   Check if `--export-json` argument is empty string `""`:
   ```python
   if parsed_args.export_json is not None:
       export_path = parsed_args.export_json.strip()
       if not export_path:
           formatter.render_error("Export Error", "Export JSON file path cannot be empty.")
           return 1
       summary_data = engine.state.get_summary()
       try:
           with open(export_path, "w", encoding="utf-8") as f:
               json.dump(summary_data, f, indent=2, ensure_ascii=False)
           formatter.render_info("Export Complete", f"Assembly configuration exported to {export_path}")
       except Exception as e:
           formatter.render_error("Export Failed", f"Failed to write JSON export: {e}")
           return 1
   ```

3. **Wrap Stage Execution Loop with Domain Exception Catching**:
   ```python
   while step_idx < len(stages):
       stage = stages[step_idx]
       try:
           stage_res = engine.step(stage=stage, current_config=current_config)

           formatter.render_stage_progress(stage, stage.step_number, 5)
           formatter.render_option_grid(stage_res.choices)

           if is_non_interactive:
               if not stage_res.choices:
                   formatter.render_error("Assembly Error", f"No available choices for stage {stage.value}")
                   return 1
               chosen_card = stage_res.choices[0]
               engine.select_option(stage, chosen_card.id)
               current_config[stage.value] = chosen_card.id
               step_idx += 1
           else:
               response = hitl.prompt_stage_approval(stage_res)
               if response.decision == HITLDecision.ACCEPT:
                   if not stage_res.choices:
                       formatter.render_error("Assembly Error", f"No available choices for stage {stage.value}")
                       return 1
                   chosen_card = stage_res.choices[0]
                   engine.select_option(stage, chosen_card.id)
                   current_config[stage.value] = chosen_card.id
                   step_idx += 1
               elif response.decision == HITLDecision.EDIT:
                   chosen_card = hitl.prompt_option_selection(stage_res.choices)
                   if chosen_card is None:
                       formatter.render_error("Assembly Error", "No option selected.")
                       return 1
                   card_id = chosen_card.id if hasattr(chosen_card, "id") else chosen_card.get("id")
                   engine.select_option(stage, card_id)
                   current_config[stage.value] = card_id
                   step_idx += 1
               elif response.decision == HITLDecision.DETAILS:
                   formatter.render_info("Stage Details", f"Detailed specs for stage {stage.display_name_en}:")
                   formatter.render_option_grid(stage_res.choices)
               elif response.decision == HITLDecision.HELP:
                   help_text = (
                       "HitL Interactive Commands:\n"
                       "  • y / yes: Accept the recommended option\n"
                       "  • edit / e: Select a specific option card from the list\n"
                       "  • details / d: Display detailed technical specifications\n"
                       "  • help / h: View this help guide\n"
                       "  • n / no (or Enter): Decline selection and revert to previous assembly stage"
                   )
                   formatter.render_info("HitL Help Guide", help_text)
               else:  # DECLINE
                   if step_idx > 0:
                       step_idx -= 1
                       prev_stage = stages[step_idx]
                       if prev_stage.value in current_config:
                           del current_config[prev_stage.value]
                       engine.state.undo_last_stage()
                       formatter.render_info("Step Reverted", f"Reverted to stage: {stages[step_idx].display_name_en}")
                   else:
                       formatter.render_info("Session Aborted", "User cancelled assembly at initial stage.")
                       return 1
       except OlympusSpecialistError as e:
           formatter.render_error("Assembly Engine Error", str(e))
           return 1
       except Exception as e:
           formatter.render_error("Unexpected Error", str(e))
           return 1
   ```

---

## 4. Independent Verification Method & Verification Suite

Worker M1 and subsequent reviewers can verify the remediation using the commands below:

1. **Tier 1 Feature Test Suite**:
   ```bash
   .venv/bin/pytest tests/tier1_features/test_fi_r1_cli_and_engine.py -v
   ```
   *Expected Result*: 3 passed in <0.1s.

2. **Tier 5 Adversarial Test Suite**:
   ```bash
   .venv/bin/pytest tests/tier5_adversarial/test_cli_stress_m1.py -v
   ```
   *Expected Result*: All tests pass without exceptions.

3. **Empirical Stress Test Suite**:
   ```bash
   .venv/bin/python scratch/stress_test_m1.py
   ```
   *Expected Result*: All 38 stress test assertions pass (0 failures).

4. **Specific Defect Verification Commands**:
   - **Markup Escaping**:
     `.venv/bin/python -c "from src.cli.formatter import RichFormatter; rf = RichFormatter(); rf.render_error('Export Error', 'Failed file [Errno 2]: [/tmp/foo]')"`
   - **HitL Details Handling**:
     `.venv/bin/python -c "from src.cli.hitl import HITLHandler; h = HITLHandler(input_func=lambda p: 'details'); resp = h.prompt_stage_approval({'choices': []}); print(resp.decision)"`
   - **Empty Choices Handling**:
     `.venv/bin/python -c "from src.cli.hitl import HITLHandler; print(HITLHandler(non_interactive=True).prompt_option_selection([]))"`
   - **JSON Serialization**:
     `.venv/bin/python -c "import json; from src.engine.sequential_thinking import SequentialThinkingEngine, OptionCard, AssemblyStage; e = SequentialThinkingEngine(); e.state.add_selection(AssemblyStage.FRAME, OptionCard(id='1', stage='frame', model_name='M', arabic_description='', english_specs={'tags': {'a', 'b'}})); print(json.dumps(e.state.get_summary()))"`
   - **Empty Export Path**:
     `.venv/bin/python -c "from src.cli.main import run_cli; assert run_cli(['--non-interactive', '--export-json', '']) == 1"`
