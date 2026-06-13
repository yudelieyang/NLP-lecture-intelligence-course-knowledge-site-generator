---
name: local-first-lecture-knowledge-app
description: Use this skill when improving, debugging, extending, or QA-checking a local-first lecture knowledge app that converts PDF/MD/DOCX course materials into versioned interactive knowledge sites, with separate Offline Mode and Online LLM Mode behavior.
---

# Local-first Lecture Knowledge App Development Skill

## Purpose

Use this skill for work on the Local-first Lecture Knowledge App in `C:\Users\24832\Desktop\ec508NLP`.

The app converts local course materials into versioned interactive knowledge sites. It must keep local/offline behavior honest, separate Online LLM behavior clearly, and verify generated output through final HTML-level QA.

## When to Use This Skill

Use this skill when improving, debugging, extending, or QA-checking:

- material extraction from PDF, Markdown, or DOCX;
- versioned site generation under `output_sites/`;
- Source Explorer or Source-grounded Notes;
- Offline Mode / Online LLM Mode boundaries;
- LLM summary generation, parsing, validation, fallback, or telemetry;
- generated site UI, bilingual text, mode banner, feature matrix, slide gallery, sources panel, glossary, or practice generator;
- FastAPI dashboard behavior;
- QA report rules and generated artifact inspection.

Use repository files and generated artifacts as the source of truth. Do not infer capabilities from stale README text or roadmap notes without checking code.

## Non-Goals and Assumptions

Do not assume cloud deployment, user login, SaaS storage, GitHub Pages publishing, OCR, handwriting recognition, web upload, or stable PPTX/Jupyter support unless explicitly requested and implemented.

`README.md` may be stale or conflicted in this project. Treat it as context only until verified against `scripts/`, `app/`, `templates/`, and the latest `output_sites/` artifacts.

Favor the safer rule when documents conflict: local-first, testable, explicit about LLM limitations, and conservative about claimed capabilities.

## Project Path and Expected Workflow

Project path:

```text
C:\Users\24832\Desktop\ec508NLP
```

Expected user workflow:

```text
Place PDF / MD / DOCX files into input_materials/
Start the local dashboard with run_app.bat, or run python scripts/generate_site.py
Choose Offline Mode or Online LLM Mode
Generate a new versioned site under output_sites/<run_id>/
Open index.html and use search, source references, slide figures, glossary, and practice tools
Inspect metadata.json and qa_report.json for generation status
```

## Product Modes

### Offline Mode

Offline Mode is the local-only baseline. It must work without network access, provider configuration, LLM calls, or API keys.

Offline Mode can provide:

- PDF / MD / DOCX reading;
- extracted source sections and page references;
- versioned static output;
- cleaned source excerpts;
- searchable source index;
- slide figures and Slide Figure Gallery where PDF rendering succeeds;
- Lecture Map from source structure;
- Cross-Lecture References based on local evidence;
- basic glossary;
- template-based practice;
- QA reports;
- privacy-first local workflow.

Offline Mode must not claim to provide:

- high-quality Chinese structured summaries;
- deep LLM-style concept explanations;
- Creative Extension Practice;
- hard application scenario generation;
- advanced cross-lecture reasoning;
- advanced code-cloze generation.

If LLM is disabled or unavailable, do not generate fake Chinese summary paragraphs from empty templates. Render cleaned source excerpts, slide figures, source references, and explicit fallback status instead.

### Online LLM Mode

Online LLM Mode may call a configured remote LLM API or local model endpoint. It requires explicit provider configuration and must disclose:

- API key or local endpoint requirement;
- network and provider availability requirements;
- possible API cost;
- privacy risk because selected source text may be sent to the configured provider;
- API keys must never be written into generated output, logs, metadata, QA reports, docs, or the repository.

Online LLM Mode can provide, when calls succeed and outputs validate:

- Chinese source-grounded structured summaries;
- richer Chinese concept explanations;
- enriched glossary explanations;
- Source-grounded Practice with model help;
- Creative Extension Practice;
- application scenario questions;
- code cloze questions;
- cross-lecture reasoning or relation explanations.

LLM failures are normal operational states. Record missing summaries and reasons in metadata/QA/UI, then fall back to cleaned source excerpts. Never render raw LLM response text as a fallback.

## Supported Inputs

Confirmed current generator inputs are defined in `scripts/utils.py`:

```text
.pdf
.md
.markdown
.docx
```

Implementation expectations:

- PDF uses PyMuPDF / `fitz` for page text and slide images.
- Markdown uses local text reading.
- DOCX uses `python-docx` or equivalent local parsing.

Roadmap only unless explicitly implemented and tested:

```text
PPTX
ipynb / Jupyter Notebook
OCR
handwritten note recognition
image formula recognition
complex chart understanding
```

Do not document roadmap formats as stable supported inputs.

## Core Data Model

Normalize every input format into lecture-like units. Even non-PDF files should fit the same concept.

Representative shape:

```json
{
  "lectureId": "lecture-17",
  "lectureTitle": "Lecture 17 -- NeuralNetwork.Advanced.Features 2",
  "sourceFile": "Lecture 17 -- NeuralNetwork.Advanced.Features 2.pdf",
  "sourceType": "pdf",
  "pagesOrSections": [
    {
      "id": "lecture-17-page-003",
      "title": "Convolutional Neural Networks",
      "text": "...",
      "sourceRef": "Lecture 17, p.3",
      "pageNumber": 3
    }
  ],
  "fullText": "..."
}
```

If a filename has a lecture number, preserve it for sorting and references. If no lecture number exists, generate stable fallback names such as `Lecture Unit 01`.

Raw fields such as `text`, `fullText`, `raw_text`, `page_text`, quote text, and term context are not safe inputs for ordinary explanatory paragraphs without cleaning and container-specific rendering.

## Output Versioning

Never overwrite old generated sites. Every generation must create a new folder:

```text
output_sites/<run_id>/
  index.html
  style.css
  script.js
  search-index.json
  metadata.json
  qa_report.json
  qa_report.html
  assets/
    slides/
```

Maintain `output_sites/runs.json` with run ID, project name, creation time, input counts, output path, generation mode, LLM status, and QA status.

Do not delete existing `output_sites/` folders unless the user explicitly asks for cleanup.

## Local Dashboard Requirements

The dashboard is a local control panel, not a cloud product. Use FastAPI for the current local dashboard path and bind to `127.0.0.1` by default.

Dashboard should expose:

- input material list;
- project settings;
- explicit generation mode selection;
- LLM provider settings;
- LLM connection test;
- generate button;
- generated versions;
- QA report links;
- logs and status;
- open generated site;
- open input/output folder actions where safe.

Do not use only a vague `Enable LLM` checkbox. Use explicit mode names:

```text
Offline Mode
Online LLM Mode
```

Offline UI copy should communicate: no API key required, files stay local, source excerpts/search/slide gallery/lecture map/cross-lecture links/template practice are generated.

Online UI copy should communicate: API key and network may be required, selected source text may be sent to provider, cost and privacy depend on provider, Chinese summaries and advanced practice require validated LLM output.

## LLM Provider Configuration

Current provider concepts include OpenAI-compatible endpoints and Ollama-style local endpoints through `scripts/llm_client.py`.

API keys must be read from `.env` through an environment variable name such as `OPENAI_API_KEY` or `GEMINI_API_KEY`. Do not paste real API key values into config examples, generated sites, metadata, QA reports, logs, docs, commits, or issue text.

After editing `.env`, restart the local app so environment loading is refreshed.

Provider telemetry may include booleans and counts such as connection status, calls attempted, calls succeeded, calls failed, parse successes, and repair attempts. It must not include secret values.

## Mode Disclosure in Generated Site

Generated `index.html` must visibly disclose the generation mode.

Offline Mode copy should state that no LLM calls were used and the site organizes local source materials into a searchable lecture explorer.

Online LLM Mode copy should state that source-grounded summaries and advanced practice may use the configured LLM provider.

Generated `index.html` must include a feature availability matrix. At minimum, the matrix should distinguish:

| Feature | Offline Mode | Online LLM Mode |
|---|---|---|
| PDF / MD / DOCX reading | Available | Available |
| Versioned output site | Available | Available |
| Source references | Available | Available |
| Cleaned source excerpts | Available | Available |
| Search index | Available | Available |
| Slide figures | Available | Available |
| Slide Figure Gallery | Available | Available |
| Lecture Map | Available | Available |
| Cross-Lecture References | Available, heuristic | Available, optionally LLM enhanced |
| Basic glossary | Available | Available |
| Enriched glossary | Limited | Available with validated LLM output |
| Template practice | Available | Available |
| Chinese structured summaries | Requires Online LLM | Available with validated LLM output |
| Creative Extension Practice | Requires Online LLM | Available |
| Application scenario questions | Requires Online LLM | Available |
| Advanced code cloze generation | Limited | Available |
| Cross-lecture reasoning | Limited | Available |
| Privacy | Fully local | Depends on provider |

Do not show API keys in generated output.

## Bilingual UI Requirements

If the generated site supports Chinese/English UI switching, all new UI text must join the existing i18n mechanism.

Include translation keys for:

- generation mode labels;
- Offline/Online descriptions;
- feature matrix;
- source explorer/source notes labels;
- sources panel;
- practice restrictions;
- QA labels or dashboard text when applicable.

Do not hardcode new English-only UI blocks in generated pages. Preserve English technical terms such as GPT, T5, Transformer, attention, top-p sampling, and Mixture of Experts when they are domain terms.

## Offline Mode Features

### Source Explorer

Offline Mode should behave as a source explorer, not an AI notes generator. Prefer labels such as `Source Explorer` or `Source-grounded Explorer` when no validated LLM summary exists.

Render:

- cleaned source excerpts;
- page/source references;
- selected short source quotes only when useful;
- slide figures;
- links into lecture map and related sections.

Do not render raw PDF text dumps, course headers, professor/university metadata, or long English slide sentences as ordinary explanatory paragraphs.

### Lecture Map

Lecture Map is structure extraction, not summarization. Build it from evidence such as source section titles, PDF page titles, top-of-page text, page order, and normalized headings.

Avoid `Page 1`, `Page 2`, etc. as main section titles except inside Sources or page references.

### Slide Figure Gallery

Slide Figure Gallery should collect useful slide images extracted from PDFs, group them by lecture, show thumbnails and page references, and support opening the slide in context.

If filtering is implemented, filters should be evidence-based and should not claim visual understanding beyond available metadata.

### Cross-Lecture References

Offline cross-lecture references must be evidence-based. Use shared terms, glossary overlap, similar titles, TF-IDF overlap, repeated model names, source structure, and lecture order.

Each related lecture card should show:

- related lecture title;
- relation type;
- shared terms or evidence;
- link to the related lecture.

### Sources Panel

Sources lists can become long. Render each lecture's full Sources list as a collapsible panel using native `details/summary` when possible.

Recommended behavior:

- source count <= 3 may open by default;
- source count > 3 should be collapsed by default;
- inline page-ref badges in paragraphs, figures, quotes, and glossary entries should remain visible.

Recommended structure:

```html
<details class="sources-panel">
  <summary>
    <span data-site-i18n="sources.title">Sources</span>
    <span class="sources-count">12</span>
  </summary>
  <ul class="sources-list">
    ...
  </ul>
</details>
```

## Online LLM Summary Generation

This is the most failure-prone part of the app. Treat LLM output as untrusted data until parsed, validated, normalized, and sanitized.

### Required JSON Schema

LLM summaries must return valid JSON only. The current implementation keeps schema and validation rules in `scripts/llm_summary.py`.

Representative shape:

```json
{
  "summaryTitle": "string",
  "language": "zh",
  "generationType": "llm_summary_zh",
  "sections": [
    {
      "title": "string",
      "paragraphs": [
        {
          "text": "string",
          "sourceRefs": ["Lecture 02, p.1"]
        }
      ],
      "keyTerms": ["NLP", "Machine Learning"],
      "sourceQuotes": [
        {
          "text": "short original source wording only if necessary",
          "sourceRef": "Lecture 02, p.1"
        }
      ]
    }
  ],
  "glossaryCandidates": [
    {
      "term": "string",
      "briefExplanation": "string",
      "sourceRefs": ["Lecture 02, p.1"]
    }
  ],
  "warnings": []
}
```

Ordinary explanatory paragraphs should come from validated Chinese summary fields, not from raw source text, quote text, term context, or raw LLM response.

### Prompt Rules

Prompts for summary generation must require:

- valid JSON only;
- no Markdown;
- no fenced code blocks around JSON;
- no explanation outside JSON;
- Chinese explanatory paragraphs with necessary English technical terms preserved;
- source refs for every paragraph;
- no raw slide text pasted as paragraphs;
- no course metadata, professor names, university names, repeated course titles, or repeated lecture headers in ordinary paragraph fields.

Prompting is not enough. The code must still validate, normalize, and sanitize.

### Parsing, Validation, Repair, and Fallback

Maintain this flow:

1. Build constrained prompt.
2. Receive raw response.
3. Extract JSON.
4. Validate schema.
5. Normalize fields.
6. Sanitize paragraphs and titles.
7. Render structured fields only.
8. Record telemetry and per-lecture status.

Implementation helpers should include or preserve:

- `extract_json_from_llm_response`;
- `validate_llm_summary_schema`;
- `normalize_llm_summary`;
- `strip_markdown_artifacts`;
- `sanitize_llm_paragraph`;
- missing summary status with reason.

If parsing or schema validation fails, attempt repair only through a structured repair prompt. If repair fails, mark the lecture summary as missing, show the reason, fall back to cleaned source excerpts, and never render the raw LLM response.

## Glossary Behavior

Glossary term names may remain English because the course material is technical and often English-first.

Offline Mode glossary should show:

- term name;
- source occurrences;
- short cleaned excerpt or basic local explanation;
- page/source references.

It must not pretend to have deep Chinese explanations if no LLM was used.

Online LLM Mode glossary may show:

- English term name;
- Chinese explanation;
- source references;
- explanation labels such as `Source-grounded explanation`, `AI supplemental explanation`, or `Offline basic entry`.

Avoid placeholder or mojibake-like text, empty definitions, and generic "No explanation available" entries when a safer omission is possible.

## Practice Generator

Practice Generator must respect generation mode and selected question type.

Offline Mode allows:

- basic multiple-choice templates;
- concept review templates;
- short-answer templates;
- simple code cloze templates where context is sufficient.

Mark offline practice as template-based and local.

Disable or mark as Requires Online LLM:

- Creative Extension Practice;
- hard application scenarios;
- advanced code cloze generation;
- cross-lecture synthesis;
- freer business or system-design scenarios.

Online LLM Mode may allow:

- Source-grounded Practice;
- Creative Extension Practice;
- application scenario questions;
- code cloze questions;
- hard questions;
- cross-lecture questions.

Allowed question type values:

```text
multiple-choice
concept
short-answer
code-cloze
application-scenario
mixed
```

Question type selection is a hard constraint. If selected type is not `mixed`, every generated question must match the selected type. Enforce this after LLM generation as well as in the prompt.

## QA Report Requirements

Generate and inspect:

```text
qa_report.json
qa_report.html
metadata.json
index.html
```

QA must inspect the final generated `index.html`, not only intermediate Python data structures.

Track at least:

- `generationMode`;
- `llmEnabled`;
- `llmConnectionOk`;
- `llmCallsAttempted`;
- `llmCallsSucceeded`;
- `llmCallsFailed`;
- `llmParseSucceeded`;
- `llmRepairAttempted`;
- `llmRepairSucceeded`;
- source notes generated by state;
- raw-like paragraph count;
- English leakage paragraph count;
- metadata leakage count;
- long English run count;
- low-quality Chinese fallback count;
- source quote count;
- bad glossary entry count;
- page-title heading count;
- slide figure count;
- lecture map count;
- slide gallery image count;
- cross-lecture reference count;
- sources panel count;
- collapsible sources count;
- LLM summary status per lecture;
- Markdown artifact count in rendered LLM summaries.

Final HTML ordinary paragraphs must fail or warn if they contain:

- `Wayne Snyder`;
- `Boston University`;
- `CS 505`;
- `Introduction to Natural Language Processing`;
- full lecture/course header patterns;
- long English slide-text runs not justified by technical terms;
- raw Markdown artifacts from LLM output;
- raw PDF dumps.

Allowed English locations include short source quotes, Sources panels, slide figure captions, filenames, page references, code/pre blocks, search index entries, and glossary term names.

If Online LLM Mode has `llmCallsAttempted = 0`, fail. If a lecture lacks a validated LLM summary in Online LLM Mode, show the reason in UI and QA.

A run should not be reported as fully successful when it only has partial LLM success. For example, an inspected run with `1/22` validated summaries is a partial Online LLM run even if the connection test succeeded.

## Common Failure Modes and Fixes

### Chinese summaries look like dense Markdown

Likely cause: raw LLM response was rendered directly.

Fix: enforce JSON schema, parse, validate, normalize, sanitize, repair invalid responses if possible, and render structured fields only.

### Offline output has fake Chinese summaries

Likely cause: fallback heuristic generated generic Chinese summary paragraphs.

Fix: disable fake summaries offline; render cleaned source excerpts, figures, and source references instead.

### Some lectures have no LLM summary

Likely causes: insufficient text, LLM call failure, rate limit, token limit, parse failure, schema invalid response, or skipped config.

Fix: record per-lecture status and reason, show missing status in UI, attempt structured repair for parse/schema failures, and fallback visibly to cleaned source excerpts.

### QA says passed but page looks wrong

Likely cause: QA checked intermediate data only or skipped the real HTML class/container where bad text rendered.

Fix: parse final `index.html`, inspect actual rendered containers, search known bad strings, and update QA hard-fail conditions.

### Long English slide text appears in ordinary paragraphs

Likely cause: raw `text`, `fullText`, `page_text`, quote text, or term context entered a paragraph renderer.

Fix: trace the HTML node back to `site_builder.py` or template code, identify the exact data field, and only render cleaned excerpts in source containers or validated `summary_zh`-style fields in explanatory paragraphs.

### Source quotes dominate the page

Likely cause: too many quotes or overlong quote text.

Fix: bound quote count and quote length. Keep long source text in Sources or source excerpt containers, not ordinary explanations.

### Practice ignores selected type

Likely cause: prompt-only constraint without post-generation filtering.

Fix: enforce selected type in local generation and after LLM generation. Only `mixed` may return multiple types.

## Testing Checklist

### Offline Mode

- `generationMode = offline`.
- No LLM calls attempted.
- No API key required.
- No fake Chinese summary templates.
- Source Explorer shows cleaned source excerpts.
- Page/source references are present.
- Lecture Map exists for multi-section lectures.
- Slide Gallery exists when PDF slide images are available.
- Cross-Lecture References exist where local evidence supports them.
- Sources panels collapse/expand.
- LLM-only practice features are disabled or marked Requires Online LLM.
- QA report is generated and final HTML leakage counts are acceptable.

### Online LLM Mode

- LLM connection test result is recorded.
- `generationMode = online_llm`.
- `llmCallsAttempted > 0` for a real Online LLM generation.
- Successful summaries are structured sections.
- Missing summaries show reason.
- No raw Markdown fences or raw LLM response text appears in `index.html`.
- JSON parse/validation/repair telemetry is recorded.
- API key values do not appear in HTML, metadata, QA reports, logs, docs, or Git.
- Partial LLM success is reported as partial, not as full success.

### Frontend

- Chinese/English UI switch updates mode banner and feature matrix.
- New UI text uses the existing i18n mechanism.
- Search works.
- Sources panels collapse and expand.
- Slide gallery/lightbox works when slide assets exist.
- Practice Generator respects selected question type.
- Creative Extension is visually and textually separated from source-grounded content.
- Dashboard can open generated output and QA report where implemented.
- Text does not overlap or overflow in common desktop/mobile viewports if UI layout was changed.

## Required Report After Major Changes

After any major change, report:

1. Files read.
2. Files modified.
3. Functions/templates changed.
4. New output version path.
5. Generation mode used.
6. LLM provider/connection status without secret values.
7. LLM call, parse, repair, success, and missing counts.
8. QA status and important leakage counts.
9. Whether known bad strings remain in ordinary `index.html` body paragraphs.
10. Whether source quotes, sources, captions, code/pre, glossary names, and page references still allow necessary English.
11. Whether Offline Mode and Online LLM Mode behave differently as intended.
12. What could not be confirmed.
