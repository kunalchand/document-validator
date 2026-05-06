# Document Validator

A document compliance verification system. Upload a rules document, extract structured compliance rules using an LLM, review and edit them, then audit any user document against those rules.

## How It Works

**Phase 1 — Rules Extraction**
Upload a rules document (PDF, DOCX, or plain text). The backend segments it, sends each section to an LLM in parallel, and streams real-time progress back to the UI via Server-Sent Events. The final event delivers the full extracted rules list.

**Phase 2 — Audit** *(coming soon)*
Upload a user document and run it against the confirmed rules. Each rule is evaluated using RAG (retrieval-augmented generation) — evidence passages are retrieved from a vector DB and passed to the LLM for a pass/fail decision.

## Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+
- One of the following LLM setups:
  - [Ollama](https://ollama.com) running locally (default) — `ollama pull llama2` or `ollama pull mistral`
  - Anthropic API key
  - Grok (xAI) API key

## Setup & Run

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env        # then edit .env with your provider choice
python main.py              # starts on http://localhost:8000
```

API docs available at `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
cp .env.example .env        # edit VITE_API_BASE_URL if backend is not on port 8000
npm run dev                 # starts on http://localhost:3000
```

## LLM Provider Configuration

Set these in `backend/.env`:

```env
# Ollama (local, no API key required)
LLM_PROVIDER=ollama
LLM_MODEL=llama2            # or mistral, or any model you have pulled
OLLAMA_HOST=http://localhost:11434

# Anthropic (Claude)
LLM_PROVIDER=anthropic
LLM_API_KEY=sk-ant-...
LLM_MODEL=claude-haiku-4-5-20251001

# Grok (xAI)
LLM_PROVIDER=grok
LLM_API_KEY=xai-...
LLM_MODEL=grok-3-mini
```

Restart the backend after changing the provider.

## Supported Input Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| PDF | `.pdf` | Text extracted page-by-page |
| Word | `.docx`, `.doc` | Paragraph text extracted |
| Plain text | `.txt` or paste | Used directly |

Max file size: 10 MB. Max pasted text: 50,000 characters.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, Material UI 5, React Router |
| Backend | Python, FastAPI, LangGraph |
| LLM | Ollama / Anthropic / Grok — config-driven |
| Streaming | Server-Sent Events (sse-starlette) |
| Vector DB | Phase 2 — TBD |

## Project Structure

```
document-validator/
├── frontend/     # React application
├── backend/      # FastAPI + LangGraph pipeline
└── CLAUDE.md     # Full technical reference for contributors
```

See [CLAUDE.md](./CLAUDE.md) for the complete architecture reference, design decisions, and contribution guide.
