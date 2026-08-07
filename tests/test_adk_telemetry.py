"""
Tests for Google ADK App and Hierarchical Token Usage Tracker.
"""

import pytest
from olympus_specialist.adk_app import create_adk_app
from olympus_specialist.telemetry.hierarchical_tracker import (
    HierarchicalTokenTracker,
    TokenUsage,
)


def test_hierarchical_tracker_initialization():
    tracker = HierarchicalTokenTracker(session_id="test_session")
    assert tracker.session_id == "test_session"
    assert "root_specialist" in tracker.nodes


def test_hierarchical_tracker_agent_registration():
    tracker = HierarchicalTokenTracker(session_id="test_reg")
    subnode = tracker.register_agent(
        agent_id="test_subagent",
        agent_name="Test Subagent",
        role="Testing Role",
        parent_agent_id="root_specialist",
    )
    assert subnode.agent_id == "test_subagent"
    assert "test_subagent" in tracker.nodes["root_specialist"].children_ids


def test_token_usage_addition_and_cost_calculation():
    tracker = HierarchicalTokenTracker(session_id="test_cost")
    cost = tracker.calculate_cost(
        model_name="gemini-2.5-flash",
        prompt_tokens=1000,
        candidates_tokens=500,
    )
    # 1000 prompt tokens @ $0.075/1M = $0.000075
    # 500 candidate tokens @ $0.30/1M = $0.00015
    # Total = $0.000225
    assert cost == pytest.approx(0.000225, rel=1e-3)

    u1 = TokenUsage(prompt_tokens=100, candidates_tokens=50, total_tokens=150, cost_usd=0.01)
    u2 = TokenUsage(prompt_tokens=200, candidates_tokens=100, total_tokens=300, cost_usd=0.02)
    u3 = u1.add(u2)

    assert u3.prompt_tokens == 300
    assert u3.candidates_tokens == 150
    assert u3.total_tokens == 450
    assert u3.cost_usd == pytest.approx(0.03)


def test_adk_app_query_processing():
    app = create_adk_app("test_adk_query_session")
    result = app.process_query(
        user_query="Recommend metallurgical microscope with 100x magnification.",
        parameters={"frame": "BX53", "objective": "PLN100X"},
    )

    assert result["status"] == "COMPLETED"
    assert "recommendation" in result
    assert "telemetry" in result

    telemetry = result["telemetry"]
    assert telemetry["total_agents"] >= 4
    assert telemetry["session_token_usage"]["total_tokens"] > 0
    assert "root_specialist" in telemetry["agent_hierarchy"]
    assert "optical_compatibility_validator" in telemetry["agent_hierarchy"]
