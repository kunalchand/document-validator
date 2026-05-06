# Document Validator — Project Reference

## Overview
A document compliance verification system. Takes a rules document and a user document, extracts structured rules from the former, and evaluates the latter against those rules — producing a structured compliance report with pass/fail status and supporting evidence per rule.

## Tech Stack
| Layer      | Technology                                                    |
|------------|---------------------------------------------------------------|
| Frontend   | React.js 18 + Vite + Material UI 5 + React Router            |
| Backend    | Python (FastAPI)                                              |
| Pipeline   | LangGraph                                                     |
| LLM        | Ollama (local) / Anthropic (Claude) / Grok (xAI) — config-driven |
| Streaming  | Server-Sent Events (sse-starlette)                            |
| Vector DB  | TBD (Chroma / FAISS / Pinecone) — Phase 2                    |

## Architecture

### Two-Phase Pipeline
The backend processes documents in two separate API calls:

**Phase 1 — Rules Extraction**
- Input: rules document (PDF, DOC/DOCX, or raw text)
- Route input → parse → segment into structural sections
- Fan-out: parallel LLM workers extract structured rule objects per section
- Fan-in: aggregate, deduplicate, validate
- Output: structured JSON list of rules
- Progress: streamed in real-time via SSE

**Phase 2 — Audit / Compliance Check**
- Input: user document + extracted rules from Phase 1
- Route input → parse → embed chunks into vector DB
- Fan-out: per-rule RAG agent retrieves relevant chunks, evaluates pass/fail
- Fan-in: aggregate into final compliance report
- Output: structured JSON report (rule ID, status, reasoning, evidence)

### API Endpoints
| Method | Path                          | Description                                      |
|--------|-------------------------------|--------------------------------------------------|
| GET    | `/`                           | Root health check                                |
| GET    | `/health`                     | Application health status                        |
| POST   | `/api/v1/extract-rules`       | Phase 1 — extract rules (returns JSON on completion) |
| POST   | `/api/v1/extract-rules-stream`| Phase 1 — extract rules with SSE progress stream |
| POST   | `/api/v1/audit`               | Phase 2 — audit document against rules (placeholder) |

## Folder Structure
```
document-validator/
├── frontend/                           # React.js application (Vite)
│   ├── public/                         # Static assets
│   ├── src/
│   │   ├── components/                 # Reusable UI components
│   │   │   ├── DocumentUploadForm.jsx  # Orchestrates upload flow (phase-agnostic)
│   │   │   ├── DocumentTypeSelector.jsx# File/text toggle
│   │   │   ├── FileUploadArea.jsx      # Drag-and-drop file upload with validation
│   │   │   ├── TextInputArea.jsx       # Textarea input with char limit
│   │   │   ├── RuleCard.jsx            # Individual rule card with inline editing
│   │   │   ├── RulesList.jsx           # List of rules with search/filter
│   │   │   ├── ReadyForAudit.jsx       # Phase 1 completion screen
│   │   │   ├── ConfirmationDialog.jsx  # Reusable confirmation modal
│   │   │   └── ExtractionProgress.jsx  # Live + completed SSE progress display
│   │   ├── pages/
│   │   │   └── Phase1.jsx              # Three-step flow: Upload → Review → Ready
│   │   ├── services/
│   │   │   ├── apiClient.js            # Axios client with interceptors
│   │   │   └── documentService.js      # API methods (extractRulesStream, audit)
│   │   ├── utils/
│   │   │   └── fileValidator.js        # File and text validation helpers
│   │   ├── types/
│   │   │   └── extraction.ts           # TypeScript interfaces for SSE event schema
│   │   ├── constants/
│   │   │   └── documentTypes.js        # File types, sizes, formats
│   │   ├── App.jsx                     # Root component with Router + MUI theme
│   │   └── main.jsx                    # React entry point
│   ├── index.html                      # HTML entry
│   ├── vite.config.js                  # Vite configuration with API proxy
│   ├── package.json                    # Dependencies
│   ├── .env                            # Environment variables (gitignored)
│   ├── .env.example                    # Environment variable template
│   └── .gitignore
│
├── backend/                            # Python / FastAPI application
│   ├── app/
│   │   ├── main.py                     # FastAPI app setup with middleware & handlers
│   │   ├── config.py                   # Settings and configuration (pydantic)
│   │   ├── core/
│   │   │   ├── logger.py               # configure_logging() + get_logger(); file + console output
│   │   │   ├── exceptions.py           # Custom exception classes
│   │   │   └── __init__.py
│   │   ├── api/                        # REST API layer (v1 routing)
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       │   ├── rules.py        # POST /extract-rules (sync JSON response)
│   │   │       │   ├── stream.py       # POST /extract-rules-stream (SSE response)
│   │   │       │   ├── audit.py        # POST /audit (Phase 2 placeholder)
│   │   │       │   └── __init__.py
│   │   │       ├── schemas.py          # Pydantic request/response models
│   │   │       └── __init__.py
│   │   ├── providers/                  # LLM provider abstraction layer
│   │   │   ├── base.py                 # LLMProvider + EmbeddingProvider ABCs (async-only interface)
│   │   │   ├── schemas.py              # LLMRequest/Response, EmbeddingRequest/Response
│   │   │   ├── factory.py              # ProviderFactory + ProviderType enum
│   │   │   ├── ollama_provider.py      # Local Ollama via httpx REST (no API key required)
│   │   │   ├── anthropic_provider.py   # Claude via anthropic SDK
│   │   │   ├── grok_provider.py        # xAI Grok via OpenAI-compatible API
│   │   │   ├── dummy_provider.py       # DummyEmbeddingProvider — Phase 2 placeholder only
│   │   │   ├── README.md               # Provider documentation
│   │   │   ├── PROVIDER_TEMPLATE.md    # How to add new providers
│   │   │   └── __init__.py
│   │   ├── parsers/                    # Document parsers
│   │   │   ├── base.py                 # Abstract DocumentParser base class
│   │   │   ├── pdf_parser.py           # PDFParser — text extraction via PyPDF2
│   │   │   ├── docx_parser.py          # DOCXParser — text extraction via python-docx
│   │   │   ├── text_parser.py          # TextParser — passthrough for plain text
│   │   │   └── __init__.py
│   │   ├── agents/                     # Agent logic and schemas
│   │   │   ├── schemas.py              # DocumentSegment, RuleCandidate (Pydantic)
│   │   │   ├── nodes.py                # Pure functions: segment_text, build_extraction_prompt,
│   │   │   │                           #   parse_llm_response, deduplicate_rules
│   │   │   ├── events.py               # SSE event schema: ExtractionEvent and related types
│   │   │   └── __init__.py
│   │   ├── pipeline/                   # LangGraph graph definitions
│   │   │   ├── phase1_state.py         # Phase1State TypedDict (LangGraph state)
│   │   │   ├── phase1_graph.py         # Phase1Pipeline: LangGraph graph + run() + stream()
│   │   │   └── __init__.py
│   │   ├── utils/
│   │   │   ├── validators.py           # Input validation logic
│   │   │   └── __init__.py
│   │   ├── constants/                  # App-wide constants
│   │   └── __init__.py
│   ├── logs/                           # Runtime log files (gitignored except .gitkeep)
│   │   └── .gitkeep
│   ├── tests/                          # Backend tests (coming soon)
│   ├── main.py                         # Entry point for running server
│   ├── .env                            # Environment variables (gitignored)
│   ├── .env.example                    # Environment variable template
│   ├── .gitignore
│   ├── requirements.txt                # Python dependencies
│   └── README.md                       # Backend documentation
│
└── CLAUDE.md                           # This file
```

## Frontend Implementation Status

### Phase 1: Rules Extraction & Confirmation
Three-step user flow with Material UI components:

**Step 1: Upload Rules Document**
- Document type selector (File upload or Paste text)
- File upload area with drag-and-drop and validation
- Text input area with character limit tracking
- Supports PDF, DOCX, and raw text
- Max file size: 10MB, max text: 50,000 characters
- **Connected to real SSE endpoint** — streams extraction progress in real-time
- `ExtractionProgress` renders inside the main Paper card, above the upload form, from the moment the first event arrives

**Step 2: Review & Confirm**
- `ExtractionProgress` persists at the top of the same Paper card in a collapsed "Extraction Complete" state — expand to view the full event log
- Displays extracted rules in card-based UI below the progress summary
- Search by title/description
- Filter by severity (high/medium/low)
- Rule summary stats (total count, breakdown by severity)
- Inline editing: modify conditions and expected evidence
- Add/remove individual conditions and evidence items
- Delete rules with confirmation dialog
- "Upload New Document" button with confirmation (clears events, rules, and error state)
- "Confirm Rules & Continue" button to move to step 3

**Step 3: Ready for Audit**
- Success confirmation screen
- Rules summary (count and status)
- Info about Phase 2
- "Back to Review" button (returns to step 2)
- "Proceed to Phase 2: Audit Document" button (TODO: navigate to Phase 2)

### ExtractionProgress Component (`ExtractionProgress.jsx`)
Dual-mode SSE progress display — live during extraction, persistent log after completion.

**Features**:
- Receives `events` prop — array of `ExtractionEvent` objects from backend SSE stream
- Collapsible card with current stage name and overall progress bar
- Segment-level progress text (e.g., "Segment 3 of 7 • 12 rules found so far")
- Color-coded stages: parsing (blue) / segmentation (orange) / extraction (purple) / finalization (green)
- Animated spinning icon for the active stage, checkmark for all completed stages
- When `isComplete`: all four stages show the checkmark (finalization stage no longer stuck on "active")
- **Expandable details panel** shows:
  - Key metrics grid (document size, sections found, rules found/unique)
  - Section titles identified (as chips)
  - Processing timeline showing all four stages with status badges
  - Full event log with timestamps
- Error state: red border, warning icon, error message
- Starts collapsed by default — useful on step 1 where it acts as an audit trail

### Toast Notifications (Snackbar)
MUI `Snackbar` in `Phase1.jsx` at the container level — persists across step transitions.

| Trigger | Severity | Message |
|---------|----------|---------|
| `extraction_complete` with `failed_segments > 0` | warning | "N section(s) failed during extraction — results may be incomplete. Check backend logs for details." |
| `error` SSE event | error | "Extraction failed: \<message\>" |
| Network / fetch error | error | Error message from the thrown exception |

### Layout — Single Card Surface
`ExtractionProgress` lives inside the `<Paper>` card for all steps:
- **Before extraction**: card shows the upload form only (no events yet)
- **During extraction**: progress bar at the top of the card; upload form hidden while loading
- **Step 1 (review)**: collapsed "Extraction Complete" summary at top of card; header text and rules list below
- **"Upload New Document"**: clears `extractionEvents`, `extractionError`, and rules — card returns to clean upload state

### Routing
React Router v6 with a single production route:
- `/` → `Phase1` page (main application flow)

### Component Architecture
- **DocumentUploadForm**: Reusable component accepting `phase` prop for multi-phase support
- **RuleCard**: Editable rule with expand/collapse for conditions and evidence
- **RulesList**: Stateful list with search, filter, and CRUD operations
- **ConfirmationDialog**: Reusable modal for destructive actions
- **ExtractionProgress**: Live + completed SSE event display with collapsible details; driven entirely by `events` prop
- Material UI theme applied globally via `ThemeProvider`

### Services & Utilities
- **apiClient.js**: Axios instance with baseURL and error interceptor
- **documentService.js**:
  - `extractRules()` — sync extraction endpoint (for future use)
  - `extractRulesStream()` — **SSE streaming endpoint** for real-time progress (used by Phase1)
  - `auditDocument()` / `auditDocumentWithText()` — Phase 2 audit endpoints
- **fileValidator.js**: Validation for file type, size, and text length
- **documentTypes.js**: Constants for MIME types, extensions, limits

### TypeScript Types (`types/extraction.ts`)
Full TypeScript interface definitions for the SSE event schema — mirrors the Python Pydantic models:
- `ExtractionEvent` — top-level event interface
- `ExtractionEventType` — union of all 10 valid event type strings
- `ExtractionStage` — pipeline stage union
- `ExtractionProgress` — `current`, `total`, `percent`
- `ExtractionEventData` — all contextual data fields including `failed_segments` and `extracted_rules`

### Build & Run
```bash
cd frontend
npm install
npm run dev              # Runs on http://localhost:3000
npm run build            # Production build
```

## Backend Implementation Status

### API Layer (Phase 1 - REST API)

**Framework**: FastAPI with automatic Swagger/OpenAPI documentation

**Endpoints Implemented**:
- `GET /` - Root health check
- `GET /health` - Application health status
- `POST /api/v1/extract-rules` - Extract rules, returns `ExtractRulesResponse` on completion
- `POST /api/v1/extract-rules-stream` - Extract rules with SSE progress streaming
- `POST /api/v1/audit` - Audit document against rules (Phase 2 placeholder)

**Request/Response Models** (`app/api/v1/schemas.py`):
- `Rule`: id, title, description, conditions[], expected_evidence[], section, severity, status
- `ExtractRulesResponse`: document_id, total_rules, rules[], extraction_timestamp, status
- `AuditResultRule`: rule_id, rule_title, status, confidence, reasoning, evidence[]
- `AuditResponse`: document_id, total/passed/failed rules, compliance_score, results[], audit_timestamp
- `ErrorResponse`: status, message, detail

**Core Components**:
1. **Configuration** (`config.py`): Pydantic BaseSettings, LRU-cached singleton; defaults to `ollama` + `llama2`; includes `log_file` setting
2. **Logging** (`core/logger.py`): `configure_logging(log_level, log_file)` sets up the root logger once at startup with a console `StreamHandler` and a `RotatingFileHandler` (10 MB per file, 5 backups). `get_logger(name)` returns named child loggers that inherit both handlers. Called from `main.py` before any logger is created.
3. **Exceptions** (`core/exceptions.py`): `InvalidInputException` (400), `FileParseFailed` (422), `ExtractionFailed` (500), `AuditFailed` (500)
4. **Validation** (`utils/validators.py`): `validate_file()`, `validate_text()`

**Log file**: written to `backend/logs/app.log` by default. Tail it live:
```bash
tail -f backend/logs/app.log
```
Set `LOG_FILE=` (empty) in `backend/.env` to disable file logging.

**Build & Run**:
```bash
cd backend
pip install -r requirements.txt
python main.py                    # Runs on http://localhost:8000
```

Access Swagger at `http://localhost:8000/docs`

### Provider Abstraction Layer

**Pattern**: Abstract Factory with Python ABC (Abstract Base Classes)

**Interface** (`app/providers/base.py`) — async-only, trimmed to what the pipeline actually uses:
```python
class LLMProvider(ABC):
    async def generate(self, request: LLMRequest) -> LLMResponse: ...
    def provider_name(self) -> str: ...          # property
```

**Implemented LLM Providers**:
| Provider | File | Auth | Default Model |
|----------|------|------|---------------|
| Ollama (local) | `ollama_provider.py` | None — no API key needed | `llama2` |
| Anthropic (Claude) | `anthropic_provider.py` | `LLM_API_KEY=sk-ant-...` | `claude-haiku-4-5-20251001` |
| Grok (xAI) | `grok_provider.py` | `LLM_API_KEY=xai-...` | `grok-3-mini` |

**Embedding**: `DummyEmbeddingProvider` in `dummy_provider.py` — placeholder only; real embedding providers added in Phase 2.

**Switching providers** — set in `backend/.env`:
```env
# Ollama (local, default)
LLM_PROVIDER=ollama
LLM_MODEL=llama2           # or mistral, or any installed model
OLLAMA_HOST=http://localhost:11434

# Anthropic
LLM_PROVIDER=anthropic
LLM_API_KEY=sk-ant-...
LLM_MODEL=claude-haiku-4-5-20251001

# Grok
LLM_PROVIDER=grok
LLM_API_KEY=xai-...
LLM_MODEL=grok-3-mini
```

### Agentic Layer (Phase 1 - Implemented)

#### Document Parsers (`app/parsers/`)
- **`base.py`**: Abstract `DocumentParser` with `parse(content) -> str` and `supported_formats` property
- **`pdf_parser.py`**: `PDFParser` — extracts text page-by-page via PyPDF2
- **`docx_parser.py`**: `DOCXParser` — extracts paragraphs via python-docx
- **`text_parser.py`**: `TextParser` — passthrough, decodes bytes if needed

#### Agent Schemas (`app/agents/schemas.py`)
- **`DocumentSegment`**: index, title, content, char_count
- **`RuleCandidate`**: title, description, conditions[], expected_evidence[], severity, section, source_segment_index

#### Agent Nodes (`app/agents/nodes.py`)
Pure helper functions used by the pipeline nodes:
- **`segment_text(text, max_chars=3000)`**: Splits on section headings (numbered, ALL-CAPS, markdown, Article/Section/Chapter patterns), falls back to paragraph-boundary chunking
- **`build_extraction_prompt(segment)`**: Formats the structured JSON-extraction prompt for the LLM
- **`parse_llm_response(content, segment_index)`**: Strips markdown fences, extracts JSON array, validates and constructs `RuleCandidate` objects; on JSON decode error logs the first 300 characters of the LLM response for debugging
- **`deduplicate_rules(candidates)`**: Removes duplicates by normalized title

#### SSE Event Schema (`app/agents/events.py`)
Pydantic models that mirror the TypeScript types in `frontend/src/types/extraction.ts`:
- **`ExtractionEventType`** (str Enum): `parsing_started`, `parsing_complete`, `segmentation_started`, `segmentation_complete`, `extraction_started`, `extraction_progress`, `extraction_complete`, `finalization_started`, `finalization_complete`, `error`
- **`ExtractionStage`** (str Enum): `parsing`, `segmentation`, `extraction`, `finalization`
- **`ExtractionProgress`**: current, total, percent
- **`ExtractionEventData`**: char_count, page_count, section_count, section_titles, segment_index, segment_title, rules_in_segment, total_rules_so_far, **`failed_segments`** (count of worker failures in `extraction_complete`), total_rules, unique_rules, extracted_rules (only in `finalization_complete`)
- **`ExtractionEvent`**: event_type, stage, message, progress, data, timestamp, event_id

#### LangGraph State (`app/pipeline/phase1_state.py`)
```python
class Phase1State(TypedDict):
    input_type: str                          # "pdf" | "docx" | "text"
    raw_file_bytes: Optional[bytes]
    raw_filename: Optional[str]
    raw_text: Optional[str]
    parsed_text: Optional[str]
    segments: List[DocumentSegment]
    rule_candidates: List[RuleCandidate]
    extracted_rules: List[dict]
    errors: Annotated[List[str], operator.add]   # accumulated warnings
```

#### Phase1Pipeline (`app/pipeline/phase1_graph.py`)
LangGraph `StateGraph` with four nodes and two execution modes:

**Graph flow**: `parse_input → segment_content → orchestrate_extraction → finalize_rules`

**Nodes**:
- `parse_input`: Routes to the correct parser; emits `parsing_started`, `parsing_complete`
- `segment_content`: Calls `segment_text()`; emits `segmentation_started`, `segmentation_complete` (with section count and titles)
- `orchestrate_extraction`: Dispatches `asyncio.gather` fan-out of worker tasks; emits `extraction_started`, one `extraction_progress` per segment (with `asyncio.Lock` for safe concurrent counter), `extraction_complete` — the `extraction_complete` event includes `failed_segments` count so the frontend can warn the user if any workers failed
- `finalize_rules`: Deduplicates, assigns `rule_NNN` IDs; emits `finalization_started`, `finalization_complete` (with full `extracted_rules` list in event data)

**Error observability**:
- `_worker_extract` uses `logger.exception()` — full traceback written to log file on any LLM or parse failure
- `_orchestrate_extraction` counts failed workers and includes the count in `extraction_complete` event data (`failed_segments` field) and in the event message

**Event emission**: `_emit()` calls `asyncio.Queue.put_nowait()` — non-blocking, safe from both sync and async nodes

**`run()` method**: Standard async call returning `list[dict]` when complete (used by `/extract-rules` endpoint)

**`stream()` method**: Async generator using `asyncio.Queue` + `asyncio.create_task` pattern. Pipeline runs as a background task; `stream()` drains the queue and yields `ExtractionEvent` objects. A sentinel (`_STREAM_DONE`) signals end of stream. Used by `/extract-rules-stream` endpoint.

### SSE Streaming Endpoint (`app/api/v1/endpoints/stream.py`)

**`POST /api/v1/extract-rules-stream`**

Key design decisions:
- Input validation and file reading happen **before** `EventSourceResponse` is returned, so invalid inputs return standard HTTP 400/422 JSON (not SSE error events)
- `Last-Event-ID` header is read for SSE spec compliance; event IDs are sequential integers
- `retry: 5000ms` sent with every event (browser reconnect interval)
- Each event frame: `event=<event_type>`, `id=<sequential_int>`, `data=<ExtractionEvent JSON>`, `retry=5000`
- Pipeline errors after the stream opens are delivered as `error` SSE events
- Final `finalization_complete` event carries the complete `extracted_rules` list — frontend reads rules from this event without a separate API call

**Frontend consumption** (since `EventSource` only supports GET, file uploads use `fetch()`):
```javascript
const response = await fetch('/api/v1/extract-rules-stream', {
  method: 'POST',
  body: formData,
})
const reader = response.body.getReader()
// Read chunks, split on '\n', parse lines starting with 'data: '
// Final event (finalization_complete) contains event.data.extracted_rules
```

## Key Design Decisions

**Backend**:
- Rules extraction is a deterministic structuring problem — no vector DB in Phase 1
- Vector DB is used only for the user document in Phase 2
- Map-reduce (fan-out / fan-in) with `asyncio.gather` for parallel per-segment LLM calls
- Stateless between API calls — rules are passed explicitly by the client
- No LangGraph interrupts or checkpointing in v1 (kept simple intentionally)
- All three input types (PDF, DOCX, raw text) normalized to plain text before pipeline entry
- **Provider-agnostic LLM interface** — async-only (`generate`), no sync/batch variants; concurrency handled by `asyncio.gather` at the pipeline level
- **Two endpoint modes**: `/extract-rules` (sync JSON) and `/extract-rules-stream` (SSE) — same pipeline, different execution paths (`run()` vs `stream()`)
- **Circular import prevention**: pipeline layer (`app/pipeline/`) never imports from API layer (`app/api/`); pipeline returns `list[dict]`, API layer owns Pydantic conversion
- `sse-starlette==1.6.5` pinned for compatibility with FastAPI 0.104.1 (starlette<0.28, anyio<4)
- **Logging**: `configure_logging()` called once at app startup; root logger gets both console and rotating file handler; all module loggers inherit via standard Python logging hierarchy

**Frontend**:
- **SSE Integration** (`documentService.extractRulesStream()`):
  - Uses native `fetch()` API with `ReadableStream` instead of `EventSource` (which only supports GET)
  - Handles streaming response by reading chunks, splitting on newlines, and parsing `data: ` lines as JSON events
  - Calls `onEvent` callback for each event, allowing real-time UI updates without accumulating in memory
- `ExtractionProgress` component is driven entirely by an `events` prop — no internal fetching
- `ExtractionProgress` lives inside the `<Paper>` card for all steps — single card surface; no blank card during loading
- SSE event schema is defined in both Python (Pydantic) and TypeScript (interfaces) to keep the contract explicit and type-safe on both ends
- Phase1 component manages extraction state (`extractionEvents`, `extractionError`) and automatically transitions to review step when `finalization_complete` event arrives with `extracted_rules`
- Partial failures (some segments failed, but extraction completed) surface as a MUI Snackbar warning rather than a fatal error — user is informed but can still review the partial results
- No demo/simulator code in production — all data flows from the real backend

## Standards & Conventions

**Backend**:
- SOLID principles throughout (Dependency Inversion, Open/Closed, Single Responsibility)
- Abstract Factory pattern for provider abstraction
- Structured logging with appropriate levels (DEBUG / INFO / WARNING / ERROR); `logger.exception()` used for unexpected failures to capture full tracebacks
- Consistent HTTP error responses: `{ status, message, detail }`
- All secrets via environment variables — never hardcoded
- Type-safe with Pydantic validation for all requests/responses and SSE events
- Async-first design; pipeline nodes emit via `put_nowait` (non-blocking)

**Frontend & General**:
- SOLID principles throughout
- `.env` files excluded from version control; `.env.example` documents required variables
- No directional icons (arrows) on buttons — text labels speak for themselves
- Confirmation dialogs for destructive actions (data loss, deletion)
- Component props are the single source of truth — no hidden internal API calls in display components
- Toast notifications (MUI Snackbar) for non-fatal warnings that survive step transitions

## Environment Variables

**Backend** (`backend/.env.example`):
- `APP_ENV` - Environment (production)
- `LOG_LEVEL` - Logging level (DEBUG/INFO/WARNING/ERROR)
- `LOG_FILE` - Path to log file relative to `backend/` (default: `logs/app.log`; set empty to disable)
- `LLM_PROVIDER` - LLM provider: `ollama` | `anthropic` | `grok`
- `LLM_API_KEY` - API key (not required for Ollama)
- `LLM_MODEL` - Model name (provider-specific; e.g. `llama2`, `mistral`, `claude-haiku-4-5-20251001`)
- `OLLAMA_HOST` - Ollama server URL (default: `http://localhost:11434`)
- `EMBEDDING_PROVIDER` - `dummy` (Phase 1 placeholder)
- File limits: `MAX_FILE_SIZE_MB`, `MAX_TEXT_LENGTH`, `MAX_RULES`
- CORS: `CORS_ORIGINS`

**Frontend** (`frontend/.env.example`):
- `VITE_API_BASE_URL` - Backend API URL (default: `http://localhost:8000`)
- `VITE_APP_ENV` - Environment (`production`)

## Next Steps

### Backend (Priority)
1. Set up vector database (Chroma / FAISS / Pinecone) for Phase 2 embedding storage
2. Implement Phase 2 RAG-based audit pipeline (`app/agents/`, `app/pipeline/`)
3. Add real embedding provider (OpenAI, Ollama embeddings) to replace `DummyEmbeddingProvider`
4. Implement Phase 2 SSE streaming endpoint for audit progress
5. Write test suite (`backend/tests/`)

### Frontend (Priority)
1. ✅ **COMPLETE**: Phase 1 — real SSE extraction, ExtractionProgress, rules review flow
2. ✅ **COMPLETE**: Toast notifications (Snackbar) for partial failures and fatal errors
3. ✅ **COMPLETE**: Persistent extraction log on step 1 (collapsed "Extraction Complete" summary)
4. Build Phase 2 frontend (Audit Document upload and compliance results view)
5. Add error recovery UI (retry button when extraction fails)

### Integration & Testing
- End-to-end test with a real PDF document across all three LLM providers
- Performance tuning (Ollama concurrency, segment size optimization)
- Comprehensive test coverage (unit, integration, E2E)

## Future Improvements
- Persistent storage for extracted rules (session or DB)
- Human-in-the-loop review via LangGraph checkpointing
- Citations linking rules to specific evidence passages
- Full compliance dashboard with visual reporting
- Export rules and reports (PDF, CSV)
- Bulk rule management (import/export)
- Phase 2 SSE streaming for audit progress
