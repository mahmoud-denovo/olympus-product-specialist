# Original User Request

## Initial Request — 2026-08-05T08:17:12Z

<USER_REQUEST>
# Teamwork Project Prompt — olympus-product-specialist

Build the **`olympus-product-specialist`** agent — an AI-First, zero-cloud-cost default, interactive product specialist CLI agent for Evident/Olympus microscopy products.

Working directory: `/Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist`
Integrity mode: `development`

## Requirements

### R1. Autonomous & Interactive HitL CLI Interface
Provide a rich, step-by-step interactive CLI interface tailored for non-technical sales and logistics staff. The agent must use the native `SequentialThinking` protocol to break down complex microscopy configurations (Frame, Light Source, Objectives, Camera Adapters, Software) into discrete steps, pausing to present comparative choices in plain Arabic prose + English technical terms and waiting for explicit user approval before proceeding.

### R2. Zero-Cloud-Cost Local Core & Controlled Gemini API Evaluation Judge
By default, execution must operate on the local `Antigravity CLI (agy)` pool with zero cloud token cost. Integrate a controlled `LLM Judge` using `GEMINI_API_KEY` (Google AI Studio) with strict daily rate limits and spending caps for deep accuracy verification, zero-hallucination checks, and partner-ready evaluation.

### R3. Live Evident/Olympus Web Validation & Local Knowledge Graph
Incorporate a live web inspector that fetches real-time specs directly from the official Evident/Olympus website to validate model numbers and prevent hallucinated URLs. Persist optical compatibility rules into a local SQLite Knowledge Graph.

### R4. Legacy Reference Preservation (Rule B-01)
Establish a `legacy_reference/` directory containing a migration map of laws from `olympus-workspace-agent`. Enforce **Rule B-01**: zero code or decision from the legacy workspace is adopted without explicit prior user presentation and approval.

## Acceptance Criteria

### Core Functionality & UX
- [ ] Terminal CLI executes with `rich` UI and step-by-step logging.
- [ ] Agent pauses at optical assembly steps for user confirmation (Human-in-the-Loop).
- [ ] `legacy_reference/MIGRATION_MAP.md` is initialized with Rule B-01 explicitly documented.

### Governance & Verification
- [ ] Zero-cloud-cost fallback verified with local `agy` pool by default.
- [ ] Controlled LLM Judge module created with rate limiting over `GEMINI_API_KEY`.
- [ ] Live web validator correctly verifies product URLs against official domain.

</USER_REQUEST>

## Follow-up — 2026-08-05T08:25:27Z

Note that the code, structure, skills, and patterns in the legacy project (olympus-workspace-agent) contain sub-optimal practices, anti-patterns, and mismatched structures. DO NOT blindly copy or rely on code/architecture from the old project. Treat everything from legacy as a reference concept only, subject to Rule B-01 (strict clean-slate re-architecture with explicit user approval for any adopted concepts). Ensure code in olympus-product-specialist is clean, robust, modern, and production-ready from scratch.

## Follow-up — 2026-08-05T08:36:35Z

CRITICAL NON-BLOCKING CLOUD DEFERRAL POLICY:
1. Full directory permissions granted to local workspace (/Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist).
2. DO NOT STOP OR BLOCK WORKFLOW WHEN WAITING FOR CLOUD PERMISSION.
3. If a component requires paid cloud LLM calls/resources, create a Cloud Plan Request file in `cloud_requests/` outlining the reason and cost estimate.
4. IMMEDIATELY FALL BACK to a local mock/stub or local `agy` pool simulation to CONTINUE implementation and testing without blocking or waiting.
5. Work MUST continue asynchronously. Never halt execution for user cloud approval.

## Follow-up — 2026-08-05T08:39:40Z

MANDATORY MOCK DATA TRANSPARENCY DIRECTIVE:
1. Every mock data structure, simulated output, fallback response, or stubbed cloud API MUST be explicitly tagged with `[MOCK_DATA]` or `[SIMULATED]`.
2. All CLI logs, agent outputs, and system responses generated via a mock or fallback MUST clearly state the mock source (e.g., "[MOCK_DATA] Gemini Cloud Judge simulated locally using local rule heuristic").
3. Maintain a centralized registry in `docs/MOCK_REGISTRY.md` listing every active mock/stub in the project so the user can easily distinguish simulated responses from real live responses.
4. Ensure zero confusion: The user must NEVER be misled into thinking a simulated or mock response is real production data.

## Follow-up — 2026-08-05T08:40:09Z

MANDATORY MOCK MARKER & COLORIZATION DIRECTIVE:
1. Every mock, stub, fallback script, and simulated response across the entire repository (including python code, scripts, CLI output, logging, and DB records) MUST include explicit structural markers.
2. In Terminal/CLI output: Colorize mock tags with distinctive styling (e.g., bold yellow/orange background or `[MOCK_DATA]` prefix) so it immediately catches the human eye.
3. In Code/Scripts: Annotate functions, classes, and return dictionaries with `@mock_marker` decorators or a top-level comment `# [MOCK_IMPLEMENTATION]`.
4. In DB/State: Add a `is_mock: true` boolean column/field to all saved entities in SQLite/JSON state.
5. Absolute requirement: A human looking at ANY script, code block, terminal log, or DB entry must instantly recognize whether it is real or simulated.

## Follow-up — 2026-08-05T08:43:15Z

STRICT DATA ISOLATION & ZERO-POLLUTION DIRECTIVE:
1. NEVER WRITE MOCK, DUMMY, OR SIMULATED DATA INTO THE PRODUCTION KNOWLEDGE GRAPH OR PRODUCTION SQLITE DATABASE.
2. Production Knowledge Graph and Database MUST CONTAIN ONLY VERIFIED, REAL DATA SOURCED FROM OFFICIAL DOCUMENTATION / DIRECT SOURCES.
3. If mock data or testing fixtures are needed during development, they MUST live in an isolated, sandboxed test database/file (e.g., `tests/fixtures/mock_sandbox.db` or `dev_sandbox.sqlite`), NEVER touching `production_knowledge.db`.
4. Ensure ZERO DATA POLLUTION: Production databases must remain 100% clean and pristine without needing any manual cleanup later.

## Follow-up — 2026-08-05T08:43:34Z

MINIMIZE MOCKING & PREFER REAL LOCAL EXECUTION DIRECTIVE:
1. MINIMIZE the use of mocks, stubs, and synthetic data to the absolute minimum necessary.
2. PREFER REAL, DETERMINISTIC LOCAL EXECUTION: Use real local scripts, real local SQLite queries, real local Python rule engines, and real local live web scraping wherever possible without cloud cost.
3. Use stubs ONLY as an emergency fallback when an unapproved external cloud service is touched, and never as a default substitute for real local logic.
4. Objective: Build a robust, real, functioning system locally, not a facade of mocks.

## Follow-up — 2026-08-05T08:46:01Z

MANDATORY SOURCE OF TRUTH & SCIENTIFIC VALIDATION DIRECTIVE:
1. Official Evident/Olympus website (with all tabs, spec sheets, and manuals) is the SINGLE CANONICAL SOURCE OF TRUTH for product data, optical specs, and component compatibility.
2. STRICT VERIFICATION GATEWAY: BEFORE ANY information, spec, link, or rule is entered into the Knowledge Graph, Knowledge Base, RAG index, or Vector Search database, it MUST undergo mandatory scientific/technical validation.
3. EVERY stored entity, chunk, or optical node MUST store explicit source attribution metadata (URL, page tab, specification reference, timestamp) pointing back to the official Source of Truth.
4. ZERO UNVALIDATED ENTRY: No unverified fact or hallucinated data is permitted into the RAG/KG pipelines under any circumstance.
5. Clear Separation of Concerns: Technical/Scientific Product Truth is strictly validated against the official site; Sales & Negotiation Skills operates as a separate domain layer.







