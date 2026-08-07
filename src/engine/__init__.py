"""
SequentialThinking Engine Package.
Implements the 5-stage optical assembly state machine and domain exceptions.
"""

from src.engine.sequential_thinking import (
    AssemblyStage,
    OptionCard,
    StageResult,
    AssemblyState,
    SequentialThinkingEngine,
    OlympusSpecialistError,
    EngineError,
    InvalidStageError,
    IncompatibleComponentError,
)

__all__ = [
    "AssemblyStage",
    "OptionCard",
    "StageResult",
    "AssemblyState",
    "SequentialThinkingEngine",
    "OlympusSpecialistError",
    "EngineError",
    "InvalidStageError",
    "IncompatibleComponentError",
]
