"""
Rich UI Formatter module for Evident/Olympus Product Specialist CLI.
Renders rich panels, progress indicators, bilingual cards, status badges, and assembly summary tables.
"""

from typing import Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich.box import ROUNDED, DOUBLE
from rich.markup import escape

from src.engine.sequential_thinking import AssemblyStage, OptionCard, AssemblyState, normalize_stage


def render_step_progress(stage: str | AssemblyStage, current_step: int, total_steps: int = 5) -> str:
    """
    Format step progress string containing step index and bilingual stage title.
    """
    try:
        norm_stage = normalize_stage(stage)
        ar_name = norm_stage.display_name_ar
        en_name = norm_stage.display_name_en
        stage_str = norm_stage.value
    except Exception:
        ar_name = str(stage)
        en_name = str(stage)
        stage_str = str(stage)

    return f"[Step {current_step}/{total_steps}] Stage: {stage_str} | مرحلة: {ar_name} ({en_name})"


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


def render_option_cards(cards: list[OptionCard | dict]) -> str:
    """
    Render string representation of multiple option cards.
    """
    rendered = []
    for idx, card in enumerate(cards, start=1):
        card_text = render_bilingual_card(card)
        rendered.append(f"Option #{idx}:\n{card_text}")
    return "\n\n".join(rendered)


class RichFormatter:
    """
    Renders rich terminal UI visual components using rich panels, tables, and columns.
    """

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()

    # [MOCK_IMPLEMENTATION]
    def render_header(self) -> None:
        """Render main CLI application header banner."""
        title = Text("EVIDENT / OLYMPUS MICROSCOPY PRODUCT SPECIALIST AGENT", style="bold cyan")
        subtitle = Text("Interactive SequentialThinking HitL Engine (Clean-Slate Architecture)", style="italic dim white")
        mock_badge = Text(" [MOCK_DATA] ", style="bold yellow on black")

        content = Text.assemble(title, "\n", subtitle, "\n", mock_badge, justify="center")
        panel = Panel(content, box=DOUBLE, border_style="cyan", padding=(1, 2))
        self.console.print(panel)

    def render_stage_progress(self, current_stage: AssemblyStage | str, stage_idx: int, total_stages: int = 5) -> None:
        """Print stage progress header panel to console."""
        try:
            norm_stage = normalize_stage(current_stage)
            ar_title = norm_stage.display_name_ar
            en_title = norm_stage.display_name_en
        except Exception:
            ar_title = str(current_stage)
            en_title = str(current_stage)

        progress_msg = f"[bold yellow]Step {stage_idx}/{total_stages}[/bold yellow] : [bold white]{escape(str(ar_title))}[/bold white] | [dim]{escape(str(en_title))}[/dim]"
        panel = Panel(progress_msg, box=ROUNDED, border_style="yellow", padding=(0, 1))
        self.console.print(panel)

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

    def render_option_grid(self, cards: list[OptionCard | dict]) -> None:
        """Display list of option cards in panel format to console."""
        panels = [self.render_bilingual_option_card(card, index=idx + 1) for idx, card in enumerate(cards)]
        for panel in panels:
            self.console.print(panel)

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

    def render_error(self, title: str, message: str) -> None:
        """Render error panel to console."""
        content = f"[bold red]{escape(str(title))}[/bold red]\n{escape(str(message))}"
        panel = Panel(content, box=ROUNDED, border_style="red", padding=(1, 2))
        self.console.print(panel)

    def render_info(self, title: str, message: str) -> None:
        """Render info panel to console."""
        content = f"[bold cyan]{escape(str(title))}[/bold cyan]\n{escape(str(message))}"
        panel = Panel(content, box=ROUNDED, border_style="cyan", padding=(1, 2))
        self.console.print(panel)
