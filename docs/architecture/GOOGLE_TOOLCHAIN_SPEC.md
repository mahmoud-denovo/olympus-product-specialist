# Google Toolchain Integration Architecture: ADK, Antigravity SDK & agents-cli

> **Document Location:** `docs/architecture/GOOGLE_TOOLCHAIN_SPEC.md`
> **Target Project:** `olympus-product-specialist`
> **Standard:** Start from where Google stopped (Zero Reinventing of the Wheel)

---

## 1. Executive Summary & Philosophy

كلامك دقيق 100% وفي صلب احترافية بناء الأنظمة المؤسسية: **"البدء من حيث انتهى العالم وعدم إعادة اختراع العجلة."**

تعتمد البنية التحتية لمنصة **Olympus Product Specialist** بالكامل على منظومة أدوات جوجل الرسمية الممتازة المتاحة في جهازنا:

```mermaid
graph TD
    subgraph "1. Developer & Lifecycle CLI (agents-cli)"
        A_CLI["agents-cli CLI Tool"] -->|Scaffold, Eval & Playground| DevLoop["Local Playground & Evals"]
        A_CLI -->|Publish & Deploy| CloudRun["GCP Agent Runtime / Cloud Run"]
    end

    subgraph "2. Runtime Agent Engine (Google ADK & Antigravity SDK)"
        ADK["Google ADK (Agent Development Kit)"] -->|Agent Tree & Routing| RootAgent["Root Specialist Orchestrator"]
        AGY_SDK["google-antigravity-sdk / Local agy"] -->|Optical Compatibility ($0 Local)| SubAgents["Local Subagents Pool"]
        
        RootAgent & SubAgents --> Telemetry["Hierarchical Token Tracker"]
    end

    subgraph "3. Native Enterprise Capabilities (Built-in Google SDK Features)"
        Telemetry --> Caching["Vertex AI Context Caching"]
        Telemetry --> Playground["agents-cli playground (Visual Debug UI)"]
        Telemetry --> EvalsEngine["agents-cli eval (Golden Scenario Grader)"]
    end
```

---

## 2. Comprehensive Toolchain Inventory (الأدوات والـ SDKs المتوفرة وكيف نستخدمها)

| الأداة / الـ SDK | الميزة المتاحة مبنياً (Built-in Feature) | كيف نستخدمها في المشروع لحفظ التوكنز والجهد |
| :--- | :--- | :--- |
| **`agents-cli`** | أداة جوجل الرسمية لإدارة دورة حياة الـ Agents (`create`, `eval`, `playground`, `deploy`, `publish`). | تُستخدم لإشغال واجهة الـ **Playground المحلية** لاختبار الاستجابات بصرياً، وتوليد تقارير الـ Evals التلقائية عبر `agents-cli eval`. |
| **`Google ADK` (Agent Development Kit)** | إطار العمل الرسمي لبناء الـ Agent Hierarchy والـ Routing والـ State Management. | مدمج في `src/olympus_specialist/adk_app.py` وملف الـ Manifest الرسمي `agents-cli-manifest.yaml`. |
| **`Antigravity SDK / agy`** | المحرك المحلي السريع لتنفيذ النماذج والسكربتات مجاناً دون تكلفة للكلاود ($0 Local Execution). | مدمج في `src/core/agy_runner.py` لتنفيذ قواعد المطابقة المجهرية محلياً 100%. |
| **`google-genai` Python SDK** | مكتبة جوجل الرسمية الحديثة للتعامل مع Gemini 2.5 Flash / Pro و Context Caching. | نستخدمها للربط المباشر مع Vertex AI واستغلال الـ Context Caching لحفظ التوكنز بنسبة 80%. |

---

## 3. How We Leverage Built-in Features (توفير التوكنز والتطوير الأذكى)

1. **إعادة استخدام الـ Playground المدمج:**
   * بدل بناء واجهة تجريبية من الصفر، يمكننا إطلاق الـ Playground الرسمي لجوجل فوراً عبر الأمر:
     `agents-cli playground --manifest agents-cli-manifest.yaml`
2. **الـ Context Caching مع Gemini 2.5 Flash:**
   * نقوم بتخزين كتالوج المنتجات وقواعد التوافق المجهري الثابتة في **Vertex AI Context Cache**، مما يخفض تكلفة التوكنز والـ Latency في كل طلب جديد بشكل هائل.
3. **تتبع التوكنز الهيكلي (Hierarchical Telemetry Tracker):**
   * مدمج في `src/olympus_specialist/telemetry/hierarchical_tracker.py` ليعطي تقارير دقيقة بأسماء الـ Subagents واستهلاك كل منها بالتوكنز والدولار.

---

## 4. Immediate Action Plan in Repo

* 📄 **المستند الموثق في المشروع:** [`docs/architecture/GOOGLE_TOOLCHAIN_SPEC.md`](file:///Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/docs/architecture/GOOGLE_TOOLCHAIN_SPEC.md)
* 🚀 **أمر تشغيل الـ Playground للتجربة البصرية:**
  ```bash
  agents-cli playground --manifest agents-cli-manifest.yaml
  ```
