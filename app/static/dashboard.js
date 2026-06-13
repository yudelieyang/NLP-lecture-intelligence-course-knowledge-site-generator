const $ = (id) => document.getElementById(id);

const I18N = {
  zh: {
    headerEyebrow: "本地优先控制台",
    appTitle: "Local Lecture Knowledge App",
    appSubtitle: "从本地课程材料生成版本化学习知识站点。",
    uiLanguage: "界面语言",
    refreshFiles: "刷新文件列表",
    openInput: "打开 input_materials 文件夹",
    inputMaterials: "输入材料",
    checking: "检查中...",
    materialsHelp: "支持：.pdf、.md、.docx。路线图：.pptx、.ipynb。",
    materialsEmpty: "请把 PDF / MD / DOCX 文件放入 input_materials/ 文件夹，然后点击刷新。",
    createInput: "创建 input_materials 文件夹",
    projectSettings: "项目设置",
    projectName: "项目名称",
    minContentChars: "最小文本长度",
    contentLanguage: "生成内容语言 / 界面快捷切换",
    preserveTerms: "保留英文专业术语",
    enableLlm: "启用 LLM",
    generationMode: "Generation Mode",
    llmSettings: "LLM 设置",
    keyWarning: "仅限本地浏览器界面使用。不要提交 key，不要把本应用暴露到公网。",
    provider: "Provider",
    endpoint: "Endpoint",
    model: "Model",
    apiKeyEnv: "API key 环境变量名",
    testLlm: "测试 LLM 连接",
    envHint: "请优先在 .env 中配置真实 API key。网页不会显示 API key。",
    llmDisabledHint: "Chinese summaries require LLM. The generated site will show cleaned source excerpts instead.",
    llmFailedHint: "LLM connection failed. The generated site will use cleaned source excerpts.",
    llmConnectedHint: "LLM connected. Chinese source-grounded summaries will be generated.",
    generate: "生成",
    generateHelp: "每次生成都会创建新的 output_sites/<run_id>/，不会覆盖旧版本。",
    generateNew: "生成新站点",
    versions: "历史版本",
    refreshVersions: "刷新版本",
    logs: "状态 / 日志",
    ready: "就绪。",
    noRun: "还没有运行记录。",
    supportedOther: (supported, other) => `${supported} 个支持 · ${other} 个其他`,
    file: "文件",
    type: "类型",
    size: "大小",
    status: "状态",
    none: "无",
    noVersions: "还没有生成版本。",
    inputFiles: (count) => `${count} 个输入文件`,
    open: "打开",
    showFolder: "显示文件夹",
    qaReport: "QA 报告",
    qaStatus: (status) => `QA：${status || "未生成"}`,
    llmTelemetry: "LLM 生成统计",
    llmCalls: "调用",
    llmParse: "解析成功",
    llmRepair: "修复",
    llmSummary: "LLM Summary",
    deleteSoon: "删除功能待加入",
    checkingInput: "正在检查 input_materials...",
    generating: "正在生成新站点，请稍候...",
    openGenerated: "打开生成站点",
    openOutputFolder: "打开输出文件夹",
    siteGenerated: "站点生成成功。",
    errorPrefix: "错误",
    inputReady: "input_materials 文件夹已准备好。",
  },
  en: {
    headerEyebrow: "Local-first dashboard",
    appTitle: "Local Lecture Knowledge App",
    appSubtitle: "Generate versioned study knowledge sites from local lecture materials.",
    uiLanguage: "UI language",
    refreshFiles: "Refresh file list",
    openInput: "Open input_materials folder",
    inputMaterials: "Input Materials",
    checking: "Checking...",
    materialsHelp: "Supported: .pdf, .md, .docx. Roadmap: .pptx, .ipynb.",
    materialsEmpty: "Put PDF / MD / DOCX files into input_materials/, then click Refresh.",
    createInput: "Create input_materials folder",
    projectSettings: "Project Settings",
    projectName: "Project name",
    minContentChars: "Min content chars",
    contentLanguage: "Content language / UI quick switch",
    preserveTerms: "Preserve English terms",
    enableLlm: "Enable LLM",
    generationMode: "Generation Mode",
    llmSettings: "LLM Settings",
    keyWarning: "Browser/local UI only. Do not commit keys. Do not expose this app publicly.",
    provider: "Provider",
    endpoint: "Endpoint",
    model: "Model",
    apiKeyEnv: "API key environment variable",
    testLlm: "Test LLM Connection",
    envHint: "Prefer configuring real API keys in .env. The webpage will not display API keys.",
    llmDisabledHint: "Chinese summaries require LLM. The generated site will show cleaned source excerpts instead.",
    llmFailedHint: "LLM connection failed. The generated site will use cleaned source excerpts.",
    llmConnectedHint: "LLM connected. Chinese source-grounded summaries will be generated.",
    generate: "Generate",
    generateHelp: "Each run creates a new output_sites/<run_id>/ version and does not overwrite old versions.",
    generateNew: "Generate New Site",
    versions: "Generated Versions",
    refreshVersions: "Refresh versions",
    logs: "Status / Logs",
    ready: "Ready.",
    noRun: "No run yet.",
    supportedOther: (supported, other) => `${supported} supported · ${other} other`,
    file: "File",
    type: "Type",
    size: "Size",
    status: "Status",
    none: "none",
    noVersions: "No generated versions yet.",
    inputFiles: (count) => `${count} input file(s)`,
    open: "Open",
    showFolder: "Show folder",
    qaReport: "QA Report",
    qaStatus: (status) => `QA: ${status || "not generated"}`,
    llmTelemetry: "LLM telemetry",
    llmCalls: "Calls",
    llmParse: "Parse succeeded",
    llmRepair: "Repair",
    llmSummary: "LLM Summary",
    deleteSoon: "Delete coming soon",
    checkingInput: "Checking input_materials...",
    generating: "Generating new site. Please wait...",
    openGenerated: "Open generated site",
    openOutputFolder: "Open output folder",
    siteGenerated: "Site generated successfully.",
    errorPrefix: "ERROR",
    inputReady: "input_materials folder is ready.",
  },
};

let uiLang = localStorage.getItem("dashboard-ui-language") || "zh";
let lastMaterials = null;
let lastRuns = null;

function t(key, ...args) {
  const value = I18N[uiLang]?.[key] ?? I18N.en[key] ?? key;
  return typeof value === "function" ? value(...args) : value;
}

function applyLanguage() {
  document.documentElement.lang = uiLang === "zh" ? "zh-CN" : "en";
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  if ($("uiLanguage")) $("uiLanguage").value = uiLang;
  if ($("language")) $("language").value = uiLang;
  if (lastMaterials) renderMaterials(lastMaterials);
  if (lastRuns) renderRuns(lastRuns);
  const box = $("statusBox");
  if (box?.dataset.statusKey) box.textContent = t(box.dataset.statusKey);
}

function setStatus(message, type = "", key = "") {
  const box = $("statusBox");
  box.className = `status ${type}`;
  box.textContent = message;
  box.dataset.statusKey = key;
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await response.json();
  if (!response.ok || data.ok === false) {
    throw new Error(data.detail || data.error || data.message || response.statusText);
  }
  return data;
}

function formatSize(bytes) {
  if (bytes > 1024 * 1024) return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
  if (bytes > 1024) return `${Math.round(bytes / 1024)} KB`;
  return `${bytes} B`;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function getPayload() {
  const generationMode = document.querySelector("input[name='generationMode']:checked")?.value || "offline";
  return {
    projectName: $("projectName").value.trim() || "Local Lecture Knowledge Site",
    minContentChars: Number($("minContentChars").value || 3000),
    language: $("language").value,
    preserveEnglishTerms: $("preserveEnglishTerms").checked,
    generationMode,
    llmEnabled: generationMode === "online_llm",
    llmProvider: $("llmProvider").value,
    llmEndpoint: $("llmEndpoint").value.trim(),
    llmModel: $("llmModel").value.trim(),
    apiKeyEnv: $("apiKeyEnv").value.trim() || "OPENAI_API_KEY",
  };
}

function applyConfig(config) {
  $("projectName").value = config.projectName || "Local Lecture Knowledge Site";
  $("minContentChars").value = config.minContentChars ?? 3000;
  $("language").value = config.language || "zh";
  $("preserveEnglishTerms").checked = config.preserveEnglishTerms !== false;
  const online = (config.generationMode || ((config.llm?.provider || "none") !== "none" ? "online_llm" : "offline")) === "online_llm";
  if ($("modeOffline")) $("modeOffline").checked = !online;
  if ($("modeOnlineLlm")) $("modeOnlineLlm").checked = online;
  $("llmProvider").value = config.llm?.provider === "ollama" ? "ollama" : "openai_compatible";
  $("llmEndpoint").value = config.llm?.baseUrl || config.llm?.endpoint || "";
  $("llmModel").value = config.llm?.model || "";
  $("apiKeyEnv").value = config.llm?.apiKeyEnv || "OPENAI_API_KEY";
  updateLlmVisibility();
}

function updateLlmVisibility() {
  const online = document.querySelector("input[name='generationMode']:checked")?.value === "online_llm";
  $("llmPanel").style.display = online ? "block" : "none";
  const hint = $("llmModeHint");
  if (hint) {
    hint.textContent = online ? t("llmFailedHint") : t("llmDisabledHint");
  }
}

function renderMaterials(data) {
  lastMaterials = data;
  $("materialsSummary").textContent = t("supportedOther", data.supportedCount, data.unsupportedCount);
  $("materialsEmpty").hidden = data.files.length > 0;
  if (!data.files.length) {
    $("materialsTable").innerHTML = "";
    return;
  }
  $("materialsTable").innerHTML = `<table>
    <thead><tr><th>${t("file")}</th><th>${t("type")}</th><th>${t("size")}</th><th>${t("status")}</th></tr></thead>
    <tbody>${data.files.map((file) => `<tr>
      <td>${escapeHtml(file.name)}</td>
      <td>${escapeHtml(file.extension || `(${t("none")})`)}</td>
      <td>${formatSize(file.sizeBytes)}</td>
      <td class="status-${escapeHtml(file.status)}">${escapeHtml(file.status)}</td>
    </tr>`).join("")}</tbody>
  </table>`;
}

function renderRuns(data) {
  lastRuns = data;
  const runs = data.runs || [];
  if (!runs.length) {
    $("runsList").innerHTML = `<p class="muted">${t("noVersions")}</p>`;
    return;
  }
  $("runsList").innerHTML = runs.map((run) => `<article class="run-card">
    <strong>${escapeHtml(run.projectName || "Project")} · ${escapeHtml(run.runId)}</strong>
    <span class="muted">${escapeHtml(run.createdAt || "")} · ${t("inputFiles", (run.processedFiles || []).length)}</span>
    <span class="muted">${escapeHtml(run.outputDir || "")}</span>
    <span class="qa-status qa-${escapeHtml(run.qaReport?.status || "missing")}">${escapeHtml(t("qaStatus", run.qaReport?.status))}</span>
    <div class="button-row">
      <button data-open-site="${escapeHtml(run.runId)}">${t("open")}</button>
      <button data-open-folder="${escapeHtml(run.runId)}">${t("showFolder")}</button>
      <button data-open-qa="${escapeHtml(run.runId)}" ${run.qaReport ? "" : "disabled"}>${t("qaReport")}</button>
      <button disabled title="${t("deleteSoon")}">${t("deleteSoon")}</button>
    </div>
  </article>`).join("");
  document.querySelectorAll("[data-open-site]").forEach((btn) => {
    btn.addEventListener("click", () => openTarget("site", btn.dataset.openSite));
  });
  document.querySelectorAll("[data-open-folder]").forEach((btn) => {
    btn.addEventListener("click", () => openTarget("run", btn.dataset.openFolder));
  });
  document.querySelectorAll("[data-open-qa]").forEach((btn) => {
    btn.addEventListener("click", () => openTarget("qa", btn.dataset.openQa));
  });
}

function renderGenerationResult(result) {
  const telemetry = result.llmTelemetry || {};
  const summary = result.llmSummary || {};
  const telemetryHtml = telemetry.llmEnabled ? `<div class="telemetry-grid">
    <span>${t("llmCalls")}: ${Number(telemetry.llmCallsAttempted || 0)} / ${Number(telemetry.llmCallsSucceeded || 0)} / ${Number(telemetry.llmCallsFailed || 0)}</span>
    <span>${t("llmParse")}: ${Number(telemetry.llmParseSucceeded || 0)}</span>
    <span>${t("llmRepair")}: ${Number(telemetry.llmRepairAttempted || 0)} / ${Number(telemetry.llmRepairSucceeded || 0)}</span>
    <span>${t("llmSummary")}: ${Number(summary.successCount || 0)} success / ${Number(summary.missingCount || 0)} missing</span>
  </div>` : "";
  $("generationResult").innerHTML = `<strong>${escapeHtml(result.runId)}</strong><br>${escapeHtml(result.outputPath)}${telemetryHtml}<div class="button-row"><button id="openGeneratedBtn">${t("openGenerated")}</button><button id="openOutputFolderBtn">${t("openOutputFolder")}</button></div>`;
}

async function refreshMaterials() {
  const data = await api("/api/materials");
  renderMaterials(data);
}

async function refreshRuns() {
  const data = await api("/api/runs");
  renderRuns(data);
}

async function loadConfig() {
  const data = await api("/api/config");
  applyConfig(data.config);
}

async function refreshAll() {
  await Promise.all([loadConfig(), refreshMaterials(), refreshRuns()]);
  applyLanguage();
  setStatus(t("ready"), "ok", "ready");
}

async function generateSite() {
  $("generateBtn").disabled = true;
  $("generationResult").hidden = true;
  $("logs").textContent = `${t("checkingInput")}\n`;
  setStatus(t("generating"));
  try {
    const result = await api("/api/generate", {
      method: "POST",
      body: JSON.stringify(getPayload()),
    });
    $("logs").textContent = (result.logs || []).join("\n");
    $("generationResult").hidden = false;
    renderGenerationResult(result);
    $("openGeneratedBtn").addEventListener("click", () => openTarget("site", result.runId));
    $("openOutputFolderBtn").addEventListener("click", () => openTarget("run", result.runId));
    setStatus(result.message || t("siteGenerated"), "ok");
    await refreshRuns();
  } catch (error) {
    setStatus(error.message, "error");
    $("logs").textContent += `\n${t("errorPrefix")}: ${error.message}`;
  } finally {
    $("generateBtn").disabled = false;
  }
}

async function openTarget(type, runId = "") {
  await api("/api/open", {
    method: "POST",
    body: JSON.stringify({ type, runId }),
  });
}

async function createInputDir() {
  await api("/api/create-input-dir", { method: "POST", body: "{}" });
  await refreshMaterials();
  setStatus(t("inputReady"), "ok");
}

async function testLlm() {
  const result = await api("/api/test-llm", {
    method: "POST",
    body: JSON.stringify(getPayload()),
  });
  setStatus(result.message, result.ok ? "ok" : "error");
  const hint = $("llmModeHint");
  if (hint) hint.textContent = result.ok ? t("llmConnectedHint") : t("llmFailedHint");
}

$("uiLanguage").addEventListener("change", () => {
  uiLang = $("uiLanguage").value;
  localStorage.setItem("dashboard-ui-language", uiLang);
  applyLanguage();
});
$("language").addEventListener("change", () => {
  uiLang = $("language").value;
  localStorage.setItem("dashboard-ui-language", uiLang);
  applyLanguage();
});
$("refreshBtn").addEventListener("click", () => refreshMaterials().catch((error) => setStatus(error.message, "error")));
$("refreshRunsBtn").addEventListener("click", () => refreshRuns().catch((error) => setStatus(error.message, "error")));
$("openInputBtn").addEventListener("click", () => openTarget("input").catch((error) => setStatus(error.message, "error")));
$("createInputBtn").addEventListener("click", () => createInputDir().catch((error) => setStatus(error.message, "error")));
$("generateBtn").addEventListener("click", generateSite);
$("testLlmBtn").addEventListener("click", () => testLlm().catch((error) => setStatus(error.message, "error")));
document.querySelectorAll("input[name='generationMode']").forEach((input) => input.addEventListener("change", updateLlmVisibility));

applyLanguage();
refreshAll().catch((error) => setStatus(error.message, "error"));
