## 2026-08-05T08:18:01Z

<USER_REQUEST>
You are the Project Orchestrator for the olympus-product-specialist project.

Working directory: /Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist
Your agent metadata directory: /Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/.agents/orchestrator

User request file: /Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/ORIGINAL_REQUEST.md

Instructions:
1. Read ORIGINAL_REQUEST.md to understand all project requirements (R1-R4) and acceptance criteria.
2. Initialize your metadata directory with plan.md, progress.md, and context.md.
3. Decompose the work into concrete milestones and tasks.
4. Spawn subagents as needed to perform research, implementation, and verification.
5. Continuously update progress.md as work proceeds.
6. Once all requirements and acceptance criteria are fully met and verified, report completion to the Sentinel.
</USER_REQUEST>

## 2026-08-05T08:25:34Z

<CRITICAL_DIRECTIVE>
Note that the code, structure, skills, and patterns in the legacy project (olympus-workspace-agent) contain sub-optimal practices, anti-patterns, and mismatched structures. DO NOT blindly copy or rely on code/architecture from the old project. Treat everything from legacy as a reference concept only, subject to Rule B-01 (strict clean-slate re-architecture with explicit user approval for any adopted concepts). Ensure code in olympus-product-specialist is clean, robust, modern, and production-ready from scratch.
</CRITICAL_DIRECTIVE>

## 2026-08-05T08:36:43Z

<CRITICAL_DIRECTIVE>
CRITICAL NON-BLOCKING CLOUD DEFERRAL POLICY:
1. Full directory permissions granted to local workspace (/Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist).
2. DO NOT STOP OR BLOCK WORKFLOW WHEN WAITING FOR CLOUD PERMISSION.
3. If a component requires paid cloud LLM calls/resources, create a Cloud Plan Request file in `cloud_requests/` outlining the reason and cost estimate.
4. IMMEDIATELY FALL BACK to a local mock/stub or local `agy` pool simulation to CONTINUE implementation and testing without blocking or waiting.
5. Work MUST continue asynchronously. Never halt execution for user cloud approval.
</CRITICAL_DIRECTIVE>

## 2026-08-05T08:39:45Z

<CRITICAL_DIRECTIVE>
MANDATORY MOCK DATA TRANSPARENCY DIRECTIVE:
1. Every mock data structure, simulated output, fallback response, or stubbed cloud API MUST be explicitly tagged with `[MOCK_DATA]` or `[SIMULATED]`.
2. All CLI logs, agent outputs, and system responses generated via a mock or fallback MUST clearly state the mock source (e.g., "[MOCK_DATA] Gemini Cloud Judge simulated locally using local rule heuristic").
3. Maintain a centralized registry in `docs/MOCK_REGISTRY.md` listing every active mock/stub in the project so the user can easily distinguish simulated responses from real live responses.
4. Ensure zero confusion: The user must NEVER be misled into thinking a simulated or mock response is real production data.
</CRITICAL_DIRECTIVE>

## 2026-08-05T08:40:13Z

<CRITICAL_DIRECTIVE>
MANDATORY MOCK MARKER & COLORIZATION DIRECTIVE:
1. Every mock, stub, fallback script, and simulated response across the entire repository (including python code, scripts, CLI output, logging, and DB records) MUST include explicit structural markers.
2. In Terminal/CLI output: Colorize mock tags with distinctive styling (e.g., bold yellow/orange background or `[MOCK_DATA]` prefix) so it immediately catches the human eye.
3. In Code/Scripts: Annotate functions, classes, and return dictionaries with `@mock_marker` decorators or a top-level comment `# [MOCK_IMPLEMENTATION]`.
4. In DB/State: Add a `is_mock: true` boolean column/field to all saved entities in SQLite/JSON state.
5. Absolute requirement: A human looking at ANY script, code block, terminal log, or DB entry must instantly recognize whether it is real or simulated.
</CRITICAL_DIRECTIVE>

## 2026-08-05T08:43:20Z

<CRITICAL_DIRECTIVE>
STRICT DATA ISOLATION & ZERO-POLLUTION DIRECTIVE:
1. NEVER WRITE MOCK, DUMMY, OR SIMULATED DATA INTO THE PRODUCTION KNOWLEDGE GRAPH OR PRODUCTION SQLITE DATABASE.
2. Production Knowledge Graph and Database MUST CONTAIN ONLY VERIFIED, REAL DATA SOURCED FROM OFFICIAL DOCUMENTATION / DIRECT SOURCES.
3. If mock data or testing fixtures are needed during development, they MUST live in an isolated, sandboxed test database/file (e.g., `tests/fixtures/mock_sandbox.db` or `dev_sandbox.sqlite`), NEVER touching `production_knowledge.db` (`data/knowledge_graph.db`).
4. Ensure ZERO DATA POLLUTION: Production databases must remain 100% clean and pristine without needing any manual cleanup later.
</CRITICAL_DIRECTIVE>

## 2026-08-05T08:43:39Z

<CRITICAL_DIRECTIVE>
MINIMIZE MOCKING & PREFER REAL LOCAL EXECUTION DIRECTIVE:
1. MINIMIZE the use of mocks, stubs, and synthetic data to the absolute minimum necessary.
2. PREFER REAL, DETERMINISTIC LOCAL EXECUTION: Use real local scripts, real local SQLite queries, real local Python rule engines, and real local live web scraping wherever possible without cloud cost.
3. Use stubs ONLY as an emergency fallback when an unapproved external cloud service is touched, and never as a default substitute for real local logic.
4. Objective: Build a robust, real, functioning system locally, not a facade of mocks.
</CRITICAL_DIRECTIVE>

## 2026-08-05T09:16:10Z

<USER_REQUEST>
Orchestrator Status Check: Milestone M1 completed and verified.

Please resume execution for:
- Milestone M2: Zero-Cloud-Cost Local agy Core & Controlled Gemini LLM Judge with daily rate limits and spending caps.
- Milestone M3: Live Evident/Olympus Web Validator & Local SQLite Knowledge Graph with scientific verification gateway and source attribution metadata.
- Milestone M4: Legacy Reference Preservation (legacy_reference/MIGRATION_MAP.md & Rule B-01 clean-slate enforcement).

Ensure all critical directives are strictly enforced across all subagents. Update progress.md when complete.
</USER_REQUEST>


## 2026-08-05T08:46:06Z

<CRITICAL_DIRECTIVE>
MANDATORY SOURCE OF TRUTH & SCIENTIFIC VALIDATION DIRECTIVE:
1. Official Evident/Olympus website (with all tabs, spec sheets, and manuals) is the SINGLE CANONICAL SOURCE OF TRUTH for product data, optical specs, and component compatibility.
2. STRICT VERIFICATION GATEWAY: BEFORE ANY information, spec, link, or rule is entered into the Knowledge Graph, Knowledge Base, RAG index, or Vector Search database, it MUST undergo mandatory scientific/technical validation.
3. EVERY stored entity, chunk, or optical node MUST store explicit source attribution metadata (URL, page tab, specification reference, timestamp) pointing back to the official Source of Truth.
4. ZERO UNVALIDATED ENTRY: No unverified fact or hallucinated data is permitted into the RAG/KG pipelines under any circumstance.
5. Clear Separation of Concerns: Technical/Scientific Product Truth is strictly validated against the official site; Sales & Negotiation Skills operates as a separate domain layer.
</CRITICAL_DIRECTIVE>

## 2026-08-05T12:16:18Z

<USER_REQUEST>
You are Project Orchestrator Successor (Gen 2) for the olympus-product-specialist project.

Working directory: /Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist
Metadata directory: /Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/.agents/orchestrator
Parent Conversation ID: 9d50f7ef-522c-4e67-b66b-1fcea2f93780

Instructions:
1. Resume work at /Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/.agents/orchestrator.
2. Read handoff.md, BRIEFING.md, ORIGINAL_REQUEST.md, DISPATCH.md, PROJECT.md, TEST_INFRA.md, and progress.md for full context.
3. Your parent is 9d50f7ef-522c-4e67-b66b-1fcea2f93780 — use this conversation ID for all status updates and escalation (send_message).
4. Start your own 10-minute heartbeat cron task via `schedule`.
5. Execute Milestones M2, M3, M4, and M5 to complete the project:
   - Milestone M2: Zero-Cloud-Cost Local agy Core (`src/core/agy_runner.py`) & Controlled Gemini LLM Judge (`src/judge/gemini_judge.py`) with rate limits and spending caps.
   - Milestone M3: Live Evident/Olympus Web Validator (`src/validator/web_inspector.py`) & Local SQLite Knowledge Graph (`src/db/knowledge_graph.py`) with scientific validation gateway and source attribution metadata.
   - Milestone M4: Legacy Reference Preservation (`legacy_reference/MIGRATION_MAP.md` & `src/guardrails/rule_b01.py` clean-slate Rule B-01 enforcement).
   - Milestone M5: Final E2E Integration Pass (100% pass rate across Tiers 1-4) & Tier 5 White-Box Adversarial Coverage Hardening.
6. Strictly enforce all 7 Critical Directives across all subagents.
7. Continuously update progress.md and report completion to the parent/Sentinel when all acceptance criteria are fully met.
</USER_REQUEST>








