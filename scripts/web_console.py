from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.generate_site import DEFAULT_CONFIG, ROOT, deep_update, generate_from_config, load_config, scan_input_files
from scripts.run_registry import load_runs
from scripts.utils import SUPPORTED_EXTENSIONS, detect_lecture_number


CONFIG_PATH = ROOT / "config.json"
ENV_PATH = ROOT / ".env"
GENERATION_LOCK = threading.Lock()
LAST_LOG: list[str] = []


def json_dumps(data: Any) -> bytes:
    return json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")


def read_json_body(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    length = int(handler.headers.get("Content-Length", "0") or "0")
    if length <= 0:
        return {}
    raw = handler.rfile.read(length)
    return json.loads(raw.decode("utf-8") or "{}")


def relative_or_absolute(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def current_config() -> dict[str, Any]:
    return load_config(CONFIG_PATH if CONFIG_PATH.exists() else None)


def write_config(config: dict[str, Any]) -> None:
    CONFIG_PATH.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")


def update_env_var(name: str, value: str) -> None:
    if not name or not value:
        return
    lines = ENV_PATH.read_text(encoding="utf-8").splitlines() if ENV_PATH.exists() else []
    prefix = f"{name}="
    updated = False
    next_lines = []
    for line in lines:
        if line.startswith(prefix):
            next_lines.append(f"{name}={value}")
            updated = True
        else:
            next_lines.append(line)
    if not updated:
        next_lines.append(f"{name}={value}")
    ENV_PATH.write_text("\n".join(next_lines) + "\n", encoding="utf-8")


def input_file_records(config: dict[str, Any]) -> list[dict[str, Any]]:
    input_dir = (ROOT / str(config.get("inputDir", "input_materials"))).resolve()
    if not input_dir.exists():
        return []
    records = []
    for path in scan_input_files(input_dir):
        stat = path.stat()
        records.append(
            {
                "name": path.name,
                "path": relative_or_absolute(path),
                "extension": path.suffix.lower(),
                "lectureNumber": detect_lecture_number(path),
                "sizeBytes": stat.st_size,
            }
        )
    return records


def run_records(config: dict[str, Any]) -> list[dict[str, Any]]:
    output_dir = (ROOT / str(config.get("outputDir", "output_sites"))).resolve()
    runs = load_runs(output_dir)
    return list(reversed(runs))


def latest_run(config: dict[str, Any]) -> dict[str, Any] | None:
    runs = run_records(config)
    return runs[0] if runs else None


def safe_output_file(config: dict[str, Any], url_path: str) -> Path | None:
    output_dir = (ROOT / str(config.get("outputDir", "output_sites"))).resolve()
    suffix = unquote(url_path.removeprefix("/site/")).replace("/", os.sep)
    target = (output_dir / suffix).resolve()
    try:
        target.relative_to(output_dir.resolve())
    except ValueError:
        return None
    return target if target.is_file() else None


def open_path(path: Path) -> None:
    if sys.platform.startswith("win"):
        os.startfile(path)  # type: ignore[attr-defined]
    else:
        webbrowser.open(path.as_uri() if path.is_file() else str(path))


CONSOLE_HTML = r"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Lecture Knowledge Console</title>
  <style>
    :root { --bg:#f6f3ee; --card:#fffdf8; --ink:#202938; --muted:#667085; --line:#ded7ca; --blue:#174a7c; --green:#147a50; --red:#b42318; }
    * { box-sizing: border-box; }
    body { margin:0; background:var(--bg); color:var(--ink); font:15px/1.65 "Segoe UI","Microsoft YaHei",Arial,sans-serif; }
    header { position:sticky; top:0; z-index:2; display:flex; justify-content:space-between; gap:16px; align-items:center; padding:18px 28px; border-bottom:1px solid var(--line); background:rgba(255,253,248,.94); backdrop-filter:blur(10px); }
    h1 { margin:0; font-size:22px; }
    main { display:grid; grid-template-columns: 340px minmax(0, 1fr); gap:20px; max-width:1280px; margin:0 auto; padding:22px; }
    .panel { border:1px solid var(--line); border-radius:18px; background:var(--card); box-shadow:0 10px 28px rgba(40,35,25,.08); padding:18px; }
    .panel h2 { margin:0 0 10px; font-size:17px; color:var(--blue); }
    .stack { display:grid; gap:14px; }
    label { display:grid; gap:6px; font-weight:700; color:var(--blue); }
    input, select { width:100%; border:1px solid var(--line); border-radius:10px; padding:9px 10px; background:#fff; color:var(--ink); font:inherit; }
    button, .button { border:1px solid var(--line); border-radius:999px; background:#fff; color:var(--blue); cursor:pointer; padding:9px 13px; font-weight:800; text-decoration:none; display:inline-flex; align-items:center; justify-content:center; gap:6px; }
    button.primary { background:var(--blue); border-color:var(--blue); color:#fff; }
    button.success { background:var(--green); border-color:var(--green); color:#fff; }
    button:disabled { opacity:.55; cursor:not-allowed; }
    .actions { display:flex; flex-wrap:wrap; gap:10px; margin-top:12px; }
    .muted { color:var(--muted); font-size:13px; }
    .status { padding:10px 12px; border-radius:12px; background:#eef5ff; color:var(--blue); }
    .status.error { background:#fff0f0; color:var(--red); }
    .status.ok { background:#ecfdf3; color:var(--green); }
    table { width:100%; border-collapse:collapse; }
    th,td { border-bottom:1px solid var(--line); padding:9px 8px; text-align:left; vertical-align:top; }
    th { color:var(--blue); font-size:12px; text-transform:uppercase; letter-spacing:.06em; }
    .tabs { display:flex; gap:8px; flex-wrap:wrap; margin-bottom:14px; }
    .tab.active { background:var(--blue); color:#fff; }
    .view { display:none; }
    .view.active { display:block; }
    pre { overflow:auto; white-space:pre-wrap; word-break:break-word; border:1px solid var(--line); border-radius:14px; background:#101827; color:#e6edf6; padding:14px; min-height:150px; }
    .run-card { display:grid; gap:8px; border:1px solid var(--line); border-radius:14px; padding:12px; margin-bottom:10px; background:#fff; }
    .run-card strong { color:var(--blue); }
    @media (max-width: 860px) { main { grid-template-columns:1fr; padding:14px; } header { align-items:flex-start; flex-direction:column; } }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>Local-first Lecture Knowledge Console</h1>
      <div class="muted">本地控制台：检测文件、生成项目、查看版本、配置 LLM、打开结果网页。</div>
    </div>
    <div class="actions">
      <button id="refresh">Refresh</button>
      <button id="open-input">Open input_materials</button>
      <button id="open-latest" class="success">Open latest site</button>
    </div>
  </header>
  <main>
    <aside class="stack">
      <section class="panel">
        <h2>Project</h2>
        <label>Project name <input id="projectName"></label>
        <label>Input folder <input id="inputDir"></label>
        <label>Output folder <input id="outputDir"></label>
        <label>Minimum content chars <input id="minContentChars" type="number" min="0"></label>
        <div class="actions"><button id="save-config">Save config</button><button id="generate" class="primary">Generate site</button></div>
        <p class="muted">文件仍然放在本地 input_materials，不提供上传入口。</p>
      </section>
      <section class="panel">
        <h2>LLM Config</h2>
        <label>Provider
          <select id="llmProvider"><option value="none">none</option><option value="openai_compatible">openai_compatible</option><option value="ollama">ollama</option></select>
        </label>
        <label>Base URL <input id="llmBaseUrl" placeholder="http://localhost:11434 or https://api.example.com/v1"></label>
        <label>Model <input id="llmModel" placeholder="model name"></label>
        <label>API key env name <input id="llmApiKeyEnv" placeholder="OPENAI_API_KEY"></label>
        <label>API key value <input id="llmApiKeyValue" type="password" placeholder="optional; saved to local .env"></label>
        <p class="muted">Ollama 不需要 API key。API key 只写入本地 .env。</p>
      </section>
    </aside>
    <section class="panel">
      <div class="tabs">
        <button class="tab active" data-tab="files">Files</button>
        <button class="tab" data-tab="runs">Versions</button>
        <button class="tab" data-tab="log">Log</button>
      </div>
      <div id="status" class="status">Loading...</div>
      <div class="view active" id="view-files">
        <h2>Detected input files</h2>
        <div id="files"></div>
      </div>
      <div class="view" id="view-runs">
        <h2>Generated versions</h2>
        <div id="runs"></div>
      </div>
      <div class="view" id="view-log">
        <h2>Generation log</h2>
        <pre id="log"></pre>
      </div>
    </section>
  </main>
  <script>
    const $ = (id) => document.getElementById(id);
    let state = {};
    function setStatus(text, cls = "") { const el = $("status"); el.className = "status " + cls; el.textContent = text; }
    async function api(path, options = {}) {
      const res = await fetch(path, { headers: {"Content-Type":"application/json"}, ...options });
      const data = await res.json();
      if (!res.ok || data.ok === false) throw new Error(data.error || res.statusText);
      return data;
    }
    function formConfig() {
      return {
        projectName: $("projectName").value.trim(),
        inputDir: $("inputDir").value.trim(),
        outputDir: $("outputDir").value.trim(),
        minContentChars: Number($("minContentChars").value || 0),
        llm: {
          provider: $("llmProvider").value,
          baseUrl: $("llmBaseUrl").value.trim(),
          model: $("llmModel").value.trim(),
          apiKeyEnv: $("llmApiKeyEnv").value.trim() || "OPENAI_API_KEY",
          apiKeyValue: $("llmApiKeyValue").value,
          temperature: 0.2
        }
      };
    }
    function fillConfig(config) {
      $("projectName").value = config.projectName || "";
      $("inputDir").value = config.inputDir || "input_materials";
      $("outputDir").value = config.outputDir || "output_sites";
      $("minContentChars").value = config.minContentChars ?? 300;
      $("llmProvider").value = config.llm?.provider || "none";
      $("llmBaseUrl").value = config.llm?.baseUrl || config.llm?.endpoint || "";
      $("llmModel").value = config.llm?.model || "";
      $("llmApiKeyEnv").value = config.llm?.apiKeyEnv || "OPENAI_API_KEY";
    }
    function renderFiles(files) {
      if (!files.length) { $("files").innerHTML = "<p class='muted'>没有检测到 PDF / MD / DOCX。请把文件放入 input_materials 后点击 Refresh。</p>"; return; }
      $("files").innerHTML = `<table><thead><tr><th>Name</th><th>Type</th><th>Lecture</th><th>Size</th></tr></thead><tbody>${files.map(f => `<tr><td>${f.name}</td><td>${f.extension}</td><td>${f.lectureNumber ?? "Unit"}</td><td>${Math.round(f.sizeBytes/1024)} KB</td></tr>`).join("")}</tbody></table>`;
    }
    function renderRuns(runs) {
      if (!runs.length) { $("runs").innerHTML = "<p class='muted'>还没有生成版本。</p>"; return; }
      $("runs").innerHTML = runs.map(run => `<article class="run-card"><strong>${run.runId}</strong><span class="muted">${run.createdAt} · ${run.processedFiles?.length || 0} files · LLM ${run.llmEnabled ? "enabled" : "disabled"}</span><div class="actions"><a class="button" target="_blank" href="/site/${run.runId}/index.html">Open in browser</a><button data-open-run="${run.runId}">Open folder</button></div></article>`).join("");
      document.querySelectorAll("[data-open-run]").forEach(btn => btn.addEventListener("click", () => openTarget("run", btn.dataset.openRun)));
    }
    async function refresh() {
      const data = await api("/api/status");
      state = data;
      fillConfig(data.config);
      renderFiles(data.files);
      renderRuns(data.runs);
      $("log").textContent = (data.lastLog || []).join("\n");
      setStatus(`Ready. ${data.files.length} input file(s), ${data.runs.length} generated version(s).`, "ok");
    }
    async function saveConfig() {
      await api("/api/config", { method:"POST", body: JSON.stringify(formConfig()) });
      $("llmApiKeyValue").value = "";
      await refresh();
      setStatus("Config saved.", "ok");
    }
    async function generate() {
      $("generate").disabled = true;
      setStatus("Generating site. This may take a few minutes...");
      $("log").textContent = "";
      try {
        const data = await api("/api/generate", { method:"POST", body: JSON.stringify({ config: formConfig(), saveConfig: true }) });
        $("llmApiKeyValue").value = "";
        $("log").textContent = data.log.join("\n");
        await refresh();
        setStatus(`Generated: ${data.result.metadata.runId}`, "ok");
      } catch (err) {
        setStatus(err.message, "error");
      } finally {
        $("generate").disabled = false;
      }
    }
    async function openTarget(type, runId = "") {
      await api("/api/open", { method:"POST", body: JSON.stringify({ type, runId }) });
    }
    document.querySelectorAll(".tab").forEach(btn => btn.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach(x => x.classList.remove("active"));
      document.querySelectorAll(".view").forEach(x => x.classList.remove("active"));
      btn.classList.add("active"); $("view-" + btn.dataset.tab).classList.add("active");
    }));
    $("refresh").addEventListener("click", () => refresh().catch(e => setStatus(e.message, "error")));
    $("save-config").addEventListener("click", () => saveConfig().catch(e => setStatus(e.message, "error")));
    $("generate").addEventListener("click", generate);
    $("open-input").addEventListener("click", () => openTarget("input"));
    $("open-latest").addEventListener("click", () => openTarget("latest").catch(e => setStatus(e.message, "error")));
    refresh().catch(e => setStatus(e.message, "error"));
  </script>
</body>
</html>"""


class ConsoleHandler(BaseHTTPRequestHandler):
    server_version = "LectureKnowledgeConsole/0.1"

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"[console] {self.address_string()} - {fmt % args}")

    def send_json(self, data: Any, status: int = 200) -> None:
        body = json_dumps(data)
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_text(self, text: str, content_type: str = "text/html; charset=utf-8") -> None:
        body = text.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        config = current_config()
        if parsed.path == "/":
            self.send_text(CONSOLE_HTML)
            return
        if parsed.path == "/api/status":
            runs = run_records(config)
            self.send_json(
                {
                    "ok": True,
                    "root": str(ROOT),
                    "config": config,
                    "supportedExtensions": sorted(SUPPORTED_EXTENSIONS),
                    "files": input_file_records(config),
                    "runs": runs,
                    "latestRun": runs[0] if runs else None,
                    "lastLog": LAST_LOG,
                }
            )
            return
        if parsed.path.startswith("/site/"):
            target = safe_output_file(config, parsed.path)
            if not target:
                self.send_json({"ok": False, "error": "File not found or outside output directory."}, HTTPStatus.NOT_FOUND)
                return
            content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
            data = target.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        self.send_json({"ok": False, "error": "Not found."}, HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802
        try:
            if self.path == "/api/config":
                data = read_json_body(self)
                config = clean_config(data)
                write_config(config)
                update_env_var(config.get("llm", {}).get("apiKeyEnv", "OPENAI_API_KEY"), data.get("llm", {}).get("apiKeyValue", ""))
                self.send_json({"ok": True, "config": current_config()})
                return
            if self.path == "/api/generate":
                data = read_json_body(self)
                config = clean_config(data.get("config") or current_config())
                if data.get("saveConfig", True):
                    write_config(config)
                    update_env_var(config.get("llm", {}).get("apiKeyEnv", "OPENAI_API_KEY"), data.get("config", {}).get("llm", {}).get("apiKeyValue", ""))
                if GENERATION_LOCK.locked():
                    self.send_json({"ok": False, "error": "Generation is already running."}, HTTPStatus.CONFLICT)
                    return
                logs: list[str] = []
                with GENERATION_LOCK:
                    LAST_LOG.clear()
                    def log(line: str = "") -> None:
                        logs.append(str(line))
                        LAST_LOG.append(str(line))
                    result = generate_from_config(config, open_after=False, log=log)
                self.send_json({"ok": True, "result": result, "log": logs})
                return
            if self.path == "/api/open":
                data = read_json_body(self)
                config = current_config()
                open_type = data.get("type")
                if open_type == "input":
                    target = (ROOT / str(config.get("inputDir", "input_materials"))).resolve()
                elif open_type == "latest":
                    run = latest_run(config)
                    if not run:
                        raise RuntimeError("No generated site yet.")
                    target = ROOT / run["outputDir"] / "index.html"
                elif open_type == "run":
                    run_id = str(data.get("runId") or "")
                    target = (ROOT / str(config.get("outputDir", "output_sites")) / run_id).resolve()
                else:
                    raise RuntimeError("Unknown open target.")
                target.mkdir(parents=True, exist_ok=True) if open_type == "input" else None
                open_path(target)
                self.send_json({"ok": True, "path": str(target)})
                return
            self.send_json({"ok": False, "error": "Not found."}, HTTPStatus.NOT_FOUND)
        except Exception as exc:  # noqa: BLE001 - local console should report all errors as JSON
            self.send_json({"ok": False, "error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)


def clean_config(data: dict[str, Any]) -> dict[str, Any]:
    config = json.loads(json.dumps(DEFAULT_CONFIG))
    deep_update(config, data)
    llm = dict(config.get("llm") or {})
    llm.pop("apiKeyValue", None)
    config["llm"] = llm
    return config


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Start the local lecture knowledge web console.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--open", action="store_true", help="Open the console in the default browser.")
    args = parser.parse_args(argv)

    server = ThreadingHTTPServer((args.host, args.port), ConsoleHandler)
    url = f"http://{args.host}:{args.port}/"
    print(f"Local web console running at {url}")
    print("Press Ctrl+C to stop.")
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping console.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
