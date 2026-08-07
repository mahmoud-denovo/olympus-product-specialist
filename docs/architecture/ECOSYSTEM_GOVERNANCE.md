# Project Ecosystem Governance: Brain, Skills, Artifacts & Metadata Standard

> **Document Location:** `docs/architecture/ECOSYSTEM_GOVERNANCE.md`
> **Target Project:** `olympus-product-specialist`

---

## 1. Enterprise Architecture Overview (هيكلية النظام الشاملة)

```mermaid
graph TD
    subgraph "Project Local Repository (olympus-product-specialist/)"
        RepoDocs["docs/architecture/ (Roadmaps, Artifacts & Reports)"]
        RepoAgents[".agents/ (Local Brain, Rules, Skills & Handoffs)"]
        RepoSrc["src/ (Production Execution Code)"]
    end

    subgraph "Agent Runtime Execution (System Environment)"
        SystemBrain["~/.gemini/antigravity/ (Temp System Brain / Cache)"]
        GlobalSkills["~/.gemini/antigravity-cli/skills/ (Global Skills Repo)"]
    end

    RepoAgents <== "Project Mirror & Sync" ==> SystemBrain
    GlobalSkills ==> "Selective Import & Isolation" ==> RepoAgents
    RepoDocs <== "Version Control & Commit History" ==> RepoSrc
```

---

## 2. Comprehensive Handling Strategy (كيفية التعامل مع الأركان الأربعة)

### **أ) الـ Brain (ذاكرة وعقل الـ Agent):**
- **المشكلة السابقة:** كانت سجلات العقل (`Brain Logs`) تُحفظ في مجلد النظام المجهول خارج الريبو (`~/.gemini/antigravity/brain/...`) مما يجعلها غير مرئية للشريك والمطور في الـ IDE.
- **الحل النهائي:** 
  نقوم بربط وعكس الـ Brain داخل مجلد محلي بالريبو اسمه **`.agents/`**:
  * `.agents/plan.md` : خطط العمل الجارية.
  * `.agents/progress.md` : تتبع الإنجاز لحظة بلحظة.
  * `.agents/handoff.md` : التوثيق لنقل المهام بين المطورين والـ Subagents.

---

### **ب) الـ Skills والـ Tools (المهارات والأدوات المستخدمة):**
- **المبدأ المعماري:** عدم حرق توكنز بمهارات غير لازمة، واستدعاء المهارات المناسبة فقط للـ Phase الجاري.
- **الآلية في المشروع:**
  * مجلد **`.agents/skills/`** داخل المشروع يحتوي على الـ Skills المخصصة للمنتج (مثل `microscopy-rules`, `optical-compatibility`, `evident-validator`).
  * إذا احتجنا سكيلز عامة (مثل `google-agents-cli-publish` أو `bigquery-sql`)، نقوم باستيرادها ونسخها مباشرة إلى `.agents/skills/` لتكون مسجلة ومحفوظة بداخل الريبو ومع الجيت هاب.

---

### **ج) الـ Artifacts والـ Metadata (المخرجات والبيانات الوصفية):**
- **المبدأ:** أي ملف خطة، رسم بياني (Diagram)، تقرير تقييم، أو بطاقة مواصفات يُعتبر **Artifact**.
- **الآلية:**
  1. كل Artifact يرافقة ملف **Metadata JSON** يصف اسمه، إصداره، وتاريخ تحديثه.
  2. يتم حفظ جميع الـ Artifacts بداخل مجلد **`docs/architecture/`** في الريبو الرئيسي للمشروع.
  3. تظهر الـ Artifacts مباشرة في شجرة ملفات الـ IDE ليراها المطور والشريك، وتدخل في الـ Git Commit.

---

## 3. Visualized Directory Mapping (خريطة المسارات في الريبو)

```
olympus-product-specialist/
├── .agents/                        # Local Project Brain & Agent State
│   ├── plan.md                     # Current Agent Active Plan
│   ├── progress.md                 # Real-time Execution Tracking
│   ├── handoff.md                  # Team & Agent Handoff Log
│   ├── rules/                      # System Rules & Guardrails
│   └── skills/                     # Project-Specific & Imported Skills
├── docs/                           # Project Artifacts & Documentation
│   └── architecture/               # Single Source of Truth
│       ├── MASTER_ROADMAP.md       # Master Execution Roadmap
│       ├── ECOSYSTEM_GOVERNANCE.md # This Governance Standard
│       └── M_AXIS_COMPLIANCE.md    # M-Axis Audit & Alignment Log
└── src/                            # Production Execution Source Code
```
