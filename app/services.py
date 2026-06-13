from __future__ import annotations

import json
import os
import sys
import webbrowser
from pathlib import Path
from typing import Any

from scripts.generate_site import DEFAULT_CONFIG, ROOT, deep_update, generate_from_config, load_config, scan_input_files
from scripts.llm_client import LLMClient
from scripts.run_registry import load_runs
from scripts.utils import SUPPORTED_EXTENSIONS, detect_lecture_number


CONFIG_PATH = ROOT / "config.json"
ENV_PATH = ROOT / ".env"


def get_config() -> dict[str, Any]:
    return load_config(CONFIG_PATH if CONFIG_PATH.exists() else None)


def save_config(config: dict[str, Any]) -> dict[str, Any]:
    clean = normalize_config(config)
    CONFIG_PATH.write_text(json.dumps(clean, ensure_ascii=False, indent=2), encoding="utf-8")
    return clean


def normalize_config(data: dict[str, Any]) -> dict[str, Any]:
    config = json.loads(json.dumps(DEFAULT_CONFIG))
    deep_update(config, data or {})
    llm = dict(config.get("llm") or {})
    llm.pop("apiKeyValue", None)
    config["llm"] = llm
    return config


def write_env_value(name: str, value: str | None) -> None:
    if not name or not value:
        return
    lines = ENV_PATH.read_text(encoding="utf-8").splitlines() if ENV_PATH.exists() else []
    prefix = f"{name}="
    updated = False
    next_lines: list[str] = []
    for line in lines:
        if line.startswith(prefix):
            next_lines.append(f"{name}={value}")
            updated = True
        else:
            next_lines.append(line)
    if not updated:
        next_lines.append(f"{name}={value}")
    ENV_PATH.write_text("\n".join(next_lines) + "\n", encoding="utf-8")


def materials_status(config: dict[str, Any] | None = None) -> dict[str, Any]:
    config = config or get_config()
    input_dir = (ROOT / str(config.get("inputDir", "input_materials"))).resolve()
    input_dir.mkdir(parents=True, exist_ok=True)
    files = []
    supported_count = 0
    unsupported_count = 0
    roadmap_extensions = {".pptx", ".ipynb"}
    for path in sorted([p for p in input_dir.iterdir() if p.is_file()], key=lambda p: p.name.lower()):
        extension = path.suffix.lower()
        supported = extension in SUPPORTED_EXTENSIONS and path.name.lower() != "readme.md"
        if supported:
            supported_count += 1
            status = "supported"
        elif extension in roadmap_extensions:
            unsupported_count += 1
            status = "roadmap"
        else:
            unsupported_count += 1
            status = "unsupported"
        files.append(
            {
                "name": path.name,
                "extension": extension,
                "sizeBytes": path.stat().st_size,
                "supported": supported,
                "status": status,
                "lectureNumber": detect_lecture_number(path),
            }
        )
    return {
        "inputDir": str(input_dir.relative_to(ROOT)),
        "exists": input_dir.exists(),
        "files": files,
        "supportedCount": supported_count,
        "unsupportedCount": unsupported_count,
    }


def supported_materials(config: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    config = config or get_config()
    input_dir = (ROOT / str(config.get("inputDir", "input_materials"))).resolve()
    if not input_dir.exists():
        return []
    records = []
    for path in scan_input_files(input_dir):
        records.append(
            {
                "name": path.name,
                "extension": path.suffix.lower(),
                "sizeBytes": path.stat().st_size,
                "lectureNumber": detect_lecture_number(path),
                "supported": True,
                "status": "supported",
            }
        )
    return records


def runs_status(config: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    config = config or get_config()
    output_dir = (ROOT / str(config.get("outputDir", "output_sites"))).resolve()
    return list(reversed(load_runs(output_dir)))


def generate_site_from_dashboard(payload: dict[str, Any]) -> dict[str, Any]:
    config = dashboard_payload_to_config(payload)
    logs: list[str] = []

    def log(line: str = "") -> None:
        logs.append(str(line))

    result = generate_from_config(config, open_after=False, log=log)
    metadata = result["metadata"]
    return {
        "ok": True,
        "runId": metadata["runId"],
        "outputPath": str(Path(metadata["outputDir"]) / "index.html"),
        "inputFileCount": len(metadata.get("processedFiles") or []),
        "warnings": metadata.get("failedFiles") or [],
        "llmTelemetry": {
            "llmEnabled": metadata.get("llmEnabled"),
            "llmConnectionOk": metadata.get("llmConnectionOk"),
            "llmCallsAttempted": metadata.get("llmCallsAttempted", 0),
            "llmCallsSucceeded": metadata.get("llmCallsSucceeded", 0),
            "llmCallsFailed": metadata.get("llmCallsFailed", 0),
            "llmParseSucceeded": metadata.get("llmParseSucceeded", 0),
            "llmRepairAttempted": metadata.get("llmRepairAttempted", 0),
            "llmRepairSucceeded": metadata.get("llmRepairSucceeded", 0),
        },
        "llmSummary": (metadata.get("qaReport") or {}).get("llmSummary"),
        "logs": logs,
        "message": "Site generated successfully.",
    }


def dashboard_payload_to_config(payload: dict[str, Any]) -> dict[str, Any]:
    generation_mode = payload.get("generationMode") or ("online_llm" if payload.get("llmEnabled") else "offline")
    llm_enabled = generation_mode == "online_llm"
    llm_provider = payload.get("llmProvider") or "none"
    config = {
        "projectName": payload.get("projectName") or DEFAULT_CONFIG["projectName"],
        "inputDir": payload.get("inputDir") or "input_materials",
        "outputDir": payload.get("outputDir") or "output_sites",
        "templateDir": payload.get("templateDir") or "templates",
        "minContentChars": int(payload.get("minContentChars") or 3000),
        "language": payload.get("language") or "zh",
        "preserveEnglishTerms": bool(payload.get("preserveEnglishTerms", True)),
        "generationMode": generation_mode,
        "llm": {
            "provider": llm_provider if llm_enabled else "none",
            "baseUrl": payload.get("llmEndpoint") or "",
            "model": payload.get("llmModel") or "",
            "apiKeyEnv": payload.get("apiKeyEnv") or "OPENAI_API_KEY",
            "temperature": 0.2,
        },
    }
    return normalize_config(config)


def create_input_dir() -> dict[str, Any]:
    input_dir = (ROOT / str(get_config().get("inputDir", "input_materials"))).resolve()
    input_dir.mkdir(parents=True, exist_ok=True)
    return {"ok": True, "path": str(input_dir)}


def safe_project_path(relative_path: str) -> Path:
    target = (ROOT / relative_path).resolve()
    try:
        target.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise ValueError("Only project-internal paths can be opened.") from exc
    return target


def open_project_target(target_type: str, run_id: str | None = None) -> dict[str, str]:
    config = get_config()
    if target_type == "input":
        target = safe_project_path(str(config.get("inputDir", "input_materials")))
        target.mkdir(parents=True, exist_ok=True)
    elif target_type == "latest":
        runs = runs_status(config)
        if not runs:
            raise ValueError("No generated site is available yet.")
        target = safe_project_path(str(Path(runs[0]["outputDir"]) / "index.html"))
    elif target_type == "run":
        if not run_id:
            raise ValueError("runId is required.")
        target = safe_project_path(str(Path(config.get("outputDir", "output_sites")) / run_id))
    elif target_type == "site":
        if not run_id:
            raise ValueError("runId is required.")
        target = safe_project_path(str(Path(config.get("outputDir", "output_sites")) / run_id / "index.html"))
    elif target_type == "qa":
        if not run_id:
            raise ValueError("runId is required.")
        html_report = safe_project_path(str(Path(config.get("outputDir", "output_sites")) / run_id / "qa_report.html"))
        json_report = safe_project_path(str(Path(config.get("outputDir", "output_sites")) / run_id / "qa_report.json"))
        target = html_report if html_report.exists() else json_report
    else:
        raise ValueError("Unknown open target.")
    if not target.exists():
        raise ValueError(f"Path does not exist: {target}")
    if sys.platform.startswith("win"):
        os.startfile(target)  # type: ignore[attr-defined]
    else:
        webbrowser.open(target.as_uri() if target.is_file() else str(target))
    return {"path": str(target)}


def test_llm_connection(payload: dict[str, Any]) -> dict[str, Any]:
    config = dashboard_payload_to_config({**payload, "llmEnabled": True})
    client = LLMClient(config.get("llm") or {})
    ok, message = client.test_connection()
    return {
        "ok": ok,
        "message": message,
        "diagnostics": client.diagnostics(),
        "llmCallsAttempted": client.calls_attempted,
        "llmCallsSucceeded": client.calls_succeeded,
        "llmCallsFailed": client.calls_failed,
    }
