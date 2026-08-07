from typing import Any, Dict, List, Optional
from ..logging.logger import log_step

class SelfHealingEngine:
    """Autonomous diagnostic gate and remediation engine."""
    
    def __init__(self):
        self.retry_limit = 3

    def diagnose_and_repair(
        self,
        session_id: str,
        step_index: int,
        error: Exception,
        missing_slots: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Intercepts tool errors/missing parameters and formats a self-correction strategy."""
        missing_slots = missing_slots or []
        log_step(
            session_id=session_id,
            step_index=step_index,
            action="SELF_HEALING_DIAGNOSIS",
            status="INTERCEPTED",
            details={"missing_slots": missing_slots},
            error=str(error)
        )
        
        remediation_payload = {
            "needs_user_clarification": len(missing_slots) > 0,
            "missing_slots": missing_slots,
            "remediation_instruction": (
                f"Clarification required for missing slots: {', '.join(missing_slots)}"
                if missing_slots else "Retrying tool execution with normalized inputs."
            )
        }
        
        log_step(
            session_id=session_id,
            step_index=step_index,
            action="SELF_HEALING_REPAIR",
            status="REMEDIATED",
            details=remediation_payload
        )
        return remediation_payload
