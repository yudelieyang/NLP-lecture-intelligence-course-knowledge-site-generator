# Local-first Lecture Knowledge App Development Skill

## Purpose

Use this skill when improving or extending the `Local-first Lecture Knowledge App`, a local study-material processing project that converts course materials into a versioned interactive knowledge site.

Core project path used in development:

```text
C:\Users\24832\Desktop\ec508NLP
```

Expected workflow:

```text
User places PDF / MD / DOCX files into input_materials/
→ starts the local dashboard with run_app.bat
→ chooses Offline Mode or Online LLM Mode
→ generates a new versioned output site under output_sites/
→ opens index.html and studies/searches/practices
```

Do not assume cloud deployment, user login, GitHub Pages, OCR, or web upload unless explicitly requested.

---

## Product Modes

### Offline Mode

Offline Mode is a local source-explorer mode. It must not call remote LLM APIs and must not pretend to generate high-quality Chinese summaries.

Offline Mode should provide:

- PDF / MD / DOCX reading
- versioned output sites
- cleaned source excerpts
- source references
- searchable index
- slide figures extracted from PDFs
- Slide Figure Gallery
- Lecture Map / intelligent outline
- Cross-Lecture References based on shared terms and source structure
- basic glossary
- template-based practice questions
- QA report
- privacy-first local workflow

Offline Mode should not claim to provide:

- high-quality Chinese structured summaries
- deep concept explanations
- Creative Extension Practice
- hard application scenario questions
- cross-lecture reasoning
- advanced code-cloze generation

If LLM is disabled, do not generate fake Chinese summaries using empty templates such as:

```text
这一部分围绕 {term} 展开。
课件在这里不是单独罗列概念，而是在说明 {title} 如何服务于本讲的问题。
本部分主要围绕 {terms} 展开。
由于当前未启用 LLM，这里只提供基于关键词和来源页的保守中文概述。
```

Instead, render cleaned source excerpts, slide figures, source references, and source explorer sections.

### Online LLM Mode

Online LLM Mode is the intelligent generation mode. It may call remote LLM APIs or a configured local LLM endpoint. It requires explicit configuration.

Online LLM Mode can provide:

- Chinese source-grounded summaries
- structured Chinese study notes
- enriched glossary explanations
- Source-grounded Practice
- Creative Extension Practice
- application scenario questions
- code cloze questions
- cross-lecture reasoning
- LLM-generated relation explanations
- advanced practice generation

Must disclose:

- API key is required
- selected source text may be sent to the configured provider
- network and provider availability matter
- API usage may incur cost
- API key must never be written into output files or committed to the repo

---

## Supported Inputs

First stable implementation target:

```text
PDF → MD → DOCX
```

Roadmap only unless explicitly requested:

```text
PPTX
ipynb / Jupyter Notebook
OCR
handwritten note recognition
image formula recognition
complex chart understanding
```

PDF should use PyMuPDF / `fitz` for page text and slide images. MD should use local text reading. DOCX should use `python-docx` or an equivalent parser.

---

## Core Data Model

Normalize all input formats into lecture-like units:

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

Use the `Lecture` concept even for non-PDF files. If no lecture number exists, generate `Lecture Unit 01`, `Lecture Unit 02`, etc.

---

## Output Versioning

Never overwrite old generated sites. Every generation run should create:

```text
output_sites/<run_id>/
├── index.html
├── style.css
├── script.js
├── search-index.json
├── metadata.json
├── qa_report.json
├── qa_report.html
└── assets/
    └── slides/
```

Maintain `output_sites/runs.json` with runId, projectName, createdAt, inputFileCount, outputPath, generationMode, LLM status, and QA status.

---

## Dashboard Requirements

The local dashboard should be a user-friendly local web control panel, not a cloud SaaS. Use FastAPI if adding a local dashboard. Bind to `127.0.0.1`, not `0.0.0.0` by default.

The dashboard should expose:

- input material list
- project settings
- generation mode selection
- LLM settings
- generate button
- generated versions
- QA report buttons
- logs/status
- open generated site
- open output folder

Do not use only a vague `Enable LLM` checkbox. Provide explicit mode choice:

```text
Offline Mode
Online LLM Mode
```

Offline Mode UI copy:

```text
No API key required. Files stay local.
Generates source excerpts, search, slide gallery, lecture map, cross-lecture links, and template practice.
```

Online LLM Mode UI copy:

```text
Requires API key and network connection.
Generates Chinese summaries, enriched glossary, advanced practice, and creative extensions.
```

---

## LLM Provider Configuration

Common OpenAI-compatible examples:

### OpenAI

```text
Provider: openai_compatible
Endpoint: https://api.openai.com/v1
Model: account-supported model
API key env var: OPENAI_API_KEY
```

### Gemini via OpenAI-compatible endpoint

```text
Provider: openai_compatible
Endpoint: https://generativelanguage.googleapis.com/v1beta/openai/
Model: gemini-2.5-flash
API key env var: GEMINI_API_KEY
```

`.env` example:

```text
GEMINI_API_KEY=<real key>
```

After editing `.env`, restart the local app. Never output or log the actual API key.

---

## index.html Mode Disclosure

Generated `index.html` must visibly explain which mode was used and which features are available.

For Offline Mode:

```text
Generation Mode: Offline Mode
This site was generated without LLM calls. It organizes source materials into a searchable lecture explorer.
```

For Online LLM Mode:

```text
Generation Mode: Online LLM Mode
Chinese source-grounded summaries and advanced practice were generated using the configured LLM provider.
```

Do not show API keys in output files.

### Feature Matrix

Include a feature availability matrix:

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
| Cross-Lecture References | Available, heuristic | Available, with optional LLM explanation |
| Basic glossary | Available | Available |
| Enriched glossary | Limited | Available |
| Template practice | Available | Available |
| Chinese structured summaries | Requires LLM | Available |
| Creative Extension Practice | Requires LLM | Available |
| Application scenario questions | Requires LLM | Available |
| Advanced code cloze generation | Limited | Available |
| Cross-lecture reasoning | Limited | Available |
| Privacy | Fully local | Depends on provider |

This matrix must support the site’s Chinese/English UI language switch.

---

## Bilingual UI Requirements

If the site supports Chinese/English UI switching, all new UI text must join the same i18n mechanism. Include keys for generation mode, offline/online labels, feature matrix, sources panel, source explorer notes, practice restrictions, and QA labels.

Do not hardcode new English-only UI blocks.

---

## Offline Mode Features

### Source Explorer

In Offline Mode, use `Source Explorer` or `Source-grounded Explorer`, not `Source-grounded Notes`, to avoid implying generated summaries.

Render cleaned source excerpts, slide figures, page references, source quotes where useful, and lecture map links.

### Lecture Map

Lecture Map is structure extraction, not summarization. Generate from PDF page titles, font size if available, top-of-page text, slide title, page order, and normalized section titles. Do not use `Page 1`, `Page 2`, etc. as main section titles except inside Sources.

### Slide Figure Gallery

Slide Gallery should collect key slide images extracted from PDFs, group by lecture, show thumbnails and page references, support lightbox, support “open in notes,” and support filters such as all / diagrams / formulas / tables / architecture / examples.

### Cross-Lecture References

Offline cross-lecture references should be evidence-based. Use shared terms, shared glossary terms, similar slide titles, TF-IDF overlap, repeated model names, and lecture order. Each related lecture card should show related lecture title, relation type, shared terms, and a link.

---

## Sources Panel

Sources lists can become very long. Render each lecture’s full Sources list as a collapsible panel using native `details/summary` when possible.

Recommended structure:

```html
<details class="sources-panel">
  <summary>
    <span data-i18n="sources.title">Sources</span>
    <span class="sources-count">12</span>
  </summary>
  <div class="sources-list">
    ...
  </div>
</details>
```

Default behavior: if sources count <= 3, may open by default; if sources count > 3, collapsed by default.

Do not remove inline page-ref badges from paragraphs, figures, quotes, or glossary entries.

---

## LLM Summary Generation

This is the most failure-prone part.

Do not let raw LLM responses directly enter HTML.

### Correct Principle

LLM produces structured data. The app parses, validates, normalizes, and renders structured fields. Do not rely on a model’s natural Markdown formatting.

### Required JSON Schema

For each lecture, LLM should return valid JSON only:

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

Prompt rules:

```text
Return valid JSON only.
Do not return Markdown.
Do not wrap JSON in ```json fences.
Do not include explanations outside JSON.
Write explanatory paragraphs in Chinese.
Preserve important English technical terms.
Every paragraph must include sourceRefs.
Do not paste raw slide text as paragraphs.
Do not include course metadata such as course number, instructor name, university name, or repeated lecture title.
```

### Parsing and Repair

Implement or maintain:

- `extract_json_from_llm_response`
- `validate_llm_summary_schema`
- `normalize_llm_summary`
- `strip_markdown_artifacts`
- `sanitize_llm_paragraph`

If parsing fails, do one repair attempt. If repair fails, mark lecture summary as missing, show reason in UI, fallback to cleaned source excerpt, and never render raw LLM response.

---

## Glossary Behavior

Glossary term names may be in English because source lectures are often in English.

Offline Mode should show term name, source occurrences, short cleaned excerpt, and page references. Do not pretend to have deep Chinese explanations if no LLM is used.

Online LLM Mode should show English term name, Chinese explanation, source references, and an explanation mode label such as:

```text
Source-grounded explanation
AI supplemental explanation
Offline basic entry
```

Avoid placeholders:

```text
从源材料中提取的关键词。
重要术语。
关键词。
No explanation available.
```

---

## Practice Generator

Practice Generator must respect mode.

Offline Mode allows basic multiple-choice templates, concept review templates, short-answer templates, and simple code cloze templates. Mark as:

```text
Template-based practice · available offline
```

Disable or mark as Requires LLM: Creative Extension Practice, hard application scenario, advanced code cloze, and cross-lecture synthesis.

Online LLM Mode allows Source-grounded Practice, Creative Extension Practice, application scenario, code cloze, hard questions, and cross-lecture questions.

Question type selection must be a hard constraint. Allowed values:

```text
multiple-choice
concept
short-answer
code-cloze
application-scenario
mixed
```

If selected type is not `mixed`, all generated questions must match the selected type.

---

## QA Report Requirements

Generate `qa_report.json` and `qa_report.html`.

Include:

- generationMode
- llmEnabled
- llmConnectionOk
- llmCallsAttempted
- llmCallsSucceeded
- llmCallsFailed
- llmParseSucceeded
- llmRepairAttempted
- llmRepairSucceeded
- sourceNotesGeneratedBy counts
- rawLikeParagraphCount
- englishLeakageParagraphCount
- metadataLeakageCount
- lowQualityChineseFallbackCount
- sourceQuoteCount
- badGlossaryEntryCount
- pageTitleHeadingCount
- slideFigureCount
- lectureMapCount
- slideGalleryImageCount
- crossLectureReferenceCount
- sourcesPanelCount
- collapsibleSourcesCount
- llmSummary statuses per lecture

HTML-level QA should inspect generated `index.html`, not only intermediate data.

Fail or warn if normal body contains `Wayne Snyder`, `Boston University`, `CS 505`, `Introduction to Natural Language Processing`, long English runs not justified by technical terms, low-quality fallback templates, or raw Markdown artifacts from LLM.

If Online LLM Mode has `llmCallsAttempted = 0`, fail.

If a lecture lacks LLM summary in Online LLM Mode, show reason in UI and QA report.

---

## Common Failure Modes and Fixes

### Chinese summaries look like dense Markdown

Likely cause: raw LLM response was rendered directly.

Fix: enforce JSON schema, parse / validate / normalize, repair invalid responses, render structured sections only.

### Offline output has fake Chinese summaries

Likely cause: fallback heuristic generated template Chinese paragraphs.

Fix: disable fake summaries offline; render cleaned source excerpts instead.

### Some lectures have no LLM summary

Likely causes: insufficient text, LLM call failed, parse failed, schema invalid, skipped by config, rate limit / token limit.

Fix: record per-lecture status, show reason in UI, repair parse failures, fallback visibly.

### QA says passed but page looks wrong

Likely cause: QA checks intermediate fields, not generated HTML; problematic text is in another HTML class.

Fix: parse final `index.html`, inspect real rendered classes, search known bad strings, and update QA conditions.

---

## Testing Checklist

### Offline Mode

- generationMode = offline
- no LLM calls attempted
- no fake Chinese summary templates
- Source Explorer shows cleaned source excerpts
- Lecture Map exists
- Slide Gallery exists
- Cross-Lecture References exist
- advanced LLM-only practice is disabled or marked Requires LLM

### Online LLM Mode

- LLM connection test succeeds
- generationMode = online_llm
- llmCallsAttempted > 0
- llmCallsSucceeded > 0
- LLM summaries are structured sections
- no raw Markdown artifacts
- missing summaries show reason
- glossary explanations are enriched and labeled

### Frontend

- Chinese/English UI switch updates mode banner and feature matrix
- Sources panels collapse/expand
- Search works
- Slide lightbox works
- Practice generator respects selected question type
- QA report opens from dashboard

---

## Reporting Requirements

After any major change, report:

1. Modified files.
2. New output version path.
3. Generation mode used.
4. LLM connection status.
5. LLM call counts.
6. Number of successful summaries.
7. Number of missing summaries and reasons.
8. QA summary.
9. Whether bad strings remain in `index.html`.
10. Whether Offline Mode and Online LLM Mode behave differently as intended.
