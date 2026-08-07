# Execution Plan — olympus-product-specialist

## Phase 0: Survey & Assessment
- Step 0.1: Initialize orchestrator metadata (DISPATCH.md, BRIEFING.md, plan.md, progress.md, context.md).
- Step 0.2: Start heartbeat cron timer.
- Step 0.3: Dispatch 3 parallel Explorers (`teamwork_preview_explorer`) to explore scope, dependencies, environment, existing legacy workspace references (if any), and specs.
- Step 0.4: Synthesize explorer reports and generate `PROJECT.md` with Feature Inventory, Milestones, and Interface Contracts.

## Phase 1: Decomposition & Track Setup
- Step 1.1: Setup E2E Testing Track (spawn sub-orchestrator or dispatch test writers for opaque-box test runner & test cases Tiers 1-4).
- Step 1.2: Define implementation milestone boundaries (e.g. M1: CLI & SequentialThinking HitL interface, M2: Zero-Cloud agy Core & Controlled Gemini LLM Judge, M3: Web Inspector & SQLite Knowledge Graph, M4: Legacy Reference Preservation Rule B-01).

## Phase 2: Milestone Execution Loop
- Step 2.1: Execute Implementation Milestones sequentially/parallelly via iteration loop: Explorer -> Worker -> Reviewer -> Challenger -> Forensic Auditor -> Gate Check.
- Step 2.2: Ensure zero tolerance on Forensic Audit verdicts (Binary Veto).

## Phase 3: Final E2E Integration & Hardening
- Step 3.1: Verify 100% pass rate on E2E test suite (Tiers 1-4).
- Step 3.2: Execute Tier 5 Adversarial Coverage Hardening (Challenger-driven white-box testing).

## Phase 4: Final Reporting & Sentinel Handoff
- Step 4.1: Collect final audit and verification reports.
- Step 4.2: Present completion report to Sentinel / Parent.
