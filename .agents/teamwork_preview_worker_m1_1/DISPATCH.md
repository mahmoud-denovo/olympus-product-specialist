## 2026-08-05T08:29:06Z
Worker 1 for Milestone M1 (Interactive CLI & SequentialThinking HitL Engine) in olympus-product-specialist.

Your assigned metadata working directory is: /Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/.agents/teamwork_preview_worker_m1_1
Project directory: /Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist
User request path: /Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/ORIGINAL_REQUEST.md
Project master doc: /Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/PROJECT.md
Architecture analysis path: /Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/.agents/teamwork_preview_explorer_m1_1/analysis.md

Write Ownership: You exclusively own `src/cli/`, `src/engine/`, `src/__init__.py`.

Task:
1. Read ORIGINAL_REQUEST.md, PROJECT.md, and M1 Explorer analysis report at /Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/.agents/teamwork_preview_explorer_m1_1/analysis.md.
2. Implement clean-slate production Python 3.14 modules:
   - `src/__init__.py`
   - `src/engine/__init__.py`
   - `src/engine/sequential_thinking.py`: Implement the 5-stage SequentialThinking state machine (`FRAME` -> `LIGHT_SOURCE` -> `OBJECTIVES` -> `CAMERA_ADAPTER` -> `SOFTWARE`), dataclasses (`AssemblyStage`, `OptionCard`, `StageResult`, `AssemblyState`), catalog options with plain Arabic descriptions + English technical specs, and interface contract `step(stage, current_config)`.
   - `src/cli/__init__.py`
   - `src/cli/formatter.py`: Implement `RichFormatter` rendering rich panels, progress headers, bilingual cards, status badges, and completed assembly summary tables.
   - `src/cli/hitl.py`: Implement `HITLHandler` for interactive Human-in-the-Loop prompts (`[y/N/edit]`) with fallback to non-interactive default choices when `--non-interactive` flag is passed.
   - `src/cli/main.py`: CLI entrypoint with `argparse`, orchestrating the 5-stage HitL loop, interactive & non-interactive execution modes, and `--export-json` option.
3. Test your implementation using the virtual environment at `.venv`:
   - Run `/Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/.venv/bin/python -m src.cli.main --help`
   - Run `/Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/.venv/bin/python -m src.cli.main --non-interactive`
   - Run `/Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/.venv/bin/pytest` if tests exist.
4. Document commands run and verification results in your handoff report at /Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/.agents/teamwork_preview_worker_m1_1/handoff.md.

MANDATORY INTEGRITY WARNING: DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Send a message back when done with the path to your handoff report.
