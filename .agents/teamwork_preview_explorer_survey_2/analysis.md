# Comprehensive Requirement Analysis & UX/Governance Specification — olympus-product-specialist

**Author**: Survey Explorer 2  
**Date**: 2026-08-05T08:25:00Z  
**Project**: `olympus-product-specialist`  
**Working Directory**: `/Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/.agents/teamwork_preview_explorer_survey_2`  

---

## 1. Executive Summary & Problem Scope

The `olympus-product-specialist` agent is an AI-first, interactive, zero-cloud-cost default Command Line Interface (CLI) application engineered for non-technical sales and logistics staff at Evident/Olympus microscopy divisions.

### Core Objectives:
1. **Interactive Optical System Assembly**: Assist non-technical sales and logistics agents in configuring complex biological and industrial microscopes step-by-step across 5 primary optical/hardware modules:
   - **Frame / Stand** (e.g. BX53, IX73, CX23, SZX16)
   - **Light Source & Illumination Engine** (e.g. Halogen 100W, LED True Color, Mercury/Xenon Arc Lamp)
   - **Objectives & Optical Nosepieces** (e.g. UPlanFLN 10X, UPlanSApo 60XO, APO 100X Oil, RMS vs M25 threads)
   - **Camera Adapters & Digital Imaging** (e.g. C-mount 0.5x, C-mount 1x, F-mount, DP28 / DP23 cameras)
   - **Software & Accessories** (e.g. cellSens Standard/Dimension, motorized stages, filter cubes)
2. **Zero-Cloud-Cost Core Engine**: Execute configuration logic natively using the local `Antigravity CLI (agy)` pool (`/Users/amirahajeer/.local/bin/agy`) without incurring external API token costs.
3. **Controlled LLM Judge**: Integrate a guarded evaluation module leveraging Google AI Studio (`GEMINI_API_KEY`) with daily rate limits and expenditure caps to perform zero-hallucination checks, accuracy grading, and partner-ready proposal validation.
4. **Live Evident/Olympus Web Validation**: Real-time HTTP spec fetching and model validation against official domains (`evident-scientific.com` and `olympus-lifescience.com`).
5. **Local SQLite Knowledge Graph**: High-performance local relational database storing optical compatibility laws (mounting threads, working distances, optical path infinity lengths, power input, software OS compatibility).
6. **Legacy Preservation & Governance (Rule B-01)**: Isolation of legacy migration mappings in `legacy_reference/MIGRATION_MAP.md` from `olympus-workspace-agent`, enforcing **Rule B-01**: *Zero code or decision from the legacy workspace is adopted without explicit prior user presentation and approval.*

---

## 2. Granular Feature Inventory (Requirements & Acceptance Criteria Mining)

### 2.1 Requirement Mining Matrix

| Req ID | Title | Summary Description | Verification Method |
|---|---|---|---|
| **R1** | Autonomous & Interactive HitL CLI Interface | Rich, step-by-step CLI interface using native `SequentialThinking` protocol; pauses at optical assembly steps for user confirmation with plain Arabic prose + English technical terms. | `pytest tests/test_cli_ux.py` with mock terminal input & Rich output capture. |
| **R2** | Zero-Cloud-Cost Core & Controlled Gemini LLM Judge | Default execution on local `agy` pool; controlled Gemini LLM Judge via `GEMINI_API_KEY` with strict rate limits & spending caps. | `pytest tests/test_llm_judge.py` testing agy fallback & rate limiter boundaries. |
| **R3** | Web Validation & Local Knowledge Graph | Real-time URL/spec validation against official Evident/Olympus web domains + SQLite Knowledge Graph persisting optical rules. | `pytest tests/test_web_validator.py` & `pytest tests/test_knowledge_graph.py`. |
| **R4** | Legacy Preservation (Rule B-01) | `legacy_reference/MIGRATION_MAP.md` initialization documenting legacy laws; enforcement of Rule B-01. | `pytest tests/test_legacy_governance.py` validating Rule B-01 audit triggers. |

---

### 2.2 Granular Feature Inventory Items

#### Feature Group 1: Autonomous & Interactive HitL CLI Interface (R1)

- **FI-R1.1: Rich Terminal UI Framework**
  - *Description*: Construct a CLI presentation layer built on Python `rich` library (`rich.console.Console`, `rich.panel.Panel`, `rich.table.Table`, `rich.prompt.Prompt`).
  - *Acceptance Criterion*: CLI renders styled text, tables, status spinners, and color-coded warning banners without raw text clutter.
  - *Testability*: Testable via `rich.console.Console(record=True)` output capture assertions.

- **FI-R1.2: Native SequentialThinking Reasoning Pipeline**
  - *Description*: Implement a multi-step reasoning protocol that decomposes complex microscopy queries into sequential sub-tasks (Frame -> Light Source -> Objectives -> Camera Adapter -> Software).
  - *Acceptance Criterion*: Each step is logged sequentially with step numbers, rationale, and state progression.
  - *Testability*: Testable by inspecting step emission logs and state machine transitions.

- **FI-R1.3: Bilingual Presentation (Plain Arabic Prose + English Technical Terms)**
  - *Description*: Present assembly recommendations and optical choice rationale in clear, accessible Arabic prose while preserving exact English model numbers and technical specs.
  - *Example*: "تم اختيار العدسة الشيئية ذات التكبير العالي (Objective UPlanSApo 60XO, NA 1.42, WD 0.15mm) لأنها توفر دقة عالية للعينات البيولوجية."
  - *Acceptance Criterion*: All user-facing optical cards include non-technical Arabic explanation alongside exact English technical terms (NA, WD, FOV, Mount).
  - *Testability*: Regex assertion on output text for Arabic script characters + English optical terms.

- **FI-R1.4: Human-in-the-Loop (HitL) Assembly Confirmation Pause**
  - *Description*: The system pauses execution after each optical component recommendation, presenting a structured confirmation menu `[y/N/edit/details]` and waiting for explicit CLI keyboard input.
  - *Acceptance Criterion*: System does NOT proceed to the next optical subsystem until the user confirms the current selection.
  - *Testability*: Mock `stdin` input testing transition on 'y', prompt repetition on invalid input, and cancellation on 'N'.

---

#### Feature Group 2: Zero-Cloud-Cost Core & Controlled Gemini LLM Judge (R2)

- **FI-R2.1: Local `agy` CLI Pool Execution Engine**
  - *Description*: Implement a subprocess / local execution adapter that routes standard reasoning and configuration tasks to `/Users/amirahajeer/.local/bin/agy` with zero cloud token consumption.
  - *Acceptance Criterion*: System operates end-to-end without cloud API keys when Gemini LLM Judge is not invoked.
  - *Testability*: Execute CLI with `GEMINI_API_KEY` unset, confirming successful optical configuration via `agy`.

- **FI-R2.2: Controlled Gemini LLM Judge Integration**
  - *Description*: Implement an opt-in evaluation module using `GEMINI_API_KEY` to grade optical configuration proposals, verify zero-hallucination compliance, and generate partner-ready output scores.
  - *Acceptance Criterion*: LLM Judge produces structured JSON evaluation reports containing accuracy score (0-100%), hallucination flags, and partner compliance notes.
  - *Testability*: Mock HTTP responses from Gemini API endpoint to verify response parsing and score computation.

- **FI-R2.3: Daily Rate Limiter & Spending Cap Enforcement**
  - *Description*: Wrap the Gemini LLM Judge in a strict rate limiter (e.g. max 50 requests/day) and daily cost tracking guard (e.g. max $0.50/day).
  - *Acceptance Criterion*: When daily request count or spending cap is reached, LLM Judge calls are blocked and fall back to local `agy` verification with a CLI warning banner.
  - *Testability*: Simulate 51st request or cap breach; verify fallback mechanism and block status.

---

#### Feature Group 3: Live Web Validation & Local Knowledge Graph (R3)

- **FI-R3.1: Evident/Olympus Official Domain Web Validator**
  - *Description*: Live web inspector that validates product URLs and spec pages against official domains (`evident-scientific.com`, `olympus-lifescience.com`, `olympus-global.com`).
  - *Acceptance Criterion*: Any URL outside approved domain whitelist is flagged as untrusted/hallucinated; valid URLs are fetched and verified for HTTP 200 and product SKU presence.
  - *Testability*: Test URL validator against `https://www.evident-scientific.com/en/microscopes/bx53/` (valid) vs `https://fake-olympus-store.com/bx53` (rejected).

- **FI-R3.2: SQLite Knowledge Graph Initialization & Schema**
  - *Description*: Initialize a local SQLite database (`data/knowledge_graph.db`) storing structured optical components, specs, and compatibility constraints.
  - *Acceptance Criterion*: SQLite database table structure created with tables `components`, `compatibility_rules`, `optical_mounts`, `web_cache`.
  - *Testability*: SQLite schema verification via table inspection queries (`PRAGMA table_info`).

- **FI-R3.3: Optical Compatibility Rules Engine**
  - *Description*: Query SQLite Knowledge Graph to enforce physical & optical compatibility laws:
    1. *Objective Thread Compatibility*: RMS (0.8" x 36 tpi) vs M25 (M25 x 0.75mm) vs M32.
    2. *Illumination Power Match*: 100W Halogen housing requires 12V 100W power supply unit.
    3. *Camera Mount Focal Match*: C-mount adapter 0.5x vs 1x field of view matching camera sensor size (e.g., 2/3" vs 1/1.8").
    4. *Software OS Requirement*: cellSens 3.2+ requires Windows 10/11 64-bit.
  - *Acceptance Criterion*: Incompatible combinations (e.g., M25 objective into RMS nosepiece without adapter) trigger an immediate optical violation warning.
  - *Testability*: Unit tests submitting incompatible pairs and verifying rejection output.

---

#### Feature Group 4: Legacy Preservation & Rule B-01 Governance (R4)

- **FI-R4.1: Legacy Reference Directory Structure**
  - *Description*: Create directory `legacy_reference/` at root with `MIGRATION_MAP.md` mapping laws from `olympus-workspace-agent`.
  - *Acceptance Criterion*: `legacy_reference/MIGRATION_MAP.md` exists and contains explicit documentation of Rule B-01.
  - *Testability*: File existence check & content assertion for "Rule B-01".

- **FI-R4.2: Rule B-01 Explicit Approval Protocol Engine**
  - *Description*: Core rule enforcement: Any code pattern, decision logic, or mapping imported from `olympus-workspace-agent` requires an explicit user presentation card and CLI approval prompt before execution.
  - *Acceptance Criterion*: Execution halts and prompts the user whenever a legacy law is referenced.
  - *Testability*: Trigger legacy rule check and verify prompt interception.

---

## 3. Detailed User Experience (UX) Architecture

### 3.1 SequentialThinking Workflow Specification

The CLI follows a 5-step SequentialThinking lifecycle:

```
[User Request]
      │
      ▼
┌─────────────────────────────────────────────────────────┐
│ Step 1: Query Analysis & Subsystem Decomposition        │
│ - Identify targeted application (Biological/Industrial) │
│ - Determine required microscope frame class             │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ Step 2: Knowledge Graph Compatibility Lookup            │
│ - Query SQLite DB for compatible Light Source & Optics   │
│ - Filter objective thread sizes, working distances      │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ Step 3: Dual-Language HitL Step Presentation            │
│ - Render rich card: Plain Arabic prose rationale        │
│ - Render technical table: English SKUs, NA, WD, Mount   │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ Step 4: Human-in-the-Loop Confirmation Pause            │
│ - Prompt: "هل توافق على اختيار مكون الهيكل الموصى به؟" │
│ - Input: [y] Accept | [n] Reject | [e] Edit | [d] Details│
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ Step 5: Web Validation & Final Bill of Materials (BOM)  │
│ - Verify URLs on evident-scientific.com                 │
│ - Output complete, validated configuration report       │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Bilingual UX Interface Design (Arabic Prose + English Tech Terms)

To ensure clarity for non-technical sales staff, every optical assembly card follows this standard template format:

#### Example Step Presentation Card (Step 3: Objectives Selection)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ 🔬 الخطوة 3 من 5: اختيار العدسات الشيئية (Objectives Selection)              │
├─────────────────────────────────────────────────────────────────────────────┤
│ 📝 الشرح باللغة العربية:                                                    │
│ تم اختيار مجموعة عدسات سلسلة UPlanSApo عالية الدقة لأنها توفر تصحيحاً لونياً    │
│ كاملاً (Apochromatic) وفتحة عددية ممتازة (High NA)، مما يجعلها مثالية للتصوير   │
│ البيولوجي المتقدم والفلورة (Fluorescence Imaging).                          │
│                                                                             │
│ ⚙️ الفحص الفني للتوافق البصري (Optical Compatibility Check):                 │
│ ✅ سن اللولب (Thread): RMS (0.8" x 36 tpi) - متوافق مع البرج (Nosepiece)   │
│ ✅ مسافة المسار البصري (Parfocal Distance): 45mm - قياسي                    │
├─────────────────────────────────────────────────────────────────────────────┤
│ 📊 المواصفات التقنية التفصيلية (Technical Specifications):                  │
│ ┌──────────────┬──────────────┬────────┬──────────┬──────────┬────────────┐ │
│ │ Part Number  │ Model Name   │ Magnif.│ NA       │ WD (mm)  │ Cover Glass│ │
│ ├──────────────┼──────────────┼────────┼──────────┼──────────┼────────────┤ │
│ │ N1480500     │ UPlanSApo 10X│ 10x    │ 0.40     │ 3.1      │ 0.17mm     │ │
│ │ N1480800     │ UPlanSApo 40X│ 40x    │ 0.95     │ 0.18     │ 0.11-0.23mm│ │
│ │ N1481100     │ UPlanSApo100X│ 100x   │ 1.40 Oil │ 0.13     │ 0.17mm     │ │
│ └──────────────┴──────────────┴────────┴──────────┴──────────┴────────────┘ │
├─────────────────────────────────────────────────────────────────────────────┤
│ ❓ تأكيد المستخدم (Human-in-the-Loop Confirmation):                         │
│ هل ترغب في اعتمـاد هذه العدسات الشيئية في التجميع البصري؟                   │
│ [Y] موافقة وانتقال | [N] رفض | [E] تعديل الاختيارات | [D] عرض تفاصيل Web    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Governance, Safety & Architecture Specification

### 4.1 Zero-Cloud-Cost Core via `agy` Local Pool

```
                       ┌─────────────────────────┐
                       │  User Configuration CLI │
                       └────────────┬────────────┘
                                    │
                         Is LLM Judge explicitly
                         requested for deep audit?
                                   / \
                                  /   \
                             NO  /     \  YES
                                /       \
                               ▼         ▼
             ┌───────────────────┐     ┌───────────────────────────┐
             │ Local Core Engine │     │ Gemini LLM Judge Module   │
             │ via `agy` CLI     │     │ (Requires GEMINI_API_KEY) │
             │ Zero Cloud Cost   │     └─────────────┬─────────────┘
             └───────────────────┘                   │
                                          Daily Cap / Rate Limit
                                                 Exceeded?
                                                    / \
                                               YES /   \ NO
                                                  /     \
                                                 ▼       ▼
                                       ┌──────────┐    ┌──────────┐
                                       │ Fallback │    │ Execute  │
                                       │ to agy   │    │ Gemini   │
                                       └──────────┘    └──────────┘
```

- **Default Execution Route**: System defaults to local execution using `/Users/amirahajeer/.local/bin/agy`.
- **Zero API Key Requirement for Core**: Core CLI functions (SequentialThinking, SQLite Knowledge Graph lookup, Rich formatting, HitL prompts, Web URL validation) require NO cloud API keys.

### 4.2 Controlled Gemini LLM Judge Architecture

- **Environment Variable**: `GEMINI_API_KEY` (Google AI Studio).
- **Daily Quotas & Spending Caps**:
  - `MAX_DAILY_JUDGE_CALLS`: 50 calls / 24-hour rolling window.
  - `MAX_DAILY_JUDGE_SPEND_USD`: $0.50 / day.
- **State File**: `.agents/teamwork_preview_explorer_survey_2/llm_judge_quota.json` (or system state dir).
- **Evaluation Output Schema**:
  ```json
  {
    "timestamp": "2026-08-05T08:25:00Z",
    "configuration_id": "CONFIG-BX53-BIO-001",
    "accuracy_score": 98.5,
    "zero_hallucination_pass": true,
    "partner_readiness_grade": "A+",
    "flagged_issues": [],
    "recommendation": "Partner-ready configuration for biological research."
  }
  ```

### 4.3 Official Web Inspector & Domain Validator

- **Whitelisted Domains**:
  - `https://www.evident-scientific.com/`
  - `https://www.olympus-lifescience.com/`
  - `https://www.olympus-global.com/`
- **Validation Pipeline**:
  1. Parse input URL scheme & hostname.
  2. Match hostname against whitelist regex: `^([a-z0-9-]+\.)*(evident-scientific\.com|olympus-lifescience\.com|olympus-global\.com)$`.
  3. Perform HEAD/GET HTTP request with custom User-Agent.
  4. Parse DOM to verify SKU / Part Number presence.
  5. Cache result in SQLite `web_cache` table to minimize redundant HTTP calls.

### 4.4 Local SQLite Knowledge Graph Design

- **Database File**: `data/knowledge_graph.db`
- **Tables & DDL Schemas**:

```sql
-- 1. Components Catalog
CREATE TABLE IF NOT EXISTS components (
    part_number TEXT PRIMARY KEY,
    model_name TEXT NOT NULL,
    category TEXT NOT NULL, -- Frame, LightSource, Objective, CameraAdapter, Software
    series TEXT,            -- BX3, IX3, CX2, UPlanSApo, etc.
    description_ar TEXT,
    description_en TEXT,
    official_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Optical Specifications
CREATE TABLE IF NOT EXISTS optical_specs (
    part_number TEXT PRIMARY KEY,
    thread_type TEXT,       -- RMS, M25, M32, C-Mount, F-Mount
    magnification REAL,
    numerical_aperture REAL,
    working_distance_mm REAL,
    field_number REAL,
    voltage_volts REAL,
    wattage_watts REAL,
    FOREIGN KEY(part_number) REFERENCES components(part_number)
);

-- 3. Compatibility Rules Matrix
CREATE TABLE IF NOT EXISTS compatibility_rules (
    rule_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_category TEXT NOT NULL,
    target_category TEXT NOT NULL,
    rule_type TEXT NOT NULL, -- MUST_MATCH, INCOMPATIBLE, REQUIRES_ADAPTER
    param_name TEXT NOT NULL, -- thread_type, power_supply, sensor_size
    description_ar TEXT NOT NULL,
    description_en TEXT NOT NULL
);

-- 4. Validation & Web Cache
CREATE TABLE IF NOT EXISTS web_cache (
    url TEXT PRIMARY KEY,
    http_status INTEGER,
    is_valid_domain BOOLEAN,
    verified_sku TEXT,
    last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4.5 Legacy Reference Preservation & Rule B-01 Protocol

- **File Path**: `legacy_reference/MIGRATION_MAP.md`
- **Content Requirements**:
  1. Table mapping legacy laws from `olympus-workspace-agent`.
  2. Explicit section stating **Rule B-01**:
     > **Rule B-01 Mandatory Declaration**:  
     > *Zero code or decision from the legacy workspace (`olympus-workspace-agent`) is adopted without explicit prior user presentation and approval in the interactive CLI.*
  3. Legacy Audit Interceptor module (`src/governance/legacy_governance.py`) that checks any legacy adoption against the HitL prompt engine.

---

## 5. Testability & Verification Methodologies

### 5.1 Test Suite Structure

| Test File | Target Functionality | Verification Command |
|---|---|---|
| `tests/test_cli_ux.py` | Rich UI rendering, step logging, bilingual prompt formatting | `pytest tests/test_cli_ux.py -v` |
| `tests/test_hitl.py` | Human-in-the-Loop pause & user confirmation handling | `pytest tests/test_hitl.py -v` |
| `tests/test_agy_core.py` | Zero-cloud-cost fallback & `agy` CLI integration | `pytest tests/test_agy_core.py -v` |
| `tests/test_llm_judge.py` | Gemini LLM Judge rate limits & spending caps | `pytest tests/test_llm_judge.py -v` |
| `tests/test_web_validator.py` | Official Evident/Olympus domain URL validation | `pytest tests/test_web_validator.py -v` |
| `tests/test_knowledge_graph.py` | SQLite Knowledge Graph optical compatibility queries | `pytest tests/test_knowledge_graph.py -v` |
| `tests/test_legacy_governance.py` | Rule B-01 enforcement & migration map checks | `pytest tests/test_legacy_governance.py -v` |

---

## 6. Summary of Architectural Deliverables for Implementation

1. `legacy_reference/MIGRATION_MAP.md`: Documenting Rule B-01 and legacy migration items.
2. `data/knowledge_graph.db`: Local SQLite database pre-populated with optical specs.
3. `src/cli/ui.py` & `src/cli/sequential_thinking.py`: Rich CLI interface with dual-language HitL prompts.
4. `src/core/agy_engine.py`: Local Antigravity CLI zero-cloud execution handler.
5. `src/governance/llm_judge.py`: Controlled Gemini API judge with rate limits.
6. `src/validation/web_inspector.py`: Official domain whitelist web validator.
7. `src/governance/legacy_governance.py`: Rule B-01 audit guard.

---
*End of Analysis Report.*
