# Project: olympus-product-specialist

An AI-First, zero-cloud-cost default, interactive product specialist CLI agent for Evident/Olympus microscopy products.

## Architecture

The system is designed as a modular, local-first Python application with clean separation of concerns and zero-cloud default execution:

```
[CLI Interface (rich UI)] ──► [SequentialThinking Engine (5-Stage Assembly)]
         │                                       │
         ▼                                       ▼
[Rule B-01 Guardrail]                 [SQLite Knowledge Graph]
         │                                       │
         ▼                                       ▼
[Evident Web Inspector]               [Local agy Pool (Zero Cloud Cost)]
         │                                       │
         └───────────────────┬───────────────────┘
                             ▼
                 [Controlled Gemini LLM Judge]
```

### Core Components:
1. **CLI & HitL Engine (`src/cli/`, `src/engine/`)**: Terminal UI using `rich` rendering step-by-step progress, bilingual Arabic prose + English technical terminology cards, and pausing for interactive user approval at each assembly step.
2. **Execution Core (`src/core/`)**: Zero-cloud-cost execution engine using local `Antigravity CLI (agy)` runner (`/Users/amirahajeer/.local/bin/agy`).
3. **Controlled LLM Judge (`src/judge/`)**: Opt-in accuracy verification over Google AI Studio (`GEMINI_API_KEY`) with hard daily token rate limits (max 50 req/day) and spending caps ($0.50/day). Graceful fallback to `agy` when unconfigured or capped.
4. **Web Inspector (`src/validator/`)**: Real-time HTTP validator fetching product specs from official Evident/Olympus domains (`evident-scientific.com`, `olympus-lifescience.com`), validating model numbers via category regexes, with SQLite offline caching fallback.
5. **Knowledge Graph (`src/db/`)**: Local SQLite relational database (`data/knowledge_graph.db`) persisting optical compatibility rules (UIS2 standard, RMS/M25/M32 objective adapters, parfocality, sensor vignetting, filter cube generation lockouts).
6. **Legacy Reference Guardrail (`legacy_reference/`, `src/guardrails/`)**: `legacy_reference/MIGRATION_MAP.md` enforcing **Rule B-01** (zero legacy code or decision adopted without explicit prior user presentation and approval).

---

## Feature Inventory

| # | Feature ID | Feature Name & Description | Milestone | Source |
|---|------------|----------------------------|-----------|--------|
| 1 | FI-R1.1 | Terminal CLI execution with `rich` UI and step-by-step progress logging | M1 | ORIGINAL_REQUEST R1 |
| 2 | FI-R1.2 | Native `SequentialThinking` protocol engine for 5-stage microscopy configuration (Frame, Light Source, Objectives, Camera Adapter, Software) | M1 | ORIGINAL_REQUEST R1 |
| 3 | FI-R1.3 | Bilingual card presentation (Plain Arabic prose + English technical terms) with interactive prompt for explicit Human-in-the-Loop approval | M1 | ORIGINAL_REQUEST R1 |
| 4 | FI-R2.1 | Zero-Cloud-Cost default execution engine wrapping local `Antigravity CLI (agy)` pool | M2 | ORIGINAL_REQUEST R2 |
| 5 | FI-R2.2 | Controlled `LLM Judge` module using `GEMINI_API_KEY` (Google AI Studio) with strict daily rate limits and spending caps for accuracy & zero-hallucination checks | M2 | ORIGINAL_REQUEST R2 |
| 6 | FI-R2.3 | Graceful fallback mechanism to local `agy` pool when Gemini API key is absent, rate-limited, or spending-capped | M2 | ORIGINAL_REQUEST R2 |
| 7 | FI-R3.1 | Live Evident/Olympus web inspector with official domain whitelist & regex validation to verify model numbers and prevent hallucinated URLs | M3 | ORIGINAL_REQUEST R3 |
| 8 | FI-R3.2 | Local SQLite Knowledge Graph (`data/knowledge_graph.db`) with normalized schema persisting optical compatibility rules (UIS2 standard, RMS/M25/M32 objective thread adapters, parfocality, vignetting, filter cube generation lockouts) | M3 | ORIGINAL_REQUEST R3 |
| 9 | FI-R3.3 | Offline cache & fallback mechanism for web validator using local SQLite knowledge database when network is unavailable | M3 | ORIGINAL_REQUEST R3 |
| 10 | FI-R4.1 | Establish `legacy_reference/` directory with `legacy_reference/MIGRATION_MAP.md` mapping laws from `olympus-workspace-agent` | M4 | ORIGINAL_REQUEST R4 |
| 11 | FI-R4.2 | Enforce **Rule B-01** guardrail ensuring zero legacy code or decision is adopted without explicit prior user presentation and prompt approval | M4 | ORIGINAL_REQUEST R4 |
| 12 | FI-E2E | Comprehensive E2E opaque-box test suite (Tiers 1-4) & Tier 5 white-box adversarial coverage hardening | M5 | Acceptance Criteria |

---

## Milestones

| # | Milestone Name | Scope | Dependencies | Status |
|---|----------------|-------|--------------|--------|
| M1 | Interactive CLI & SequentialThinking HitL Engine | `src/cli/`, `src/engine/` | None | PLANNED |
| M2 | Zero-Cloud Local Core (`agy`) & Controlled Gemini LLM Judge | `src/core/`, `src/judge/` | M1 | PLANNED |
| M3 | Live Evident Web Inspector & SQLite Knowledge Graph | `src/validator/`, `src/db/` | M2 | PLANNED |
| M4 | Legacy Reference Preservation & Rule B-01 Guardrail | `legacy_reference/`, `src/guardrails/` | M1 | PLANNED |
| M5 | E2E Integration Pass (Tiers 1-4) & Tier 5 Adversarial Hardening | `tests/`, `TEST_READY.md` | M1, M2, M3, M4 | PLANNED |

---

## Interface Contracts

### CLI Engine ↔ SequentialThinking Protocol
- `SequentialThinkingEngine.step(stage: AssemblyStage, current_config: Dict) -> StageResult`
- `StageResult`: `{ stage: str, choices: List[OptionCard], prompt_ar: str, prompt_en: str, requires_hitl: bool }`
- `OptionCard`: `{ id: str, model_name: str, arabic_description: str, english_specs: Dict, price_tier: str, optical_compatibility_status: bool }`

### CLI Engine ↔ Rule B-01 Guardrail
- `RuleB01Guardrail.check_legacy_adoption(concept_id: str, details: Dict) -> UserApprovalRequest`
- `UserApprovalRequest.render_prompt_and_wait(user_input_func) -> bool`

### Core Runner ↔ LLM Judge
- `LocalAgyRunner.run_prompt(prompt: str) -> ExecutionResult`
- `GeminiJudge.evaluate_configuration(config: Dict, criteria: EvaluationCriteria) -> JudgeVerdict`
- `JudgeVerdict`: `{ score: float, zero_hallucination_passed: bool, accuracy_passed: bool, reasoning: str, cost_charged: float, source: Literal['gemini', 'agy_fallback'] }`

### Web Inspector ↔ Knowledge Graph
- `EvidentWebInspector.validate_url(url: str) -> ValidationResult`
- `EvidentWebInspector.verify_model_number(model: str) -> ModelVerificationResult`
- `KnowledgeGraph.check_optical_compatibility(component_a: Component, component_b: Component) -> CompatibilityResult`
- `CompatibilityResult`: `{ compatible: bool, reasons: List[str], required_adapters: List[str], rule_violations: List[str] }`

---

## Code Layout

```
olympus-product-specialist/
├── .agents/                      # Agent metadata (plans, progress, handoffs) — NO CODE
├── legacy_reference/              # Migration maps & reference concepts (Rule B-01)
│   └── MIGRATION_MAP.md
├── data/                         # Local SQLite Knowledge Graph data files
│   └── knowledge_graph.db
├── src/                          # Modern, clean-slate production source code
│   ├── __init__.py
│   ├── cli/                      # Rich UI and step-by-step CLI interface
│   │   ├── __init__.py
│   │   ├── main.py               # Main CLI entrypoint
│   │   ├── formatter.py          # Rich formatting & bilingual optical cards
│   │   └── hitl.py               # Human-in-the-Loop interactive approval handler
│   ├── engine/                   # SequentialThinking protocol engine
│   │   ├── __init__.py
│   │   └── sequential_thinking.py # 5-stage optical assembly engine
│   ├── core/                     # Zero-cloud-cost execution engine
│   │   ├── __init__.py
│   │   └── agy_runner.py         # Antigravity CLI (agy) local wrapper
│   ├── judge/                    # Controlled Gemini API evaluation judge
│   │   ├── __init__.py
│   │   └── gemini_judge.py       # Rate-limited, cost-capped LLM Judge
│   ├── validator/                # Evident/Olympus web inspector & validator
│   │   ├── __init__.py
│   │   └── web_inspector.py      # Domain whitelist & regex validator
│   ├── db/                       # Local SQLite Knowledge Graph
│   │   ├── __init__.py
│   │   ├── schema.py             # DDL & table initialization
│   │   └── knowledge_graph.py    # Optical compatibility queries & rules
│   └── guardrails/               # Rule B-01 legacy guardrail
│       ├── __init__.py
│       └── rule_b01.py           # Legacy adoption confirmation prompt
└── tests/                        # Requirement-driven E2E & unit test suite
    ├── tier1_features/
    ├── tier2_boundaries/
    ├── tier3_pairwise/
    ├── tier4_scenarios/
    └── tier5_adversarial/
```
