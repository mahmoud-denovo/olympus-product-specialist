import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, Optional

LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "structured_steps.jsonl"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("olympus_specialist")

def log_step(
    session_id: str,
    step_index: int,
    action: str,
    status: str,
    details: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None
) -> Dict[str, Any]:
    """Records a structured step log with correlation IDs in JSONL format."""
    entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "session_id": session_id,
        "step_index": step_index,
        "action": action,
        "status": status,
        "details": details or {},
        "error": error
    }
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
        
    logger.info(f"[{session_id}] Step {step_index} | {action} | {status}")
    return entry
