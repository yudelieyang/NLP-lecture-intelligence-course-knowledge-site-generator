const sidebar = document.getElementById("sidebar");
const menu = document.getElementById("menu-toggle");
const theme = document.getElementById("theme-toggle");
const mobileTheme = document.getElementById("theme-toggle-mobile");
const siteLanguage = document.getElementById("site-ui-language");
const topButton = document.getElementById("back-to-top");
const main = document.querySelector("main");
const pageSections = [...main.querySelectorAll(":scope > .lecture-section")];
const pages = pageSections.filter((page) => page.id !== "unprocessed");
const pageIds = pages.map((page) => page.id);
const lecturePages = pages.filter((page) => page.id.startsWith("lecture-"));
const navLinks = [...document.querySelectorAll(".sidebar a[href^='#']")];
const lectureLinks = [...document.querySelectorAll(".nav-lecture")];
const siteGenerationMode = document.body.dataset.generationMode || "offline";

pageSections.forEach((page) => page.classList.add("lecture-page"));

const siteUiTranslations = {
  zh: {
    menu: "目录",
    theme: "主题",
    toggleTheme: "切换主题",
    uiLanguage: "界面语言",
    searchPlaceholder: "搜索笔记...",
    overview: "课程总览",
    failedFiles: "未能处理的文件",
    practiceTitle: "备考题生成器",
    practiceDesc: "Source-grounded Practice 严格基于资料；Creative Extension 可生成应用场景和系统设计题。",
    questionSource: "题目来源",
    keyword: "关键词",
    questionType: "题型",
    difficulty: "难度",
    count: "数量",
    answerDisplay: "答案显示",
    generatePractice: "生成练习题",
    revealAnswers: "显示全部答案",
    copyQuestions: "复制题目",
    practiceHint: "重复点击 Generate 会重新采样上下文，并尽量生成不同角度、不同术语和不同场景的问题。",
  },
  en: {
    menu: "Menu",
    theme: "Theme",
    toggleTheme: "Toggle theme",
    uiLanguage: "UI language",
    searchPlaceholder: "Search notes...",
    overview: "Overview",
    failedFiles: "Failed files",
    practiceTitle: "Exam Practice Generator",
    practiceDesc: "Source-grounded Practice stays within the source; Creative Extension can generate application and system-design scenarios.",
    questionSource: "Question source",
    keyword: "Keyword",
    questionType: "Question type",
    difficulty: "Difficulty",
    count: "Count",
    answerDisplay: "Answer display",
    generatePractice: "Generate Practice Questions",
    revealAnswers: "Reveal all answers",
    copyQuestions: "Copy questions",
    practiceHint: "Click Generate repeatedly to resample context and vary angles, terms, and scenarios.",
  },
};

Object.assign(siteUiTranslations.zh, {
  practiceTypeHint: "选择具体题型时只生成该题型；Mixed 才会混合题型。",
  "mode.generationMode": "生成模式",
  "mode.offline": "本地离线模式",
  "mode.onlineLlm": "联网 LLM 模式",
  "mode.offlineDescription": "本站点未调用 LLM 生成。系统将原始学习资料整理为可搜索、可跳转、可追溯来源的讲义浏览器。",
  "mode.onlineDescription": "本站点使用联网 LLM 生成。中文总结、增强术语解释和高级练习题可能调用了已配置的模型接口。",
  "mode.availableOffline": "离线可用",
  "mode.requiresLlm": "需要联网 LLM",
  "mode.limitedOffline": "离线基础支持",
  "mode.availableWithLlm": "LLM 模式可用",
  "mode.featureMatrix": "功能可用性对照表",
  "mode.currentGenerationMode": "当前生成模式",
  "mode.privacyNote": "本地离线模式会将文件保留在本机；联网 LLM 模式可能会把选定的来源文本发送给已配置的模型服务商。",
  "mode.fullyLocal": "完全本地",
  "mode.dependsOnProvider": "取决于服务商",
  "mode.feature": "功能",
  "mode.cardSourceExplorer": "可搜索 Source Explorer",
  "mode.cardSourceExplorerDesc": "浏览清洗后的原文摘录和来源引用。",
  "mode.cardSlideGalleryDesc": "查看从 PDF 页面提取的图示、公式、表格和课件截图。",
  "mode.cardChineseSummary": "基于来源文本和引用生成的结构化中文笔记。",
  "mode.cardChineseSummaryRequiresDesc": "启用联网 LLM 模式后可生成中文结构化笔记。",
  "mode.cardAdvancedPractice": "高级练习",
  "mode.cardAdvancedPracticeDesc": "自由拓展、应用场景和更难的综合题可以使用已配置的模型。",
  "mode.sourceExplorer": "Source Explorer",
  "mode.sourceGroundedNotes": "Source-grounded Notes",
  "mode.sourceExplorerNote": "本地离线模式显示清洗后的原文摘录和课件截图，不伪装成 AI 中文总结。",
  "mode.sourceGroundedNote": "使用已上传资料和来源引用生成的 LLM 笔记。",
  "mode.llmDisabledFallback": "LLM 未启用：当前显示清洗后的来源摘录，而不是生成式中文总结。",
  "mode.practiceOfflineNote": "模板练习可离线使用。自由拓展、高难应用场景、高级代码填空和跨讲义综合需要联网 LLM 模式。",
  "mode.practiceOnlineNote": "联网 LLM 模式：source-grounded 和 creative practice 可以使用已配置的模型。",
  "features.pdfReading": "PDF / MD / DOCX 读取",
  "features.versionedOutput": "版本化站点输出",
  "features.sourceRefs": "来源引用",
  "features.cleanedExcerpts": "清洗后的原文摘录",
  "features.searchIndex": "搜索索引",
  "features.slideFigures": "课件截图",
  "features.slideGallery": "课件图片画廊",
  "features.lectureMap": "智能讲义目录",
  "features.crossLectureReferences": "跨讲义引用网络",
  "features.basicGlossary": "基础术语表",
  "features.enrichedGlossary": "增强术语解释",
  "features.templatePractice": "模板练习题",
  "features.chineseSummaries": "中文结构化总结",
  "features.creativePractice": "自由拓展练习",
  "features.applicationScenarios": "应用场景题",
  "features.codeCloze": "代码填空题生成",
  "features.crossLectureReasoning": "跨讲义综合推理",
  "features.privacy": "隐私",
  "sources.title": "来源",
  "sources.count": "条来源",
  "sources.expandHint": "点击查看来源引用",
  "sources.generatedFrom": "来源文件",
  "sources.page": "页",
});

Object.assign(siteUiTranslations.en, {
  practiceTypeHint: "When a specific type is selected, only that type is generated; Mixed is the only multi-type mode.",
  "mode.generationMode": "Generation Mode",
  "mode.offline": "Offline Mode",
  "mode.onlineLlm": "Online LLM Mode",
  "mode.offlineDescription": "This site was generated without LLM calls. It organizes your source materials into a searchable lecture explorer.",
  "mode.onlineDescription": "This site was generated with an online LLM. Chinese summaries, enriched glossary entries, and advanced practice questions may use the configured model provider.",
  "mode.availableOffline": "Available offline",
  "mode.requiresLlm": "Requires Online LLM",
  "mode.limitedOffline": "Limited offline",
  "mode.availableWithLlm": "Available with LLM",
  "mode.featureMatrix": "Feature Availability Matrix",
  "mode.currentGenerationMode": "Current generation mode",
  "mode.privacyNote": "Offline Mode keeps files local. Online LLM Mode may send selected source text to the configured provider.",
  "mode.fullyLocal": "Fully local",
  "mode.dependsOnProvider": "Depends on provider",
  "mode.feature": "Feature",
  "mode.cardSourceExplorer": "Searchable Source Explorer",
  "mode.cardSourceExplorerDesc": "Browse cleaned source excerpts with source references.",
  "mode.cardSlideGalleryDesc": "View extracted diagrams, formulas, tables, and slide figures.",
  "mode.cardChineseSummary": "Structured Chinese notes generated from source text and references.",
  "mode.cardChineseSummaryRequiresDesc": "Enable Online LLM Mode to generate Chinese structured notes.",
  "mode.cardAdvancedPractice": "Advanced Practice",
  "mode.cardAdvancedPracticeDesc": "Creative extensions, application scenarios, and harder synthesis questions can use the configured model.",
  "mode.sourceExplorer": "Source Explorer",
  "mode.sourceGroundedNotes": "Source-grounded Notes",
  "mode.sourceExplorerNote": "Offline Mode shows cleaned excerpts and slide figures instead of AI-written summaries.",
  "mode.sourceGroundedNote": "Generated with LLM using uploaded source materials and source references.",
  "mode.llmDisabledFallback": "LLM disabled: showing cleaned source excerpts instead of generated Chinese summaries.",
  "mode.practiceOfflineNote": "Template-based practice is available offline. Creative Extension, hard application scenarios, advanced code cloze, and cross-lecture synthesis require Online LLM Mode.",
  "mode.practiceOnlineNote": "Online LLM Mode: source-grounded and creative practice can use the configured model.",
  "features.pdfReading": "PDF / MD / DOCX reading",
  "features.versionedOutput": "Versioned output site",
  "features.sourceRefs": "Source references",
  "features.cleanedExcerpts": "Cleaned source excerpts",
  "features.searchIndex": "Search index",
  "features.slideFigures": "Slide figures",
  "features.slideGallery": "Slide Figure Gallery",
  "features.lectureMap": "Lecture Map",
  "features.crossLectureReferences": "Cross-Lecture References",
  "features.basicGlossary": "Basic glossary",
  "features.enrichedGlossary": "Enriched glossary",
  "features.templatePractice": "Template practice",
  "features.chineseSummaries": "Chinese structured summaries",
  "features.creativePractice": "Creative Extension Practice",
  "features.applicationScenarios": "Application scenario questions",
  "features.codeCloze": "Code cloze generation",
  "features.crossLectureReasoning": "Cross-lecture reasoning",
  "features.privacy": "Privacy",
  "sources.title": "Sources",
  "sources.count": "sources",
  "sources.expandHint": "Click to view source references",
  "sources.generatedFrom": "Generated from",
  "sources.page": "Page",
});

let siteUiLanguage = localStorage.getItem("site-ui-language") || "zh";

function siteT(key) {
  return siteUiTranslations[siteUiLanguage]?.[key] || siteUiTranslations.en[key] || key;
}

function applySiteLanguage() {
  document.documentElement.lang = siteUiLanguage === "zh" ? "zh-CN" : "en";
  document.querySelectorAll("[data-site-i18n]").forEach((node) => {
    node.textContent = siteT(node.dataset.siteI18n);
  });
  document.querySelectorAll("[data-site-i18n-placeholder]").forEach((node) => {
    node.setAttribute("placeholder", siteT(node.dataset.siteI18nPlaceholder));
  });
  if (siteLanguage) siteLanguage.value = siteUiLanguage;
}

siteLanguage?.addEventListener("change", () => {
  siteUiLanguage = siteLanguage.value;
  localStorage.setItem("site-ui-language", siteUiLanguage);
  applySiteLanguage();
});

function pageIdFromHash(hash = location.hash) {
  const targetId = hash.replace(/^#/, "");
  if (!targetId) return "overview";
  if (pageIds.includes(targetId)) return targetId;
  const lectureMatch = targetId.match(/^(lecture-\d+)(?:-|$)/);
  return lectureMatch && pageIds.includes(lectureMatch[1]) ? lectureMatch[1] : "overview";
}

function currentPage() {
  return pages.find((page) => page.classList.contains("active-page"));
}

function updateActiveLink(targetId) {
  navLinks.forEach((link) => link.classList.remove("active"));
  const exact = document.querySelector(`.sidebar a[href="#${CSS.escape(targetId)}"]`);
  const pageLink = document.querySelector(`.sidebar a[href="#${CSS.escape(pageIdFromHash(`#${targetId}`))}"]`);
  (exact || pageLink)?.classList.add("active");
}

function addPageNavigation() {
  pages.forEach((page, index) => {
    if (page.querySelector(":scope > .page-navigation")) return;
    const navigation = document.createElement("nav");
    navigation.className = "page-navigation";
    navigation.setAttribute("aria-label", "章节切换");
    const previous = pages[index - 1];
    const next = pages[index + 1];
    if (previous) {
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.target = previous.id;
      button.textContent = `← 上一页：${previous.id === "overview" ? "课程总览" : previous.querySelector(".eyebrow")?.textContent || previous.id}`;
      navigation.appendChild(button);
    }
    if (next) {
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.target = next.id;
      button.textContent = `下一页：${next.querySelector(".eyebrow")?.textContent || next.id} →`;
      navigation.appendChild(button);
    }
    page.appendChild(navigation);
  });
}

function scrollWithinPage(targetId) {
  const target = document.getElementById(targetId);
  if (target && target !== currentPage()) target.scrollIntoView({ behavior: "smooth", block: "start" });
  else main.scrollTo({ top: 0, behavior: "smooth" });
}

function showPage(targetId, options = {}) {
  const pageId = pageIdFromHash(`#${targetId}`);
  pages.forEach((page) => page.classList.toggle("active-page", page.id === pageId));
  updateActiveLink(targetId);
  if (options.updateHash !== false && location.hash !== `#${targetId}`) {
    history.pushState(null, "", `#${targetId}`);
  }
  requestAnimationFrame(() => scrollWithinPage(targetId));
}

menu?.addEventListener("click", () => {
  const open = sidebar.classList.toggle("open");
  menu.setAttribute("aria-expanded", String(open));
});

function toggleTheme() {
  document.body.classList.toggle("dark");
  localStorage.setItem("nlp-theme", document.body.classList.contains("dark") ? "dark" : "light");
}

theme?.addEventListener("click", toggleTheme);
mobileTheme?.addEventListener("click", toggleTheme);

if (localStorage.getItem("nlp-theme") === "dark") document.body.classList.add("dark");
applySiteLanguage();

lectureLinks.forEach((link) => {
  link.addEventListener("click", (event) => {
    event.preventDefault();
    const group = link.closest(".nav-group");
    const wasOpen = group.classList.contains("open");
    document.querySelectorAll(".nav-group.open").forEach((item) => item.classList.remove("open"));
    if (!wasOpen) group.classList.add("open");
    showPage(link.hash.slice(1));
  });
});

document.querySelector(".nav-overview")?.addEventListener("click", (event) => {
  event.preventDefault();
  showPage("overview");
});

document.querySelectorAll(".nav-page").forEach((link) => {
  link.addEventListener("click", (event) => {
    event.preventDefault();
    showPage(link.hash.slice(1));
  });
});

document.querySelectorAll(".nav-children a").forEach((link) => {
  link.addEventListener("click", (event) => {
    event.preventDefault();
    showPage(link.hash.slice(1));
  });
});

document.addEventListener("click", (event) => {
  const button = event.target.closest(".page-navigation button");
  if (button) showPage(button.dataset.target);
});

document.querySelectorAll(".sidebar a").forEach((link) => {
  link.addEventListener("click", () => {
    if (window.innerWidth <= 900) {
      sidebar.classList.remove("open");
      menu?.setAttribute("aria-expanded", "false");
    }
  });
});

main.addEventListener("scroll", () => topButton.classList.toggle("visible", main.scrollTop > 500));
topButton.addEventListener("click", () => main.scrollTo({ top: 0, behavior: "smooth" }));
window.addEventListener("hashchange", () => showPage(location.hash.slice(1), { updateHash: false }));

addPageNavigation();
showPage(location.hash.slice(1) || "overview", { updateHash: false });

const searchInput = document.getElementById("site-search");
const searchResults = document.getElementById("search-results");
let searchIndex = [];
let latestResults = [];
let searchTimer = 0;

function normalizeSearchText(value) {
  return (value || "")
    .toLowerCase()
    .normalize("NFKC")
    .replace(/[^\p{L}\p{N}\s-]+/gu, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function wordsOf(value) {
  return normalizeSearchText(value).match(/[a-z0-9-]+/g) || [];
}

function levenshtein(a, b) {
  if (a === b) return 0;
  if (!a.length) return b.length;
  if (!b.length) return a.length;
  const row = Array.from({ length: b.length + 1 }, (_, index) => index);
  for (let i = 1; i <= a.length; i += 1) {
    let previous = row[0];
    row[0] = i;
    for (let j = 1; j <= b.length; j += 1) {
      const current = row[j];
      row[j] = Math.min(
        row[j] + 1,
        row[j - 1] + 1,
        previous + (a[i - 1] === b[j - 1] ? 0 : 1)
      );
      previous = current;
    }
  }
  return row[b.length];
}

function fuzzyTokenMatch(token, haystack, haystackWords) {
  if (!token) return false;
  if (haystack.includes(token)) return true;
  if (/[\u4e00-\u9fff]/.test(token)) return haystack.includes(token);
  return haystackWords.some((word) => {
    if (word.startsWith(token)) return true;
    if (token.length < 5 || word.length < 5) return false;
    const limit = Math.max(token.length, word.length) >= 9 ? 2 : 1;
    return levenshtein(token, word) <= limit;
  });
}

function scoreRecord(record, query) {
  const normalizedQuery = normalizeSearchText(query);
  if (!normalizedQuery) return 0;
  const queryTokens = normalizedQuery.split(" ").filter(Boolean);
  const titleText = normalizeSearchText(`${record.lectureTitle || ""} ${record.sectionTitle || ""}`);
  const termsText = normalizeSearchText((record.terms || []).join(" "));
  const bodyText = normalizeSearchText(`${record.text || ""} ${record.snippet || ""}`);
  const haystack = `${titleText} ${termsText} ${bodyText}`;
  const haystackWords = wordsOf(haystack);
  let score = 0;

  if (haystack.includes(normalizedQuery)) score += 100;
  if (titleText.includes(normalizedQuery)) score += 45;
  if (termsText.includes(normalizedQuery)) score += 38;

  let matchedTokens = 0;
  for (const token of queryTokens) {
    if (titleText.includes(token)) score += 18;
    if (termsText.includes(token)) score += 16;
    if (bodyText.includes(token)) score += 10;
    if (fuzzyTokenMatch(token, haystack, haystackWords)) {
      matchedTokens += 1;
      score += 8;
    }
  }
  if (queryTokens.length && matchedTokens === queryTokens.length) score += 28;
  if (queryTokens.length > 1 && matchedTokens < queryTokens.length) score = 0;
  return score;
}

function makeSnippet(record, query) {
  const source = record.snippet || record.text || "";
  const normalizedQuery = normalizeSearchText(query);
  const firstToken = normalizedQuery.split(" ")[0];
  const lower = source.toLowerCase();
  const index = firstToken ? lower.indexOf(firstToken.toLowerCase()) : -1;
  const start = index > 42 ? index - 42 : 0;
  const clipped = source.slice(start, start + 190);
  const prefix = start > 0 ? "…" : "";
  return `${prefix}${clipped}${source.length > start + 190 ? "…" : ""}`;
}

function highlightSnippet(value, query) {
  let output = escapeHtml(value);
  const tokens = normalizeSearchText(query).split(" ").filter((token) => token.length >= 2);
  for (const token of tokens) {
    if (/[\u4e00-\u9fff]/.test(token)) {
      output = output.replaceAll(escapeHtml(token), `<mark class="search-mark">${escapeHtml(token)}</mark>`);
    } else {
      const pattern = new RegExp(`(${token.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "ig");
      output = output.replace(pattern, '<mark class="search-mark">$1</mark>');
    }
  }
  return output;
}

function pageRefsHtml(record) {
  return (record.pageRefs || [])
    .slice(0, 2)
    .map((ref) => `<span class="page-ref">${escapeHtml(ref)}</span>`)
    .join("");
}

function renderSearchResults(query) {
  const normalizedQuery = normalizeSearchText(query);
  if (!searchResults) return;
  if (!normalizedQuery) {
    searchResults.classList.remove("open");
    searchResults.innerHTML = "";
    latestResults = [];
    return;
  }
  latestResults = searchIndex
    .map((record) => ({ record, score: scoreRecord(record, normalizedQuery) }))
    .filter((item) => item.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, 8)
    .map((item) => item.record);

  searchResults.classList.add("open");
  if (!latestResults.length) {
    searchResults.innerHTML = '<p class="search-empty">未找到匹配内容。可以尝试英文术语或更短关键词。</p>';
    return;
  }

  const summary = `<p class="search-summary">找到 ${latestResults.length} 条相关笔记</p>`;
  const items = latestResults.map((record, index) => {
    const lectureLabel = record.lectureId === "overview" ? "Overview" : record.lectureId.replace("lecture-", "Lecture ");
    const snippetHtml = highlightSnippet(makeSnippet(record, query), query);
    return `<button class="search-result" type="button" data-search-index="${index}">
      <span class="search-result-kicker"><span>${escapeHtml(lectureLabel)}</span><span>${Math.max(1, Math.round(scoreRecord(record, query)))}</span></span>
      <span class="search-result-title">${escapeHtml(record.sectionTitle || record.lectureTitle || record.id)}</span>
      <span class="search-result-snippet">${snippetHtml}</span>
      <span class="search-result-refs">${pageRefsHtml(record)}</span>
    </button>`;
  }).join("");
  searchResults.innerHTML = summary + items;
}

function focusSearchTarget(record) {
  const targetId = record.id || record.lectureId || "overview";
  showPage(targetId);
  window.setTimeout(() => {
    const target = document.getElementById(targetId) || document.getElementById(record.lectureId);
    if (!target) return;
    target.classList.remove("search-hit-focus");
    void target.offsetWidth;
    target.classList.add("search-hit-focus");
    target.scrollIntoView({ behavior: "smooth", block: "start" });
    window.setTimeout(() => target.classList.remove("search-hit-focus"), 2600);
  }, 80);
}

function buildDomSearchIndex() {
  const records = [];
  pageSections.forEach((page) => {
    if (page.id === "unprocessed") return;
    const lectureTitle = page.querySelector("h1")?.textContent?.trim() || "课程总览";
    page.querySelectorAll(":scope > section, :scope > .story-step, .example-card, .notebook-cell, .slide-figure").forEach((section, index) => {
      const id = section.id || page.id;
      const heading = section.querySelector("h2,h3,h4")?.textContent?.trim() || lectureTitle;
      const text = section.textContent.replace(/\s+/g, " ").trim();
      const refs = [...section.querySelectorAll(".page-ref")].map((ref) => ref.textContent.replace(/^\[|\]$/g, "").trim());
      const terms = [...section.querySelectorAll(".term")].map((term) => term.textContent.trim());
      if (text) {
        records.push({
          id,
          lectureId: page.id,
          lectureTitle,
          sectionTitle: heading,
          text,
          snippet: text.slice(0, 180),
          pageRefs: refs,
          terms,
        });
      }
    });
  });
  return records;
}

async function initSearch() {
  if (!searchInput || !searchResults) return;
  try {
    const response = await fetch("search-index.json");
    if (!response.ok) throw new Error("search-index unavailable");
    searchIndex = await response.json();
  } catch {
    searchIndex = buildDomSearchIndex();
  }
  searchInput.addEventListener("input", () => {
    window.clearTimeout(searchTimer);
    searchTimer = window.setTimeout(() => renderSearchResults(searchInput.value), 180);
  });
  searchInput.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      searchInput.value = "";
      renderSearchResults("");
      return;
    }
    if (event.key === "Enter" && latestResults[0]) {
      event.preventDefault();
      focusSearchTarget(latestResults[0]);
    }
  });
  searchResults.addEventListener("click", (event) => {
    const button = event.target.closest(".search-result");
    if (!button) return;
    const record = latestResults[Number(button.dataset.searchIndex)];
    if (record) focusSearchTarget(record);
  });
}

const searchIndexReady = initSearch();

const practice = document.getElementById("practice-generator");
const practiceOutput = practice?.querySelector(".practice-output");
const practiceStatus = practice?.querySelector(".practice-status");
const practiceSource = practice?.querySelector(".practice-source");
const practiceKeyword = practice?.querySelector(".practice-keyword");
const practiceType = practice?.querySelector(".practice-type");
const practiceDifficulty = practice?.querySelector(".practice-difficulty");
const practiceCount = practice?.querySelector(".practice-count");
const practiceAnswerMode = practice?.querySelector(".practice-answer-mode");
const practiceMode = practice?.querySelector(".practice-mode");
const customPracticeContext = practice?.querySelector(".custom-practice-context");
const generatePracticeButton = practice?.querySelector(".generate-practice-btn");
const revealAllButton = practice?.querySelector(".reveal-all-answers-btn");
const copyQuestionsButton = practice?.querySelector(".copy-questions-btn");
const llmEndpointInput = practice?.querySelector(".llm-endpoint");
const llmModelInput = practice?.querySelector(".llm-model");
const llmApiKeyInput = practice?.querySelector(".llm-api-key");
const practiceTabs = [...(practice?.querySelectorAll(".practice-tab") || [])];
const practiceExtensionNote = practice?.querySelector(".practice-extension-note");
let practiceScope = practiceTabs.find((tab) => tab.classList.contains("active"))?.dataset.practiceModeTab || "source";
let lastPracticeQuestions = [];
const practiceState = {
  isGenerating: false,
  generationId: 0,
  originalButtonText: generatePracticeButton?.textContent || "Generate Practice Questions",
  recentQuestionSignatures: [],
  recentScenarioSignatures: [],
};

const fallbackTermHints = {
  attention: "attention 让模型动态关注输入序列中的相关位置，而不是平均处理全部 token。",
  "attention weights": "attention weights 表示不同输入位置对当前输出的重要性分布。",
  Transformer: "Transformer 使用 self-attention 建模 token 之间的直接依赖，并减少 RNN 的串行瓶颈。",
  BERT: "BERT 使用 bidirectional context 和 masked language modeling 学习理解型表示。",
  GPT: "GPT 通常使用 decoder-only Transformer 和 autoregressive next-token prediction。",
  T5: "T5 将多种 NLP 任务统一为 text-to-text 格式。",
  RNN: "RNN 通过 hidden state 在时间步之间传递历史信息。",
  ASR: "ASR 将 speech signal 转换为文本，常结合 acoustic model 与 language model。",
  "language model": "language model 为 token 序列分配概率，并可预测下一个 token。",
  "n-gram": "n-gram 使用前面有限个 token 近似完整历史上下文。",
  smoothing: "smoothing 为未见过的 n-gram 分配非零概率，缓解数据稀疏问题。",
  perplexity: "perplexity 用于衡量 language model 对测试文本的不确定性，数值越低通常表示模型越好。",
  "bag-of-words": "bag-of-words 将文本表示为词项计数，忽略词序信息。",
  "TF-IDF": "TF-IDF 同时考虑词频和逆文档频率，用于衡量词项对文档的区分性。",
  "cosine similarity": "cosine similarity 用向量夹角衡量两个文本表示的相似度。",
  PCA: "PCA 通过线性投影保留主要方差方向，用于降维和表示分析。",
  "word embedding": "word embedding 将词映射到连续向量空间，使语义相近的词在向量空间中更接近。",
  "distributional semantics": "distributional semantics 基于上下文分布相似性理解词义。",
  word2vec: "word2vec 通过预测上下文或中心词学习 word embedding。",
  tokenization: "tokenization 将原始文本切分为模型可处理的 token。",
  embedding: "embedding 将离散 token 映射为连续向量表示。",
  "acoustic model": "acoustic model 建模音频特征与语音单位之间的关系。",
};

function setPracticeStatus(message) {
  if (practiceStatus) practiceStatus.textContent = message || "";
}

function getPracticeOptions() {
  return {
    practiceScope,
    source: practiceSource?.value || "current-lecture",
    keyword: practiceKeyword?.value.trim() || searchInput?.value.trim() || "",
    type: normalizeQuestionType(practiceType?.value || "mixed"),
    difficulty: practiceDifficulty?.value || "medium",
    count: Number(practiceCount?.value || 5),
    answerMode: practiceAnswerMode?.value || "hidden",
    lectureId: getCurrentLectureId(),
    seed: createGenerationSeed(),
    avoidRecent: true,
  };
}

function normalizeQuestionType(value) {
  const map = {
    mcq: "multiple-choice",
    multipleChoice: "multiple-choice",
    "multiple choice": "multiple-choice",
    shortAnswer: "short-answer",
    codeCloze: "code-cloze",
    application: "application-scenario",
    scenario: "application-scenario",
  };
  return map[value] || value || "mixed";
}

function allowedPracticeTypes(difficulty = "medium", requestedType = "mixed", scope = practiceScope) {
  requestedType = normalizeQuestionType(requestedType);
  const sourceTypes = difficulty === "hard"
    ? ["multiple-choice", "multiple-choice", "concept", "short-answer", "short-answer", "code-cloze"]
    : ["multiple-choice", "multiple-choice", "multiple-choice", "concept", "concept", "short-answer", "code-cloze"];
  const creativeTypes = difficulty === "hard"
    ? ["multiple-choice", "concept", "short-answer", "code-cloze", "application-scenario", "application-scenario", "application-scenario"]
    : ["multiple-choice", "multiple-choice", "concept", "short-answer", "code-cloze", "application-scenario"];
  const pool = scope === "creative" ? creativeTypes : sourceTypes;
  if (requestedType === "mixed") return pool;
  return [requestedType];
}

function updatePracticeScope(nextScope) {
  practiceScope = nextScope === "creative" ? "creative" : "source";
  practiceTabs.forEach((tab) => {
    const active = tab.dataset.practiceModeTab === practiceScope;
    tab.classList.toggle("active", active);
    tab.setAttribute("aria-selected", String(active));
  });
  if (practiceExtensionNote) practiceExtensionNote.hidden = practiceScope !== "creative";
  updatePracticeTypeHint();
}

function updatePracticeTypeHint() {
  const hint = practice?.querySelector(".practice-type-hint");
  if (!hint || !practiceType) return;
  const selected = normalizeQuestionType(practiceType.value);
  if (selected === "mixed") {
    hint.textContent = "Mixed 会混合生成多种题型。";
  } else if (practiceScope === "source" && selected === "application-scenario") {
    hint.textContent = "Source-grounded application scenarios will stay close to uploaded notes. For freer business scenarios, use Creative Extension Practice.";
  } else {
    hint.textContent = "当前将只生成该题型。";
  }
}

function offlinePracticeRequiresLlm(options) {
  if (siteGenerationMode === "online_llm") return false;
  const type = normalizeQuestionType(options.type);
  return options.practiceScope === "creative" || options.difficulty === "hard" || type === "application-scenario";
}

function setPracticeLoading(isLoading) {
  if (!generatePracticeButton) return;
  generatePracticeButton.disabled = isLoading;
  generatePracticeButton.textContent = isLoading ? "Generating..." : practiceState.originalButtonText;
}

function clearPracticeOutput() {
  lastPracticeQuestions = [];
  if (practiceOutput) {
    practiceOutput.innerHTML = "";
    practiceOutput.dataset.generationId = "";
  }
  if (revealAllButton) revealAllButton.disabled = true;
  if (copyQuestionsButton) copyQuestionsButton.disabled = true;
}

function renderPracticeLoading(generationId) {
  if (!practiceOutput) return;
  practiceOutput.dataset.generationId = String(generationId);
  practiceOutput.innerHTML = '<div class="note practice-loading">正在生成备考题，请稍候...</div>';
}

function renderPracticeEmpty(message) {
  clearPracticeOutput();
  if (practiceOutput) {
    practiceOutput.innerHTML = `<div class="note">${escapeHtml(message || "当前上下文不足，建议选择更多内容或输入关键词。")}</div>`;
  }
}

function renderPracticeError(error) {
  clearPracticeOutput();
  if (practiceOutput) {
    practiceOutput.innerHTML = `<div class="note warning">生成失败：${escapeHtml(error?.message || String(error))}</div>`;
  }
}

function getCurrentLectureId() {
  return currentPage()?.id || "overview";
}

function createGenerationSeed() {
  return Date.now() + Math.floor(Math.random() * 1000000);
}

function seededRandom(seed) {
  let state = Math.abs(Math.floor(seed || Date.now())) % 2147483647;
  if (state === 0) state = 1;
  return () => {
    state = (state * 16807) % 2147483647;
    return (state - 1) / 2147483646;
  };
}

function pickRandom(items, random) {
  if (!items.length) return undefined;
  return items[Math.floor(random() * items.length)];
}

function shuffleArray(items, random = Math.random) {
  const copy = [...items];
  for (let i = copy.length - 1; i > 0; i -= 1) {
    const j = Math.floor(random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

function sampleContextItems(records, count, random) {
  const target = Math.min(records.length, Math.max(6, count * 2));
  return shuffleArray(records, random).slice(0, target);
}

function collectTerms(records, random = Math.random) {
  const terms = new Set();
  records.forEach((record) => {
    (record.terms || []).forEach((term) => terms.add(term));
    const heading = record.sectionTitle?.replace(/^\d+\.\s*/, "").trim();
    if (heading && /^[A-Za-z][A-Za-z0-9 /-]{1,50}$/.test(heading) && !/^lecture\b/i.test(heading)) {
      terms.add(heading);
    }
  });
  Object.keys(fallbackTermHints).forEach((term) => {
    const haystack = records.map((record) => `${record.text || ""} ${record.sectionTitle || ""}`).join(" ").toLowerCase();
    if (haystack.includes(term.toLowerCase())) terms.add(term);
  });
  return shuffleArray([...terms].filter((term) => term && !/^lecture\b/i.test(term)), random);
}

function sourceRefs(records, random = Math.random) {
  const refs = [];
  records.forEach((record) => (record.pageRefs || []).forEach((ref) => refs.push(ref)));
  return shuffleArray([...new Set(refs)], random).slice(0, 3);
}

function questionSignature(question) {
  return normalizeSearchText(question?.question || "").slice(0, 160);
}

function scenarioSignature(question) {
  return normalizeSearchText(question?.scenario || "").slice(0, 180);
}

function rememberQuestions(questions) {
  const signatures = questions.map(questionSignature).filter(Boolean);
  practiceState.recentQuestionSignatures.push(...signatures);
  practiceState.recentQuestionSignatures = practiceState.recentQuestionSignatures.slice(-80);
  const scenarioSignatures = questions
    .filter((question) => question.type === "application-scenario")
    .map(scenarioSignature)
    .filter(Boolean);
  practiceState.recentScenarioSignatures.push(...scenarioSignatures);
  practiceState.recentScenarioSignatures = practiceState.recentScenarioSignatures.slice(-80);
}

function isRecentlyUsed(question) {
  return practiceState.recentQuestionSignatures.includes(questionSignature(question));
}

function isScenarioRecentlyUsed(question) {
  const signature = scenarioSignature(question);
  return Boolean(signature && practiceState.recentScenarioSignatures.includes(signature));
}

function contextText(records) {
  return records.map((record) => {
    const refs = (record.pageRefs || []).join(", ");
    return `[${record.lectureTitle || ""} / ${record.sectionTitle || ""}${refs ? ` / ${refs}` : ""}] ${record.text || record.snippet || ""}`;
  }).join("\n\n");
}

async function getPracticeContext(options = getPracticeOptions()) {
  await searchIndexReady;
  const source = options.source || "current-lecture";
  const count = Number(options.count || 5);
  const random = seededRandom(options.seed || createGenerationSeed());
  if (source === "custom-context") {
    const text = customPracticeContext?.value.trim() || "";
    if (!text) return [];
    return [{
      id: "custom-practice-context",
      lectureId: getCurrentLectureId(),
      lectureTitle: "Custom context",
      sectionTitle: "自定义内容",
      text,
      snippet: text.slice(0, 180),
      pageRefs: [],
      terms: Object.keys(fallbackTermHints).filter((term) => text.toLowerCase().includes(term.toLowerCase())),
    }];
  }
  if (source === "search-context") {
    const query = options.keyword || "";
    if (!query) return [];
    const pool = searchIndex
      .map((record) => ({ record, score: scoreRecord(record, query) }))
      .filter((item) => item.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, Math.max(12, count * 4))
      .map((item) => item.record);
    return sampleContextItems(pool, count, random);
  }
  const lectureId = options.lectureId || getCurrentLectureId();
  const effectiveLectureId = lectureId === "overview" ? "lecture-18" : lectureId;
  const pool = searchIndex
    .filter((record) => record.lectureId === effectiveLectureId)
    .slice(0, Math.max(16, count * 5));
  return sampleContextItems(pool, count, random);
}

const questionAngles = ["definition", "motivation", "mechanism", "limitation", "comparison", "application", "formula", "example"];
const mcqTemplates = {
  easy: [
    "下列哪一项最准确描述了 {term}？",
    "在本讲中，{term} 最直接对应哪个概念？",
    "{term} 的基本作用是什么？",
  ],
  medium: [
    "为什么课程需要引入 {term}？",
    "{term} 主要解决了此前方法中的哪类问题？",
    "根据本讲内容，{term} 与模型效果提升的关系是什么？",
  ],
  hard: [
    "如果没有 {term}，模型在复杂 NLP 任务中最可能遇到什么限制？",
    "相较于旧方法，{term} 在信息建模路径上提供了什么改进？",
    "从机制角度看，{term} 的关键贡献和潜在局限分别是什么？",
  ],
};
const conceptTemplates = {
  easy: [
    "请用自己的话解释 {term} 的含义。",
    "{term} 在本讲中为什么是一个需要掌握的基础概念？",
    "请结合 page reference 说明 {term} 的核心思想。",
  ],
  medium: [
    "{term} 与本讲前面介绍的方法有什么关系？",
    "为什么 {term} 在这条 lecture 知识线中重要？",
    "{term} 解决了什么问题，又留下了什么局限？",
  ],
  hard: [
    "请从 motivation、mechanism、limitation 三个角度分析 {term}。",
    "如果把 {term} 用到真实 NLP 系统中，最需要注意什么失效场景？",
    "请比较 {term} 与相关旧方法在建模假设上的差异。",
  ],
};
const shortAnswerTemplates = {
  easy: [
    "简要说明 {term} 的工作机制。",
    "用 2 到 3 句话解释 {term} 在本讲中的作用。",
    "请说出 {term} 的一个现实 NLP 应用场景。",
  ],
  medium: [
    "请根据笔记内容总结 {term} 的输入、输出和目标。",
    "请说明 {term} 是如何从一个具体问题中被引入的。",
    "请用“问题 -> 方法 -> 局限”的方式说明 {term}。",
  ],
  hard: [
    "请分析 {term} 的机制优势，以及它不能完全解决的问题。",
    "请比较 {term} 和相关旧方法在 sequence data 或 representation learning 上的区别。",
    "请判断 {term} 在实际系统中可能失败的条件，并说明原因。",
  ],
};
const genericDistractors = {
  easy: [
    "随机删除输入 token",
    "把所有词按字母顺序排序",
    "只保留句子的最后一个 token",
    "完全不依赖训练数据",
    "只适用于图像分类，不能用于 NLP",
  ],
  medium: [
    "把所有输入位置赋予完全相同的重要性",
    "用人工规则替代模型学习",
    "直接把所有文本转换为固定标签，不考虑上下文",
    "只根据词频决定 token 的语义关系",
    "忽略 sequence data 中的顺序依赖",
  ],
  hard: [
    "只通过局部窗口捕捉依赖，因此无法利用长距离上下文",
    "把 bidirectional context 误当成 left-to-right generation",
    "只优化词表查找，不改变模型的信息流路径",
    "把 representation learning 简化为手工 feature engineering",
    "只建模 acoustic feature，不结合 language model 约束",
  ],
};
const termSpecificCorrect = {
  attention: "让模型根据当前任务动态关注输入序列中的相关位置",
  "attention weights": "表示不同输入位置对当前输出的重要性分布",
  Transformer: "使用 self-attention 直接建模 token 之间的关系，并减少 RNN 的串行瓶颈",
  BERT: "使用 bidirectional context 和 masked language modeling 学习理解型表示",
  GPT: "通过 autoregressive next-token prediction 生成文本",
  T5: "把多种 NLP 任务统一为 text-to-text framework",
  RNN: "通过 hidden state 在 time steps 之间传递历史信息",
  ASR: "将 speech signal 转换为文本，通常结合 acoustic model 与 language model",
  "language model": "为 token 序列分配概率，并预测后续 token",
  "n-gram": "用有限长度的前文近似完整历史上下文，从而估计下一个 token 的概率",
  smoothing: "为未见过或低频的 n-gram 分配更合理的非零概率",
  perplexity: "衡量 language model 对测试序列的不确定性，常用于比较模型质量",
  "bag-of-words": "把文本表示为词项计数或权重，但通常忽略词序",
  "TF-IDF": "用词频和逆文档频率衡量词项对文档的区分性",
  "cosine similarity": "通过向量夹角衡量两个文本表示的相似度",
  PCA: "通过保留主要方差方向进行线性降维",
  "word embedding": "把离散词项映射到连续向量空间以表达语义关系",
  "distributional semantics": "根据词在上下文中的分布相似性推断语义",
  word2vec: "通过预测中心词或上下文学习 word embedding",
  tokenization: "将原始文本切分为模型可处理的 token",
  embedding: "把离散 token 映射为连续向量表示",
  "acoustic model": "建模音频特征与语音单位之间的关系",
};

function fillTemplate(template, term) {
  return template.replaceAll("{term}", term);
}

function answerLetter(index) {
  return ["A", "B", "C", "D"][index] || "A";
}

function inferTermExplanation(term, record) {
  return termSpecificCorrect[term] || fallbackTermHints[term] || record?.snippet || `${term} 是本讲中的重要概念，需要结合对应 lecture 的上下文理解。`;
}

function buildMcqChoices(correct, term, difficulty, terms, random) {
  const relatedDistractors = shuffleArray(terms, random)
    .filter((candidate) => candidate && candidate !== term)
    .slice(0, 4)
    .map((candidate) => {
      if (difficulty === "hard") return `把 ${candidate} 的作用误认为 ${term} 的核心机制`;
      if (difficulty === "medium") return `主要依赖 ${candidate}，但不需要建模上下文关系`;
      return `${candidate} 与 ${term} 完全相同`;
    });
  const pool = [...relatedDistractors, ...genericDistractors[difficulty], ...genericDistractors.medium];
  const distractors = shuffleArray([...new Set(pool)], random).slice(0, 3);
  const rawChoices = shuffleArray([
    { text: correct, correct: true },
    ...distractors.map((text) => ({ text, correct: false })),
  ], random).slice(0, 4);
  const answerIndex = rawChoices.findIndex((choice) => choice.correct);
  return {
    choices: rawChoices.map((choice, index) => `${answerLetter(index)}. ${choice.text}`),
    answer: answerLetter(answerIndex),
  };
}

function buildMcq(records, terms, difficulty, random, attempt) {
  const record = pickRandom(records, random) || records[attempt % records.length];
  const term = pickRandom(terms, random) || record?.sectionTitle || "本讲核心概念";
  const angle = pickRandom(questionAngles, random);
  const template = pickRandom(mcqTemplates[difficulty] || mcqTemplates.medium, random);
  const correct = inferTermExplanation(term, record);
  const { choices, answer } = buildMcqChoices(correct, term, difficulty, terms, random);
  return {
    type: "multiple-choice",
    difficulty,
    question: `${fillTemplate(template, term)}（角度：${angle}）`,
    choices,
    answer,
    explanation: `${correct} 复习时需要结合本讲中的 ${angle} 视角，而不是只背术语定义。`,
    sourcePageRefs: sourceRefs([record, ...records], random),
    relatedTerms: shuffleArray([term, ...terms.filter((item) => item !== term)], random).slice(0, 4),
  };
}

function buildConceptQuestion(records, terms, difficulty, random, attempt) {
  const record = pickRandom(records, random) || records[attempt % records.length];
  const term = pickRandom(terms, random) || record?.sectionTitle || "本讲核心概念";
  const angle = pickRandom(questionAngles, random);
  const template = pickRandom(conceptTemplates[difficulty] || conceptTemplates.medium, random);
  const text = contextText(records).toLowerCase();
  let answer = inferTermExplanation(term, record);
  if (text.includes("bert") && text.includes("gpt") && random() > 0.45) {
    answer = "BERT 偏向 bidirectional context 和 masked language modeling；GPT 偏向 left-to-right autoregressive generation。两者都属于 Transformer family，但训练目标和任务视角不同。";
  } else if (text.includes("rnn") && text.includes("transformer") && random() > 0.45) {
    answer = "RNN 依赖 hidden state 按 time step 传递信息，Transformer / self-attention 让 token 间可以直接建立关系，因此更容易处理长距离依赖和并行训练。";
  }
  return {
    type: "concept",
    difficulty,
    question: `${fillTemplate(template, term)}（请突出 ${angle} 角度。）`,
    answer,
    explanation: record?.snippet || "答案应结合对应 lecture 的定义、例子和 page reference。",
    sourcePageRefs: sourceRefs([record, ...records], random),
    relatedTerms: shuffleArray([term, ...terms.filter((item) => item !== term)], random).slice(0, 4),
  };
}

function buildShortAnswer(records, terms, difficulty, random, attempt = 0) {
  const record = pickRandom(records, random) || records[attempt % records.length];
  const term = pickRandom(terms, random) || record?.sectionTitle || "本讲方法";
  const angle = pickRandom(questionAngles, random);
  const template = pickRandom(shortAnswerTemplates[difficulty] || shortAnswerTemplates.medium, random);
  return {
    type: "short-answer",
    difficulty,
    question: `${fillTemplate(template, term)}（侧重 ${angle}。）`,
    answer: inferTermExplanation(term, record),
    explanation: "复习时重点不是背定义，而是能说明该概念为什么被引入、解决了什么、又留下什么后续问题。",
    sourcePageRefs: sourceRefs([record, ...records], random),
    relatedTerms: shuffleArray([term, ...terms.filter((item) => item !== term)], random).slice(0, 4),
  };
}

function contextHas(records, patterns) {
  const text = contextText(records).toLowerCase();
  return patterns.some((pattern) => text.includes(pattern.toLowerCase()));
}

function inspiredRefs(records, random) {
  const refs = sourceRefs(records, random);
  return refs.length ? refs.map((ref) => `Inspired by ${ref}`) : ["Inspired by current lecture notes"];
}

const SCENARIO_DOMAINS = [
  "online education",
  "customer service",
  "healthcare notes",
  "legal document review",
  "meeting assistant",
  "search engine",
  "translation platform",
  "speech assistant",
  "coding assistant",
  "research paper assistant",
  "lecture note generator",
  "enterprise knowledge base",
];
const SCENARIO_ROLES = ["老板", "产品经理", "客户", "老师", "研究员", "客服负责人", "数据团队", "学生用户"];
const SCENARIO_INPUT_TYPES = ["short text", "long document", "conversation history", "PDF slides", "lecture recording", "speech waveform", "bilingual text", "noisy transcript", "user query", "multimodal input"];
const SCENARIO_OUTCOMES = ["classification", "semantic search", "summarization", "translation", "transcription", "question answering", "exam question generation", "terminology explanation", "recommendation", "structured knowledge base"];
const SCENARIO_CONSTRAINTS = ["low latency", "privacy", "local-only deployment", "noisy input", "limited labeled data", "domain-specific terminology", "long context", "multilingual users", "limited compute", "need page references"];
const SCENARIO_ANGLES = ["method-selection", "pipeline-design", "failure-diagnosis", "tradeoff-analysis", "system-improvement", "evaluation-metric", "limitation-analysis"];

function buildScenarioText(profile, difficulty, random) {
  const role = pickRandom(SCENARIO_ROLES, random);
  const domain = pickRandom(profile.domains || SCENARIO_DOMAINS, random);
  const inputType = pickRandom(profile.inputs || SCENARIO_INPUT_TYPES, random);
  const outcome = pickRandom(profile.outcomes || SCENARIO_OUTCOMES, random);
  const constraint = pickRandom(SCENARIO_CONSTRAINTS, random);
  const businessNeed = pickRandom(profile.businessNeeds, random);
  if (difficulty === "hard") {
    return `${role}说：“我们在 ${domain} 场景里经常收到 ${inputType}，我希望系统能自动完成 ${outcome}。${businessNeed} 还有一个现实限制：${constraint}。你先别跟我讲模型名，先告诉我系统应该怎么拆。”`;
  }
  if (difficulty === "medium") {
    return `一个 ${domain} 系统需要处理 ${inputType}，目标是 ${outcome}。当前问题是：${businessNeed} 约束是 ${constraint}。`;
  }
  return `一个 ${domain} 系统需要用 ${profile.relatedTerms.slice(0, 2).join(" / ")} 相关方法处理 ${inputType}，并完成 ${outcome}。`;
}

function buildCodeClozeQuestion(records, terms, difficulty, random, attempt = 0) {
  const refs = inspiredRefs(records, random);
  const candidates = [];
  if (contextHas(records, ["attention", "softmax", "transformer", "self-attention"])) {
    candidates.push({
      topic: "softmax / attention weights",
      question: "请补全 softmax 的归一化步骤，使 attention scores 可以转换为 attention weights。",
      code: `import numpy as np

def softmax(x):
    e = np.exp(x - np.max(x))
    return ______

scores = np.array([0.1, 2.0, 0.3])
weights = softmax(scores)
print(weights.round(3))`,
      blanks: [{ blank: "______", answer: "e / e.sum()", explanation: "指数化后的分数需要除以总和，才能形成概率分布。" }],
      explanation: "attention weights 通常由 scores 经过 softmax 得到，所有权重加起来为 1。",
      relatedTerms: ["softmax", "attention weights"],
    });
    candidates.push({
      topic: "scaled dot-product attention",
      question: "请补全 scaled dot-product attention 的 score 和 context 计算。",
      code: `import numpy as np

def softmax(x):
    e = np.exp(x - x.max(axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)

Q = np.array([[1.0, 0.0]])
K = np.array([[1.0, 0.0], [0.0, 1.0]])
V = np.array([[0.8, 0.2], [0.1, 0.9]])
d_k = Q.shape[-1]

scores = ____1____
weights = softmax(scores)
context = ____2____
print(context.round(3))`,
      blanks: [
        { blank: "____1____", answer: "(Q @ K.T) / np.sqrt(d_k)", explanation: "Query 和 Key 的点积需要除以 sqrt(d_k) 稳定尺度。" },
        { blank: "____2____", answer: "weights @ V", explanation: "attention weights 对 Value 做加权求和得到 context。" },
      ],
      explanation: "Hard 版本要求同时补全 QK^T / sqrt(d_k) 和加权 Value 两个步骤。",
      relatedTerms: ["scaled dot-product attention", "self-attention", "Transformer"],
    });
  }
  if (contextHas(records, ["rnn", "hidden state", "sequence data"])) {
    candidates.push({
      topic: "RNN hidden state update",
      question: "请补全 toy RNN 的 hidden state 更新公式。",
      code: `import numpy as np

tokens = ["not", "very", "good"]
emb = {"not": -1.0, "very": 0.2, "good": 1.0}
h = 0.0

for token in tokens:
    x_t = emb[token]
    h = ______
    print(token, round(h, 3))`,
      blanks: [{ blank: "______", answer: "np.tanh(0.6 * x_t + 0.8 * h)", explanation: "当前 hidden state 同时依赖当前输入 x_t 和上一时刻 h。" }],
      explanation: "普通 RNN 的关键是把历史状态传入当前时间步，而不是独立处理每个 token。",
      relatedTerms: ["RNN", "hidden state", "sequence data"],
    });
  }
  if (contextHas(records, ["gradient descent", "loss", "regression"])) {
    candidates.push({
      topic: "gradient descent update",
      question: "请补全参数更新，使 loss 沿负梯度方向下降。",
      code: `theta = 3.0
learning_rate = 0.1

for step in range(5):
    gradient = 2 * theta
    theta = ______
    print(round(theta, 3))`,
      blanks: [{ blank: "______", answer: "theta - learning_rate * gradient", explanation: "gradient descent 使用 theta <- theta - eta * gradient。" }],
      explanation: "learning rate 控制每次更新的步长；方向是负梯度方向。",
      relatedTerms: ["gradient descent", "loss function"],
    });
  }
  if (contextHas(records, ["cross entropy", "classification", "probability", "supervised"])) {
    candidates.push({
      topic: "cross entropy",
      question: "请补全二分类 cross entropy 中正确类别概率的 loss。",
      code: `import math

y = 1
p = 0.8
loss = ______
print(round(loss, 3))`,
      blanks: [{ blank: "______", answer: "-math.log(p)", explanation: "当真实标签 y=1 时，cross entropy 惩罚 -log(p)。" }],
      explanation: "cross entropy 不只看预测是否正确，还会惩罚模型信心不足。",
      relatedTerms: ["cross entropy", "classification"],
    });
  }
  if (contextHas(records, ["masked language modeling", "bert", "mask"])) {
    candidates.push({
      topic: "masked language modeling toy example",
      question: "请补全 toy MLM 的候选词打分，使模型利用左右上下文选择 [MASK]。",
      code: `sentence = ["the", "student", "[MASK]", "the", "book"]
candidates = {"read": ("student", "book"), "ate": ("student", "book")}

def score(word):
    left, right = candidates[word]
    return ______

print(max(candidates, key=score))`,
      blanks: [{ blank: "______", answer: "(left == \"student\") + (right == \"book\")", explanation: "MLM 可以同时利用 mask 左右两侧上下文。" }],
      explanation: "BERT 的 masked language modeling 训练目标鼓励模型学习 bidirectional context。",
      relatedTerms: ["BERT", "masked language modeling"],
    });
  }
  if (contextHas(records, ["gpt", "next-token", "autoregressive", "sampling"])) {
    candidates.push({
      topic: "next-token prediction toy example",
      question: "请补全 next-token prediction 的选择逻辑。",
      code: `next_token_probs = {"language": 0.15, "model": 0.65, "audio": 0.05}
next_token = ______
print(next_token)`,
      blanks: [{ blank: "______", answer: "max(next_token_probs, key=next_token_probs.get)", explanation: "toy greedy decoding 选择概率最高的下一个 token。" }],
      explanation: "GPT-style generation 反复根据 prompt context 预测下一个 token。",
      relatedTerms: ["GPT", "next-token prediction", "autoregressive generation"],
    });
  }
  if (contextHas(records, ["audio", "waveform", "spectrogram", "asr"])) {
    candidates.push({
      topic: "waveform frame feature",
      question: "请补全 frame energy 计算，把 raw waveform 转成简单 acoustic feature。",
      code: `import numpy as np

wave = np.array([0.0, 0.5, 1.0, 0.5, 0.0, -0.5, -1.0, -0.5])
frames = wave.reshape(2, 4)
energy = ______
print(energy.round(3))`,
      blanks: [{ blank: "______", answer: "(frames ** 2).mean(axis=1)", explanation: "frame energy 常用平方均值表示每帧能量。" }],
      explanation: "ASR 前通常需要把 continuous waveform 变成 frame-level acoustic features。",
      relatedTerms: ["audio processing", "spectrogram", "ASR"],
    });
  }
  if (!candidates.length) {
    candidates.push({
      topic: "feature vector",
      question: "请补全文本 feature vector 的简单计数逻辑。",
      code: `vocab = ["good", "bad", "not"]
tokens = ["not", "good"]
vector = [______ for word in vocab]
print(vector)`,
      blanks: [{ blank: "______", answer: "tokens.count(word)", explanation: "bag-of-words 特征可以用词项计数构造。" }],
      explanation: "这个 cloze 检查学生是否理解文本如何被转成 feature vector。",
      relatedTerms: ["feature vector", "bag-of-words"],
    });
  }
  const template = pickRandom(candidates, random);
  const hardCandidates = candidates.filter((item) => item.blanks.length > 1);
  const selected = difficulty === "hard" && hardCandidates.length ? pickRandom(hardCandidates, random) : template;
  return {
    type: "code-cloze",
    difficulty,
    question: `${selected.question}（${difficulty} cloze 变体 ${attempt}：${selected.topic}）`,
    code: selected.code,
    blanks: selected.blanks,
    answer: selected.blanks.map((blank) => `${blank.blank}: ${blank.answer}`).join("; "),
    explanation: selected.explanation,
    sourcePageRefs: refs,
    relatedTerms: selected.relatedTerms,
  };
}

function scenarioProfile(records, terms, difficulty, random) {
  const text = contextText(records).toLowerCase();
  if (text.includes("asr") || text.includes("audio") || text.includes("spectrogram")) {
    return {
      title: "老板式需求：自动会议纪要与搜索",
      scenario: difficulty === "hard"
        ? "老板说：“我希望用户上传一段会议录音后，系统能自动整理重点、区分谁说了什么、生成待办事项，并且可以按主题搜索会议内容。”"
        : "一个课堂录音系统需要把 speech audio 转成可搜索文字，并生成简短摘要。",
      answer: "可以设计 audio processing -> ASR -> speaker diarization -> summarization -> information extraction -> embedding / retrieval 的 pipeline。",
      pipeline: ["audio processing / spectrogram features：把 waveform 转成可建模特征", "ASR / acoustic model：将语音转换为文本", "speaker diarization：区分说话人", "summarization：生成会议重点", "information extraction：抽取 action items", "embedding / retrieval：支持主题搜索"],
      limitations: ["噪声和多人重叠说话会降低识别准确率", "隐私和数据合规需要单独处理", "LLM 生成纪要可能 hallucinate，需要评估和人工校验"],
      relatedTerms: ["ASR", "acoustic model", "language model", "embedding"],
      domains: ["meeting assistant", "online education", "lecture note generator", "enterprise knowledge base"],
      inputs: ["lecture recording", "speech waveform", "noisy transcript"],
      outcomes: ["transcription", "summarization", "semantic search", "exam question generation"],
      businessNeeds: [
        "用户不想反复听完整录音，但需要快速定位重点和待办事项。",
        "系统必须区分不同说话人的贡献，并保留可追溯的原文依据。",
        "学生希望课后直接得到可搜索的复习网页和练习题。",
      ],
    };
  }
  if (text.includes("bert") || text.includes("masked language modeling")) {
    return {
      title: "缺失词与上下文理解系统",
      scenario: difficulty === "hard"
        ? "产品经理说：“我希望系统能读懂一句话里空缺位置最可能是什么，而且判断时不要只看前半句。”"
        : "系统需要根据左右上下文恢复句子中的 [MASK] token。",
      answer: "应考虑 BERT-style masked language modeling 和 bidirectional context，让模型同时利用左右两侧信息。",
      pipeline: ["tokenization：切分输入文本", "mask prediction：预测被遮盖 token", "bidirectional encoder：同时利用左右上下文", "fine-tuning：迁移到分类、QA 或抽取任务"],
      limitations: ["MLM 本身不适合直接做自由文本生成", "领域词汇需要足够的预训练或 fine-tuning 数据"],
      relatedTerms: ["BERT", "masked language modeling", "bidirectional context"],
      domains: ["research paper assistant", "enterprise knowledge base", "legal document review"],
      inputs: ["short text", "long document", "user query"],
      outcomes: ["question answering", "classification", "terminology explanation"],
      businessNeeds: [
        "用户给出的句子常有缺失或上下文依赖，系统需要结合前后内容判断含义。",
        "业务方希望系统理解一句话里的关系，而不是只根据左侧文字猜测。",
        "文档里有大量领域术语，需要根据上下文解释空缺或歧义位置。",
      ],
    };
  }
  if (text.includes("gpt") || text.includes("t5") || text.includes("text-to-text")) {
    return {
      title: "统一文本任务接口",
      scenario: difficulty === "hard"
        ? "老板说：“我不想分别维护摘要、翻译、问答三套系统。能不能让用户只输入一段说明，系统就知道该输出什么？”"
        : "团队希望把 summarization、translation 和 QA 统一成 text input -> text output。",
      answer: "可以使用 text-to-text framework 表达任务，也可以用 GPT-style prompt context 做生成。T5 强调统一任务格式，GPT 强调 autoregressive next-token prediction。",
      pipeline: ["task prefix / prompt：说明任务", "text-to-text model：统一输入输出接口", "generation decoding：产生目标文本", "evaluation：按任务检查准确性和 hallucination"],
      limitations: ["不同任务仍需要不同评价指标", "prompt 设计会影响稳定性", "生成模型可能输出看似合理但不正确的内容"],
      relatedTerms: ["GPT", "T5", "text-to-text framework", "next-token prediction"],
      domains: ["coding assistant", "customer service", "lecture note generator", "research paper assistant"],
      inputs: ["user query", "long document", "conversation history"],
      outcomes: ["summarization", "translation", "question answering", "structured knowledge base"],
      businessNeeds: [
        "团队不想为每个文本任务维护一套独立接口。",
        "用户希望输入自然语言指令后，系统能继续写、改写或生成结构化结果。",
        "同一个产品里同时有摘要、问答和翻译需求，需要统一交互方式。",
      ],
    };
  }
  if (text.includes("attention") || text.includes("transformer") || text.includes("self-attention")) {
    return {
      title: "长文档自动找重点",
      scenario: difficulty === "hard"
        ? "客户说：“我们的报告很长，我希望系统回答问题时自己知道该看哪些段落，而不是把所有句子平均处理。”"
        : "一个 NLP 系统需要处理长文本，并动态关注与当前 query 相关的 token 或句子。",
      answer: "应考虑 attention / self-attention，让模型用 attention weights 动态分配不同输入位置的重要性。Transformer 可以并行建模 token-token 关系。",
      pipeline: ["tokenization / embedding：得到 token 表示", "self-attention：计算 token-token 依赖", "attention weights：突出相关位置", "downstream head：用于分类、抽取或生成"],
      limitations: ["长上下文计算成本高", "attention weights 不总是可解释证据", "仍需要位置编码和任务评估"],
      relatedTerms: ["attention", "attention weights", "self-attention", "Transformer"],
      domains: ["search engine", "enterprise knowledge base", "customer service", "research paper assistant"],
      inputs: ["long document", "conversation history", "user query", "PDF slides"],
      outcomes: ["semantic search", "question answering", "summarization", "classification"],
      businessNeeds: [
        "用户的问题只和长文档中的少数段落相关，平均处理所有句子会稀释关键信息。",
        "系统经常在长对话里忽略早先提到的重要限制。",
        "业务方希望模型能自己找重点，但仍需要解释结果来自哪些内容。",
      ],
    };
  }
  if (text.includes("machine translation") || text.includes("encoder-decoder")) {
    return {
      title: "长句机器翻译",
      scenario: difficulty === "hard"
        ? "老板说：“我希望把用户输入的英文自动翻成中文，而且句子很长时不能把前半句意思漏掉。”"
        : "机器翻译系统需要处理 source sentence 和 target sentence 的 sequence-to-sequence 映射。",
      answer: "可以使用 encoder-decoder 架构，并引入 attention 缓解 fixed context vector 的信息瓶颈。",
      pipeline: ["encoder：读取 source sequence", "decoder：逐步生成 target sequence", "attention：每步动态查看 source tokens", "evaluation：用人工评估或自动指标检查译文质量"],
      limitations: ["长句和歧义仍可能导致错译", "低资源语言需要更多数据或迁移学习"],
      relatedTerms: ["machine translation", "encoder-decoder", "attention"],
      domains: ["translation platform", "customer service", "enterprise knowledge base"],
      inputs: ["bilingual text", "long document", "conversation history"],
      outcomes: ["translation", "summarization", "structured knowledge base"],
      businessNeeds: [
        "长句前半部分的信息经常在输出中丢失。",
        "用户希望跨语言客服回复保持原意和上下文。",
        "平台需要保留术语一致性，同时处理不同语言的词序差异。",
      ],
    };
  }
  if (text.includes("rnn") || text.includes("sequence data") || text.includes("hidden state")) {
    return {
      title: "顺序敏感的评论理解",
      scenario: difficulty === "hard"
        ? "老板说：“用户评论里经常有 not good、not very good 这种表达。系统不能只看到 good 就判断正面。”"
        : "评论分类系统需要区分 not good 和 good not 这类顺序造成的语义差异。",
      answer: "需要 sequence modeling。RNN 使用 hidden state 逐 token 累积上下文；如果长距离依赖明显，可以考虑 LSTM / GRU 或 attention-based model。",
      pipeline: ["tokenization：得到 token sequence", "sequence model：按顺序处理 token", "hidden state / gate：保留上下文", "classifier：输出 sentiment label"],
      limitations: ["vanilla RNN 容易遗忘远距离信息", "LSTM / GRU 仍然串行，长文本可考虑 Transformer"],
      relatedTerms: ["sequence data", "RNN", "hidden state", "LSTM", "GRU"],
      domains: ["customer service", "online education", "speech assistant"],
      inputs: ["short text", "conversation history", "user query"],
      outcomes: ["classification", "question answering", "recommendation"],
      businessNeeds: [
        "表达里的词序会改变含义，系统不能只统计词是否出现。",
        "用户前面提到的限制会影响最后一句话的真实意图。",
        "系统经常看到正面词就误判，忽略前面的否定或转折。",
      ],
    };
  }
  return {
    title: "用户评论自动分类",
    scenario: difficulty === "hard"
      ? "老板说：“我想自动判断大量用户评论是正面还是负面，还要知道模型为什么会错。”"
      : "系统需要基于 labeled data 学习 text classification。",
    answer: "可以构建 feature vector，训练 supervised classifier，并用 precision、recall、F1 和 confusion matrix 分析错误。",
    pipeline: ["data labeling：准备正负样本", "feature vector：BOW / TF-IDF 或 embedding", "classifier：Naive Bayes / logistic regression / neural network", "evaluation：precision、recall、F1、confusion matrix"],
    limitations: ["类别不平衡会误导 accuracy", "手工特征难覆盖复杂语义", "需要验证集防止 overfitting"],
    relatedTerms: ["supervised learning", "feature vector", "classification", "evaluation"],
    domains: ["customer service", "healthcare notes", "legal document review", "enterprise knowledge base"],
    inputs: ["short text", "long document", "user query"],
    outcomes: ["classification", "recommendation", "structured knowledge base"],
    businessNeeds: [
      "团队有一批标注样本，希望自动判断新文本属于哪个类别。",
      "错误类型的业务成本不同，不能只看总体准确率。",
      "系统需要能解释哪些输入特征推动了分类结果。",
    ],
  };
}

function buildApplicationScenarioQuestion(records, terms, difficulty, random, attempt = 0) {
  const profile = scenarioProfile(records, terms, difficulty, random);
  const subtypes = difficulty === "hard"
    ? ["pipeline-design", "tradeoff-analysis", "system-improvement"]
    : difficulty === "medium"
      ? ["scenario-to-tech", "failure-diagnosis", "method-selection", "system-improvement"]
      : ["method-selection", "concept-to-scenario"];
  const scenarioSubtype = pickRandom(subtypes, random);
  const refs = inspiredRefs(records, random);
  const scenario = buildScenarioText(profile, difficulty, random);
  const easyChoices = [
    `A. ${profile.relatedTerms.slice(0, 2).join(" + ")}`,
    "B. 随机删除输入 token，不建立模型",
    "C. 只按字母顺序排序文本",
    "D. 完全不需要评价指标",
  ];
  const choices = difficulty === "easy" ? shuffleArray(easyChoices, random) : null;
  const answer = difficulty === "easy"
    ? `应选择与 ${profile.relatedTerms.join(", ")} 相关的方案。${profile.answer}`
    : profile.answer;
  const subtypeQuestions = {
    "concept-to-scenario": "这个课件概念适合解决场景中的哪一部分？请说明理由。",
    "scenario-to-tech": "应该考虑什么模型机制或 NLP pipeline？请说明为什么。",
    "method-selection": "应该优先选择哪类方法？请结合场景目标解释。",
    "failure-diagnosis": "如果系统表现不稳定，最可能的问题来源是什么？应该如何改进？",
    "tradeoff-analysis": "请分析两种可选方案的 trade-off，并给出推荐。",
    "pipeline-design": "请把需求拆成技术 pipeline，并说明每个模块的作用。",
    "system-improvement": "如果已有系统只能勉强完成目标，你会怎样升级它？请说明改进模块和风险。",
  };
  return {
    type: "application-scenario",
    scenarioSubtype,
    difficulty,
    subtype: scenarioSubtype,
    scenario,
    question: `${subtypeQuestions[scenarioSubtype] || "应该选择什么技术思路？请说明为什么它适合这个场景。"}（场景变体 ${attempt}）`,
    choices,
    answer,
    suggestedPipeline: profile.pipeline,
    limitations: profile.limitations,
    explanation: `这类题训练的是从业务需求反推技术方案：先识别输入、输出和约束，再选择模型机制和评价方式。本题与 ${profile.relatedTerms.join(", ")} 等 lecture 知识点相关。`,
    sourcePageRefs: refs,
    relatedTerms: profile.relatedTerms,
    title: profile.title,
  };
}

function buildRandomQuestion(records, terms, difficulty, requestedType, random, attempt, options = {}) {
  const types = allowedPracticeTypes(difficulty, requestedType, options.practiceScope || practiceScope);
  const type = pickRandom(types, random) || "concept";
  if (type === "multiple-choice") return buildMcq(records, terms, difficulty, random, attempt);
  if (type === "short-answer") return buildShortAnswer(records, terms, difficulty, random, attempt);
  if (type === "code-cloze") return buildCodeClozeQuestion(records, terms, difficulty, random, attempt);
  if (type === "application-scenario") return buildApplicationScenarioQuestion(records, terms, difficulty, random, attempt);
  return buildConceptQuestion(records, terms, difficulty, random, attempt);
}

function generateQuestionsLocal(records, options) {
  if (!records.length) return [];
  const random = seededRandom(options.seed || createGenerationSeed());
  const difficulty = options.difficulty || "medium";
  const requestedType = normalizeQuestionType(options.type || "mixed");
  const targetCount = Math.max(1, Math.min(10, Number(options.count || 5)));
  const sampledRecords = sampleContextItems(records, targetCount, random);
  const terms = collectTerms(sampledRecords, random);
  const usableTerms = terms.length ? terms : ["language model", "NLP method", "model limitation", "training objective", "evaluation metric"];
  const questions = [];
  const seen = new Set();
  const seenScenarios = new Set();
  const maxAttempts = targetCount * 20;
  const mixedCycle = requestedType === "mixed" ? shuffleArray(allowedPracticeTypes(difficulty, "mixed", options.practiceScope), random) : [];
  let attempts = 0;

  while (questions.length < targetCount && attempts < maxAttempts) {
    attempts += 1;
    const plannedType = requestedType === "mixed" ? (mixedCycle[questions.length] || "concept") : requestedType;
    const question = buildRandomQuestion(sampledRecords, usableTerms, difficulty, plannedType, random, attempts, options);
    const signature = questionSignature(question);
    const scenarioSig = scenarioSignature(question);
    if (!question || seen.has(signature) || (options.avoidRecent && isRecentlyUsed(question))) continue;
    if (question.type === "application-scenario" && (seenScenarios.has(scenarioSig) || (options.avoidRecent && isScenarioRecentlyUsed(question)))) continue;
    seen.add(signature);
    if (scenarioSig) seenScenarios.add(scenarioSig);
    questions.push({ ...question, id: `local-${options.seed || Date.now()}-${attempts}` });
  }

  while (questions.length < targetCount && attempts < maxAttempts * 2) {
    attempts += 1;
    const plannedType = requestedType === "mixed" ? (mixedCycle[questions.length] || "concept") : requestedType;
    const question = buildRandomQuestion(sampledRecords, usableTerms, difficulty, plannedType, random, attempts, options);
    const signature = questionSignature(question);
    const scenarioSig = scenarioSignature(question);
    if (!question || seen.has(signature)) continue;
    if (question.type === "application-scenario" && seenScenarios.has(scenarioSig)) continue;
    seen.add(signature);
    if (scenarioSig) seenScenarios.add(scenarioSig);
    questions.push({ ...question, id: `local-${options.seed || Date.now()}-${attempts}` });
  }

  if (!questions.length) {
    questions.push({
      ...buildRandomQuestion(sampledRecords, usableTerms, difficulty, requestedType === "mixed" ? "short-answer" : requestedType, random, 0, options),
      id: `local-${options.seed || Date.now()}-fallback`,
    });
  }
  return questions.slice(0, targetCount);
}

function finalizePracticeQuestions(questions, records, options) {
  const targetCount = Math.max(1, Math.min(10, Number(options.count || 5)));
  const selectedType = normalizeQuestionType(options.type || "mixed");
  const fresh = [];
  const seenQuestions = new Set();
  const seenScenarios = new Set();
  for (const question of questions || []) {
    question.type = normalizeQuestionType(question.type);
    if (selectedType !== "mixed" && question.type !== selectedType) {
      console.warn("Question type mismatch:", question.type, "expected:", selectedType);
      continue;
    }
    const qSig = questionSignature(question);
    const sSig = scenarioSignature(question);
    if (!qSig || seenQuestions.has(qSig)) continue;
    if (question.type === "application-scenario" && (seenScenarios.has(sSig) || isScenarioRecentlyUsed(question))) continue;
    seenQuestions.add(qSig);
    if (sSig) seenScenarios.add(sSig);
    fresh.push(question);
    if (fresh.length >= targetCount) break;
  }
  if (fresh.length < targetCount) {
    const fallback = generateQuestionsLocal(records, { ...options, type: selectedType, count: targetCount - fresh.length, seed: createGenerationSeed() });
    fallback.forEach((question) => {
      question.type = normalizeQuestionType(question.type);
      if (selectedType !== "mixed" && question.type !== selectedType) return;
      const qSig = questionSignature(question);
      const sSig = scenarioSignature(question);
      if (!seenQuestions.has(qSig) && !(question.type === "application-scenario" && seenScenarios.has(sSig))) {
        seenQuestions.add(qSig);
        if (sSig) seenScenarios.add(sSig);
        fresh.push(question);
      }
    });
  }
  if (selectedType !== "mixed" && fresh.length < targetCount) {
    setPracticeStatus(`Only generated ${fresh.length} ${selectedType} questions from current context.`);
  }
  return fresh.slice(0, targetCount);
}

function saveLlmSettings() {
  if (!practice) return;
  localStorage.setItem("practice-mode", practiceMode?.value || "local");
  localStorage.setItem("practice-endpoint", llmEndpointInput?.value || "");
  localStorage.setItem("practice-model", llmModelInput?.value || "");
  localStorage.setItem("practice-api-key", llmApiKeyInput?.value || "");
}

function loadLlmSettings() {
  if (!practice) return;
  if (practiceMode) practiceMode.value = localStorage.getItem("practice-mode") || "local";
  if (llmEndpointInput) llmEndpointInput.value = localStorage.getItem("practice-endpoint") || "";
  if (llmModelInput) llmModelInput.value = localStorage.getItem("practice-model") || "";
  if (llmApiKeyInput) llmApiKeyInput.value = localStorage.getItem("practice-api-key") || "";
}

async function generateQuestionsWithLLM(records, options) {
  const endpoint = llmEndpointInput?.value.trim();
  const model = llmModelInput?.value.trim();
  const apiKey = llmApiKeyInput?.value.trim();
  if (!endpoint || !model || !apiKey) throw new Error("LLM settings incomplete");
  const prompt = {
    model,
    messages: [
      {
        role: "system",
        content: "You generate exam practice questions for an NLP course. Preserve English technical terms. Return valid JSON only. Supported types are exactly: multiple-choice, concept, short-answer, code-cloze, application-scenario. If selectedQuestionType is not mixed, every generated question MUST have exactly that type and no other type. Only when selectedQuestionType is mixed may you generate multiple question types. If practiceScope is source, use only the provided notes context and keep application scenarios close to uploaded notes with source references. If practiceScope is creative, clearly treat application scenarios as Creative Extension inspired by the notes. Do not repeat questions from recent history.",
      },
      {
        role: "user",
        content: `Context:\n${contextText(records).slice(0, 9000)}\n\nRecent questions to avoid:\n${practiceState.recentQuestionSignatures.slice(-20).join("\n") || "(none)"}\n\nRecent scenarios to avoid:\n${practiceState.recentScenarioSignatures.slice(-20).join("\n") || "(none)"}\n\nTask:\nGenerate ${options.count} questions.\npracticeScope: ${options.practiceScope || "source"}.\nselectedQuestionType: ${normalizeQuestionType(options.type)}.\nIf selectedQuestionType is not "mixed", every generated question MUST have exactly this type: ${normalizeQuestionType(options.type)}. Do not generate any other question type. Only when selectedQuestionType = "mixed" may you generate multiple question types.\nDifficulty: ${options.difficulty}.\nUse different question angles such as definition, motivation, mechanism, limitation, comparison, application, formula, and example. For multiple-choice, randomize the correct answer position across A/B/C/D and make distractors plausible.\nCode cloze questions must use short Python snippets, preferably numpy or standard library, with one or two blanks and deterministic answers.\nApplication scenario questions in Source-grounded Practice must stay close to uploaded notes and include source references. Application scenario questions in Creative Extension may use realistic NLP/AI work scenarios.\n\nJSON schema examples:\n{"questions":[\n{"type":"code-cloze","difficulty":"medium","question":"...","code":"import numpy as np\\n... ______ ...","blanks":[{"blank":"______","answer":"e / e.sum()","explanation":"..."}],"answer":"______ = e / e.sum()","explanation":"...","sourcePageRefs":["Lecture 18, p.7"],"relatedTerms":["softmax","attention weights"]},\n{"type":"application-scenario","scenarioSubtype":"pipeline-design","subtype":"pipeline-design","difficulty":"hard","scenario":"Boss says: ...","question":"...","choices":null,"answer":"...","expectedAnswer":"...","suggestedPipeline":["ASR: ...","speaker diarization: ..."],"limitations":["noise","privacy"],"explanation":"Creative Extension inspired by Lecture 23, pp.4-8.","sourcePageRefs":["Creative Extension inspired by Lecture 23, pp.4-8"],"relatedTerms":["ASR","acoustic model","language model"]},\n{"type":"multiple-choice","difficulty":"medium","question":"...","choices":["A. ...","B. ...","C. ...","D. ..."],"answer":"A","explanation":"...","sourcePageRefs":["Lecture 18, p.7"],"relatedTerms":["attention"]}\n]}`,
      },
    ],
    temperature: 0.3,
  };
  const response = await fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify(prompt),
  });
  if (!response.ok) throw new Error(`LLM API failed: ${response.status}`);
  const data = await response.json();
  const content = data.choices?.[0]?.message?.content || data.output_text || "";
  const parsed = JSON.parse(content.replace(/^```json|```$/g, "").trim());
  if (!Array.isArray(parsed.questions)) throw new Error("Invalid LLM JSON");
  return parsed.questions;
}

function renderPracticeQuestions(questions, options = {}) {
  if (!practiceOutput) return;
  lastPracticeQuestions = questions;
  rememberQuestions(questions);
  revealAllButton.disabled = !questions.length;
  copyQuestionsButton.disabled = !questions.length;
  if (!questions.length) {
    practiceOutput.innerHTML = '<div class="note">当前上下文不足，建议选择更多内容或输入关键词。</div>';
    return;
  }
  const visible = options.answerMode === "visible";
  practiceOutput.innerHTML = questions.map((question, index) => {
    const refs = (question.sourcePageRefs || []).map((ref) => `<span class="page-ref">${escapeHtml(ref)}</span>`).join("");
    const choices = question.choices?.length ? `<ol class="question-choices">${question.choices.map((choice) => `<li>${escapeHtml(choice)}</li>`).join("")}</ol>` : "";
    const answerHidden = visible ? "" : " hidden";
    const type = question.type || "question";
    const typeClass = `${type.replace(/[^a-z0-9-]/gi, "-")}-question`;
    const codeBlock = question.code ? `<pre class="code-question-block"><code class="language-python">${escapeHtml(question.code)}</code></pre>` : "";
    const scenarioBox = question.scenario ? `<div class="scenario-box"><strong>Scenario:</strong><p>${escapeHtml(question.scenario)}</p></div>` : "";
    const subtype = question.scenarioSubtype ? `<span class="question-subtype">${escapeHtml(question.scenarioSubtype)}</span>` : "";
    const pipeline = question.suggestedPipeline?.length
      ? `<div class="pipeline-list"><strong>Suggested pipeline:</strong><ol>${question.suggestedPipeline.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ol></div>`
      : "";
    const limitations = question.limitations?.length
      ? `<div class="limitations-list"><strong>Limitations:</strong><ul>${question.limitations.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul></div>`
      : "";
    const blankAnswers = question.blanks?.length
      ? `<div class="blank-answer"><strong>Blank answers:</strong>${question.blanks.map((blank) => `<p><code>${escapeHtml(blank.blank)}</code> = <code>${escapeHtml(blank.answer)}</code><br><span>${escapeHtml(blank.explanation || "")}</span></p>`).join("")}</div>`
      : "";
    const answerText = question.answer || question.expectedAnswer || "";
    const answerCode = question.type === "code-cloze" && answerText
      ? `<pre class="code-question-block answer-code"><code class="language-python">${escapeHtml(answerText)}</code></pre>`
      : escapeHtml(answerText);
    return `<article class="practice-question-card ${typeClass}">
      <div class="question-meta"><span class="question-type">${escapeHtml(type)}</span><span class="question-difficulty">${escapeHtml(question.difficulty || practiceDifficulty?.value || "medium")}</span>${subtype}${refs}</div>
      <h4>Q${index + 1}. ${escapeHtml(question.title || question.question || "")}</h4>
      ${scenarioBox}
      ${question.scenario ? `<p><strong>Question:</strong> ${escapeHtml(question.question || "")}</p>` : ""}
      ${codeBlock}
      ${choices}
      <button class="reveal-answer-btn" type="button">${visible ? "Hide answer" : "Show answer"}</button>
      <div class="question-answer"${answerHidden}><strong>${question.type === "application-scenario" ? "Suggested answer" : "Answer"}:</strong> ${answerCode}${blankAnswers}${pipeline}${limitations}<p><strong>Explanation:</strong> ${escapeHtml(question.explanation || "")}</p></div>
    </article>`;
  }).join("");
}

function questionsAsText() {
  return lastPracticeQuestions.map((question, index) => {
    const choices = question.choices?.length ? `\n${question.choices.join("\n")}` : "";
    const code = question.code ? `\nCode:\n${question.code}` : "";
    const scenario = question.scenario ? `\nScenario: ${question.scenario}` : "";
    const blanks = question.blanks?.length ? `\nBlanks:\n${question.blanks.map((blank) => `${blank.blank}: ${blank.answer} (${blank.explanation || ""})`).join("\n")}` : "";
    const pipeline = question.suggestedPipeline?.length ? `\nPipeline:\n${question.suggestedPipeline.join("\n")}` : "";
    const limitations = question.limitations?.length ? `\nLimitations:\n${question.limitations.join("\n")}` : "";
    return `Q${index + 1}. ${question.title || question.question}${scenario}${code}${choices}\nAnswer: ${question.answer || question.expectedAnswer || ""}${blanks}${pipeline}${limitations}\nExplanation: ${question.explanation || ""}\nSource: ${(question.sourcePageRefs || []).join(", ")}`;
  }).join("\n\n");
}

async function handleGeneratePracticeQuestions(event) {
  event?.preventDefault();
  if (practiceState.isGenerating) return;
  const generationId = ++practiceState.generationId;
  practiceState.isGenerating = true;
  setPracticeLoading(true);
  clearPracticeOutput();
  renderPracticeLoading(generationId);
  const options = getPracticeOptions();
  console.debug("[practice] generate start", options);
  if (offlinePracticeRequiresLlm(options)) {
    renderPracticeEmpty("This question type requires Online LLM Mode.");
    setPracticeStatus("This question type requires Online LLM Mode.");
    practiceState.isGenerating = false;
    setPracticeLoading(false);
    return;
  }
  setPracticeStatus("正在收集上下文...");

  try {
    saveLlmSettings();
    const records = await getPracticeContext(options);
    console.debug("[practice] context items", records.length);
    if (generationId !== practiceState.generationId) return;
    if (!records.length) {
      renderPracticeEmpty("当前上下文不足，建议选择更多内容或输入关键词。");
      setPracticeStatus("当前上下文不足，建议选择更多内容或输入关键词。");
      return;
    }

    let questions;
    let usedFallback = false;
    try {
      if (practiceMode?.value === "api") {
        setPracticeStatus("正在调用 LLM API...");
        questions = await generateQuestionsWithLLM(records, options);
      } else {
        questions = generateQuestionsLocal(records, options);
      }
    } catch (error) {
      usedFallback = true;
      questions = generateQuestionsLocal(records, options);
      if (generationId === practiceState.generationId) {
        setPracticeStatus(`API 调用失败，已 fallback 到本地模板模式。${error.message}`);
      }
    }

    if (generationId !== practiceState.generationId) return;
    questions = finalizePracticeQuestions(questions, records, options);
    console.debug("[practice] generated questions", questions.length);
    renderPracticeQuestions(questions, options);
    if (!usedFallback) {
      setPracticeStatus(`已基于 ${records.length} 条笔记上下文生成 ${questions.length} 道题。`);
    }
  } catch (error) {
    console.error("Practice generation failed:", error);
    if (generationId === practiceState.generationId) {
      renderPracticeError(error);
      setPracticeStatus("生成失败，请调整上下文或稍后重试。");
    }
  } finally {
    if (generationId === practiceState.generationId) {
      practiceState.isGenerating = false;
      setPracticeLoading(false);
      console.debug("[practice] generate done");
    }
  }
}

function bindPracticeGeneratorEvents() {
  if (!practice) return;
  if (practice.dataset.bound === "true") return;
  practice.dataset.bound = "true";
  loadLlmSettings();
  updatePracticeScope(practiceScope);
  practiceTabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      updatePracticeScope(tab.dataset.practiceModeTab);
      setPracticeStatus(
        practiceScope === "creative"
          ? "Creative Extension Practice：会生成应用场景题，内容是基于资料启发的拓展。"
          : "Source-grounded Practice：只基于当前资料生成定义、机制、简答和代码填空题。"
      );
    });
  });
  practiceSource?.addEventListener("change", () => {
    const custom = practiceSource.value === "custom-context";
    const keyword = practiceSource.value === "search-context";
    customPracticeContext.hidden = !custom;
    practiceKeyword.disabled = !keyword;
  });
  practiceSource?.dispatchEvent(new Event("change"));
  practiceType?.addEventListener("change", updatePracticeTypeHint);
  updatePracticeTypeHint();
  [practiceMode, llmEndpointInput, llmModelInput, llmApiKeyInput].forEach((input) => input?.addEventListener("change", saveLlmSettings));
  generatePracticeButton?.addEventListener("click", handleGeneratePracticeQuestions);
  practiceOutput?.addEventListener("click", (event) => {
    const button = event.target.closest(".reveal-answer-btn");
    if (!button) return;
    const answer = button.closest(".practice-question-card")?.querySelector(".question-answer");
    if (!answer) return;
    answer.hidden = !answer.hidden;
    button.textContent = answer.hidden ? "Show answer" : "Hide answer";
  });
  revealAllButton?.addEventListener("click", () => {
    practiceOutput?.querySelectorAll(".question-answer").forEach((answer) => { answer.hidden = false; });
    practiceOutput?.querySelectorAll(".reveal-answer-btn").forEach((button) => { button.textContent = "Hide answer"; });
  });
  copyQuestionsButton?.addEventListener("click", async () => {
    const text = questionsAsText();
    try {
      if (!navigator.clipboard?.writeText) throw new Error("Clipboard API unavailable");
      await navigator.clipboard.writeText(text);
      setPracticeStatus("题目已复制。");
    } catch {
      const textarea = document.createElement("textarea");
      textarea.value = text;
      textarea.setAttribute("readonly", "");
      textarea.style.position = "fixed";
      textarea.style.left = "-9999px";
      document.body.appendChild(textarea);
      textarea.select();
      const copied = document.execCommand?.("copy");
      textarea.remove();
      if (copied) {
        setPracticeStatus("题目已复制。");
      } else {
        const range = document.createRange();
        range.selectNodeContents(practiceOutput);
        const selection = window.getSelection?.();
        selection?.removeAllRanges();
        selection?.addRange(range);
        setPracticeStatus("复制权限受限，已选中题目文本，请按 Ctrl+C。");
      }
    }
  });
}

bindPracticeGeneratorEvents();

document.querySelectorAll(".gallery-filters button").forEach((button) => {
  button.addEventListener("click", () => {
    const filter = button.dataset.filter || "all";
    document.querySelectorAll(".gallery-card").forEach((card) => {
      card.hidden = filter !== "all" && card.dataset.galleryType !== filter;
    });
  });
});

const codeDemos = [
  {
    targetId: "lecture-9-example-gradient-descent-loss",
    topic: "Gradient descent",
    ref: "Lecture 9, pp.19-29",
    purpose: "这个示例把参数更新拆成 before / after：如果参数固定，loss 永远不变；加入 gradient descent 后，参数会沿负梯度方向移动，loss 逐步下降。",
    beforeTitle: "Before: 参数固定，loss 不会改善",
    beforeCode: `theta = 3.0

def loss(theta):
    return theta ** 2

for step in range(4):
    print(step, round(theta, 3), round(loss(theta), 3))`,
    beforeOutput: "输出中的 theta 一直是 3.0，loss 一直是 9.0。模型没有学习过程。",
    afterTitle: "After: 用 gradient descent 更新参数",
    afterCode: `theta = 3.0
learning_rate = 0.2

def loss(theta):
    return theta ** 2

for step in range(4):
    gradient = 2 * theta
    theta -= learning_rate * gradient
    print(step, round(theta, 3), round(loss(theta), 3))`,
    afterOutput: "theta 会逐步靠近 0，loss 也随之下降。真实模型只是把 theta 换成很多参数。",
    explanation: "Lecture 9 的核心是把 supervised learning 变成可优化问题。gradient 告诉我们当前参数让 loss 增长最快的方向，gradient descent 则反向走一步。",
  },
  {
    targetId: "lecture-10-example-confusion-matrix",
    topic: "Feature vector classifier",
    ref: "Lecture 10, pp.2-10",
    purpose: "这个示例展示从 rule-based 文本分类过渡到 data-driven classifier：before 只看关键词，after 把文本变成 feature vector，再用权重计算概率。",
    beforeTitle: "Before: 手写关键词规则",
    beforeCode: `def rule_based_spam(text):
    spam_words = {"free", "winner", "prize"}
    return "spam" if spam_words & set(text.lower().split()) else "normal"

print(rule_based_spam("free prize now"))
print(rule_based_spam("limited offer now"))`,
    beforeOutput: "规则容易解释，但只要表达方式变化，就可能漏掉同类文本。",
    afterTitle: "After: feature vector + logistic function",
    afterCode: `import math

vocab = ["free", "winner", "prize", "meeting"]
weights = [1.8, 1.5, 1.2, -1.4]
bias = -1.0

def vectorize(text):
    words = text.lower().split()
    return [words.count(word) for word in vocab]

def predict_spam(text):
    x = vectorize(text)
    logit = sum(w * xi for w, xi in zip(weights, x)) + bias
    prob = 1 / (1 + math.exp(-logit))
    return prob

print(round(predict_spam("free prize now"), 3))`,
    afterOutput: "输出是概率，而不是硬规则。模型可以通过 labeled data 学习 weights。",
    explanation: "Lecture 10 关注 supervised classifier。feature vector 让文本进入模型，logistic function 把线性分数变成概率，评价指标再判断这个分类器是否可靠。",
  },
  {
    targetId: "lecture-10-step-19-30",
    topic: "Neural network forward pass",
    ref: "Lecture 10, pp.19-25",
    purpose: "这个示例展示为什么 hidden layer 和 activation function 能突破单层线性模型的限制。代码只演示 forward pass，不训练真实网络。",
    beforeTitle: "Before: 单层线性模型",
    beforeCode: `import numpy as np

x = np.array([1.0, 0.0])  # two text features
W = np.array([0.8, -0.4])
b = 0.1

score = x @ W + b
print(round(score, 3))`,
    beforeOutput: "单层模型只能给出线性分数，复杂特征组合需要手工设计。",
    afterTitle: "After: hidden layer + ReLU",
    afterCode: `import numpy as np

x = np.array([1.0, 0.0])
W1 = np.array([[0.8, -0.2], [0.3, 0.7]])
b1 = np.array([0.0, 0.1])
W2 = np.array([1.2, -0.6])

hidden = np.maximum(0, x @ W1 + b1)  # ReLU
score = hidden @ W2
print(hidden.round(3), round(score, 3))`,
    afterOutput: "hidden layer 先学习中间表示，再输出分类分数。这就是 representation learning 的最小直觉。",
    explanation: "neural network 的价值不是把公式写复杂，而是让模型自己组合 feature。activation function 提供非线性，使边界不再只是单条直线。",
  },
  {
    targetId: "lecture-12-example-hidden-state",
    topic: "RNN hidden state",
    ref: "Lecture 12, pp.9-18",
    purpose: "这个重点示例展示 sequence data 为什么不能只按 token 独立处理，以及 RNN 如何通过 hidden state 把前文带到后续时间步。",
    beforeTitle: "Before: 每个 token 独立打分",
    beforeCode: `tokens = ["not", "very", "good"]

def classify_token_independent(tokens):
    scores = []
    for token in tokens:
        if token == "good":
            scores.append(1)
        elif token == "bad":
            scores.append(-1)
        else:
            scores.append(0)
    return sum(scores)

print(classify_token_independent(tokens))`,
    beforeOutput: "输出为 1。模型只看到 good 的正面分数，没有真正保存 not very 的上下文。",
    afterTitle: "After: hidden state 逐步累积上下文",
    afterCode: `import numpy as np

tokens = ["not", "very", "good"]
emb = {
    "not": np.array([-1.0, 0.0]),
    "very": np.array([0.0, 0.5]),
    "good": np.array([1.0, 1.0]),
}
W_x = np.array([[0.7, 0.2], [0.1, 0.6]])
W_h = np.array([[0.4, -0.3], [0.2, 0.5]])

h = np.zeros(2)
for token in tokens:
    h = np.tanh(emb[token] @ W_x + h @ W_h)
    print(token, h.round(3))`,
    afterOutput: "每一步的 h 都依赖当前 token 和上一时刻 hidden state，因此 good 的表示会受到前面 not / very 的影响。",
    explanation: "RNN 的核心是 h_t = tanh(W_x x_t + W_h h_{t-1})。它把 sequence data 的顺序结构写进计算过程，但长序列仍可能遇到 vanishing gradient。",
  },
  {
    targetId: "lecture-13-example-lstm-gate",
    topic: "LSTM gate",
    ref: "Lecture 13, pp.11-21",
    purpose: "这个示例用 NLP toy sequence 展示 gate 如何控制记忆。它不是完整 LSTM / GRU，而是把普通 RNN 和记忆门控的差异拆开给读者看。",
    beforeTitle: "Before: 普通 RNN 容易稀释否定词",
    beforeCode: `tokens = ["not", "very", "good"]
signal = {"not": -1.0, "very": 0.2, "good": 1.0}

memory = 0.0
for token in tokens:
    memory = 0.45 * memory + signal[token]
    print(token, round(memory, 3))`,
    beforeOutput: "not 的负向信息会被后续 very / good 不断覆盖，最后 memory 可能被 good 拉回正向。",
    afterTitle: "After: gate-based memory 保留关键上下文",
    afterCode: `tokens = ["not", "very", "good"]
signal = {"not": -1.0, "very": 0.2, "good": 1.0}
forget_gate = {"not": 0.95, "very": 0.9, "good": 0.85}
input_gate = {"not": 1.0, "very": 0.2, "good": 0.35}

memory = 0.0
for token in tokens:
    memory = forget_gate[token] * memory + input_gate[token] * signal[token]
    print(token, round(memory, 3))`,
    afterOutput: "not 被高比例写入和保留，good 的新信息被 gate 控制，因此模型仍能记住前面的否定语境。",
    explanation: "LSTM / GRU 的直觉是让模型学习什么时候记住、什么时候忘记。gate-based memory 不消除所有长距离问题，但比 vanilla RNN 更适合保留关键上下文。",
    takeaway: "遇到否定、转折、长距离依赖时，gate 的价值是保护重要历史信息，而不是让每个 token 平等覆盖 memory。",
  },
  {
    targetId: "lecture-15-example-encoder-decoder",
    topic: "Attention weights",
    ref: "Lecture 15, pp.17-23",
    purpose: "这个示例对比 fixed context vector 和 attention。attention 让 decoder 每一步根据 query 动态查看 source tokens。",
    beforeTitle: "Before: 一个 fixed context vector",
    beforeCode: `import numpy as np

source = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
context = source.mean(axis=0)
print(context.round(2))`,
    beforeOutput: "所有 source tokens 被平均压成一个向量。长句信息容易被混在一起。",
    afterTitle: "After: query 决定 attention weights",
    afterCode: `import numpy as np

def softmax(x):
    e = np.exp(x - x.max())
    return e / e.sum()

source_tokens = ["I", "love", "NLP"]
keys = np.array([[1.0, 0.0], [0.2, 1.0], [0.8, 0.9]])
values = keys
query = np.array([0.7, 1.0])

scores = query @ keys.T
weights = softmax(scores)
context = weights @ values
print(dict(zip(source_tokens, weights.round(2))))
print(context.round(2))`,
    afterOutput: "decoder 可以更关注与当前 query 相关的 source token，而不是平均处理整个句子。",
    explanation: "attention 把 encoder-decoder 的信息瓶颈从一个固定向量改成动态读取机制。这是从 machine translation 走向 Transformer 的关键过渡。",
  },
  {
    targetId: "lecture-18-example-scaled-dot-product-attention-attention-weights",
    topic: "Scaled dot-product self-attention",
    ref: "Lecture 18, p.21",
    purpose: "这个示例展示 Transformer 中 self-attention 的最小 numpy 版本：所有 token 同时计算彼此关系，而不是像 RNN 那样串行传递 hidden state。",
    beforeTitle: "Before: RNN 串行更新",
    beforeCode: `tokens = ["the", "cat", "sat"]
h = 0

for token in tokens:
    h = h + len(token)
    print(token, h)`,
    beforeOutput: "每一步依赖上一步状态，天然串行。长距离信息必须沿时间链条传递。",
    afterTitle: "After: self-attention 同时计算 token-token 关系",
    afterCode: `import numpy as np

def softmax(x):
    e = np.exp(x - x.max(axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)

X = np.array([[1.0, 0.0], [0.8, 0.2], [0.0, 1.0]])
Q, K, V = X, X, X
d_k = Q.shape[-1]

weights = softmax((Q @ K.T) / np.sqrt(d_k))
output = weights @ V
print(weights.round(2))
print(output.round(2))`,
    afterOutput: "每个 token 都得到一行 attention weights，直接查看同一序列中的其它 token。",
    explanation: "self-attention 把序列内部关系转化为矩阵计算。positional encoding 再补上顺序信息，避免模型只知道相关性而不知道位置。",
  },
  {
    targetId: "lecture-19-example-masked-language-modeling",
    topic: "Masked language modeling",
    ref: "Lecture 19, pp.20-31",
    purpose: "这个示例对比 GPT 式 left-to-right 和 BERT 式 masked language modeling。BERT 可以同时利用左右上下文做理解型表示。",
    beforeTitle: "Before: left-to-right 只能看左边",
    beforeCode: `left_context = ["the", "student", "read"]
next_token_probs = {"book": 0.45, "quickly": 0.25, "music": 0.05}

print(max(next_token_probs, key=next_token_probs.get))`,
    beforeOutput: "只根据左侧上下文，模型倾向预测下一个 token。",
    afterTitle: "After: MLM 同时看左右上下文",
    afterCode: `sentence = ["the", "student", "[MASK]", "the", "book"]
candidates = {
    "read": ("student", "book"),
    "ate": ("student", "book"),
    "blue": ("student", "book"),
}

def score(word):
    left, right = candidates[word]
    return (left == "student") + (right == "book")

print(max(candidates, key=score))`,
    afterOutput: "masked language modeling 像完形填空：模型同时利用 [MASK] 两边的证据。",
    explanation: "BERT 的 bidirectional context 让它更适合 classification、QA 和信息抽取。它不是直接从左到右生成文本，而是学习可迁移的上下文表示。",
  },
  {
    targetId: "lecture-21-example-t5-nlp-text-to-text",
    topic: "GPT and T5 task format",
    ref: "Lecture 21, pp.16-18",
    purpose: "这个示例展示 GPT 的 next-token prediction 与 T5 的 text-to-text framework。重点是任务接口如何被统一。",
    beforeTitle: "Before: 每个任务一个接口",
    beforeCode: `tasks = {
    "sentiment": {"text": "Great movie", "labels": ["pos", "neg"]},
    "translate": {"source": "hello", "target_lang": "fr"},
}

print(tasks["sentiment"])
print(tasks["translate"])`,
    beforeOutput: "不同任务需要不同字段和处理逻辑，系统接口会变复杂。",
    afterTitle: "After: text input -> text output",
    afterCode: `text_to_text = {
    "sentiment": ("sentiment: Great movie", "positive"),
    "translate": ("translate English to French: hello", "bonjour"),
    "summarize": ("summarize: long document ...", "short summary"),
}

for task, pair in text_to_text.items():
    print(task, "=>", pair)`,
    afterOutput: "T5-style 设计把任务写成统一的输入文本和输出文本。GPT 则用 prompt context 做 next-token prediction。",
    explanation: "这种统一接口是 large language model 应用的重要工程直觉：任务差异被转移到 prompt 或 task prefix 中。",
  },
  {
    targetId: "lecture-22-example-waveform-spectrogram",
    topic: "Audio frame features",
    ref: "Lecture 22, pp.22-37",
    purpose: "这个示例不依赖 librosa，只用 numpy 展示为什么 raw waveform 需要切成 frames，再提取类似 spectrogram 的能量特征。",
    beforeTitle: "Before: raw waveform 难以直接读出结构",
    beforeCode: `import numpy as np

sr = 16000
t = np.linspace(0, 0.02, int(sr * 0.02), endpoint=False)
wave = np.sin(2 * np.pi * 440 * t)

print(wave[:8].round(3))`,
    beforeOutput: "raw waveform 是连续振幅序列。直接看数字很难知道频率结构如何随时间变化。",
    afterTitle: "After: 分帧并计算 frame energy",
    afterCode: `import numpy as np

sr = 16000
t = np.linspace(0, 0.06, int(sr * 0.06), endpoint=False)
wave = np.sin(2 * np.pi * 440 * t)

frame_size = 160
frames = wave[: len(wave) // frame_size * frame_size].reshape(-1, frame_size)
energy = (frames ** 2).mean(axis=1)

print(energy.round(4))`,
    afterOutput: "frame energy 是最简化的 acoustic feature。真实 spectrogram 会进一步分析每个 frame 的频率成分。",
    explanation: "audio processing 的输入从离散 token 变成 continuous waveform。ASR 需要先把声音变成可学习的 acoustic features，再结合 acoustic model 和 language model。",
  },
];

function renderCodeDemo(demo) {
  const scenario = demo.scenario || `当前 lecture 正在讨论 ${demo.topic} 如何解决一个具体建模问题。下面用小型 Python 片段把“旧做法的问题”和“改进后的机制”并排展示。`;
  const takeaway = demo.takeaway || demo.explanation;
  return `<div class="demo-card code-demo-card" data-demo-topic="${escapeHtml(demo.topic)}">
    <div class="demo-header code-demo-header">
      <span class="demo-badge">Python Demo</span>
      <span class="demo-topic">${escapeHtml(demo.topic)}</span>
      <span class="page-ref">${escapeHtml(demo.ref)}</span>
    </div>
    <div class="demo-section demo-goal"><strong>目标：</strong>${escapeHtml(demo.purpose)}</div>
    <div class="demo-section demo-scenario"><strong>场景：</strong>${escapeHtml(scenario)}</div>
    <div class="demo-grid before-after-grid">
      <div class="code-panel demo-panel before">
        <div class="demo-panel-title"><h4>${escapeHtml(demo.beforeTitle)}</h4><button class="copy-code-btn" type="button">Copy code</button></div>
        <pre><code class="language-python">${escapeHtml(demo.beforeCode)}</code></pre>
        <div class="output-box cell-output"><strong>Output：</strong>${escapeHtml(demo.beforeOutput)}</div>
      </div>
      <div class="code-panel demo-panel after">
        <div class="demo-panel-title"><h4>${escapeHtml(demo.afterTitle)}</h4><button class="copy-code-btn" type="button">Copy code</button></div>
        <pre><code class="language-python">${escapeHtml(demo.afterCode)}</code></pre>
        <div class="output-box cell-output"><strong>Output：</strong>${escapeHtml(demo.afterOutput)}</div>
      </div>
    </div>
    <div class="demo-explanation"><strong>解释：</strong>${escapeHtml(demo.explanation)}</div>
    <div class="takeaway-box"><strong>Takeaway：</strong>${escapeHtml(takeaway)}</div>
  </div>`;
}

function injectCodeDemos() {
  codeDemos.forEach((demo) => {
    const target = document.getElementById(demo.targetId);
    if (!target || target.dataset.demoInjected === "true") return;
    target.insertAdjacentHTML("afterend", renderCodeDemo(demo));
    target.dataset.demoInjected = "true";
  });
}

injectCodeDemos();

document.addEventListener("click", async (event) => {
  const button = event.target.closest(".copy-code-btn");
  if (!button) return;
  event.preventDefault();
  const code = button.closest(".code-panel")?.querySelector("code")?.textContent || "";
  if (!code) return;
  try {
    await navigator.clipboard.writeText(code);
    button.textContent = "Copied";
  } catch {
    const textarea = document.createElement("textarea");
    textarea.value = code;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "fixed";
    textarea.style.left = "-9999px";
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand?.("copy");
    textarea.remove();
    button.textContent = "Copied";
  }
  window.setTimeout(() => {
    button.textContent = "Copy code";
  }, 1200);
});

const lightbox = document.getElementById("slide-lightbox");
const lightboxImage = lightbox?.querySelector("img");
const lightboxCaption = lightbox?.querySelector("p");

function closeLightbox() {
  lightbox?.classList.remove("open");
  lightbox?.setAttribute("aria-hidden", "true");
}

document.addEventListener("click", (event) => {
  const image = event.target.closest(".slide-figure img");
  if (image && lightbox) {
    lightboxImage.src = image.src;
    lightboxImage.alt = image.alt;
    lightboxCaption.textContent = image.closest("figure")?.querySelector("figcaption")?.textContent || image.alt;
    lightbox.classList.add("open");
    lightbox.setAttribute("aria-hidden", "false");
    return;
  }
  if (event.target === lightbox || event.target.closest("#slide-lightbox button")) closeLightbox();
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") closeLightbox();
});
