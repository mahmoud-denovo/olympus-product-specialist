# Master Swarm Plan — Olympus Product Specialist

> **Project:** `olympus-product-specialist`  
> **Status:** ACTIVE — Sprint Phase 1  

---

## Phase Breakdown

### Phase 1: Core Foundation & Centralized Infrastructure
- [x] **Project Directory Structure:** Established `olympus-product-specialist/` root layout.
- [x] **Documentation & Governance:** Created `.agents/` protocol, original request ledger, and asset index.
- [/] **Centralized Prompts & SOPs:** Define prompt templates in `src/olympus_specialist/prompts/` and SOP engine in `src/olympus_specialist/sops/`.
- [/] **Step-by-Step Logging & Exception Hierarchy:** Implement JSONL structured logger in `src/olympus_specialist/logging/`.

### Phase 2: L1 Deterministic Core & Canonical Catalog
- [ ] **Database Schema:** Initialize PostgreSQL/SQLite relational schema for Stands, Objectives, Illumination, and Accessories.
- [ ] **Optical Compatibility Rules:** Program deterministic rules for lens-stand matching ($0 LLM cost).
- [ ] **Authorized Evident Ingestion:** Ingest and normalize official Evident catalog files with versioned source anchors.

### Phase 3: Self-Healing Agent Core & Web RAG
- [ ] **Olympus Specialist Agent:** Instantiate single orchestrator agent using Google Antigravity SDK.
- [ ] **Self-Healing Loop:** Wire autonomous error interception and remediation sub-prompt injection.
- [ ] **Evident Web Scraper Tool:** Build robots.txt compliant scraper for live spec lookups.
- [ ] **GCP Cost Circuit Breaker:** Wire $5.00/day hard budget limit on Model Garden calls.

### Phase 4: Web Application Frontend (Ribosome UI)
- [ ] **React + Vite Setup:** Scaffold web frontend in `apps/web/`.
- [ ] **Ribosome 3-Site UI:** Build A-Site (Telemetry), P-Site (Command Chat), and E-Site (Timeline Logs) with Frosted Vellum glassmorphism.
- [ ] **SSE Streaming:** Connect WebSockets / Server-Sent Events from FastAPI to React UI.

### Phase 5: Evals, QA & Goal Verification
- [ ] **Micro-Test Suite:** Run contamination, provenance, and slot-filling tests.
- [ ] **Human-in-the-Loop Simulation:** Complete 5-step interactive trial verifying minimum sufficient clarification.
