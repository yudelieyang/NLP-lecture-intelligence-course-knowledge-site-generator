# Project Guide for Codex

## Project Overview

This repository is a local-first lecture knowledge site generator. It reads lecture materials from `input_materials/`, extracts structured source sections, and writes versioned static sites under `output_sites/<run_id>/`. A local FastAPI dashboard in `app/` can configure and run the generator.

Current supported input formats are `.pdf`, `.md`, `.markdown`, and `.docx`, as defined in `scripts/utils.py`.

Note: `README.md` currently contains unresolved Git conflict markers. Treat it as useful context, not as a single reliable source of truth, until that conflict is resolved.

## How to Run

- Dashboard: run `run_app.bat`, then use `http://127.0.0.1:7860`.
- CLI generator: run `python scripts/generate_site.py`.
- Generated sites are versioned and previous `output_sites/` folders must not be deleted unless explicitly requested.

## Important Directories

- `scripts/extractors/`: PDF, Markdown, and DOCX extraction.
- `scripts/generate_site.py`: generation orchestration, config loading, LLM summary flow, site build, QA, run registry.
- `scripts/site_builder.py`: static HTML generation, source notes, feature matrix, slide gallery, lecture map, sources panels, practice UI shell.
- `scripts/llm_client.py`: optional provider client and `.env` loading.
- `scripts/llm_summary.py`: JSON-schema LLM summary prompt, parse, validate, normalize, and missing-status handling.
- `scripts/qa_report.py`: final output QA, including generated `index.html` checks.
- `app/`: FastAPI dashboard and dashboard services.
- `templates/`: generated site HTML/CSS/JS templates.
- `output_sites/`: generated artifacts and QA reports.

## Offline / Online LLM Boundary

Offline Mode must remain useful without network access, provider config, or API keys. It may provide extraction, cleaned source excerpts, source references, search, slide figures and gallery, lecture map, cross-lecture references, basic glossary, template practice, versioned output, and QA.

Offline Mode must not pretend to generate high-quality Chinese AI summaries. It should show cleaned source excerpts, slide figures, and source references instead of empty Chinese templates.

Online LLM Mode may use configured provider settings for Chinese structured summaries, enhanced explanations, and advanced or creative practice. LLM failures must be explicit and must not silently become fake summaries.

## LLM Output Rules

- LLM summaries must use the JSON schema in `scripts/llm_summary.py`.
- Raw LLM responses must never be inserted directly into `index.html`.
- Raw Markdown from an LLM must be parsed, validated, normalized, and sanitized before rendering.
- Raw PDF extracted text, `full_text`, `page_text`, quote text, and term context must not be rendered as ordinary explanatory paragraphs.
- API keys must be read from `.env` through environment variables only. Never write API key values to generated HTML, `metadata.json`, QA reports, docs, logs, or GitHub.

## QA Requirements

Run or inspect generated QA after changes that affect output. QA must check the final generated `index.html`, not only intermediate Python data.

The generated site must not pass if ordinary body paragraphs contain metadata leakage, long English slide text dumps, or sentence-level English leakage. Source quotes, sources lists, slide captions, page references, filenames, code/pre blocks, glossary term names, and search index entries may contain English when appropriate.

Latest known output checked during documentation pass: `output_sites/fastapi_smoke_test-2026-06-10_171146` had QA status `warnings`, with `htmlBodyMetadataLeakageCount = 0`, `htmlBodyEnglishLeakageParagraphCount = 0`, `htmlBodyLongEnglishRunCount = 0`, but only `1/22` validated LLM summaries because the Online LLM run mostly fell back after provider failures.

## Do-Not Rules

- Do not broaden prompts as a substitute for tracing data flow.
- Do not put raw PDF text or raw LLM output into ordinary paragraphs.
- Do not let Offline Mode claim LLM-only capabilities.
- Do not leave source lists expanded by default for large lectures.
- Do not allow source quotes to dominate the page.
- Do not weaken the Practice Generator selected question type; a specific type is a hard constraint.
- Do not expose `.env` values.
- Do not delete output sites or existing documentation unless explicitly requested.

## Required Verification Checklist

Before reporting completion for behavior changes:

1. Identify the data field and function/template that produces the affected HTML.
2. Regenerate a new output site.
3. Inspect the final `index.html` for the target containers.
4. Inspect `metadata.json` and `qa_report.json`.
5. Confirm mode boundaries, bilingual mode banner/feature matrix, and practice type constraints if touched.
6. Report any LLM partial failures or rate limits as limitations, not success.

## Reporting Format

When finishing a task, report:

- files read and changed;
- functions or templates changed;
- generated output path;
- QA status and important counts;
- what could not be confirmed;
- any remaining risk or follow-up.
