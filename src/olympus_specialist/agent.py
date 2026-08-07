import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.olympus_specialist.adk_app import create_adk_app, OlympusADKApp

app = create_adk_app()
root_agent = app

def run(prompt: str) -> str:
    res = app.process_query(user_query=prompt)
    return str(res)
