# Teamwork Capabilities & Assets Index — Olympus Product Specialist

> **Project:** `olympus-product-specialist`  
> **Updated:** 2026-08-06  

---

## 1. Environment & Models

| Asset | Type | Configuration / Environment Variable | Notes |
|---|---|---|---|
| **Reasoning Model** | LLM Model | `MODEL_REASONING` (`gemini-3.6-flash`) | Deep optical configuration & system reasoning |
| **Extraction Model** | LLM Model | `MODEL_EXTRACTION` (`gemini-3.1-flash-lite`) | High-speed web spec extraction & slot filling |
| **Embedding Model** | Vector Model | `MODEL_EMBEDDING` (`text-embedding-004`) | Semantic vector index embedding generation |
| **Agent Framework** | Python SDK | Google Antigravity SDK & ADK | Multi-agent orchestration & tool leases |

---

## 2. Tools & MCP Servers

| Asset | Type | Location / Server | Purpose |
|---|---|---|---|
| **Evident Web Scraper** | Tool | `src/olympus_specialist/tools/evident_scraper.py` | Robots.txt compliant live spec scraper |
| **Canonical Product Catalog** | Database | PostgreSQL / SQLite (`pgvector`) | $0-cost deterministic hardware schemas |
| **L1 Compatibility Engine** | Python Module | `src/olympus_specialist/domain/compatibility/` | Optical stands, objectives, & light source rules |
| **Self-Healing Engine** | Subsystem | `src/olympus_specialist/self_healing/` | Autonomous exception interception & auto-repair |
| **Centralized Prompt Registry**| Registry | `src/olympus_specialist/prompts/` | Versioned system prompts & sub-prompts |
| **GCP Cost Circuit Breaker** | Guardrail | `src/olympus_specialist/guardrails/cost_gate.py` | Hard $5.00/day limit on Model Garden calls |

---

## 3. Skills & SOPs

| Skill / SOP | Location | Trigger / Usage |
|---|---|---|
| **Managing Python Dependencies** | `SKILL.md` | `.venv` explicit execution & `uv` package management |
| **Antigravity Guide** | `SKILL.md` | Antigravity CLI/SDK orchestration standards |
| **Agent SOP Engine** | `src/olympus_specialist/sops/` | Agent standard operating procedures & audio hooks |
