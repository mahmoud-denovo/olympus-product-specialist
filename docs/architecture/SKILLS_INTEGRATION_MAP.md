# Downloaded Skills Assessment & Integration Map

> **Document Location:** `docs/architecture/SKILLS_INTEGRATION_MAP.md`
> **Source Repository:** `github.com/google/skills`

---

## 1. Assessment of Downloaded GitHub Skills

قمنا بفحص الـ 91 مهارة (`Skills`) التي تم تنزيلها اليوم من مكتبة `google/skills`. إليك التحليل المباشر للما يحتاجه مشروعنا وما نحسبه للمستقبل:

```mermaid
graph TD
    subgraph "google/skills Repository (91 Total Skills)"
        Downloaded["All Skills in System Cache"]
    end

    Downloaded --> Phase1["1. Immediate Import for Phase 1 (Core Agent Stack)"]
    Downloaded --> Phase2["2. Staging / Cloud Release Skills (Phase 2 & 3)"]
    Downloaded --> Excluded["3. Irrelevant Skills (Mobile Ads, Android UI, etc.)"]

    subgraph "Phase 1 Imported Skills (.agents/skills/)"
        P1_1["gemini-api & gemini-agents-api"]
        P1_2["agent-platform-prompt-management"]
        P1_3["agent-platform-eval-flywheel"]
        P1_4["agent-platform-skill-registry"]
        P1_5["gemini-live-api (Streaming SSE)"]
    end

    subgraph "Phase 2 & 3 Future Cloud Skills"
        P2_1["cloud-run-basics & gke-basics"]
        P2_2["bigquery-ai-ml & bigquery-basics"]
        P2_3["agent-platform-deploy"]
    end

    Phase1 ==> Phase1 Imported Skills
    Phase2 ==> Phase2 & 3 Future Cloud Skills
```

---

## 2. Selected Skills List & Purpose

### **أ) المهارات المستوردة فوراً لـ Phase 1 (تم نسخها لـ `.agents/skills/`):**
1. **`gemini-api` & `gemini-agents-api`:** أنماط التعامل مع نماذج Gemini 2.5 Flash / Pro وحفظ التوكنز عبر الـ Context Caching.
2. **`gemini-live-api`:** لإدارة الـ SSE Event Streams في الـ Real-time Interactions.
3. **`agent-platform-prompt-management`:** لإدارة نظام الـ System Prompts والحفاظ على ثبات السلوك وعدم انحراف الإجابات.
4. **`agent-platform-eval-flywheel`:** لربط التقييم المستمر بالـ Golden Scenarios ومنع أي Hallucination.
5. **`agent-platform-skill-registry`:** لحوكمة وتسجيل مهارات الـ Subagents محلياً.

---

### **ب) المهارات المؤجلة لبيئة الـ Staging والدفع للكلاود (Phase 2 & 3):**
* `cloud-run-basics`: عند تجهيز الـ Microservices المستقلة.
* `bigquery-ai-ml` & `bigquery-basics`: عندما يحتاج العميل تحليل بيانات ضخمة في الكلاود.
* `agent-platform-deploy`: للنشر النهائي على بيئة الإنتاج المؤسسية.

---

### **ج) المهارات المستبعدة كلياً (Irrelevant):**
* إعلانات الهواتف (`google-mobile-ads-*`).
* تطبيقات الأندرويد والـ IMA SDK.

---

## 3. Current Local Status in Project

جميع المهارات المختارة والمفيدة لـ Phase 1 أصبحت مدمجة ومحفوظة ومرفوعة بداخل مجلد مشروعك الرسمي:
📁 **[`.agents/skills/`](file:///Users/amirahajeer/Desktop/products-specialists-agents/olympus-product-specialist/.agents/skills/)**
