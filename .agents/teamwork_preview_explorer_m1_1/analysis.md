# Milestone M1 Architecture & Technical Design Document
**Project**: `olympus-product-specialist`
**Milestone**: M1 (Interactive CLI & SequentialThinking HitL Engine)
**Author**: Explorer 1
**Target Directory**: `src/cli/` and `src/engine/`

---

## 1. Executive Summary & Architectural Scope

Milestone M1 establishes the interactive core of the `olympus-product-specialist` agent. It provides a non-technical sales/logistics user experience while enforcing strict optical configuration rules for Evident/Olympus microscopy products.

### Core Architectural Principles:
1. **Native `SequentialThinking` Engine**: Enforces a strict 5-stage sequential optical assembly pipeline:
   - **Stage 1**: `FRAME` (Microscope Frame / Body)
   - **Stage 2**: `LIGHT_SOURCE` (Illuminator / Lamp)
   - **Stage 3**: `OBJECTIVES` (Optical Lenses & Revolving Nosepiece)
   - **Stage 4**: `CAMERA_ADAPTER` (C-Mount / TV Adapter & Mount)
   - **Stage 5**: `SOFTWARE` (Imaging & Analysis Suite)
2. **Bilingual Optical Cards**: Renders component choices in dual-language format: plain, accessible Arabic prose explaining domain suitability alongside precise English technical specs.
3. **Human-in-the-Loop (HitL) Interactive Handler**: Halts execution at each optical assembly step to present comparative options and require explicit confirmation (`[y/N/edit]`).
4. **Clean-Slate Python 3.14 Architecture**: Designed from scratch using modern Python type annotations (`dict[str, Any]`, `str | None`), `@dataclass(slots=True, kw_only=True)`, and zero legacy boilerplate.

---

## 2. Component Design & Sequence Flow

```
┌────────────────────────────────────────────────────────────────────────┐
│                              src/cli/main.py                           │
│                      (CLI Parser & Main Loop Controller)               │
└───────────┬──────────────────────────┬───────────────────────┬─────────┘
            │                          │                       │
            ▼                          ▼                       ▼
┌───────────────────────┐  ┌───────────────────────┐  ┌───────────────────────┐
│   src/cli/formatter   │  │    src/cli/hitl.py   │  │src/engine/sequential  │
│   (Rich UI Renderer)  │  │(HitL Approval Handler)│  │ _thinking.py (Engine) │
└───────────────────────┘  └───────────────────────┘  └───────────────────────┘
```

### Execution Sequence:
1. `main.py` parses CLI arguments (`--interactive`, `--export-json`, `--verbose`).
2. `SequentialThinkingEngine` initializes the `AssemblyState` session with 5 stages.
3. For each stage (1 to 5):
   a. Engine retrieves compatible `OptionCard` candidates via `evaluate_stage_options()`.
   b. `RichFormatter` displays the stage header, progress indicator, and bilingual cards.
   c. `HITLHandler` prompts the user for approval (`[y/N/edit]`).
   d. On approval (`y`), `SequentialThinkingEngine.step()` commits the selection into `AssemblyState`.
   e. On `edit`, `HITLHandler` presents option selection or parameter adjustment.
   f. On `n`, user can opt to retreat one stage or abort session cleanly.
4. After Stage 5, `RichFormatter` renders the final `AssemblySummary` table and export artifacts.

---

## 3. Concrete Data Models & Type Specifications

### 3.1 `AssemblyStage` Enum
Defines the strict 5-stage order for optical microscope configuration.

```python
from enum import StrEnum

class AssemblyStage(StrEnum):
    FRAME = "frame"
    LIGHT_SOURCE = "light_source"
    OBJECTIVES = "objectives"
    CAMERA_ADAPTER = "camera_adapter"
    SOFTWARE = "software"

    @property
    def display_name_ar(self) -> str:
        names = {
            AssemblyStage.FRAME: "هيكل المجهر (Frame)",
            AssemblyStage.LIGHT_SOURCE: "مصدر الإضاءة (Light Source)",
            AssemblyStage.OBJECTIVES: "العدسات الشيئية (Objectives)",
            AssemblyStage.CAMERA_ADAPTER: "محول الكاميرا (Camera Adapter)",
            AssemblyStage.SOFTWARE: "برنامج التحليل والتقاط الصور (Software)",
        }
        return names[self]

    @property
    def display_name_en(self) -> str:
        names = {
            AssemblyStage.FRAME: "Microscope Frame / Body",
            AssemblyStage.LIGHT_SOURCE: "Illuminator / Light Source",
            AssemblyStage.OBJECTIVES: "Optical Objectives & Nosepiece",
            AssemblyStage.CAMERA_ADAPTER: "C-Mount / TV Camera Adapter",
            AssemblyStage.SOFTWARE: "Imaging & Analysis Software Suite",
        }
        return names[self]

    @property
    def step_number(self) -> int:
        order = [
            AssemblyStage.FRAME,
            AssemblyStage.LIGHT_SOURCE,
            AssemblyStage.OBJECTIVES,
            AssemblyStage.CAMERA_ADAPTER,
            AssemblyStage.SOFTWARE,
        ]
        return order.index(self) + 1
```

### 3.2 `OptionCard` Data Model
Represents a single hardware/software component candidate presented to the user.

```python
from dataclasses import dataclass, field
from typing import Any

@dataclass(slots=True, kw_only=True)
class OptionCard:
    id: str
    stage: AssemblyStage
    model_name: str
    arabic_description: str
    english_specs: dict[str, Any]
    price_tier: str  # e.g., "Entry", "Mid-Range", "Research", "Industrial"
    optical_compatibility_status: bool = True
    incompatibility_reason: str | None = None
    recommended: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "stage": self.stage.value,
            "model_name": self.model_name,
            "arabic_description": self.arabic_description,
            "english_specs": self.english_specs,
            "price_tier": self.price_tier,
            "optical_compatibility_status": self.optical_compatibility_status,
            "incompatibility_reason": self.incompatibility_reason,
            "recommended": self.recommended,
        }
```

### 3.3 `StageResult` Data Model
Output payload from evaluating or completing a stage step.

```python
@dataclass(slots=True, kw_only=True)
class StageResult:
    stage: AssemblyStage
    stage_index: int
    total_stages: int = 5
    choices: list[OptionCard] = field(default_factory=list)
    selected_option: OptionCard | None = None
    prompt_ar: str
    prompt_en: str
    requires_hitl: bool = True
    is_completed: bool = False
    validation_messages: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage.value,
            "stage_index": self.stage_index,
            "total_stages": self.total_stages,
            "choices": [c.to_dict() for c in self.choices],
            "selected_option": self.selected_option.to_dict() if self.selected_option else None,
            "prompt_ar": self.prompt_ar,
            "prompt_en": self.prompt_en,
            "requires_hitl": self.requires_hitl,
            "is_completed": self.is_completed,
            "validation_messages": self.validation_messages,
        }
```

### 3.4 `AssemblyState` Data Model
Tracks state across the full 5-stage workflow session.

```python
from datetime import datetime, timezone
import uuid

@dataclass(slots=True, kw_only=True)
class AssemblyState:
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    current_stage: AssemblyStage = AssemblyStage.FRAME
    selected_components: dict[AssemblyStage, OptionCard] = field(default_factory=dict)
    history: list[StageResult] = field(default_factory=list)
    is_complete: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_selection(self, stage: AssemblyStage, option: OptionCard) -> None:
        self.selected_components[stage] = option
        self.updated_at = datetime.now(timezone.utc)

    def undo_last_stage(self) -> AssemblyStage | None:
        if not self.selected_components:
            return None
        last_stage = list(self.selected_components.keys())[-1]
        del self.selected_components[last_stage]
        self.current_stage = last_stage
        self.is_complete = False
        self.updated_at = datetime.now(timezone.utc)
        return last_stage

    def get_summary(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "is_complete": self.is_complete,
            "components_count": len(self.selected_components),
            "components": {
                stage.value: card.to_dict()
                for stage, card in self.selected_components.items()
            },
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
```

---

## 4. Detailed Module Architecture & Signatures

### 4.1 `src/engine/sequential_thinking.py`

**Purpose**: Protocol engine implementing the 5-stage optical microscopy assembly logic.

```python
class SequentialThinkingEngine:
    """
    Core engine managing the sequential 5-stage optical microscopy assembly.
    Implements rule validation across optical standards (UIS2, thread sizing, magnification).
    """

    def __init__(self, initial_catalog: dict[AssemblyStage, list[OptionCard]] | None = None) -> None:
        self.state = AssemblyState()
        self.catalog = initial_catalog or self._load_default_catalog()

    def get_current_stage(self) -> AssemblyStage: ...
    def evaluate_stage_options(self, stage: AssemblyStage) -> StageResult: ...
    def step(self, stage: AssemblyStage, current_config: dict[str, Any] | None = None) -> StageResult: ...
    def select_option(self, stage: AssemblyStage, option_id: str) -> StageResult: ...
    def validate_component_compatibility(self, option: OptionCard) -> tuple[bool, str | None]: ...
    def can_proceed(self) -> bool: ...
    def reset(self) -> None: ...
    def _load_default_catalog(self) -> dict[AssemblyStage, list[OptionCard]]: ...
```

#### Optical Compatibility Rules Evaluated:
- **Thread Standard**: Verify UIS2 objective thread compatibility (RMS vs M25 vs M32).
- **Light Path**: Match frame illuminator port with light source type (LED Transmitted vs Fluorescent Mercury vs Halogen).
- **Camera Sensor Coupling**: Validate C-Mount magnification factor (0.5X vs 0.63X vs 1.0X) against camera sensor size (1/2", 2/3", 1.1") to prevent optical vignetting.
- **Software License**: Ensure software module supports motorized stage/camera options selected.

---

### 4.2 `src/cli/hitl.py`

**Purpose**: Human-in-the-Loop interactive prompt handler.

```python
from enum import StrEnum

class HITLDecision(StrEnum):
    ACCEPT = "y"
    DECLINE = "n"
    EDIT = "edit"
    DETAILS = "details"
    HELP = "help"

@dataclass(slots=True, kw_only=True)
class HITLResponse:
    decision: HITLDecision
    selected_option_id: str | None = None
    custom_edits: dict[str, Any] | None = None
    raw_input: str = ""

class HITLHandler:
    """
    Interactive prompt handler for user approval, choices, and configuration edits.
    """

    def __init__(self, console: Console | None = None, input_func: Callable[[str], str] | None = None) -> None:
        self.console = console or Console()
        self._input_func = input_func or input

    def prompt_stage_approval(self, stage_result: StageResult) -> HITLResponse: ...
    def prompt_option_selection(self, choices: list[OptionCard]) -> OptionCard: ...
    def prompt_edit_stage(self, stage_result: StageResult) -> dict[str, Any]: ...
    def confirm_assembly_completion(self, state: AssemblyState) -> bool: ...
```

---

### 4.3 `src/cli/formatter.py`

**Purpose**: Rich UI rendering engine for bilingual cards, step spinners, progress bars, and assembly summaries.

```python
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

class RichFormatter:
    """
    Renders rich UI visual elements, progress indicators, bilingual cards, and summary reports.
    """

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()

    def render_header(self) -> None: ...
    def render_stage_progress(self, current_stage: AssemblyStage, stage_idx: int, total_stages: int = 5) -> None: ...
    def render_bilingual_option_card(self, card: OptionCard, index: int, is_selected: bool = False) -> Panel: ...
    def render_option_grid(self, cards: list[OptionCard]) -> None: ...
    def render_assembly_summary(self, state: AssemblyState) -> Table | Panel: ...
    def render_error(self, title: str, message: str) -> None: ...
    def render_info(self, title: str, message: str) -> None: ...
```

---

### 4.4 `src/cli/main.py`

**Purpose**: Executable CLI entrypoint and main workflow controller.

```python
import argparse

def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="olympus-specialist",
        description="Evident/Olympus Interactive Microscopy Product Specialist CLI",
    )
    parser.add_argument("--interactive", "-i", action="store_true", default=True, help="Run in interactive HitL mode")
    parser.add_argument("--export-json", "-e", type=str, default=None, help="Export final assembly JSON to file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose debug logging")
    parser.add_argument("--no-color", action="store_true", help="Disable colored terminal output")
    return parser.parse_args(args)

def run_cli_session(args: argparse.Namespace) -> int:
    """
    Orchestrates the 5-stage sequential assembly loop.
    Returns 0 on success, non-zero on failure or cancellation.
    """
    ...

def main() -> None:
    ...
```

---

## 5. Exception Handling Strategy

All domain exceptions derive from `OlympusSpecialistError`.

```
OlympusSpecialistError (Base Exception)
├── EngineError
│   ├── InvalidStageError
│   ├── IncompatibleComponentError
│   └── StageExecutionError
└── CLIUIError
    ├── UserCancelledError
    ├── InvalidInputError
    └── FormattingError
```

```python
class OlympusSpecialistError(Exception):
    """Base exception for all domain errors in olympus-product-specialist."""

class EngineError(OlympusSpecialistError):
    """Errors occurring within SequentialThinking engine."""

class InvalidStageError(EngineError):
    """Raised when an out-of-order or invalid stage transition is requested."""

class IncompatibleComponentError(EngineError):
    """Raised when selected component violates optical compatibility rules."""

class CLIUIError(OlympusSpecialistError):
    """Errors occurring within CLI presentation or HitL handler."""

class UserCancelledError(CLIUIError):
    """Raised when user cancels session at HitL prompt."""
```

---

## 6. Clean-Slate Compliance & Anti-Pattern Avoidance Matrix

| Legacy Anti-Pattern (Workspace) | Modern Clean-Slate Architecture (M1) |
|----------------------------------|-------------------------------------|
| Loose string dictionaries for optical components | `@dataclass(slots=True, kw_only=True)` with explicit `OptionCard` models |
| Unstructured print statements | `rich.console.Console` and `RichFormatter` structured UI components |
| Manual stage indexing & string checks | `AssemblyStage(StrEnum)` with explicit ordering and bilingual metadata |
| Global mutable state variables | Immutable `AssemblyState` instances tracked per session |
| Monolithic giant functions | Separated concerns across `main.py`, `formatter.py`, `hitl.py`, and `sequential_thinking.py` |

---

## 7. Next Steps for Implementer 1
- Create `src/__init__.py`, `src/cli/__init__.py`, `src/engine/__init__.py`.
- Implement `src/engine/sequential_thinking.py` with default Evident catalog cards (BX53, IX73, CX23, LED, Objectives, C-Mount, cellSens).
- Implement `src/cli/formatter.py` using `rich`.
- Implement `src/cli/hitl.py` with standard `[y/N/edit]` prompts.
- Implement `src/cli/main.py` entrypoint.
- Write unit & integration tests under `tests/tier1_features/test_m1_cli_engine.py`.
