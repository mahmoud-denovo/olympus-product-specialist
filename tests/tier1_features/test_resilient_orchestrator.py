import pytest
from olympus_specialist.workflow.resilient_orchestrator import (
    DeterministicOrchestrator,
    ErrorCounter,
    global_resilient_orchestrator
)

def test_orchestrator_initialization():
    orch = DeterministicOrchestrator("test_agent_01", "Test Specialist Agent", depth_level=1)
    assert orch.is_orchestrator is False
    assert len(orch.managed_tasks) == 0

def test_promotion_rule_task_count():
    orch = DeterministicOrchestrator("test_agent_02", "Task Heavy Agent", depth_level=1)
    for i in range(4):
        orch.add_task(f"task_{i}", f"Task Number {i}")
    
    assert len(orch.managed_tasks) == 4
    assert orch.is_orchestrator is True  # Promoted because managed_tasks > 3

def test_promotion_rule_depth_level():
    orch = DeterministicOrchestrator("deep_agent_01", "Deep Hierarchy Agent", depth_level=4)
    assert orch.is_orchestrator is True  # Promoted because depth_level > 3

def test_overload_counter_and_resilience():
    orch = DeterministicOrchestrator("resilient_agent_01", "Resilient Agent", depth_level=1)
    
    mock_calls = 0
    def mock_overloaded_api():
        nonlocal mock_calls
        mock_calls += 1
        if mock_calls < 3:
            raise RuntimeError("429 Model API is currently overloaded")
        return "SUCCESS_DATA"

    result = orch.execute_with_resilience(mock_overloaded_api)
    assert result == "SUCCESS_DATA"
    assert orch.error_counter.total_overload_errors == 2
    assert orch.error_counter.total_retry_attempts == 2
    assert orch.error_counter.consecutive_failures == 0

def test_telemetry_reporting():
    orch = DeterministicOrchestrator("telemetry_agent", "Telemetry Test", depth_level=1)
    orch.add_task("t1", "Task One")
    orch.record_overload_error("503 Service Unavailable")
    
    telemetry = orch.get_orchestrator_telemetry()
    assert telemetry["agent_id"] == "telemetry_agent"
    assert telemetry["overload_error_counters"]["total_overload_errors"] == 1
    assert "t1" in telemetry["tasks"]
