# Technical Refactoring Blueprint — Audit Remediation for Milestone M1

## Executive Summary
This document provides the exact, file-by-file code refactoring blueprint for Worker M1 to remediate all integrity audit findings identified in Auditor Report `handoff.md` (`teamwork_preview_auditor_m1_2`) and recorded in `GATE_STATUS.md`.

The remediation addresses three core compliance failures:
1. Missing `[MOCK_DATA]` tags in default catalog components and lack of `is_mock: bool` dataclass attribute in `src/engine/sequential_thinking.py`.
2. Missing `# [MOCK_IMPLEMENTATION]` structural markers and lack of colorized `[MOCK_DATA]` Rich UI badges in `src/cli/formatter.py`.
3. Discrepancy between code and attestation claims in `docs/MOCK_REGISTRY.md`.

---

## 1. Engine Refactoring Blueprint: `src/engine/sequential_thinking.py`

### 1.1 Dataclass `OptionCard` Definition (`src/engine/sequential_thinking.py:125-156`)

**Target Lines**: 125–156  
**Rationale**: Add `is_mock: bool = True` field, include `"is_mock"` in `to_dict()`, and guarantee `__getitem__` access.

```python
# BEFORE (Lines 125-156):
@dataclass(slots=True, kw_only=True)
class OptionCard:
    """Bilingual option card representing a microscopy component choice."""
    id: str
    stage: AssemblyStage | str
    model_name: str
    arabic_description: str
    english_specs: dict[str, Any]
    price_tier: str = "Mid-Range"
    optical_compatibility_status: bool = True
    incompatibility_reason: str | None = None
    recommended: bool = False

    def to_dict(self) -> dict[str, Any]:
        stage_val = self.stage.value if isinstance(self.stage, AssemblyStage) else str(self.stage)
        return {
            "id": self.id,
            "stage": stage_val,
            "model_name": self.model_name,
            "arabic_description": self.arabic_description,
            "english_specs": _make_json_serializable(self.english_specs),
            "price_tier": self.price_tier,
            "optical_compatibility_status": self.optical_compatibility_status,
            "incompatibility_reason": self.incompatibility_reason,
            "recommended": self.recommended,
        }

    def __getitem__(self, key: str) -> Any:
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(key)

# AFTER (Lines 125-158):
@dataclass(slots=True, kw_only=True)
class OptionCard:
    """Bilingual option card representing a microscopy component choice."""
    id: str
    stage: AssemblyStage | str
    model_name: str
    arabic_description: str
    english_specs: dict[str, Any]
    price_tier: str = "Mid-Range"
    optical_compatibility_status: bool = True
    incompatibility_reason: str | None = None
    recommended: bool = False
    is_mock: bool = True

    def to_dict(self) -> dict[str, Any]:
        stage_val = self.stage.value if isinstance(self.stage, AssemblyStage) else str(self.stage)
        return {
            "id": self.id,
            "stage": stage_val,
            "model_name": self.model_name,
            "arabic_description": self.arabic_description,
            "english_specs": _make_json_serializable(self.english_specs),
            "price_tier": self.price_tier,
            "optical_compatibility_status": self.optical_compatibility_status,
            "incompatibility_reason": self.incompatibility_reason,
            "recommended": self.recommended,
            "is_mock": self.is_mock,
        }

    def __getitem__(self, key: str) -> Any:
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(key)
```

---

### 1.2 Default Catalog Function `_load_default_catalog()` (`src/engine/sequential_thinking.py:261-400`)

**Target Lines**: 261–400  
**Rationale**: Add top-level `# [MOCK_IMPLEMENTATION]` comment annotation, prepend `[MOCK_DATA]` to all 15 default option model names, and explicitly pass `is_mock=True`.

```python
# BEFORE (Lines 261-274 excerpt):
    def _load_default_catalog(self) -> dict[AssemblyStage, list[OptionCard]]:
        """Load default Evident/Olympus product catalog with plain Arabic prose and English technical specs."""
        return {
            AssemblyStage.FRAME: [
                OptionCard(
                    id="IX73",
                    stage=AssemblyStage.FRAME,
                    model_name="Olympus IX73",
                    ...

# AFTER (Lines 261-402 complete refactor):
    # [MOCK_IMPLEMENTATION]
    def _load_default_catalog(self) -> dict[AssemblyStage, list[OptionCard]]:
        """Load default Evident/Olympus product catalog with plain Arabic prose and English technical specs."""
        return {
            AssemblyStage.FRAME: [
                OptionCard(
                    id="IX73",
                    stage=AssemblyStage.FRAME,
                    model_name="[MOCK_DATA] Olympus IX73",
                    arabic_description="إطار مجهر مقلوب IX73 لتطبيقات الخلية الحية المتقدمة والكيمياء التخليقية",
                    english_specs={"ports": 2, "light_path": "inverted", "stand": "IX73P2F", "optical_standard": "UIS2", "parfocal_distance": 45.0, "thread_type": "RMS"},
                    price_tier="Research",
                    recommended=True,
                    is_mock=True,
                ),
                OptionCard(
                    id="BX53",
                    stage=AssemblyStage.FRAME,
                    model_name="[MOCK_DATA] Olympus BX53",
                    arabic_description="مجهر قائم BX53 للمختبرات الطبية والأبحاث النسيجية والفحص التشخيصي",
                    english_specs={"ports": 1, "light_path": "upright", "stand": "BX53F", "optical_standard": "UIS2", "parfocal_distance": 45.0, "thread_type": "RMS"},
                    price_tier="Research",
                    is_mock=True,
                ),
                OptionCard(
                    id="CX23",
                    stage=AssemblyStage.FRAME,
                    model_name="[MOCK_DATA] Olympus CX23",
                    arabic_description="مجهر بيولوجي CX23 تعليمي خفيف الوزن للمختبرات الجامعية والطلاب",
                    english_specs={"ports": 1, "light_path": "upright", "stand": "CX23LEDRFS2", "optical_standard": "UIS2", "parfocal_distance": 45.0, "thread_type": "RMS"},
                    price_tier="Entry",
                    is_mock=True,
                ),
            ],
            AssemblyStage.LIGHT_SOURCE: [
                OptionCard(
                    id="LED-ILL",
                    stage=AssemblyStage.LIGHT_SOURCE,
                    model_name="[MOCK_DATA] Transmitted LED Illuminator",
                    arabic_description="مصدر إضاءة LED نافذ عالي الكفاءة يدوم طويلاً وبحرارة لونية ثابتة",
                    english_specs={"type": "LED", "lifetime_hours": 20000, "color_temp": "5600K", "optical_standard": "UIS2", "power": "14W"},
                    price_tier="Mid-Range",
                    recommended=True,
                    is_mock=True,
                ),
                OptionCard(
                    id="HAL-100W",
                    stage=AssemblyStage.LIGHT_SOURCE,
                    model_name="[MOCK_DATA] 100W Halogen Light House",
                    arabic_description="مصدر إضاءة هالوجين 100 واط للتصوير عالي التباين والمجال المظلم",
                    english_specs={"type": "Halogen", "power": "100W", "voltage": "12V", "optical_standard": "UIS2"},
                    price_tier="Mid-Range",
                    is_mock=True,
                ),
                OptionCard(
                    id="FLU-LED",
                    stage=AssemblyStage.LIGHT_SOURCE,
                    model_name="[MOCK_DATA] TrueChrome LED Fluorescence Module",
                    arabic_description="وحدة إضاءة فلورية LED متعددة القنوات للفحص البيولوجي عالي الحساسية",
                    english_specs={"type": "Fluorescence LED", "channels": 4, "optical_standard": "UIS2"},
                    price_tier="Research",
                    is_mock=True,
                ),
            ],
            AssemblyStage.OBJECTIVES: [
                OptionCard(
                    id="UPLSAPO60XO",
                    stage=AssemblyStage.OBJECTIVES,
                    model_name="[MOCK_DATA] UPLSAPO 60XO",
                    arabic_description="عدسة شيئية عالية الدقة مغمورة بالزيت لتطبيقات الفلورة والتصوير الدقيق",
                    english_specs={"mag": "60X", "na": 1.42, "thread": "M25", "immersion": "oil", "parfocal_distance": 45.0, "optical_standard": "UIS2"},
                    price_tier="Premium",
                    recommended=True,
                    is_mock=True,
                ),
                OptionCard(
                    id="UPLSAPO10X",
                    stage=AssemblyStage.OBJECTIVES,
                    model_name="[MOCK_DATA] UPLSAPO 10X",
                    arabic_description="عدسة شيئية 10X واسعة المجال للتصوير المسحي والعمق البؤري الممتاز",
                    english_specs={"mag": "10X", "na": 0.40, "thread": "RMS", "parfocal_distance": 45.0, "optical_standard": "UIS2"},
                    price_tier="Research",
                    is_mock=True,
                ),
                OptionCard(
                    id="PLN4X",
                    stage=AssemblyStage.OBJECTIVES,
                    model_name="[MOCK_DATA] PLN 4X Plan Achromat",
                    arabic_description="عدسة شيئية 4X مسحية للمعاينة العامة للشرائح المختبرية",
                    english_specs={"mag": "4X", "na": 0.10, "thread": "RMS", "parfocal_distance": 45.0, "optical_standard": "UIS2"},
                    price_tier="Entry",
                    is_mock=True,
                ),
            ],
            AssemblyStage.CAMERA_ADAPTER: [
                OptionCard(
                    id="U-TV1X-2",
                    stage=AssemblyStage.CAMERA_ADAPTER,
                    model_name="[MOCK_DATA] U-TV1X-2",
                    arabic_description="محول كاميرا C-Mount بتكبير 1.0X مناسب للحساسات الكبيرة بدون تقشير حوافي",
                    english_specs={"mag": "1.0X", "mount": "C-Mount", "sensor_format": "1 inch", "optical_standard": "UIS2"},
                    price_tier="Mid-Range",
                    recommended=True,
                    is_mock=True,
                ),
                OptionCard(
                    id="U-TV0.63XC",
                    stage=AssemblyStage.CAMERA_ADAPTER,
                    model_name="[MOCK_DATA] U-TV0.63XC",
                    arabic_description="محول كاميرا 0.63X مخصص للحساسات متوسطة الحجم 2/3 بوصة",
                    english_specs={"mag": "0.63X", "mount": "C-Mount", "sensor_format": "2/3 inch", "optical_standard": "UIS2"},
                    price_tier="Mid-Range",
                    is_mock=True,
                ),
                OptionCard(
                    id="U-TV0.5XC-3",
                    stage=AssemblyStage.CAMERA_ADAPTER,
                    model_name="[MOCK_DATA] U-TV0.5XC-3",
                    arabic_description="محول كاميرا 0.5X مخصص للحساسات الصغيرة 1/2 بوصة",
                    english_specs={"mag": "0.5X", "mount": "C-Mount", "sensor_format": "1/2 inch", "optical_standard": "UIS2"},
                    price_tier="Entry",
                    is_mock=True,
                ),
            ],
            AssemblyStage.SOFTWARE: [
                OptionCard(
                    id="cellSens-Dim",
                    stage=AssemblyStage.SOFTWARE,
                    model_name="[MOCK_DATA] cellSens Dimension 3.2",
                    arabic_description="حزمة برمجية متقدمة للتصوير ثلاثي الأبعاد والتحليل التلقائي مع تحكم كامل بالقطع",
                    english_specs={"version": "3.2", "modules": ["3D", "Deconvolution", "Count & Measure"], "platform": "Windows"},
                    price_tier="Research",
                    recommended=True,
                    is_mock=True,
                ),
                OptionCard(
                    id="cellSens-Standard",
                    stage=AssemblyStage.SOFTWARE,
                    model_name="[MOCK_DATA] cellSens Standard 3.2",
                    arabic_description="برنامج قياسي لالتقاط الصور والقياسات الثنائية الأبعاد في المختبرات",
                    english_specs={"version": "3.2", "modules": ["2D Measure", "Time-lapse"], "platform": "Windows"},
                    price_tier="Mid-Range",
                    is_mock=True,
                ),
                OptionCard(
                    id="cellSens-Entry",
                    stage=AssemblyStage.SOFTWARE,
                    model_name="[MOCK_DATA] cellSens Entry 3.2",
                    arabic_description="برنامج تعليمي أساسي لالتقاط الصور البسيطة وحفظها",
                    english_specs={"version": "3.2", "modules": ["Basic Capture"], "platform": "Windows"},
                    price_tier="Entry",
                    is_mock=True,
                ),
            ],
        }
```

---

### 1.3 Database Component Loader `_merge_catalog_from_db()` (`src/engine/sequential_thinking.py:437-446`)

**Target Lines**: 437–446  
**Rationale**: Explicitly set `is_mock=False` for components loaded from SQLite database.

```python
# BEFORE (Lines 437-446):
                card = OptionCard(
                    id=comp_id,
                    stage=stage,
                    model_name=model_name,
                    arabic_description=ar_name or f"مكون {model_name}",
                    english_specs=en_specs,
                    price_tier="Research",
                    recommended=False,
                )

# AFTER (Lines 437-447):
                card = OptionCard(
                    id=comp_id,
                    stage=stage,
                    model_name=model_name,
                    arabic_description=ar_name or f"مكون {model_name}",
                    english_specs=en_specs,
                    price_tier="Research",
                    recommended=False,
                    is_mock=False,
                )
```

---

### 1.4 Stage Option Evaluator `evaluate_stage_options()` (`src/engine/sequential_thinking.py:509-519`)

**Target Lines**: 509–519  
**Rationale**: Preserve `is_mock` attribute when constructing `card_copy` for validated choices.

```python
# BEFORE (Lines 509-519):
            card_copy = OptionCard(
                id=card.id,
                stage=card.stage,
                model_name=card.model_name,
                arabic_description=card.arabic_description,
                english_specs=card.english_specs,
                price_tier=card.price_tier,
                optical_compatibility_status=is_compat,
                incompatibility_reason=reason,
                recommended=card.recommended,
            )

# AFTER (Lines 509-520):
            card_copy = OptionCard(
                id=card.id,
                stage=card.stage,
                model_name=card.model_name,
                arabic_description=card.arabic_description,
                english_specs=card.english_specs,
                price_tier=card.price_tier,
                optical_compatibility_status=is_compat,
                incompatibility_reason=reason,
                recommended=card.recommended,
                is_mock=getattr(card, "is_mock", True),
            )
```

---

## 2. CLI UI Formatter Refactoring Blueprint: `src/cli/formatter.py`

### 2.1 Rich UI Helper `render_bilingual_card()` (`src/cli/formatter.py:35-56`)

**Target Lines**: 35–57  
**Rationale**: Add `# [MOCK_IMPLEMENTATION]` comment and append `[MOCK_DATA]` badge to text output when `is_mock` is True.

```python
# BEFORE (Lines 35-56):
def render_bilingual_card(card: OptionCard | dict) -> str:
    """
    Render bilingual text representation of an OptionCard containing
    model name, Arabic description, and English technical specs.
    """
    if isinstance(card, dict):
        model_name = card.get("model_name", "Unknown Model")
        ...

# AFTER (Lines 35-58):
# [MOCK_IMPLEMENTATION]
def render_bilingual_card(card: OptionCard | dict) -> str:
    """
    Render bilingual text representation of an OptionCard containing
    model name, Arabic description, and English technical specs.
    """
    if isinstance(card, dict):
        model_name = card.get("model_name", "Unknown Model")
        ar_desc = card.get("arabic_description", card.get("arabic_name", ""))
        specs = card.get("english_specs", {})
        price_tier = card.get("price_tier", "Standard")
        compat = card.get("optical_compatibility_status", True)
        is_mock = card.get("is_mock", True)
    else:
        model_name = card.model_name
        ar_desc = card.arabic_description
        specs = card.english_specs
        price_tier = card.price_tier
        compat = card.optical_compatibility_status
        is_mock = getattr(card, "is_mock", True)

    specs_str = ", ".join(f"{k}: {v}" for k, v in specs.items()) if isinstance(specs, dict) else str(specs)
    status_str = "Compatible / متوافق" if compat else "Incompatible / غير متوافق"
    mock_str = " [MOCK_DATA]" if is_mock and "[MOCK_DATA]" not in model_name else ""

    return f"[{model_name}{mock_str}] ({price_tier})\nوصف: {ar_desc}\nSpecs: {specs_str}\nStatus: {status_str}"
```

---

### 2.2 RichFormatter Header `render_header()` (`src/cli/formatter.py:78-86`)

**Target Lines**: 78–86  
**Rationale**: Add `# [MOCK_IMPLEMENTATION]` annotation and render colorized `[bold yellow on black] [MOCK_DATA] [/bold yellow on black]` Rich badge.

```python
# BEFORE (Lines 78-86):
    def render_header(self) -> None:
        """Render main CLI application header banner."""
        title = Text("EVIDENT / OLYMPUS MICROSCOPY PRODUCT SPECIALIST AGENT", style="bold cyan")
        subtitle = Text("Interactive SequentialThinking HitL Engine (Clean-Slate Architecture)", style="italic dim white")

        content = Text.assemble(title, "\n", subtitle, justify="center")
        panel = Panel(content, box=DOUBLE, border_style="cyan", padding=(1, 2))
        self.console.print(panel)

# AFTER (Lines 78-88):
    # [MOCK_IMPLEMENTATION]
    def render_header(self) -> None:
        """Render main CLI application header banner with colorized MOCK_DATA indicator."""
        title = Text("EVIDENT / OLYMPUS MICROSCOPY PRODUCT SPECIALIST AGENT", style="bold cyan")
        subtitle = Text("Interactive SequentialThinking HitL Engine (Clean-Slate Architecture)", style="italic dim white")
        mock_badge = Text(" [MOCK_DATA] ", style="bold yellow on black")

        content = Text.assemble(title, "\n", subtitle, "\n", mock_badge, justify="center")
        panel = Panel(content, box=DOUBLE, border_style="cyan", padding=(1, 2))
        self.console.print(panel)
```

---

### 2.3 Option Card Panel Renderer `render_bilingual_option_card()` (`src/cli/formatter.py:101-150`)

**Target Lines**: 101–150  
**Rationale**: Inject colorized `[bold yellow on black] [MOCK_DATA] [/bold yellow on black]` badge whenever `is_mock` is True.

```python
# BEFORE (Lines 101-127 excerpt):
    def render_bilingual_option_card(self, card: OptionCard | dict, index: int = 1, is_selected: bool = False) -> Panel:
        """Construct rich Panel for an individual option card."""
        if isinstance(card, dict):
            model_name = card.get("model_name", "Unknown Model")
            ...
        escaped_model = escape(str(model_name))
        escaped_ar_desc = escape(str(ar_desc))
        escaped_tier = escape(str(price_tier))

        header = f"[bold cyan]Option #{index}: {escaped_model}[/bold cyan]"
        if recommended:
            header += " [bold green]★ RECOMMENDED / موصى به[/bold green]"

# AFTER (Lines 101-155 complete refactor):
    # [MOCK_IMPLEMENTATION]
    def render_bilingual_option_card(self, card: OptionCard | dict, index: int = 1, is_selected: bool = False) -> Panel:
        """Construct rich Panel for an individual option card."""
        if isinstance(card, dict):
            model_name = card.get("model_name", "Unknown Model")
            ar_desc = card.get("arabic_description", card.get("arabic_name", ""))
            specs = card.get("english_specs", {})
            price_tier = card.get("price_tier", "Standard")
            compat = card.get("optical_compatibility_status", True)
            incompat_reason = card.get("incompatibility_reason")
            recommended = card.get("recommended", False)
            is_mock = card.get("is_mock", True)
        else:
            model_name = card.model_name
            ar_desc = card.arabic_description
            specs = card.english_specs
            price_tier = card.price_tier
            compat = card.optical_compatibility_status
            incompat_reason = card.incompatibility_reason
            recommended = card.recommended
            is_mock = getattr(card, "is_mock", True)

        escaped_model = escape(str(model_name))
        escaped_ar_desc = escape(str(ar_desc))
        escaped_tier = escape(str(price_tier))

        header = f"[bold cyan]Option #{index}: {escaped_model}[/bold cyan]"
        if is_mock and "[MOCK_DATA]" not in model_name:
            header += " [bold yellow on black] [MOCK_DATA] [/bold yellow on black]"
        elif is_mock:
            header += " [bold yellow on black] MOCK [/bold yellow on black]"

        if recommended:
            header += " [bold green]★ RECOMMENDED / موصى به[/bold green]"

        tier_tag = f"[dim cyan][Tier: {escaped_tier}][/dim cyan]"
        ar_text = f"[bold white]التفاصيل بالعربية:[/bold white]\n[italic green]{escaped_ar_desc}[/italic green]"

        specs_items = []
        if isinstance(specs, dict):
            for k, v in specs.items():
                specs_items.append(f"  • [bold yellow]{escape(str(k))}:[/bold yellow] {escape(str(v))}")
            specs_formatted = "\n".join(specs_items)
        else:
            specs_formatted = f"  • {escape(str(specs))}"

        en_text = f"[bold white]English Technical Specifications:[/bold white]\n{specs_formatted}"

        if compat:
            status_tag = "[bold green]✓ Optical Compatibility Verified / متوافق بصرياً[/bold green]"
        else:
            incompat_msg = escape(str(incompat_reason)) if incompat_reason else 'Optical constraint violation'
            status_tag = f"[bold red]✗ Incompatible: {incompat_msg}[/bold red]"

        border = "green" if is_selected else ("cyan" if compat else "red")

        body = f"{header} {tier_tag}\n\n{ar_text}\n\n{en_text}\n\n{status_tag}"
        return Panel(body, box=ROUNDED, border_style=border, padding=(1, 2))
```

---

### 2.4 Assembly Summary Renderer `render_assembly_summary()` (`src/cli/formatter.py:158-193`)

**Target Lines**: 158–193  
**Rationale**: Inject colorized `[bold yellow on black] [MOCK_DATA] [/bold yellow on black]` badge in the Model column for mock components.

```python
# BEFORE (Lines 158-193):
    def render_assembly_summary(self, state: AssemblyState | dict) -> Table:
        """Render completed assembly configuration summary table."""
        ...
                    table.add_row(escape(stg_name), escape(str(model)), escape(str(ar_desc)), escape(str(specs_str)), "✓ Approved")

# AFTER (Lines 158-197):
    # [MOCK_IMPLEMENTATION]
    def render_assembly_summary(self, state: AssemblyState | dict) -> Table:
        """Render completed assembly configuration summary table."""
        table = Table(title="[bold green]FINAL OPTICAL MICROSCOPY ASSEMBLY SUMMARY / ملخص التجميع النهائي[/bold green]", box=ROUNDED, show_lines=True)
        table.add_column("Stage / المرحلة", style="bold yellow", justify="left")
        table.add_column("Model / الموديل", style="bold cyan", justify="left")
        table.add_column("Arabic Description / الوصف بالعربية", style="green", justify="left")
        table.add_column("Technical Specs / المواصفات الفنية", style="white", justify="left")
        table.add_column("Status / الحالة", style="bold green", justify="center")

        if isinstance(state, dict):
            components = state.get("components", {})
            if isinstance(components, dict):
                for stage_key, card_data in components.items():
                    try:
                        norm_stg = normalize_stage(stage_key)
                        stg_name = f"{norm_stg.display_name_ar}\n({norm_stg.display_name_en})"
                    except Exception:
                        stg_name = str(stage_key)

                    if isinstance(card_data, dict):
                        model = card_data.get("model_name", "N/A")
                        ar_desc = card_data.get("arabic_description", "N/A")
                        specs = card_data.get("english_specs", {})
                        specs_str = ", ".join(f"{k}:{v}" for k, v in specs.items()) if isinstance(specs, dict) else str(specs)
                        is_mock = card_data.get("is_mock", True)
                    else:
                        model = str(card_data)
                        ar_desc = "N/A"
                        specs_str = "N/A"
                        is_mock = True

                    model_display = f"{escape(str(model))}"
                    if is_mock and "[MOCK_DATA]" not in str(model):
                        model_display = f"[bold yellow on black] [MOCK_DATA] [/bold yellow on black] {model_display}"

                    table.add_row(escape(stg_name), model_display, escape(str(ar_desc)), escape(str(specs_str)), "✓ Approved")
        else:
            for stage, card in state.selected_components.items():
                stg_name = f"{stage.display_name_ar}\n({stage.display_name_en})"
                specs_str = ", ".join(f"{k}:{v}" for k, v in card.english_specs.items()) if isinstance(card.english_specs, dict) else str(card.english_specs)
                model_name = card.model_name
                is_mock = getattr(card, "is_mock", True)

                model_display = f"{escape(str(model_name))}"
                if is_mock and "[MOCK_DATA]" not in str(model_name):
                    model_display = f"[bold yellow on black] [MOCK_DATA] [/bold yellow on black] {model_display}"

                table.add_row(escape(stg_name), model_display, escape(str(card.arabic_description)), escape(str(specs_str)), "✓ Approved")

        self.console.print(table)
        return table
```

---

## 3. Documentation Registry Refactoring Blueprint: `docs/MOCK_REGISTRY.md`

### 3.1 Registry Alignment Table Update (`docs/MOCK_REGISTRY.md:15-32`)

**Target Lines**: 15–32  
**Rationale**: Update `Model Name` column values to match exact model names from `src/engine/sequential_thinking.py` (`[MOCK_DATA] Olympus IX73`, etc.).

```markdown
<!-- BEFORE (Lines 15-31 excerpt): -->
| Stage | Model Name | Spec Summary | Tag |
|---|---|---|---|
| `FRAME` | `Olympus IX73` | Inverted frame, 2 ports, UIS2 optical standard | `[MOCK_DATA]` |
| `FRAME` | `Olympus BX53` | Upright frame, 1 port, UIS2 optical standard | `[MOCK_DATA]` |
...

<!-- AFTER (Lines 15-32 complete table): -->
| Stage | Model Name | Spec Summary | Tag |
|---|---|---|---|
| `FRAME` | `[MOCK_DATA] Olympus IX73` | Inverted frame, 2 ports, UIS2 optical standard | `[MOCK_DATA]` |
| `FRAME` | `[MOCK_DATA] Olympus BX53` | Upright frame, 1 port, UIS2 optical standard | `[MOCK_DATA]` |
| `FRAME` | `[MOCK_DATA] Olympus CX23` | Educational upright frame, UIS2 optical standard | `[MOCK_DATA]` |
| `LIGHT_SOURCE` | `[MOCK_DATA] Transmitted LED Illuminator` | LED 14W, 5600K, 20,000h lifetime | `[MOCK_DATA]` |
| `LIGHT_SOURCE` | `[MOCK_DATA] 100W Halogen Light House` | Halogen 100W, 12V | `[MOCK_DATA]` |
| `LIGHT_SOURCE` | `[MOCK_DATA] TrueChrome LED Fluorescence Module` | 4-channel fluorescence LED module | `[MOCK_DATA]` |
| `OBJECTIVES` | `[MOCK_DATA] UPLSAPO 60XO` | 60X oil immersion, NA 1.42, M25 thread | `[MOCK_DATA]` |
| `OBJECTIVES` | `[MOCK_DATA] UPLSAPO 10X` | 10X dry, NA 0.40, RMS thread | `[MOCK_DATA]` |
| `OBJECTIVES` | `[MOCK_DATA] PLN 4X Plan Achromat` | 4X dry, NA 0.10, RMS thread | `[MOCK_DATA]` |
| `CAMERA_ADAPTER` | `[MOCK_DATA] U-TV1X-2` | C-Mount 1.0X adapter | `[MOCK_DATA]` |
| `CAMERA_ADAPTER` | `[MOCK_DATA] U-TV0.63XC` | C-Mount 0.63X adapter | `[MOCK_DATA]` |
| `CAMERA_ADAPTER` | `[MOCK_DATA] U-TV0.5XC-3` | C-Mount 0.5X adapter | `[MOCK_DATA]` |
| `SOFTWARE` | `[MOCK_DATA] cellSens Dimension 3.2` | 3D, Deconvolution, Count & Measure modules | `[MOCK_DATA]` |
| `SOFTWARE` | `[MOCK_DATA] cellSens Standard 3.2` | 2D Measure, Time-lapse modules | `[MOCK_DATA]` |
| `SOFTWARE` | `[MOCK_DATA] cellSens Entry 3.2` | Basic Capture module | `[MOCK_DATA]` |
```

---

## 4. Summary of Verification Test Impact

1. `tests/tier1_features/test_fi_r1_cli_and_engine.py`:
   - `test_fi_r1_1_cli_rich_ui_and_logging`: Executes CLI and verifies step progress string. Will continue to pass 100%.
   - `test_fi_r1_2_sequential_thinking_5_stages`: Verifies 5 assembly stages using `first_card.id`. Since `id` strings remain unmodified (e.g. `"IX73"`, `"LED-ILL"`), test will pass 100%.
   - `test_fi_r1_3_bilingual_presentation_and_hitl`: Checks `render_bilingual_card()` on sample card containing `"UPLSAPO 60XO"`. Will continue to pass 100%.

2. Integrity Verification (`grep -r "MOCK" src/`):
   - Before: 0 results
   - After: >= 18 results (15 option model names, `OptionCard.is_mock` attribute, `# [MOCK_IMPLEMENTATION]` comments, and Rich UI badge formatting).
