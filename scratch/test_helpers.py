import io
from rich.console import Console
from rich.markup import escape
from src.cli.formatter import render_bilingual_card, render_option_cards, render_step_progress, RichFormatter

def test_standalone_functions():
    buffer = io.StringIO()
    console = Console(file=buffer)

    card1 = {
        "model_name": "IX73 [Frame]",
        "arabic_description": "وصف [تست]",
        "english_specs": {"mag": "[100x]"},
        "price_tier": "Standard [Tier]",
        "optical_compatibility_status": True
    }

    card2 = {
        "model_name": "Olympus [red]IX73[/red]",
        "arabic_description": "[bold red]خطر[/bold red]",
        "english_specs": {"spec": "[link=http://evil.com]click[/link]"},
        "price_tier": "Premium",
        "optical_compatibility_status": False
    }

    print("--- 1. Checking raw return values of standalone functions ---")
    s1 = render_bilingual_card(card1)
    s2 = render_option_cards([card1, card2])
    sp = render_step_progress("[bold]stage[/bold]", 1, 5)

    print("render_bilingual_card(card1):")
    print(repr(s1))
    print("render_step_progress:")
    print(repr(sp))

    print("\n--- 2. Checking console.print(render_bilingual_card(card1)) ---")
    try:
        console.print(s1)
        print("Printed s1 successfully")
    except Exception as e:
        print(f"FAILED s1 print: {type(e).__name__}: {e}")

    print("\n--- 3. Checking console.print(render_bilingual_card(card2)) ---")
    try:
        console.print(render_bilingual_card(card2))
        print("Printed card2 successfully")
    except Exception as e:
        print(f"FAILED card2 print: {type(e).__name__}: {e}")

    print("\n--- 4. Checking console.print(render_step_progress(...)) ---")
    try:
        console.print(sp)
        print("Printed step progress successfully")
    except Exception as e:
        print(f"FAILED step progress print: {type(e).__name__}: {e}")

    print("\n--- 5. Checking RichFormatter methods ---")
    rf = RichFormatter(console=console)
    try:
        rf.render_bilingual_option_card(card1)
        rf.render_bilingual_option_card(card2)
        rf.render_option_grid([card1, card2])
        rf.render_stage_progress("[bold]stage[/bold]", 1, 5)
        rf.render_error("Title [err]", "Body [msg]")
        rf.render_info("Info [tag]", "Message <xml>")
        print("RichFormatter methods rendered without error")
    except Exception as e:
        print(f"RichFormatter FAILED: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_standalone_functions()
