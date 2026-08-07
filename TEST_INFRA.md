# Test Infrastructure Documentation — olympus-product-specialist

This document specifies the end-to-end (E2E) opaque-box test runner setup, execution procedures, pass/fail semantics, and requirement traceability checklist for the **`olympus-product-specialist`** agent.

---

## 1. Test Environment Setup

The virtual environment `.venv` is isolated at the project root using `uv` with Python 3.14:

```bash
# Virtual environment creation
/Users/amirahajeer/.local/bin/uv venv /Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/.venv --python /Users/amirahajeer/.local/bin/python3.14

# Install required test runner dependencies
/Users/amirahajeer/.local/bin/uv pip install --python /Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/.venv/bin/python pytest rich httpx beautifulsoup4
```

---

## 2. Test Runner Invocation

Execute the test suite using `.venv/bin/pytest` from the project root directory:

```bash
# Run complete test suite (Tiers 1-4) with verbose output
.venv/bin/pytest -v

# Run specific test tier
.venv/bin/pytest tests/tier1_features/ -v
.venv/bin/pytest tests/tier2_boundaries/ -v
.venv/bin/pytest tests/tier3_pairwise/ -v
.venv/bin/pytest tests/tier4_scenarios/ -v

# Run with summary report
.venv/bin/pytest --tb=short -rA
```

---

## 3. Pass / Fail Semantics

- **PASS (`.`)**: All feature requirements, boundary contracts, optical compatibility rules, and assembly workflows execute as specified in `PROJECT.md` without unexpected errors or rule violations.
- **FAIL (`F`) / ImportError**: If an implementation module is missing or does not satisfy interface signatures defined in `PROJECT.md` § Interface Contracts, pytest reports an explicit failure specifying the missing interface or contract violation.
- **SKIPPED (`s`)**: Only used if explicit external hardware dependencies are unavailable.

---

## 4. Feature Coverage Checklist

| Feature ID | Feature Name & Description | Test File Location | Target Module | Status |
|------------|----------------------------|--------------------|---------------|--------|
| **FI-R1.1** | Rich Terminal CLI & step-by-step progress logging | `tests/tier1_features/test_fi_r1_cli_and_engine.py` | `src.cli.formatter`, `src.cli.main` | READY |
| **FI-R1.2** | 5-Stage `SequentialThinking` protocol engine (Frame, Light Source, Objectives, Camera Adapter, Software) | `tests/tier1_features/test_fi_r1_cli_and_engine.py` | `src.engine.sequential_thinking` | READY |
| **FI-R1.3** | Bilingual card presentation (Arabic prose + English technical terms) & HitL prompt | `tests/tier1_features/test_fi_r1_cli_and_engine.py` | `src.cli.formatter`, `src.cli.hitl` | READY |
| **FI-R2.1** | Zero-Cloud-Cost local `Antigravity CLI (agy)` execution core | `tests/tier1_features/test_fi_r2_zero_cloud_and_judge.py` | `src.core.agy_runner` | READY |
| **FI-R2.2** | Controlled `LLM Judge` module using `GEMINI_API_KEY` with rate limits & spending caps | `tests/tier1_features/test_fi_r2_zero_cloud_and_judge.py` | `src.judge.gemini_judge` | READY |
| **FI-R2.3** | Graceful fallback mechanism to local `agy` pool when Gemini key missing/capped | `tests/tier1_features/test_fi_r2_zero_cloud_and_judge.py` | `src.judge.gemini_judge`, `src.core.agy_runner` | READY |
| **FI-R3.1** | Live Evident/Olympus web inspector with domain whitelist & regex model validation | `tests/tier1_features/test_fi_r3_web_inspector_and_db.py` | `src.validator.web_inspector` | READY |
| **FI-R3.2** | Local SQLite Knowledge Graph (`data/knowledge_graph.db`) with optical compatibility rules | `tests/tier1_features/test_fi_r3_web_inspector_and_db.py` | `src.db.knowledge_graph`, `src.db.schema` | READY |
| **FI-R3.3** | Offline cache & fallback mechanism for web validator using SQLite DB | `tests/tier1_features/test_fi_r3_web_inspector_and_db.py` | `src.validator.web_inspector` | READY |
| **FI-R4.1** | `legacy_reference/MIGRATION_MAP.md` initialization & preservation | `tests/tier1_features/test_fi_r4_legacy_and_rule_b01.py` | `legacy_reference/MIGRATION_MAP.md` | READY |
| **FI-R4.2** | **Rule B-01** guardrail prompt enforcing clean-slate approval for legacy rules | `tests/tier1_features/test_fi_r4_legacy_and_rule_b01.py` | `src.guardrails.rule_b01` | READY |
| **FI-BND** | Boundary Cases: Malformed URLs, SQL injection, Rate limit overload, Optical thread mismatch, Rule B-01 input edge cases | `tests/tier2_boundaries/test_boundaries_and_edge_cases.py` | Cross-module boundaries | READY |
| **FI-PWR** | Pairwise Interactions: Engine ↔ Inspector ↔ KG ↔ HitL, Judge fallback ↔ CLI, Offline Cache fallback, Rule B-01 prompt pre-execution | `tests/tier3_pairwise/test_pairwise_interactions.py` | Cross-module integration | READY |
| **FI-SCN** | End-to-End Microscopy Assembly Workloads: Complete 5-stage fluorescence assembly & Incompatible thread adapter resolution | `tests/tier4_scenarios/test_microscopy_assembly_scenarios.py` | End-to-end workflows | READY |

---

## 5. Test Suite Architecture

```
tests/
├── conftest.py                   # Global fixtures, DB setup, mock environments
├── tier1_features/               # Requirement-driven feature unit & interface tests
│   ├── test_fi_r1_cli_and_engine.py
│   ├── test_fi_r2_zero_cloud_and_judge.py
│   ├── test_fi_r3_web_inspector_and_db.py
│   └── test_fi_r4_legacy_and_rule_b01.py
├── tier2_boundaries/             # Edge cases, resource limits, invalid inputs
│   └── test_boundaries_and_edge_cases.py
├── tier3_pairwise/               # Cross-feature interaction tests
│   └── test_pairwise_interactions.py
└── tier4_scenarios/              # Real-world 5-stage microscopy assembly workloads
    └── test_microscopy_assembly_scenarios.py
```
