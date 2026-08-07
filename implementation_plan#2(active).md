# Master Implementation Plan: Olympus Product Specialist Web Platform

> **Project:** Olympus Product Specialist Web Application  
> **Platform DNA:** DeNovo Synthesis Architecture  
> **Stack:** React + Vite + TypeScript (Frontend Web App) + FastAPI/SSE (Python Backend) + Antigravity SDK / ADK + PostgreSQL/SQLite + pgvector  
> **Status:** APPROVED FOR IMPLEMENTATION — $0 Local MVP Baseline with GCP Cost Guardrails  

---

## 1. System Architecture & Self-Healing Dataflow

The architecture features a **Self-Healing Loop** and **Centralized Management Infrastructure** alongside the 3-Layer DeNovo Engine.

```mermaid
flowchart TD
    subgraph Client_App ["1. Web Application Frontend (React + TypeScript)"]
        UI["Product Advisor UI\n(Evidence & Validation | Chat Console | Session History)"]
    end

    subgraph Central_Infra ["2. Centralized Infrastructure Layer"]
        PROMPTS["Centralized Prompt Registry\n(Versioned System Prompts)"]
        LOGGER["Step-by-Step Structured Logger\n& Exception Handler"]
        SOPS["Agent SOPs & Dynamic Skill Loader\n(Voice/Audio Ready)"]
    end

    subgraph Runtime_Core ["3. Product Specialist Core & Self-Healing Loop"]
        AGENT["Olympus Product Specialist Agent"]
        SELF_HEAL["Self-Healing Remediation Engine\n(Error Catching -> Auto-Repair -> Resumption)"]
        VALIDATOR["L1 Deterministic Compatibility Engine\n($0 Cost, No LLM in Hot Path)"]
        TOOL_SCRAPER["Evident Web Scraper & Search Tool\n(Robots.txt Compliant)"]
    end

    subgraph Storage_Layer ["4. Local Storage Layer (PostgreSQL / SQLite)"]
        CATALOG["Canonical Product Catalog\n(Stands, Objectives, Compatibility Rules)"]
        VECTOR["Semantic Vector Index (pgvector)"]
    end

    subgraph Cloud_Models ["5. Model Layer & Cost Guardrails"]
        MODELS["Gemini Models via Vertex AI / API\n(MODEL_REASONING, MODEL_EXTRACTION)"]
        KILLSWITCH["Cost Circuit Breaker & Budget Guardrail\n(Hard $5.00/day Limit)"]
    end

    UI <-->|Server-Sent Events / SSE| AGENT
    AGENT <--> PROMPTS
    AGENT <--> LOGGER
    AGENT <--> SOPS
    
    AGENT <--> SELF_HEAL
    SELF_HEAL --> LOGGER
    
    AGENT <--> VALIDATOR
    AGENT <--> TOOL_SCRAPER
    TOOL_SCRAPER --> VECTOR
    VALIDATOR --> CATALOG
    
    AGENT <--> KILLSWITCH
    KILLSWITCH <--> MODELS
```

---

## 2. Self-Healing Loop Sequence Diagram

When a tool call fails or returns malformed/incomplete data, the **Self-Healing Loop** intercepts the exception, fetches a remediation sub-prompt from the Centralized Prompt Registry, corrects the input parameters, and resumes execution seamlessly.

```mermaid
sequenceDiagram
    autonumber
    actor User as Client / Sales Lead
    participant Agent as Specialist Agent
    participant Heal as Self-Healing Engine
    participant Tool as Evident Scraper / Validator
    participant Logger as Structured Logger

    User->>Agent: "Find me a metallurgical microscope for 100x optical analysis."
    Agent->>Tool: Execute search_catalog(magnification=100)
    Tool-->>Heal: Error / Unfulfilled Slots (Missing Illumination Mode)
    
    Logger->>Logger: Log Step-by-Step Error (Correlation ID: ERR-104)
    Heal->>Agent: Inject Remediation Sub-prompt from Registry
    Agent->>User: "Which illumination mode do you need for 100x analysis? (Brightfield/Darkfield?)"
    
    User->>Agent: "Darkfield metallurgical."
    Agent->>Tool: Re-execute search_catalog(magnification=100, mode="BD")
    Tool-->>Agent: Validated Component Options
    Logger->>Logger: Log Self-Healing Recovery Success
    Agent->>User: Present verified recommendation + source citation
```

---

## 3. Directory & Module Layout

The codebase organizes prompts, logging, SOPs, and domain logic into centralized modules:

```
denovo-olympus-platform/
├── apps/
│   └── web/                         # React + Vite + TypeScript Web Application
│       ├── src/
│       │   ├── features/
│       │   │   ├── advisor/         # Product Advisor (P-Site)
│       │   │   ├── evidence/        # Evidence & Validation Panel (A-Site)
│       │   │   └── sessions/        # Session History (E-Site)
│       │   ├── components/
│       │   └── api/
│       ├── package.json
│       └── tsconfig.json
├── src/
│   └── olympus_specialist/          # Backend Python Core
│       ├── api/                     # FastAPI SSE endpoints
│       ├── prompts/                 # Centralized Prompt Registry (Versioned System Prompts)
│       ├── logging/                 # Step-by-Step Structured Logger & Exception Hierarchy
│       ├── sops/                    # Agent Standard Operating Procedures & Audio/Voice Hooks
│       ├── skills/                  # Dynamic Skill Loader (SOP-bound tools)
│       ├── self_healing/            # Autonomous Remediation Engine & Error Diagnostic Gate
│       ├── agents/                  # Specialist Agent Orchestrator
│       ├── domain/                  # Domain Business Logic (products, compatibility)
│       └── guardrails/              # Cost Circuit Breaker & GCP Daily Budget Limit ($5.00/day)
├── evals/                           # Evaluation & QA Suite
├── pyproject.toml                   # Managed via uv / .venv (managing-python-dependencies)
└── README.md
```

---

## 4. Cost Guardrails & GCP Model Garden Safety

To prevent unexpected GCP billing spikes (e.g., Model Garden / Vertex AI background charges):

1. **Hard Budget Circuit Breaker (`src/olympus_specialist/guardrails/cost_gate.py`):**
   * Tracks daily API spend.
   * Hard-blocks any model invocation if daily spend reaches **$5.00/day**.
2. **Explicit Idle Shutdown:**
   * Ensures no background model polling or unmonitored streaming loops remain active when the application is idle.

---

## 5. Open Questions & Review

> [!IMPORTANT]
> 1. **Centralized Prompt Registry Format:** Prompts will be stored as versioned YAML/Markdown templates in `src/olympus_specialist/prompts/`. Do you approve this format?
> 2. **Step-by-Step Logging:** Logs will be recorded in JSONL format with step-by-step correlation IDs (`session_id`, `step_index`, `action`, `status`, `healing_attempts`). Is this acceptable?
