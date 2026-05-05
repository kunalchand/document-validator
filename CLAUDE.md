# Document Validator — Project Reference

## Overview
A document compliance verification system. Takes a rules document and a user document, extracts structured rules from the former, and evaluates the latter against those rules — producing a structured compliance report with pass/fail status and supporting evidence per rule.

## Tech Stack
| Layer     | Technology                        |
|-----------|-----------------------------------|
| Frontend  | React.js                          |
| Backend   | Python (FastAPI)                  |
| Pipeline  | LangGraph                         |
| LLM       | OpenAI (via LangChain)            |
| Vector DB | TBD (Chroma / FAISS / Pinecone)   |

## Architecture

### Two-Phase Pipeline
The backend processes documents in two separate API calls:

**Phase 1 — Rules Extraction**
- Input: rules document (PDF, DOC/DOCX, or raw text)
- Route input → parse → segment into structural sections
- Fan-out: parallel LLM workers extract structured rule objects per section
- Fan-in: aggregate, deduplicate, validate
- Output: structured JSON list of rules

**Phase 2 — Audit / Compliance Check**
- Input: user document + extracted rules from Phase 1
- Route input → parse → embed chunks into vector DB
- Fan-out: per-rule RAG agent retrieves relevant chunks, evaluates pass/fail
- Fan-in: aggregate into final compliance report
- Output: structured JSON report (rule ID, status, reasoning, evidence)

### API Endpoints
| Method | Path              | Description                        |
|--------|-------------------|------------------------------------|
| POST   | `/extract-rules`  | Phase 1 — extract rules from document |
| POST   | `/audit`          | Phase 2 — audit document against rules |

## Folder Structure
```
document-validator/
├── frontend/                   # React.js application
│   ├── public/
│   └── src/
│       ├── components/         # Reusable UI components
│       ├── pages/              # Page-level components
│       ├── services/           # API call logic
│       ├── hooks/              # Custom React hooks
│       ├── utils/              # Shared helper functions
│       ├── constants/          # App-wide constants
│       └── assets/             # Static assets
│
├── backend/                    # Python / FastAPI application
│   ├── app/
│   │   ├── api/                # Route handlers (FastAPI routers)
│   │   ├── agents/             # LangGraph agents and nodes
│   │   ├── parsers/            # Input parsers (PDF, DOCX, text)
│   │   ├── pipeline/           # LangGraph graph definitions
│   │   ├── utils/              # Shared utilities
│   │   └── constants/          # App-wide constants
│   └── tests/                  # Backend tests
│
└── CLAUDE.md                   # This file
```

## Key Design Decisions
- Rules extraction is a deterministic structuring problem — no vector DB in Phase 1
- Vector DB is used only for the user document in Phase 2
- Map-reduce (fan-out / fan-in) pattern for both rule extraction and rule evaluation
- Stateless between API calls — rules are passed explicitly by the client
- No LangGraph interrupts or checkpointing in v1 (kept simple intentionally)
- All three input types (PDF, DOCX, raw text) are normalized to plain text before pipeline entry

## Standards & Conventions
- SOLID principles throughout frontend and backend
- Structured logging with appropriate log levels (DEBUG / INFO / WARNING / ERROR)
- Consistent HTTP error responses: `{ status, message, detail }`
- All secrets and config via environment variables — never hardcoded
- Constants file for all magic values (model names, chunk sizes, endpoint paths, etc.)
- `.env` files excluded from version control; `.env.example` documents required variables

## Environment Variables
See `frontend/.env.example` and `backend/.env.example` for required variables.

## Future Improvements
- Persistent storage for extracted rules
- Human-in-the-loop review via LangGraph checkpointing
- Citations linking rules to specific evidence passages
- Real-time progress updates (WebSocket or SSE)
- Full compliance dashboard with visual reporting
