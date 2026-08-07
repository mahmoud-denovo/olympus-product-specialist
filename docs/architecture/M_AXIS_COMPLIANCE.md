# M-Axis Audit, Alignment & Shift Tracking Governance Log

> **Document Location:** `docs/architecture/M_AXIS_COMPLIANCE.md`
> **Target Project:** `olympus-product-specialist`
> **Standard:** M-Axis (Fourth Dimensional Alignment Tracker)

---

## 1. M-Axis Alignment Principles & Governance Rules

The **M-Axis** represents the 4th-Dimensional Alignment Vector of the system architecture across time, task evolution, and multi-agent operations.

### **Rules of Engagement:**
1. **Zero Unnoticed Drift:** Any deviation from the Master Architecture, whether intentional (agreed adjustment) or caught as an unintended drift, is logged line-by-line with a single-sentence rationale.
2. **Deterministic Resiliency:** High-load API errors (e.g., `429 Model API is currently overloaded`) are treated as **triggers, not failures**. The agent never halts; it increments global overload counters and runs a 5-minute exponential backoff retry loop.
3. **Hierarchical Task Promotion:** Any subagent managing **>3 tasks** OR operating at a tree depth **>3 layers** is automatically promoted to a **Task Orchestrator Agent**.

---

## 2. Shift Counter & Drift Log (Single-Sentence Single-Line Summaries)

| Shift # | Event Type | Trigger / Shift Rationale | Status |
| :--- | :--- | :--- | :--- |
| **Shift 1** | Intentional | Shifted architecture from local-only CLI to Hybrid Desktop / API Gateway for scalability. | **APPROVED** |
| **Shift 2** | Caught Drift | Aligned legacy `SequentialThinking` CLI with `Google ADK` & `agents-cli` manifest standard. | **REMEDIATED** |
| **Shift 3** | Intentional | Decentralized agent docs to live in repository root `docs/architecture/` (Docs-as-Code). | **APPROVED** |
| **Shift 4** | Intentional | Integrated `uv` ultra-fast package manager and `google/skills` into local `.agents/skills/`. | **APPROVED** |
| **Shift 5** | Intentional | Built `DeterministicOrchestrator` with 5-minute retry backoff for API overload resilience. | **APPROVED** |

---

## 3. High-Load Overload & Retry Surface Telemetry

```mermaid
graph TD
    subgraph "Local Execution Runtime"
        AgentCall["Agent Call Executing"] --> API["Gemini / Vertex AI API"]
    end

    subgraph "Resilience Circuit Breaker"
        API -->|Overload Error 429/503| Counter["Increment Global Overload Error Counter"]
        Counter --> Timer["Start 5-Minute Retry Timer (300s Backoff)"]
        Timer --> Retry["Retry Attempt Counter +1"]
        Retry --> API
    end

    Counter --> SurfaceTelemetry["Report Total Overload & Retry Counter to Surface Dashboard"]
```

---

## 4. Current M-Axis System Metrics

- **Total M-Axis Shifts Logged:** 5 Shifts (4 Intentional, 1 Caught Drift).
- **Current Alignment Rating:** **100.0% Compliant (59/59 Tests Passing)**.
- **Overload Resiliency Circuit Breaker:** Active & Verified in `resilient_orchestrator.py`.
