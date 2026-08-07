import time
from typing import Dict

DAILY_BUDGET_CAP_USD = 5.00
_daily_spend_tracker: Dict[str, float] = {}

def get_today_key() -> str:
    return time.strftime("%Y-%m-%d", time.gmtime())

def check_budget_limit(estimated_call_cost: float = 0.01) -> bool:
    """Checks if daily spend is within the $5.00 hard budget limit."""
    today = get_today_key()
    current_spend = _daily_spend_tracker.get(today, 0.0)
    
    if current_spend + estimated_call_cost > DAILY_BUDGET_CAP_USD or current_spend >= DAILY_BUDGET_CAP_USD:
        raise PermissionError(
            f"GCP Cost Circuit Breaker Triggered: Daily spend (${current_spend:.2f}) "
            f"exceeds hard limit of ${DAILY_BUDGET_CAP_USD:.2f}/day."
        )
    return True

def record_spend(actual_call_cost: float) -> float:
    """Records spend against daily budget limit."""
    today = get_today_key()
    _daily_spend_tracker[today] = _daily_spend_tracker.get(today, 0.0) + actual_call_cost
    return _daily_spend_tracker[today]
