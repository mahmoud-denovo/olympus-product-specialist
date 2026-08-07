## 2026-08-05T08:27:39Z
You are the E2E Test Suite Creator for the olympus-product-specialist project.

Your assigned metadata working directory is: /Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/.agents/teamwork_preview_test_writer_e2e
Project directory: /Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist
User request path: /Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/ORIGINAL_REQUEST.md
Project plan path: /Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/PROJECT.md

Task:
1. Read ORIGINAL_REQUEST.md and PROJECT.md.
2. Initialize virtual environment at project root `.venv` using:
   /Users/amirahajeer/.local/bin/uv venv /Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/.venv --python /Users/amirahajeer/.local/bin/python3.14
   and install `pytest`, `rich`, `httpx`, `beautifulsoup4` via:
   /Users/amirahajeer/.local/bin/uv pip install --python /Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/.venv/bin/python pytest rich httpx beautifulsoup4
3. Create requirement-driven opaque-box tests in `tests/`:
   - `tests/conftest.py`
   - `tests/tier1_features/` (Test cases for FI-R1.1 to FI-R4.2)
   - `tests/tier2_boundaries/` (Boundary cases, invalid inputs, edge cases)
   - `tests/tier3_pairwise/` (Cross-feature interactions)
   - `tests/tier4_scenarios/` (Real-world microscopy assembly workloads)
4. Create `TEST_INFRA.md` at project root detailing test runner invocation (`.venv/bin/pytest`), pass/fail semantics, and feature checklist.
5. Create `TEST_READY.md` at project root signaling test suite availability.
6. Execute the test runner using `.venv/bin/pytest` and document test execution results.
7. Write handoff report at /Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/.agents/teamwork_preview_test_writer_e2e/handoff.md.

Mandatory Integrity Warning: DO NOT CHEAT. All tests must be genuine and execute against actual implementation modules.
Send a message back when done with the path to your handoff report.
