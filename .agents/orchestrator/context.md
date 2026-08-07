# Context — olympus-product-specialist

## Project Overview
`olympus-product-specialist` is an AI-First, zero-cloud-cost default, interactive product specialist CLI agent for Evident/Olympus microscopy products.

## Core Requirements & Acceptance Criteria
1. **R1. Autonomous & Interactive HitL CLI Interface**:
   - Rich, step-by-step interactive CLI interface for non-technical sales/logistics staff.
   - Native `SequentialThinking` protocol breaking complex microscopy configs (Frame, Light Source, Objectives, Camera Adapters, Software) into discrete steps.
   - Comparative choices in plain Arabic prose + English technical terms.
   - Pause for explicit user approval (HitL) before proceeding.
2. **R2. Zero-Cloud-Cost Local Core & Controlled Gemini API Evaluation Judge**:
   - Default execution on local `Antigravity CLI (agy)` pool with zero cloud token cost.
   - Controlled `LLM Judge` using `GEMINI_API_KEY` (Google AI Studio) with strict daily rate limits and spending caps for deep accuracy verification, zero-hallucination checks, and partner-ready evaluation.
3. **R3. Live Evident/Olympus Web Validation & Local Knowledge Graph**:
   - Live web inspector fetching real-time specs directly from official Evident/Olympus website to validate model numbers and prevent hallucinated URLs.
   - Local SQLite Knowledge Graph persisting optical compatibility rules.
4. **R4. Legacy Reference Preservation (Rule B-01)**:
   - Establish `legacy_reference/` directory containing a migration map of laws from `olympus-workspace-agent`.
   - Enforce Rule B-01: Zero code or decision from the legacy workspace is adopted without explicit prior user presentation and approval.

## Environment & Directories
- Working Directory: `/Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist`
- Metadata Directory: `/Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/.agents/orchestrator`
