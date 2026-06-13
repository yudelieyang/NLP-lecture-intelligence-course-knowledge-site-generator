---
name: local-first-lecture-knowledge-app
description: "Project workflow for the Local-first Lecture Knowledge App in ec508NLP."
---

# Local-first Lecture Knowledge App Skill

## When to Use

Use this skill when working on `C:\Users\24832\Desktop\ec508NLP`, especially for generation behavior, Source-grounded Notes, Offline/Online LLM mode boundaries, QA reports, dashboard behavior, generated site UI, or project documentation.

Use the repository files as the source of truth. Do not infer capabilities from old README text without checking code and latest generated artifacts.

## Project Modes

### Offline Mode

Offline Mode is the local-only baseline. It must work without network access, LLM provider configuration, or API keys.

Confirmed offline-capable areas include:

- reading `.pdf`, `.md`, `.markdown`, and `.docx`;
- extracting source sections and page references;
- versioned static output under `output_sites/`;
- cleaned source excerpts;
- slide figures and Slide Figure Gallery where PDF rendering succeeds;
- source references and collapsible sources panels;
- search index and search UI;
- lecture map and cross-lecture references;
- basic glossary;
- template-based practice;
- QA report generation.

Offline Mode must not fake high-quality Chinese summaries. If no LLM is available, the correct fallback is source-centered: cleaned excerpt, slide figure, and source reference.

### Online LLM Mode

Online LLM Mode may send selected source context to a configured model provider. The dashboard maps Online LLM Mode to `generationMode: "online_llm"` and enables provider settings.

Online LLM Mode is responsible for:

- Chinese structured summaries;
- richer Chinese concept explanations when implemented through validated fields;
- advanced or creative practice paths that need model reasoning;
- application scenario and synthesis-style questions when configured.

LLM failures are normal operational states. Record them in metadata and QA; do not silently replace them with fake success.

## Architecture

- `scripts/utils.py`: supported extensions and shared text helpers.
- `scripts/extractors/`: format-specific extraction.
- `scripts/generate_site.py`: config, extraction, LLM summary orchestration, static build, QA report, run registry.
- `scripts/llm_client.py`: `.env` loading and provider calls for OpenAI-compatible endpoints and Ollama.
- `scripts/llm_summary.py`: JSON schema, prompt building, response JSON extraction, validation, normalization, sanitization, and missing statuses.
- `scripts/site_builder.py`: generated HTML structure including mode banner, feature matrix, lecture map, source notes, structured LLM summary, slide gallery, sources panel, and practice generator shell.
- `scripts/qa_report.py`: QA over generated files, including final `index.html` body paragraph checks.
- `app/`: local FastAPI dashboard, generation service, LLM connection test, and run listing.
- `templates/`: generated site static template, CSS, and browser-side behavior.

## LLM Mode Rules

1. LLM summary output must follow the schema in `scripts/llm_summary.py`.
2. Parse JSON first, validate schema second, normalize/sanitize third, render last.
3. Raw LLM responses and Markdown fences must never enter generated HTML.
4. `summary_zh`-style explanatory fields are the only safe source for ordinary Chinese paragraphs. Raw source fields such as `raw_text`, `full_text`, `page_text`, quote text, and term context are not safe paragraph inputs.
5. LLM missing/failed summaries must produce explicit status data with a reason.
6. Provider telemetry belongs in metadata/QA summaries, never as hidden API secrets.

## Offline Mode Rules

1. Keep Offline Mode honest: source explorer, not AI summary mode.
2. Prefer cleaned source excerpts over fabricated Chinese templates.
3. Preserve page references and slide figures so users can inspect the original material.
4. Do not add online-only promises to Offline UI.
5. Template practice can be available offline, but advanced creative or hard synthesis paths should be labeled as requiring Online LLM Mode.

## QA Report Rules

QA must inspect final generated `index.html`, especially ordinary body paragraphs. A clean intermediate data structure is not enough.

Hard-fail conditions for ordinary explanatory paragraphs include:

- course/professor/university metadata leakage;
- `CS 505`, `Wayne Snyder`, `Boston University`, or full course title leakage;
- long English slide-text runs in ordinary paragraphs;
- Markdown artifacts from raw LLM output;
- raw PDF dumps masquerading as source notes.

Allowed English locations include short source quotes, sources panels, slide captions, page references, filenames, code/pre blocks, search index, and glossary term names.

QA should also track source quote count, collapsible sources panels, slide figure coverage, missing source references, LLM summary success/missing counts, and markdown artifacts.

## Common Failure Modes

- README may be stale or conflicted; inspect code and latest output instead.
- Offline Mode may accidentally look like a poor LLM summary if fallback text becomes a generic Chinese paragraph.
- Online LLM Mode can be rate-limited. Latest inspected run had only `1/22` validated summaries despite a successful connection test.
- Raw PDF extracted text can leak course headers or long English slide sentences if data flow is not traced.
- Raw LLM Markdown can leak into HTML if JSON schema validation is bypassed.
- Source quotes can become too numerous and drown out study notes.
- Sources lists can make pages noisy unless rendered as collapsible panels.
- Practice Generator can violate user-selected question type unless the type is enforced after generation as well as in the prompt.
- Browser-side practice API settings are suitable only for local personal use; do not present them as safe for public deployment.

## Testing Checklist

For documentation-only work:

- verify existing files before writing claims;
- do not change business logic;
- record unknowns explicitly.

For generation behavior changes:

1. Run the generator or dashboard path relevant to the change.
2. Identify the new `output_sites/<run_id>/`.
3. Inspect `metadata.json`.
4. Inspect `qa_report.json` and `qa_report.html` when needed.
5. Search final `index.html` for known leakage strings and target CSS containers.
6. Confirm source quotes, sources, captions, page refs, and code/pre remain allowed to contain English.
7. Confirm ordinary paragraphs do not contain raw English slide dumps or metadata.
8. Confirm bilingual mode banner and feature matrix still switch language if UI text was touched.
9. Confirm selected practice type remains a hard constraint if practice was touched.

## Reporting Checklist

Report:

- files and functions read;
- generated output directory;
- changed files and functions;
- LLM mode used and whether the provider connected;
- LLM summary success/missing counts;
- QA status and key leakage counts;
- what remains unverified;
- next recommended action.
