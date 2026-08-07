"""
Tests for FastAPI Web API & SSE Playground Bridge server (src/olympus_specialist/api/server.py).
Verifies SSE streaming endpoints, REST endpoints, cost circuit breaker ($5.00/day limit), telemetry, tool execution status, and self-healing.
"""

import pytest
from fastapi.testclient import TestClient

from olympus_specialist.api.server import app
from olympus_specialist.guardrails.cost_gate import DAILY_BUDGET_CAP_USD, _daily_spend_tracker, record_spend

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_daily_spend():
    """Resets daily spend tracker before each test to ensure deterministic budget state."""
    _daily_spend_tracker.clear()
    yield
    _daily_spend_tracker.clear()


def test_health_check_endpoint():
    """Tests /health and /api/v1/health endpoints."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "olympus-product-specialist-api"
    assert "cost_circuit_breaker" in data
    assert data["cost_circuit_breaker"]["daily_budget_cap_usd"] == 5.00
    assert data["cost_circuit_breaker"]["circuit_breaker_triggered"] is False


def test_cost_status_and_record():
    """Tests GET /api/v1/cost/status and POST /api/v1/cost/record."""
    # Check initial status
    res = client.get("/api/v1/cost/status")
    assert res.status_code == 200
    assert res.json()["current_spend_usd"] == 0.0

    # Record spend
    res_rec = client.post("/api/v1/cost/record", json={"call_cost": 1.25})
    assert res_rec.status_code == 200
    assert res_rec.json()["current_spend_usd"] == 1.25
    assert res_rec.json()["remaining_budget_usd"] == 3.75
    assert res_rec.json()["circuit_breaker_triggered"] is False


def test_run_query_rest_endpoint():
    """Tests POST /api/query synchronous endpoint."""
    payload = {
        "session_id": "REST-SESS-101",
        "prompt": "Inspect BX53M darkfield setup",
        "stand_id": "BX53M",
        "observation_mode": "Darkfield",
        "objective_series": "MPLFLN-BD",
    }
    response = client.post("/api/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["optical_configuration"]["compatible"] is True


def test_playground_info_endpoint():
    """Tests GET /api/v1/playground/info metadata endpoint."""
    res = client.get("/api/v1/playground/info")
    assert res.status_code == 200
    data = res.json()
    assert data["service"] == "Olympus Product Specialist Playground Bridge"
    assert "thinking" in data["sse_events"]
    assert "agent_response" in data["sse_events"]
    assert "cost_circuit_breaker" in data["sse_events"]


def test_chat_sse_stream_valid():
    """Tests POST /api/v1/chat/stream with valid optical parameters."""
    payload = {
        "session_id": "TEST-SESS-101",
        "prompt": "Configure BX53M with Brightfield and MPLFLN-BD objectives",
        "stand_id": "BX53M",
        "observation_mode": "Brightfield",
        "objective_series": "MPLFLN-BD",
        "estimated_cost": 0.001,
    }
    response = client.post("/api/v1/chat/stream", json=payload)
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]

    content = response.text
    assert "event: thinking" in content
    assert "event: tool_status" in content
    assert "event: agent_response" in content
    assert "event: telemetry" in content
    assert "event: done" in content
    assert "Evident Scientific / Olympus" in content


def test_chat_sse_stream_missing_slots_self_healing():
    """Tests POST /api/v1/chat/stream with missing parameters triggering self-healing."""
    payload = {
        "session_id": "TEST-SESS-102",
        "prompt": "Find me a microscope for metallurgical analysis",
        "stand_id": "",
        "observation_mode": "",
        "objective_series": "",
        "estimated_cost": 0.001,
    }
    response = client.post("/api/v1/chat/stream", json=payload)
    assert response.status_code == 200

    content = response.text
    assert "event: self_healing" in content
    assert "event: agent_response" in content
    assert "REMEDIATED" in content
    assert "Microscope Stand" in content


def test_chat_sse_stream_cost_circuit_breaker_triggered():
    """Tests that spending >= $5.00/day triggers the cost_circuit_breaker event."""
    # Exceed the $5.00/day limit
    record_spend(5.00)

    payload = {
        "session_id": "TEST-SESS-CAPPED",
        "prompt": "Configure IX73 microscope",
        "estimated_cost": 0.001,
    }
    response = client.post("/api/v1/chat/stream", json=payload)
    assert response.status_code == 200

    content = response.text
    assert "event: cost_circuit_breaker" in content
    assert "GCP Cost Circuit Breaker Triggered" in content
    assert "circuit_breaker_triggered" in content


def test_tools_execute_sse_stream():
    """Tests POST /api/v1/tools/execute tool status streaming."""
    payload = {
        "session_id": "TEST-SESS-TOOL",
        "tool_name": "validate_stand_optics",
        "parameters": {
            "stand_id": "GX53",
            "observation_mode": "Brightfield",
            "objective_series": "LMPLFLN-BD",
        },
    }
    response = client.post("/api/v1/tools/execute", json=payload)
    assert response.status_code == 200

    content = response.text
    assert "event: tool_status" in content
    assert "starting" in content
    assert "running" in content
    assert "completed" in content
    assert "event: done" in content


def test_tools_execute_unknown_tool_self_healing():
    """Tests POST /api/v1/tools/execute with invalid tool name triggering self-healing."""
    payload = {
        "session_id": "TEST-SESS-FAIL-TOOL",
        "tool_name": "non_existent_tool",
        "parameters": {},
    }
    response = client.post("/api/v1/tools/execute", json=payload)
    assert response.status_code == 200

    content = response.text
    assert "event: self_healing" in content
    assert "FAILED_REMEDIATED" in content
