"""
SequentialThinking Engine for Evident/Olympus Microscopy Product Assembly.
Implements the 5-stage state machine: FRAME -> LIGHT_SOURCE -> OBJECTIVES -> CAMERA_ADAPTER -> SOFTWARE.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
import json
import os
import sqlite3
from typing import Any, Callable
import uuid


class OlympusSpecialistError(Exception):
    """Base exception for all domain errors in olympus-product-specialist."""


class EngineError(OlympusSpecialistError):
    """Errors occurring within SequentialThinking engine."""


class InvalidStageError(EngineError):
    """Raised when an out-of-order or invalid stage transition is requested."""


class InvalidStageTransitionError(InvalidStageError):
    """Raised when an out-of-order stage transition is requested."""


class IncompatibleComponentError(EngineError):
    """Raised when selected component violates optical compatibility rules."""


class CLIUIError(OlympusSpecialistError):
    """Errors occurring within CLI presentation or HitL handler."""


class UserCancelledError(CLIUIError):
    """Raised when user cancels session at HitL prompt."""


class AssemblyStage(StrEnum):
    """5-stage optical assembly sequence."""
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


STAGE_ORDER = [
    AssemblyStage.FRAME,
    AssemblyStage.LIGHT_SOURCE,
    AssemblyStage.OBJECTIVES,
    AssemblyStage.CAMERA_ADAPTER,
    AssemblyStage.SOFTWARE,
]


def _make_json_serializable(obj: Any) -> Any:
    """Recursively convert non-primitive types (sets, enums, dates, uuids) to JSON serializable objects."""
    if isinstance(obj, (set, tuple)):
        return [_make_json_serializable(item) for item in obj]
    if isinstance(obj, dict):
        return {str(k): _make_json_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_make_json_serializable(item) for item in obj]
    if hasattr(obj, "value"):
        return obj.value
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, uuid.UUID):
        return str(obj)
    return obj


def normalize_stage(stage_input: str | AssemblyStage) -> AssemblyStage:
    """Normalize string or enum input to an AssemblyStage enum member."""
    if isinstance(stage_input, AssemblyStage):
        return stage_input
    val = str(stage_input).lower().strip()
    if val in ("objective", "objectives"):
        return AssemblyStage.OBJECTIVES
    for s in AssemblyStage:
        if s.value == val:
            return s
    raise InvalidStageError(f"Unknown assembly stage: {stage_input}")


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

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)


@dataclass(slots=True, kw_only=True)
class StageResult:
    """Output payload from evaluating or completing an assembly stage step."""
    stage: str
    stage_index: int
    total_stages: int = 5
    choices: list[OptionCard] = field(default_factory=list)
    selected_option: OptionCard | None = None
    prompt_ar: str = ""
    prompt_en: str = ""
    requires_hitl: bool = True
    is_completed: bool = False
    validation_messages: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage,
            "stage_index": self.stage_index,
            "total_stages": self.total_stages,
            "choices": [c.to_dict() if hasattr(c, 'to_dict') else c for c in self.choices],
            "selected_option": self.selected_option.to_dict() if self.selected_option and hasattr(self.selected_option, 'to_dict') else self.selected_option,
            "prompt_ar": self.prompt_ar,
            "prompt_en": self.prompt_en,
            "requires_hitl": self.requires_hitl,
            "is_completed": self.is_completed,
            "validation_messages": self.validation_messages,
        }

    def __getitem__(self, key: str) -> Any:
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(key)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)


@dataclass(slots=True, kw_only=True)
class AssemblyState:
    """Session state tracker across the full 5-stage assembly workflow."""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    current_stage: AssemblyStage = AssemblyStage.FRAME
    selected_components: dict[AssemblyStage, OptionCard] = field(default_factory=dict)
    history: list[StageResult] = field(default_factory=list)
    is_complete: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_selection(self, stage: AssemblyStage | str, option: OptionCard) -> None:
        stg = normalize_stage(stage)
        if stg in self.selected_components:
            del self.selected_components[stg]
        self.selected_components[stg] = option
        self.updated_at = datetime.now(timezone.utc)
        if len(self.selected_components) == 5:
            self.is_complete = True

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
        summary_raw = {
            "session_id": self.session_id,
            "is_complete": self.is_complete,
            "components_count": len(self.selected_components),
            "components": {
                stg.value: card.to_dict()
                for stg, card in self.selected_components.items()
            },
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
        return _make_json_serializable(summary_raw)


class SequentialThinkingEngine:
    """
    Protocol engine managing the 5-stage optical microscopy assembly state machine.
    Evaluates optical compatibility and enforces Human-in-the-Loop approval requirements.
    """

    def __init__(
        self,
        db_path: str | None = None,
        initial_catalog: dict[AssemblyStage, list[OptionCard]] | None = None
    ) -> None:
        self.db_path = db_path
        self.state = AssemblyState()
        self.catalog = initial_catalog if initial_catalog is not None else self._load_default_catalog()

        if self.db_path and os.path.exists(self.db_path):
            self._merge_catalog_from_db(self.db_path)

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

    def _merge_catalog_from_db(self, db_path: str) -> None:
        """Query components table from SQLite database and merge into engine catalog."""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, model_name, category, thread_type, parfocal_distance, sensor_format, optical_standard, arabic_name, english_specs
                FROM components
            """)
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                comp_id, model_name, category, thread_type, parfocal, sensor_fmt, opt_std, ar_name, en_specs_raw = row
                try:
                    stage = normalize_stage(category)
                except InvalidStageError:
                    continue

                en_specs = {}
                if en_specs_raw:
                    try:
                        en_specs = json.loads(en_specs_raw)
                    except Exception:
                        en_specs = {"raw": en_specs_raw}

                if thread_type and "thread" not in en_specs:
                    en_specs["thread"] = thread_type
                if parfocal and "parfocal_distance" not in en_specs:
                    en_specs["parfocal_distance"] = parfocal
                if sensor_fmt and "sensor_format" not in en_specs:
                    en_specs["sensor_format"] = sensor_fmt
                if opt_std and "optical_standard" not in en_specs:
                    en_specs["optical_standard"] = opt_std

                existing_ids = [c.id for c in self.catalog[stage]]
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

                if comp_id in existing_ids:
                    # Update existing card
                    for idx, c in enumerate(self.catalog[stage]):
                        if c.id == comp_id:
                            self.catalog[stage][idx] = card
                            break
                else:
                    self.catalog[stage].insert(0, card)

        except Exception:
            pass  # Fall back gracefully to built-in default catalog

    def get_current_stage(self) -> AssemblyStage:
        return self.state.current_stage

    def validate_component_compatibility(
        self,
        option: OptionCard | dict,
        current_config: dict[str, Any] | None = None
    ) -> tuple[bool, str | None]:
        """Validate optical compatibility of a component against current assembly configuration."""
        specs = option.get("english_specs", {}) if isinstance(option, dict) else option.english_specs
        current = current_config or {}

        # Optical standard check
        opt_std = specs.get("optical_standard", "UIS2")
        if opt_std != "UIS2":
            return False, f"Optical standard '{opt_std}' is incompatible with Olympus UIS2 standard."

        return True, None

    def _validate_stage_sequence(
        self,
        target_stage: AssemblyStage,
        current_config: dict[str, Any] | None = None
    ) -> None:
        """Enforce sequential stage transitions in order defined by STAGE_ORDER."""
        dependencies = {
            AssemblyStage.FRAME: [],
            AssemblyStage.LIGHT_SOURCE: [AssemblyStage.FRAME],
            AssemblyStage.OBJECTIVES: [AssemblyStage.FRAME],
            AssemblyStage.CAMERA_ADAPTER: [AssemblyStage.FRAME],
            AssemblyStage.SOFTWARE: [AssemblyStage.FRAME],
        }
        cfg = current_config or {}
        for prev_stage in dependencies.get(target_stage, []):
            in_state = prev_stage in self.state.selected_components
            in_config = prev_stage.value in cfg or prev_stage in cfg
            if not (in_state or in_config):
                raise InvalidStageTransitionError(
                    f"Cannot transition to stage '{target_stage.value}' before completing required stage '{prev_stage.value}'."
                )

    def evaluate_stage_options(
        self,
        stage: str | AssemblyStage,
        current_config: dict[str, Any] | None = None
    ) -> StageResult:
        """Evaluate available option cards for a specified stage step."""
        norm_stage = normalize_stage(stage)
        self._validate_stage_sequence(norm_stage, current_config)
        self.state.current_stage = norm_stage

        choices = self.catalog.get(norm_stage, [])
        validated_choices: list[OptionCard] = []

        for card in choices:
            is_compat, reason = self.validate_component_compatibility(card, current_config)
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
            validated_choices.append(card_copy)

        prompt_ar = f"يرجى تحديد ومراجعة الخيارات المتاحة لمرحلة: {norm_stage.display_name_ar}"
        prompt_en = f"Please evaluate and approve the choice for stage: {norm_stage.display_name_en}"

        stage_res = StageResult(
            stage=norm_stage.value,
            stage_index=norm_stage.step_number,
            total_stages=5,
            choices=validated_choices,
            prompt_ar=prompt_ar,
            prompt_en=prompt_en,
            requires_hitl=True,
            is_completed=False,
        )

        return stage_res

    def step(
        self,
        stage: str | AssemblyStage,
        current_config: dict[str, Any] | None = None
    ) -> StageResult:
        """
        Primary engine interface contract step(stage, current_config).
        Evaluates stage choices and returns StageResult payload.
        """
        return self.evaluate_stage_options(stage, current_config)

    def select_option(
        self,
        stage: str | AssemblyStage,
        option_id: str
    ) -> StageResult:
        """Commit a selected option for a given assembly stage into the session state."""
        norm_stage = normalize_stage(stage)
        self._validate_stage_sequence(norm_stage)
        choices = self.catalog.get(norm_stage, [])

        selected_card = None
        for card in choices:
            if card.id == option_id:
                selected_card = card
                break

        if not selected_card:
            raise EngineError(f"Option '{option_id}' not found in stage '{norm_stage.value}' catalog.")

        is_compat, reason = self.validate_component_compatibility(selected_card)
        if not is_compat:
            raise IncompatibleComponentError(f"Component '{option_id}' is incompatible: {reason}")

        self.state.add_selection(norm_stage, selected_card)

        result = StageResult(
            stage=norm_stage.value,
            stage_index=norm_stage.step_number,
            total_stages=5,
            choices=choices,
            selected_option=selected_card,
            prompt_ar=f"تم تأكيد اختيار {selected_card.model_name}",
            prompt_en=f"Confirmed selection: {selected_card.model_name}",
            requires_hitl=False,
            is_completed=True,
        )
        self.state.history.append(result)
        return result

    def can_proceed(self) -> bool:
        """Check if session is complete."""
        return len(self.state.selected_components) == 5

    def reset(self) -> None:
        """Reset assembly state session."""
        self.state = AssemblyState()
