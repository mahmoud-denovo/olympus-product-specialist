"""
Human-in-the-Loop (HitL) Interactive Approval Handler module.
Halts execution at each optical assembly stage to present comparative choices and request user approval.
"""

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Callable
from rich.console import Console

from src.engine.sequential_thinking import OptionCard, StageResult, AssemblyState


class HITLDecision(StrEnum):
    """User decision enum for HitL stage approval."""
    ACCEPT = "y"
    DECLINE = "n"
    EDIT = "edit"
    DETAILS = "details"
    HELP = "help"


@dataclass(slots=True, kw_only=True)
class HITLResponse:
    """Dataclass holding response payload from a HitL prompt."""
    decision: HITLDecision
    selected_option_id: str | None = None
    custom_edits: dict[str, Any] | None = None
    raw_input: str = ""


class HITLHandler:
    """
    Interactive prompt handler for user approval, option selection, and stage edits.
    Supports interactive console inputs as well as automated non-interactive fallback choices.
    """

    def __init__(
        self,
        console: Console | None = None,
        input_func: Callable[[str], str] | None = None,
        non_interactive: bool = False
    ) -> None:
        self.console = console or Console()
        self._input_func = input_func or input
        self.non_interactive = non_interactive

    def request_approval(
        self,
        card: OptionCard | dict,
        user_input_func: Callable[[], str] | None = None
    ) -> bool:
        """
        Request explicit approval for a specific component card [y/N/edit].
        Returns True if approved, False otherwise.
        """
        if self.non_interactive:
            return True

        if user_input_func is not None:
            raw = user_input_func()
        else:
            try:
                raw = self._input_func("\n[HitL] Approve configuration choice? (y/n/edit) [y]: ")
            except (EOFError, KeyboardInterrupt):
                return False

        val = raw.lower().strip()
        if not val or val in ("y", "yes", "نعم", "1", "true"):
            return True
        return False

    def prompt_stage_approval(
        self,
        stage_result: StageResult | dict,
        user_input_func: Callable[[], str] | None = None
    ) -> HITLResponse:
        """
        Prompt user to approve, decline, or request edit for a stage result.
        """
        choices = stage_result.choices if hasattr(stage_result, "choices") else stage_result.get("choices", [])
        first_id = choices[0].id if choices and hasattr(choices[0], "id") else (choices[0].get("id") if choices and isinstance(choices[0], dict) else None)

        if self.non_interactive:
            if not choices:
                return HITLResponse(decision=HITLDecision.DECLINE, selected_option_id=None, raw_input="n")
            return HITLResponse(decision=HITLDecision.ACCEPT, selected_option_id=first_id, raw_input="y")

        if user_input_func is not None:
            raw = user_input_func()
        else:
            try:
                raw = self._input_func("\n[HitL] Approve recommended component selection? [y/N/edit]: ")
            except (EOFError, KeyboardInterrupt):
                return HITLResponse(decision=HITLDecision.DECLINE, raw_input="n")

        val = raw.lower().strip()
        if val in ("y", "yes", "نعم", "1", "true"):
            return HITLResponse(decision=HITLDecision.ACCEPT, selected_option_id=first_id, raw_input=raw)
        elif val in ("edit", "e", "تعديل", "3"):
            return HITLResponse(decision=HITLDecision.EDIT, raw_input=raw)
        elif val in ("details", "d", "تفاصيل", "4"):
            return HITLResponse(decision=HITLDecision.DETAILS, raw_input=raw)
        elif val in ("help", "h", "مساعدة", "5"):
            return HITLResponse(decision=HITLDecision.HELP, raw_input=raw)
        elif val in ("n", "no", "لا", "0", "false", ""):
            return HITLResponse(decision=HITLDecision.DECLINE, raw_input=raw)
        else:
            return HITLResponse(decision=HITLDecision.DECLINE, raw_input=raw)

    def prompt_option_selection(
        self,
        choices: list[OptionCard | dict],
        user_input_func: Callable[[], str] | None = None
    ) -> OptionCard | dict | None:
        """
        Prompt user to select a component option from available choices by index.
        """
        if not choices:
            return None

        if self.non_interactive:
            return choices[0]

        if user_input_func is not None:
            raw = user_input_func()
        else:
            try:
                raw = self._input_func(f"\nSelect option index [1-{len(choices)}]: ")
            except (EOFError, KeyboardInterrupt):
                return choices[0]

        try:
            idx = int(raw.strip()) - 1
            if 0 <= idx < len(choices):
                return choices[idx]
        except ValueError:
            pass

        return choices[0]


# Alias for backward compatibility
HitLHandler = HITLHandler
