from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def registry_path(output_dir: Path) -> Path:
    return output_dir / "runs.json"


def load_runs(output_dir: Path) -> list[dict[str, Any]]:
    path = registry_path(output_dir)
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def register_run(output_dir: Path, run: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    runs = load_runs(output_dir)
    runs.append(run)
    registry_path(output_dir).write_text(json.dumps(runs, ensure_ascii=False, indent=2), encoding="utf-8")


def list_runs(output_dir: Path) -> list[dict[str, Any]]:
    return load_runs(output_dir)

