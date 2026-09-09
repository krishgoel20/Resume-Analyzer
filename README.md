# 🤖 FitScore

A LLM-powered tool that compares a resume against a job description and returns a structured match analysis — score, matching/missing skills, and actionable suggestions. The analysis pipeline is built as an explicit **LangGraph** graph with guardrails against malformed, low-quality, and adversarial input.

---

## What it does

- Upload a resume as a .pdf or .docx file, or paste resume text directly — both paths are treated identically
- Paste a job description alongside it and get an LLM-generated match analysis in one click
- Get a **match score (0-100)**, rendered as a progress bar
- See a clear breakdown of **matching skills** and **missing skills**, side by side
- Get specific, actionable **suggestions** for tailoring the resume to that job description
- Have every result **enforced against a strict schema** — the LLM cannot return malformed or incomplete output
- Get flagged with a **warning** if the result looks internally inconsistent (e.g., a near-perfect score with no missing skills)
- Have the resume text automatically **checked for prompt injection attempts** before it's sent to the LLM
- Have an **oversized, empty, or garbled file rejected upfront**, with a clear message, instead of silently producing a bad analysis

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI | Python, Streamlit |
| AI / LLM | Groq API (`openai/gpt-oss-120b`) |
| Schema / Validation | Pydantic |
| Orchestration | LangGraph |
| File Parsing | pypdf, python-docx |
| Config | python-dotenv |

---

## How It Works

```
Resume Upload / Paste
↓
[File size check — upload path only]
↓
┌─────────── LangGraph Pipeline ───────────┐
│ │
│ validate (length + prompt injection) │
│ │ │
│ error? ─┴─ no ──▶ analyze (LLM) │
│ │ │ │
│ ▼ ▼ │
│ END sanity_check │
│ │ │
│ ▼ │
│ END │
└───────────────────────────────────────────┘
↓
Result
```

---

## Project Structure

```
Resume-Analyzer/
├── app.py           # Streamlit UI; handles file upload + invokes the pipeline
├── graph.py         # LangGraph pipeline: state, nodes, conditional routing
├── analyzer.py      # LLM prompt construction and structured output logic
├── models.py        # Pydantic schema for the analysis result
├── file_utils.py    # PDF/DOCX text extraction
├── guardrails.py    # File, injection, and output validation logic
└── requirements.txt
```

---

## Setup and Installation

### Pre-requisites
- Python 3.11+
- Groq API key ([console.groq.com](https://console.groq.com))

### 1. Clone the repository

```bash
git clone https://github.com/krishgoel20/Resume-Analyzer.git
cd Resume-Analyzer
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
venv\Scripts\Activate.ps1       # Windows
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key
```

### 4. Run the app

```bash
   streamlit run app.py
```

App runs at `http://localhost:8501`.

---

## Features

### AI Features
- 🎯 **Structured LLM analysis** — a single Groq API call returns match score, matching skills, missing skills, and improvement suggestions as strict, schema-validated JSON (strict: true mode), not free-form text
- 🔀 **LangGraph-orchestrated pipeline** — validation, analysis, and output sanity-checking run as an explicit graph (validate → analyze → sanity_check) with conditional routing, rather than manual if/try branching
- ✅ **Output sanity checks** — flags internally inconsistent results (e.g., a near-perfect score with zero missing skills, or listed "matching skills" that don't actually appear in the resume text) as advisory warnings, without blocking the result

### 📄 Input Features
- **Dual input paths** — upload a .pdf/.docx file, or paste resume text directly; both paths run through identical validation and analysis logic
- **File text extraction** — pypdf and python-docx extract plain text from uploaded resumes before analysis

### 🛡️ Guardrail/Security Features
- **File validation** — rejects oversized files (>5MB), and files that produce suspiciously short or garbled extracted text (via an alphabetic-character-ratio heuristic)
- **Prompt injection detection** — keyword-based filtering catches common manipulation attempts (e.g., "ignore previous instructions") embedded in resume text before it reaches the LLM
- **Prompt hardening** — the system prompt explicitly establishes that resume content is untrusted data, never instructions, as a structural defense layer beyond keyword filtering
- **Consistent enforcement** — every guardrail applies identically to both the file-upload and text-paste paths

---

## Key Concepts Demonstrated

- **Structured LLM Output** — the analysis prompt uses Groq's response_format={"type": "json_schema", ...} with a Pydantic-generated schema and strict: true, guaranteeing the response conforms exactly to ResumeAnalysis rather than requiring text parsing.
- **Schema-first design with Pydantic** — ResumeAnalysis (with Field(ge=, le=, description=) constraints and ConfigDict(extra="forbid")) is the single source of truth for output shape, consumed both by the API call and by the rendering logic.
- **Pipeline orchestration with LangGraph** — the guardrail flow is modeled as a StateGraph with a shared PipelineState, three nodes (validate, analyze, sanity_check), and a conditional edge that routes straight to END on validation failure, making the entire control flow explicit and inspectable in one file.
- **Defense-in-depth against adversarial input** — prompt injection is addressed at two independent layers: pattern-based detection before the LLM call, and a hardened system prompt establishing an instruction-authority hierarchy in case something slips past the first layer.
- **Separation of concerns** — UI (app.py), orchestration (graph.py), LLM logic (analyzer.py), schema (models.py), file handling (file_utils.py), and validation (guardrails.py) are each isolated in their own module.
- **Environment-based configuration** — the Groq API key is loaded from a .env file excluded from version control via .gitignore, never hardcoded in source.

---

## Limitations

- **No cloud deployment yet** — the app currently runs locally only, via streamlit run app.py.
- **Keyword-based injection detection, not semantic** — the injection filter matches known phrases; a reworded or more sophisticated injection attempt could bypass it. This is a known, unsolved limitation of pattern-based defenses, not unique to this project.
- **No OCR for scanned/image-based PDFs** — a PDF with no real text layer (a scanned image) will fail the minimum-text-length check rather than being processed via OCR.
- **.doc (legacy Word format) unsupported** — only .docx is supported; python-docx cannot parse the older binary .doc format.
- **Output sanity checks are heuristic, not exhaustive** — the "verbatim skill" cross-check is a simple substring match, so it can false-positive on paraphrased skills (e.g., "REST APIs" v/s "RESTful services") and won't catch every form of hallucinated output.
- **No persistence** — each analysis is a one-off; results aren't saved, and there's no history of past analyses across sessions.
- **Single LLM provider** — tightly coupled to Groq's API and the specific model (openai/gpt-oss-120b); switching providers would require reworking the structured-output call.

---
