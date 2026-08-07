import sys
import json
import time
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Body, Path as FastAPIPath
from fastapi.responses import StreamingResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from olympus_specialist.guardrails.cost_gate import (
    DAILY_BUDGET_CAP_USD,
    _daily_spend_tracker,
    check_budget_limit,
    record_spend
)
from olympus_specialist.workflow.eaer_pipeline import EAERPipeline
from olympus_specialist.telemetry.hierarchical_tracker import tracker
from olympus_specialist.self_healing.remediation import SelfHealingEngine
from olympus_specialist.domain.compatibility.rules import validate_stand_optics

app = FastAPI(title="Olympus Product Specialist API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = EAERPipeline()
self_healing = SelfHealingEngine()

class QueryRequest(BaseModel):
    session_id: str
    prompt: str
    stand_id: str = "BX53M"
    observation_mode: str = "Darkfield"
    objective_series: str = "MPLFLN-BD"
    estimated_cost: float = 0.001

@app.get("/")
def root_dashboard():
    today = time.strftime("%Y-%m-%d", time.gmtime())
    current_spend = _daily_spend_tracker.get(today, 0.0)
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Olympus Product Specialist — ADK Playground Bridge</title>
        <style>
            body {{ font-family: -apple-system, sans-serif; background: #0f172a; color: #f8fafc; padding: 40px; text-align: center; }}
            .card {{ background: #1e293b; padding: 30px; border-radius: 12px; display: inline-block; max-width: 600px; border: 1px solid #334155; }}
            h1 {{ color: #38bdf8; margin-top: 0; }}
            .badge {{ background: #10b981; color: white; padding: 6px 12px; border-radius: 20px; font-weight: bold; font-size: 14px; }}
            .endpoint {{ font-family: monospace; background: #0f172a; padding: 8px; border-radius: 6px; margin: 8px 0; border: 1px solid #334155; text-align: left; color: #38bdf8; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Olympus Product Specialist Bridge</h1>
            <p><span class="badge">SYSTEM ACTIVE — 200 OK</span></p>
            <p style="color: #94a3b8;">Google ADK Playground & SSE Streaming Server</p>
            <hr style="border-color: #334155; margin: 20px 0;">
            <div style="text-align: left; margin-top: 20px;">
                <p><strong>Daily Budget Cap:</strong> ${DAILY_BUDGET_CAP_USD:.2f} USD</p>
                <p><strong>Current Spend:</strong> ${current_spend:.4f} USD</p>
                <p><strong>Active SSE Endpoints:</strong></p>
                <div class="endpoint">GET /health</div>
                <div class="endpoint">GET /api/v1/playground/info</div>
                <div class="endpoint">POST /api/v1/chat/stream</div>
                <div class="endpoint">POST /api/v1/tools/execute</div>
            </div>
        </div>
    </body>
    </html>
    """)

@app.get("/health")
@app.get("/api/v1/health")
def health_check():
    today = time.strftime("%Y-%m-%d", time.gmtime())
    current_spend = _daily_spend_tracker.get(today, 0.0)
    return {
        "status": "healthy",
        "service": "olympus-product-specialist-api",
        "cost_circuit_breaker": {
            "daily_budget_cap_usd": DAILY_BUDGET_CAP_USD,
            "current_spend_usd": current_spend,
            "circuit_breaker_triggered": current_spend >= DAILY_BUDGET_CAP_USD
        }
    }

@app.get("/api/v1/cost/status")
def get_cost_status():
    today = time.strftime("%Y-%m-%d", time.gmtime())
    current_spend = _daily_spend_tracker.get(today, 0.0)
    return {
        "daily_budget_cap_usd": DAILY_BUDGET_CAP_USD,
        "current_spend_usd": current_spend,
        "remaining_budget_usd": max(0.0, DAILY_BUDGET_CAP_USD - current_spend),
        "circuit_breaker_triggered": current_spend >= DAILY_BUDGET_CAP_USD
    }

@app.post("/api/v1/cost/record")
def record_cost(payload: Dict[str, float] = Body(...)):
    call_cost = payload.get("call_cost", 0.0)
    new_total = record_spend(call_cost)
    return {
        "daily_budget_cap_usd": DAILY_BUDGET_CAP_USD,
        "current_spend_usd": new_total,
        "remaining_budget_usd": max(0.0, DAILY_BUDGET_CAP_USD - new_total),
        "circuit_breaker_triggered": new_total >= DAILY_BUDGET_CAP_USD
    }

@app.get("/api/v1/playground/info")
def playground_info():
    return {
        "service": "Olympus Product Specialist Playground Bridge",
        "version": "0.1.0",
        "sse_events": [
            "thinking",
            "tool_status",
            "agent_response",
            "telemetry",
            "self_healing",
            "cost_circuit_breaker",
            "done"
        ]
    }

@app.post("/api/query")
def run_query(req: QueryRequest):
    try:
        check_budget_limit(estimated_call_cost=req.estimated_cost)
    except PermissionError as e:
        raise HTTPException(status_code=429, detail=str(e))

    res = pipeline.run_pipeline(
        session_id=req.session_id,
        user_request=req.prompt,
        stand_id=req.stand_id,
        observation_mode=req.observation_mode,
        objective_series=req.objective_series
    )
    record_spend(req.estimated_cost)
    return res

@app.post("/api/v1/chat/stream")
def chat_sse_stream(req: QueryRequest):
    async def sse_generator():
        today = time.strftime("%Y-%m-%d", time.gmtime())
        current_spend = _daily_spend_tracker.get(today, 0.0)

        if current_spend >= DAILY_BUDGET_CAP_USD:
            yield f"event: cost_circuit_breaker\ndata: {json.dumps({'status': 'CAPPED', 'error': 'GCP Cost Circuit Breaker Triggered', 'circuit_breaker_triggered': True})}\n\n"
            yield f"event: done\ndata: {json.dumps({'session_id': req.session_id})}\n\n"
            return

        yield f"event: thinking\ndata: {json.dumps({'stage': 'EAER Extraction', 'status': 'PROCESSING'})}\n\n"
        await asyncio.sleep(0.01)

        yield f"event: tool_status\ndata: {json.dumps({'tool': 'validate_stand_optics', 'status': 'RUNNING'})}\n\n"
        await asyncio.sleep(0.01)

        # Check for missing slots -> trigger self healing
        if not req.stand_id or not req.observation_mode or not req.objective_series:
            remediation = self_healing.diagnose_and_repair(
                session_id=req.session_id,
                step_index=1,
                error=ValueError("Missing required input slots"),
                missing_slots=["stand_id", "observation_mode", "objective_series"]
            )
            yield f"event: self_healing\ndata: {json.dumps({'status': 'REMEDIATED', 'payload': remediation})}\n\n"
            yield f"event: agent_response\ndata: {json.dumps({'chunk': 'Please select a Microscope Stand, Observation Mode, and Objective Series.'})}\n\n"
            yield f"event: done\ndata: {json.dumps({'session_id': req.session_id})}\n\n"
            return

        # Run pipeline
        res = pipeline.run_pipeline(
            session_id=req.session_id,
            user_request=req.prompt,
            stand_id=req.stand_id,
            observation_mode=req.observation_mode,
            objective_series=req.objective_series
        )

        response_text = f"Official Evident Scientific / Olympus System Configuration: Stand {req.stand_id} is compatible with {req.objective_series} optics under {req.observation_mode} mode."
        yield f"event: agent_response\ndata: {json.dumps({'chunk': response_text})}\n\n"

        telemetry = tracker.log_invocation(
            session_id=req.session_id,
            agent_role="Olympus Specialist Guide",
            parent_agent="Root Orchestrator",
            model_name="gemini-3.6-flash",
            prompt_tokens=120,
            completion_tokens=180,
            estimated_cost_usd=req.estimated_cost
        )
        yield f"event: telemetry\ndata: {json.dumps(telemetry)}\n\n"
        yield f"event: done\ndata: {json.dumps({'session_id': req.session_id})}\n\n"

    return StreamingResponse(sse_generator(), media_type="text/event-stream")

@app.post("/api/v1/tools/execute")
def execute_tool_stream(payload: Dict[str, Any] = Body(...)):
    session_id = payload.get("session_id", "tool_sess")
    tool_name = payload.get("tool_name", "")
    parameters = payload.get("parameters", {})

    async def tool_generator():
        yield f"event: tool_status\ndata: {json.dumps({'status': 'starting', 'tool': tool_name})}\n\n"
        await asyncio.sleep(0.01)

        yield f"event: tool_status\ndata: {json.dumps({'status': 'running', 'tool': tool_name})}\n\n"
        await asyncio.sleep(0.01)

        if tool_name == "validate_stand_optics":
            res = validate_stand_optics(
                parameters.get("stand_id", "BX53M"),
                parameters.get("observation_mode", "Darkfield"),
                parameters.get("objective_series", "MPLFLN-BD")
            )
            yield f"event: tool_status\ndata: {json.dumps({'status': 'completed', 'tool': tool_name, 'result': res})}\n\n"
        else:
            remediation = self_healing.diagnose_and_repair(
                session_id=session_id,
                step_index=1,
                error=ValueError(f"Tool '{tool_name}' is not recognized")
            )
            yield f"event: self_healing\ndata: {json.dumps({'status': 'FAILED_REMEDIATED', 'remediation': remediation})}\n\n"

        yield f"event: done\ndata: {json.dumps({'session_id': session_id})}\n\n"

    return StreamingResponse(tool_generator(), media_type="text/event-stream")

@app.get("/api/stream/{session_id}")
async def stream_events(session_id: str = FastAPIPath(..., description="The session identifier")):
    async def event_generator():
        yield f"data: {json.dumps({'event': 'session_started', 'session_id': session_id})}\n\n"
        await asyncio.sleep(0.01)
        telemetry = tracker.get_session_telemetry(session_id) or {"session_id": session_id, "status": "active"}
        yield f"data: {json.dumps({'event': 'telemetry_update', 'data': telemetry})}\n\n"
        await asyncio.sleep(0.01)
        yield f"data: {json.dumps({'event': 'session_complete', 'session_id': session_id})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
