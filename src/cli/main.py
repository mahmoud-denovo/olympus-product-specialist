"""
CLI Entrypoint module for Evident/Olympus Product Specialist Agent.
Orchestrates the 5-stage SequentialThinking HitL assembly workflow.
"""

import argparse
import json
import sys
from typing import Sequence

from rich.console import Console

from src.engine.sequential_thinking import (
    AssemblyStage,
    SequentialThinkingEngine,
    OlympusSpecialistError,
)
from src.cli.formatter import RichFormatter
from src.cli.hitl import HITLHandler, HITLDecision


def parse_args(args: Sequence[str] | None = None) -> argparse.Namespace:
    """
    Parse command line arguments for the Olympus Product Specialist CLI agent.
    """
    parser = argparse.ArgumentParser(
        prog="olympus-specialist",
        description="Evident/Olympus Interactive Microscopy Product Specialist CLI",
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        default=True,
        help="Run in interactive Human-in-the-Loop mode (default)"
    )
    parser.add_argument(
        "--non-interactive", "-n",
        action="store_true",
        default=False,
        help="Run in automated non-interactive mode selecting default choices"
    )
    parser.add_argument(
        "--export-json", "-e",
        type=str,
        default=None,
        help="Export final microscopy assembly configuration JSON to target file path"
    )
    parser.add_argument(
        "--db-path",
        type=str,
        default=None,
        help="Path to SQLite Knowledge Graph database"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored terminal output"
    )
    return parser.parse_args(args)


def run_cli(args: Sequence[str] | None = None) -> int:
    """
    Main CLI workflow controller orchestrating the 5-stage optical assembly session.
    Returns 0 on success, non-zero on failure or cancellation.
    """
    try:
        parsed_args = parse_args(args)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 0

    console = Console(no_color=parsed_args.no_color)
    formatter = RichFormatter(console=console)
    is_non_interactive = parsed_args.non_interactive

    engine = SequentialThinkingEngine(db_path=parsed_args.db_path)
    hitl = HITLHandler(console=console, non_interactive=is_non_interactive)

    formatter.render_header()

    stages = [
        AssemblyStage.FRAME,
        AssemblyStage.LIGHT_SOURCE,
        AssemblyStage.OBJECTIVES,
        AssemblyStage.CAMERA_ADAPTER,
        AssemblyStage.SOFTWARE,
    ]

    current_config = {}
    step_idx = 0

    while step_idx < len(stages):
        stage = stages[step_idx]
        try:
            stage_res = engine.step(stage=stage, current_config=current_config)

            formatter.render_stage_progress(stage, stage.step_number, 5)
            formatter.render_option_grid(stage_res.choices)

            if is_non_interactive:
                if not stage_res.choices:
                    formatter.render_error("Assembly Error", f"No available choices for stage {stage.value}")
                    return 1
                chosen_card = stage_res.choices[0]
                card_id = chosen_card.id if hasattr(chosen_card, "id") else chosen_card.get("id")
                engine.select_option(stage, card_id)
                current_config[stage.value] = card_id
                step_idx += 1
            else:
                response = hitl.prompt_stage_approval(stage_res)
                if response.decision == HITLDecision.ACCEPT:
                    if not stage_res.choices:
                        formatter.render_error("Assembly Error", f"No available choices for stage {stage.value}")
                        return 1
                    chosen_card = stage_res.choices[0]
                    card_id = chosen_card.id if hasattr(chosen_card, "id") else chosen_card.get("id")
                    engine.select_option(stage, card_id)
                    current_config[stage.value] = card_id
                    step_idx += 1
                elif response.decision == HITLDecision.EDIT:
                    chosen_card = hitl.prompt_option_selection(stage_res.choices)
                    if chosen_card is None:
                        formatter.render_error("Assembly Error", "No option selected.")
                        return 1
                    card_id = chosen_card.id if hasattr(chosen_card, "id") else chosen_card.get("id")
                    engine.select_option(stage, card_id)
                    current_config[stage.value] = card_id
                    step_idx += 1
                elif response.decision == HITLDecision.DETAILS:
                    formatter.render_info("Stage Details", f"Detailed specs for stage {stage.display_name_en}:")
                    formatter.render_option_grid(stage_res.choices)
                elif response.decision == HITLDecision.HELP:
                    help_text = (
                        "HitL Interactive Commands:\n"
                        "  • y / yes: Accept the recommended option\n"
                        "  • edit / e: Select a specific option card from the list\n"
                        "  • details / d: Display detailed technical specifications\n"
                        "  • help / h: View this help guide\n"
                        "  • n / no (or Enter): Decline selection and revert to previous assembly stage"
                    )
                    formatter.render_info("HitL Help Guide", help_text)
                else:  # DECLINE
                    if step_idx > 0:
                        step_idx -= 1
                        prev_stage = stages[step_idx]
                        if prev_stage.value in current_config:
                            del current_config[prev_stage.value]
                        engine.state.undo_last_stage()
                        formatter.render_info("Step Reverted", f"Reverted to stage: {stages[step_idx].display_name_en}")
                    else:
                        formatter.render_info("Session Aborted", "User cancelled assembly at initial stage.")
                        return 1
        except OlympusSpecialistError as e:
            formatter.render_error("Assembly Engine Error", str(e))
            return 1
        except Exception as e:
            formatter.render_error("Unexpected Error", str(e))
            return 1

    # Assembly session complete
    formatter.render_assembly_summary(engine.state)

    if parsed_args.export_json is not None:
        export_path = parsed_args.export_json.strip()
        if not export_path:
            formatter.render_error("Export Error", "Export JSON file path cannot be empty.")
            return 1
        summary_data = engine.state.get_summary()
        try:
            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(summary_data, f, indent=2, ensure_ascii=False)
            formatter.render_info("Export Complete", f"Assembly configuration exported to {export_path}")
        except Exception as e:
            formatter.render_error("Export Failed", f"Failed to write JSON export: {e}")
            return 1

    return 0


def main() -> None:
    """CLI executable entrypoint."""
    sys.exit(run_cli())


if __name__ == "__main__":
    main()
