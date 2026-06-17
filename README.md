# Multi-Agent Research Assistant

A FastAPI + LangGraph system that generates comprehensive research reports on any topic using four coordinated AI agents.

## Features

- **Research Agent** — searches the web, extracts findings and references
- **Summarization Agent** — deduplicates and organizes information
- **Fact-Checking Agent** — cross-references claims against multiple sources
- **Report Generation Agent** — produces a structured final report
- **Tavily-first search** with **DuckDuckGo fallback** when Tavily fails

## Architecture

```mermaid
flowchart LR
    Client --> FastAPI
    FastAPI --> LangGraph
    LangGraph --> ResearchAgent
    ResearchAgent --> SummarizationAgent
    SummarizationAgent --> FactCheckAgent
    FactCheckAgent --> ReportAgent
    ResearchAgent --> SearchTool
    FactCheckAgent --> SearchTool
    SearchTool --> Tavily
    SearchTool -->|"on failure"| DuckDuckGo
    ResearchAgent --> ChatOpenAI
    SummarizationAgent --> ChatOpenAI
    FactCheckAgent --> ChatOpenAI
    ReportAgent --> ChatOpenAI
    ReportAgent --> FastAPI
```

### Agent Workflow

1. **Research** — runs Tavily (or DuckDuckGo fallback) searches on the topic and LLM-generated sub-queries; extracts raw notes, URLs, and findings.
2. **Summarization** — processes research output into a structured summary with main points and observations.
3. **Fact-Check** — extracts verifiable claims, cross-searches each claim, assigns confidence scores and verification status.
4. **Report** — synthesizes all prior outputs into the final structured report.

## Setup

### Prerequisites

- Python 3.10+
- OpenAI API key
- Tavily API key (optional but recommended; DuckDuckGo is used as fallback)

### Installation

```bash
cd AI_Research_Agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set your keys:

```
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
OPENAI_MODEL=gpt-4o-mini
```

### Run the Server

```bash
uvicorn app.main:app --reload
```

API docs: http://127.0.0.1:8000/docs

## API Documentation

### `GET /api/v1/health`

Health check.

**Response:**
```json
{ "status": "ok" }
```

### `POST /api/v1/research`

Generate a research report for a topic.

**Request:**
```json
{
  "topic": "Impact of Generative AI on Software Development"
}
```

**Response:**
```json
{
  "topic": "Impact of Generative AI on Software Development",
  "executive_summary": "...",
  "key_findings": ["..."],
  "supporting_evidence": ["..."],
  "fact_check_results": [
    {
      "claim": "...",
      "status": "verified",
      "confidence": 0.85,
      "notes": "..."
    }
  ],
  "references": ["https://..."],
  "conclusion": "...",
  "search_providers_used": ["tavily"]
}
```

**cURL example:**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/research \
  -H "Content-Type: application/json" \
  -d '{"topic": "Impact of Generative AI on Software Development"}'
```

### Error Responses

| Status | Cause |
|--------|-------|
| 422 | Invalid request (e.g. topic too short) |
| 502 | Both Tavily and DuckDuckGo search failed |
| 500 | OpenAI or internal error |

## Project Structure

```
app/
├── main.py              # FastAPI application
├── config.py            # Settings and LLM factory
├── api/
│   ├── routes.py        # API endpoints
│   └── schemas.py       # Request/response models
├── agents/
│   ├── state.py         # LangGraph state definition
│   ├── graph.py         # Workflow graph
│   ├── research.py      # Research agent node
│   ├── summarization.py # Summarization agent node
│   ├── fact_check.py    # Fact-checking agent node
│   └── report.py        # Report generation agent node
└── tools/
    └── search.py        # Tavily + DuckDuckGo search
samples/                 # Example generated reports
```

## Assumptions

- **Search**: Tavily is the primary search provider; DuckDuckGo is used automatically when Tavily fails (missing key, API error, timeout).
- **No vector DB**: All context is passed through LangGraph state between agents.
- **Sync API**: Research runs synchronously in the request handler (typical run: 1–3 minutes).
- **Model**: Defaults to `gpt-4o-mini` for cost efficiency; configurable via `OPENAI_MODEL`.
- **Citations**: Agents are instructed to cite only URLs returned by search results.
- **No auth**: API is open; add authentication for production use.

## Sample Outputs

Pre-generated reports are available in [`samples/`](samples/):

- [`generative_ai_report.json`](samples/generative_ai_report.json) — Impact of Generative AI on Software Development
- [`renewable_energy_report.json`](samples/renewable_energy_report.json) — Renewable Energy Adoption in Developing Countries

To regenerate samples:

```bash
PYTHONPATH=. python scripts/generate_samples.py
```

