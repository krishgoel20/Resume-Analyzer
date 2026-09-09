# 🤖 AI Resume & Job Description Analyzer

An LLM-powered tool that compares a resume against a job description and returns a structured match analysis — score, matching/missing skills, and actionable suggestions. The analysis pipeline is built as an explicit **LangGraph** graph with guardrails against malformed, low-quality, and adversarial input.

## Features

- 📄 **Resume input** via file upload (`.pdf`, `.docx`) or direct text paste
- 🎯 **Structured analysis** — match score, matching skills, missing skills, and improvement suggestions
- ✅ **Schema-enforced output** using Pydantic + Groq's structured outputs (strict JSON schema mode, not just "best effort")
- 🔀 **LangGraph-orchestrated pipeline** — validation, analysis, and output sanity-checking as an explicit graph with conditional routing, instead of manual if/try branching
- 🛡️ **Guardrails**:
  - File size and content validation (rejects oversized, empty, or garbled files)
  - Prompt injection detection (keyword filtering + hardened system prompt)
  - Output sanity checks (flags suspicious score/skill combinations)
  - Identical validation applied to both the file-upload and text-paste input paths

## Tech Stack

- **Python**
- **Streamlit** — UI
- **Groq API** (`openai/gpt-oss-120b`) — LLM inference with structured outputs
- **Pydantic** — schema definition and validation
- **LangGraph** — pipeline orchestration (state graph with conditional edges)
- **pypdf** / **python-docx** — file text extraction

## How It Works

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


## Setup

1. Clone the repo:
```bash
   git clone https://github.com/krishgoel20/resume-analyzer.git
   cd resume-analyzer
```

2. Create a virtual environment and install dependencies:
```bash
   python -m venv venv
   venv\Scripts\Activate.ps1   # Windows
   pip install -r requirements.txt
```

3. Add your Groq API key in a `.env` file:

GROQ_API_KEY=your_key_here


4. Run the app:
```bash
   streamlit run app.py
```

## Project Structure

```
resume-analyzer/
├── app.py # Streamlit UI; handles file upload + invokes the pipeline
├── graph.py # LangGraph pipeline: state, nodes, conditional routing
├── analyzer.py # LLM prompt construction and structured output logic
├── models.py # Pydantic schema for the analysis result
├── file_utils.py # PDF/DOCX text extraction
├── guardrails.py # File, injection, and output validation logic
├── requirements.txt
└── .env # API key (not committed)
```

## What This Project Demonstrates

- Prompt engineering and system message design
- LLM structured outputs (Pydantic + JSON Schema, `strict: true` mode)
- Pipeline orchestration with LangGraph — explicit state, nodes, and conditional edges instead of nested control flow
- Defense-in-depth guardrails: input validation, prompt injection resistance, output sanity checking
- Clean separation of concerns (UI / orchestration / LLM logic / file handling / validation)