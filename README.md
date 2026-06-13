# Local-first Lecture Knowledge Generator

This project generates a versioned local HTML knowledge site from lecture materials. Put files in `input_materials/`, run the generator, and open the generated `index.html` under `output_sites/<run_id>/`.

## Generation Modes

The app has two explicit product modes.

### Offline Mode

Offline Mode is a local-only source explorer. It does not call an LLM, does not upload files, and does not require an API key. It generates cleaned source excerpts, source references, search, slide figures, a Slide Figure Gallery, Lecture Map, Cross-Lecture References, basic glossary, template practice, and a QA report.

Chinese structured summaries require Online LLM Mode. Offline Mode should not pretend to generate AI-written Chinese notes.

### Online LLM Mode

Online LLM Mode requires a configured provider, endpoint, model, API key environment variable, and network access. Necessary source text may be sent to the configured LLM provider, which can involve API cost and privacy considerations.

Online LLM Mode enables Chinese source-grounded summaries, enriched glossary explanations, advanced source-grounded practice, Creative Extension Practice, application scenario questions, advanced code cloze generation, cross-lecture reasoning, and more natural concept explanations.

## Quick Start

1. Put supported files into `input_materials/`.
2. For the browser dashboard, double-click:

```text
run_app.bat
```

This starts a local FastAPI server and opens:

```text
http://127.0.0.1:7860
```

Keep the command window open while using the app. Closing it stops the local server.

3. Click `Generate New Site`, then click `Open generated site`.

4. For the command-line generator, run:

```powershell
python scripts/generate_site.py
```

5. Open the generated path printed in the terminal, for example:

```text
output_sites/my_lecture_knowledge_site-2026-06-09_1630/index.html
```

Every run creates a new output folder and updates `output_sites/runs.json`; previous generated sites are not overwritten.

## Local Web Dashboard

The browser dashboard is local-only. It binds to `127.0.0.1`, does not upload files, and does not create a SaaS account, database, or hosted site.

It supports:

- detecting supported and unsupported files in `input_materials/`
- editing project name, input folder, output folder, and minimum extracted text length
- configuring optional LLM provider settings
- testing whether LLM configuration looks usable
- generating a new versioned site
- viewing generated versions
- opening the latest generated site or a previous run
- opening the local input folder

The dashboard does not support webpage uploads yet. Files must still be placed manually in `input_materials/`.

Technical users can start the dashboard directly:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 7860
```

## Supported Inputs

Current version:

- PDF (`.pdf`) via PyMuPDF
- Markdown (`.md`, `.markdown`)
- Word (`.docx`) via python-docx

Planned later:

- PPTX
- Jupyter Notebook (`.ipynb`)
- OCR and handwriting extraction

## Lecture Detection

If a filename contains `Lecture` or `lectures` followed by a number, the site uses that lecture number and sorts by it. Other supported files become `Lecture Unit NN`.

## LLM Configuration

The app works without an LLM key. If no model is configured, it generates a readable source-based site from extracted text and local templates.

To use an OpenAI-compatible endpoint or Ollama, copy `config.example.json` to `config.json` and edit the `llm` block. API keys should be stored in `.env`, for example:

```text
OPENAI_API_KEY=your_key_here
```

Use `"provider": "openai_compatible"` for OpenAI-compatible chat completions, or `"provider": "ollama"` for local Ollama.

## Source-grounded vs Creative Extension

The generated site separates:

- `Source-grounded Notes`: based on extracted local files and source references.
- `Creative Extension`: analogies, practice scenarios, and application questions that may go beyond the uploaded materials.

The practice generator also has two tabs:

- `Source-grounded Practice`
- `Creative Extension Practice`

This distinction is intentional. Do not treat Creative Extension content as a citation from the original slides or documents.

## Project Structure

```text
input_materials/              local input files
output_sites/                 generated versioned sites
demo_projects/ec508_nlp_demo/ retained EC508 local demo note
nlp_lecture_notes_site/       existing EC508 demo site, preserved
scripts/generate_site.py      main generator entry
scripts/extractors/           PDF/MD/DOCX extractors
scripts/llm_client.py         optional LLM wrapper
scripts/site_builder.py       HTML site builder
templates/                    CSS/JS template assets
```

## Limitations

- No SaaS, login, upload UI, database, or hosting workflow is included.
- OCR is not enabled; scanned PDFs may produce empty page warnings.
- Formula extraction depends on the source PDF text layer.
- Browser-side API keys are only suitable for local personal use.

## Copyright

Only process and share lecture materials you have permission to use. Generated summaries may still contain copyrighted course content.
