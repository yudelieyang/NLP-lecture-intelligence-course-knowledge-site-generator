from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app import services


APP_DIR = Path(__file__).resolve().parent
app = FastAPI(title="Local Lecture Knowledge App")
app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request) -> HTMLResponse:
    html = (APP_DIR / "templates" / "dashboard.html").read_text(encoding="utf-8")
    return HTMLResponse(html)


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"ok": True, "service": "Local Lecture Knowledge App", "host": "127.0.0.1"}


@app.get("/api/materials")
def materials() -> dict[str, Any]:
    return services.materials_status()


@app.get("/api/runs")
def runs() -> dict[str, Any]:
    return {"ok": True, "runs": services.runs_status()}


@app.get("/api/config")
def config() -> dict[str, Any]:
    return {"ok": True, "config": services.get_config()}


@app.post("/api/config")
async def save_config(request: Request) -> dict[str, Any]:
    payload = await request.json()
    config = services.dashboard_payload_to_config(payload)
    services.save_config(config)
    return {"ok": True, "config": config}


@app.post("/api/generate")
async def generate(request: Request) -> dict[str, Any]:
    payload = await request.json()
    try:
        config = services.dashboard_payload_to_config(payload)
        services.save_config(config)
        result = services.generate_site_from_dashboard(payload)
        return result
    except Exception as exc:  # noqa: BLE001 - convert internal errors to readable API messages
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/open")
async def open_target(request: Request) -> dict[str, Any]:
    payload = await request.json()
    try:
        result = services.open_project_target(payload.get("type", ""), payload.get("runId"))
        return {"ok": True, **result}
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/create-input-dir")
def create_input_dir() -> dict[str, Any]:
    return services.create_input_dir()


@app.post("/api/test-llm")
async def test_llm(request: Request) -> dict[str, Any]:
    payload = await request.json()
    return services.test_llm_connection(payload)
