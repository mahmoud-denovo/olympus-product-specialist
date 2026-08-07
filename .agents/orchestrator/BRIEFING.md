# BRIEFING — 2026-08-05T12:16:18Z

## Mission
Orchestrate the development and verification of olympus-product-specialist agent — an AI-First, zero-cloud-cost default, interactive product specialist CLI agent for Evident/Olympus microscopy products. Completing Milestones M2, M3, M4, and M5.

## 🔒 My Identity
- Archetype: self (Project Orchestrator Successor Gen 2)
- Roles: orchestrator, user_liaison, human_reporter, successor
- Working directory: /Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/.agents/orchestrator
- Original parent: parent
- Original parent conversation ID: 9d50f7ef-522c-4e67-b66b-1fcea2f93780

## 🔒 My Workflow
- **Pattern**: Project Pattern
- **Scope document**: /Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/PROJECT.md
1. **Decompose**: Survey codebase/requirements via Explorers -> create PROJECT.md -> decompose into parallel/sequential milestones and dual testing track.
2. **Dispatch & Execute**:
   - **Delegate (sub-orchestrator)**: Spawn sub-orchestrator per milestone.
   - **Iteration loop per milestone**: Explorer -> Worker -> Reviewer -> Challenger -> Forensic Auditor -> Gate Check.
3. **On failure** (in order): Retry -> Replace -> Skip -> Redistribute -> Redesign -> Escalate.
4. **Succession**: Self-succeed when spawn count >= 20 and subagents complete.
- **Work items**:
  1. Milestone M1: Interactive CLI & SequentialThinking HitL Engine [done]
  2. Milestone M2: Zero-Cloud-Cost Local agy Core & Controlled Gemini LLM Judge [in-progress]
  3. Milestone M3: Live Evident Web Inspector & SQLite Knowledge Graph [pending]
  4. Milestone M4: Legacy Reference Preservation & Rule B-01 Guardrail [pending]
  5. Milestone M5: Final E2E Integration Pass & Tier 5 Adversarial Hardening [pending]
- **Current phase**: 2 (Execution of M2, M3, M4, M5)
- **Current focus**: Executing Milestone M2, M3, M4, and M5

## 🔒 Key Constraints
- NEVER write, modify, or create source code files directly.
- NEVER run build/test commands yourself — require workers to do so.
- NEVER investigate or explore the problem at the code level — dispatch Explorers for technical investigation.
- Binary veto on Forensic Audit failure — zero tolerance for hardcoded tests, facade implementations, or cheating.
- Zero code or decision adopted from legacy workspace without explicit prior user presentation and approval (Rule B-01).
- STRICT CLEAN-SLATE RE-ARCHITECTURE: Legacy project (`olympus-workspace-agent`) contains sub-optimal practices, anti-patterns, and mismatched structures. DO NOT blindly copy or rely on code/architecture from legacy. Treat legacy as reference concept ONLY under Rule B-01. Build clean, robust, modern, production-ready code from scratch.
- NON-BLOCKING CLOUD DEFERRAL POLICY: Never stop or block workflow waiting for cloud permission. If cloud LLM calls are needed, write `cloud_requests/` request file, and immediately fall back to local `agy` pool or stubs to continue asynchronously.
- MANDATORY MOCK DATA TRANSPARENCY DIRECTIVE: Every mock/simulated response must be tagged with `[MOCK_DATA]`. Maintain `docs/MOCK_REGISTRY.md` listing active stubs/mocks. Never mislead the user.
- MANDATORY MOCK MARKER & COLORIZATION DIRECTIVE: All mocks/stubs/fallbacks across terminal CLI outputs (bold yellow/orange Rich badge), code decorators (`# [MOCK_IMPLEMENTATION]`), and DB/state schema (`is_mock: boolean`) MUST include explicit, eye-catching structural markers.
- STRICT DATA ISOLATION & ZERO-POLLUTION DIRECTIVE: Never write mock/simulated data into production SQLite Knowledge Graph (`data/knowledge_graph.db`). Test/mock data MUST be isolated in `tests/fixtures/mock_sandbox.db`.
- MINIMIZE MOCKING & PREFER REAL LOCAL EXECUTION DIRECTIVE: Minimize mocks/stubs. Prefer real local scripts, real SQLite queries, real local Python rule engines, and real live web scraping without cloud cost. Stubs are emergency fallbacks ONLY.
- MANDATORY SOURCE OF TRUTH & SCIENTIFIC VALIDATION DIRECTIVE: Official Evident/Olympus site is the SINGLE CANONICAL SOURCE OF TRUTH. Mandatory scientific validation gateway before entering any spec into Knowledge Graph/Vector DB. Every entity MUST store explicit source attribution metadata (URL, page tab, spec ref, timestamp). Zero unvalidated entry permitted.

## Current Parent
- Conversation ID: 9d50f7ef-522c-4e67-b66b-1fcea2f93780
- Updated: 2026-08-05T12:16:18Z

## Key Decisions Made
- Initialized Gen 2 Orchestrator Successor metadata.
- Heartbeat cron active (task-21).
- Proceeding to dispatch execution for Milestones M2, M3, M4, M5.

## Team Roster
| Agent | Type | Work Item | Status | Conv ID |
|-------|------|-----------|--------|---------|
| m2_explorer_1 | teamwork_preview_explorer | Local Core & LLM Judge Architecture | in-progress | 63f31231-7d50-4490-9d3c-4092ca1a1e3e |
| m2_explorer_2 | teamwork_preview_explorer | Edge Cases & Rate Limiter Exploration | in-progress | 3d832fa4-025b-4f43-89c1-a809b2485ade |
| m2_explorer_3 | teamwork_preview_explorer | Test Contract Exploration | in-progress | a2f5e851-e1cb-4a36-a842-8c43f385ee56 |

## Succession Status
- Succession required: no
- Spawn count: 3 / 20
- Pending subagents: 63f31231-7d50-4490-9d3c-4092ca1a1e3e, 3d832fa4-025b-4f43-89c1-a809b2485ade, a2f5e851-e1cb-4a36-a842-8c43f385ee56
- Predecessor: Gen 1
- Successor: not yet spawned


## Active Timers
- Heartbeat cron: task-21 (running every 10 min)
- Safety timer: none

## Artifact Index
- ORIGINAL_REQUEST.md — Verbatim user request and requirements R1-R4
- PROJECT.md — Project master document
- TEST_INFRA.md — E2E Test Suite Specification
- TEST_READY.md — E2E Test Readiness Signal
- docs/MOCK_REGISTRY.md — Centralized Mock Component Registry
- handoff.md — Gen 1 Handoff report
