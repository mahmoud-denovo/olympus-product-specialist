# Canonical Inter-Agent Handoff Document

- **Project Root**: `/Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/`
- **Updated At**: 2026-08-06T22:53:10Z

---

## 1. Goal & Directives Summary
Building the complete end-to-end **Olympus Product Specialist Web Application** (React/Vite Web UI + FastAPI/SSE Backend) operating with Google ADK (`agents-cli`), 4-Stage EAER Workflow Engine, $5.00/day GCP Cost Circuit Breaker, Canonical Product Catalog, Model Context Protocol (MCP) Server, Google ADK Evaluation Reporting, isolated Docker Containerization, and Production GitHub Actions CI/CD Pipeline.

---

## 2. Key Architecture & Implemented Components

1. **`agents-cli-manifest.yaml`**: Google ADK discovery manifest with temperature control per agent node.
2. **`src/olympus_specialist/guardrails/cost_gate.py`**: Hard $5.00/day GCP budget circuit breaker.
3. **`src/olympus_specialist/telemetry/hierarchical_tracker.py`**: Multi-agent hierarchical token & spend tracker.
4. **`src/olympus_specialist/adk_app.py`**: Google ADK application bridge.
5. **`src/olympus_specialist/workflow/eaer_pipeline.py`**: 4-Stage EAER pipeline (Extraction -> Amplification -> Evaluation -> Redo).
6. **`src/olympus_specialist/workflow/scenario_generator.py`**: Scenario Generator Agent for dynamic dataset amplification.
7. **`evals/datasets/golden_scenarios.json`**: 10 real-world microscopy assembly scenarios.
8. **`evals/reporters/eval_reporter.py`**: Google ADK Formal Evaluation Reporter generating `eval_report.html` and `eval_report.md`.
9. **`src/olympus_specialist/domain/products/catalog.py`**: Canonical product database schema & hybrid search repository.
10. **`src/olympus_specialist/ingestion/authorized_connector.py`**: Scientific validation gateway & connector.
11. **`src/olympus_specialist/api/server.py`**: FastAPI server & SSE streaming bridge.
12. **MCP Integration**:
    - [`.mcp/mcp_config.json`](file:///Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/.mcp/mcp_config.json)
    - [`.mcp/servers/evident_catalog_mcp.py`](file:///Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/.mcp/servers/evident_catalog_mcp.py)
13. **CI/CD Pipeline**:
    - [`.github/workflows/ci.yml`](file:///Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/.github/workflows/ci.yml)
14. **Docker Containers**:
    - [`Dockerfile.api`](file:///Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/Dockerfile.api)
    - [`Dockerfile.evals`](file:///Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/Dockerfile.evals)
    - [`Dockerfile.judge`](file:///Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/Dockerfile.judge)
    - [`docker-compose.yml`](file:///Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/docker-compose.yml)

---

## 3. Verification & Test Suite Status
- **Pytest Results**: 54/54 tests passing cleanly (`PYTHONPATH=src .venv/bin/python -m pytest tests/ -v`).
- **Google ADK Eval Benchmark**: 100.0% Pass Rate across 10 scenarios.
