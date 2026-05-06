# Document Validator — Project Reference

## Overview
A document compliance verification system. Takes a rules document and a user document, extracts structured rules from the former, and evaluates the latter against those rules — producing a structured compliance report with pass/fail status and supporting evidence per rule.

## Tech Stack
| Layer      | Technology                                        |
|------------|---------------------------------------------------|
| Frontend   | React.js 18 + Vite + Material UI 5 + React Router |
| Backend    | Python (FastAPI)                                  |
| Pipeline   | LangGraph                                         |
| LLM        | Provider-agnostic (dummy / OpenAI / Anthropic / Google / Grok) |
| Streaming  | Server-Sent Events (sse-starlette)                |
| Vector DB  | TBD (Chroma / FAISS / Pinecone) — Phase 2         |

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
│   │   │   └── ExtractionProgress.jsx  # Real-time SSE progress display
│   │   ├── pages/
│   │   │   ├── Phase1.jsx              # Three-step flow: Upload → Review → Ready
│   │   │   └── ExtractionProgressDemo.jsx  # Interactive component demo page
│   │   ├── services/
│   │   │   ├── apiClient.js            # Axios client with interceptors
│   │   │   └── documentService.js      # API methods (extract-rules, audit)
│   │   ├── utils/
│   │   │   ├── fileValidator.js        # File and text validation helpers
│   │   │   └── extractionSimulator.js  # SSE event stream simulator for demo/testing
│   │   ├── types/
│   │   │   └── extraction.ts           # TypeScript interfaces for SSE event schema
│   │   ├── constants/
│   │   │   ├── documentTypes.js        # File types, sizes, formats
│   │   │   └── dummyRules.js           # Sample extracted rules (for development)
│   │   ├── App.jsx                     # Root component with Router + MUI theme
│   │   └── main.jsx                    # React entry point
│   ├── index.html                      # HTML entry
│   ├── vite.config.js                  # Vite configuration with API proxy
│   ├── package.json                    # Dependencies
│   ├── .env.example                    # Environment variable template
│   └── .gitignore
│
├── backend/                            # Python / FastAPI application
│   ├── app/
│   │   ├── main.py                     # FastAPI app setup with middleware & handlers
│   │   ├── config.py                   # Settings and configuration (pydantic)
│   │   ├── core/
│   │   │   ├── logger.py               # Structured logging utility
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
│   │   ├── providers/                  # Provider abstraction layer
│   │   │   ├── base.py                 # Abstract base classes (LLMProvider, EmbeddingProvider)
│   │   │   ├── schemas.py              # Standardized LLMRequest/Response, EmbeddingRequest/Response
│   │   │   ├── factory.py              # Provider factory (ProviderType enum + ProviderFactory)
│   │   │   ├── dummy_provider.py       # Mock LLM/embedding — returns JSON for extraction prompts
│   │   │   ├── README.md               # Detailed provider documentation
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
│   │   │   ├── events.py               # SSE event schema: ExtractionEvent, ExtractionEventType,
│   │   │   │                           #   ExtractionStage, ExtractionProgress, ExtractionEventData
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
│   ├── tests/                          # Backend tests (coming soon)
│   ├── main.py                         # Entry point for running server
│   ├── .env                            # Environment variables (production config)
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
- Displays `ExtractionProgress` component showing live pipeline milestones

**Step 2: Review & Confirm**
- Displays extracted rules in card-based UI
- Search by title/description
- Filter by severity (high/medium/low)
- Rule summary stats (total count, breakdown by severity)
- Inline editing: modify conditions and expected evidence
- Add/remove individual conditions and evidence items
- Delete rules with confirmation dialog
- "Upload New Document" button with confirmation (prevents accidental data loss)
- "Confirm Rules & Continue" button to move to step 3

**Step 3: Ready for Audit**
- Success confirmation screen
- Rules summary (count and status)
- Info about Phase 2
- "Back to Review" button (returns to step 2)
- "Proceed to Phase 2: Audit Document" button (TODO: navigate to Phase 2)

### ExtractionProgress Component
Real-time SSE progress display for the Phase 1 extraction pipeline — **integrated into Step 1 of Phase1.jsx**.

**Features**:
- Receives `events` prop — array of real-time `ExtractionEvent` objects from backend SSE stream
- Collapsible card with current stage name and overall progress bar
- Segment-level progress text (e.g., "Segment 3 of 7 • 12 rules found so far")
- Color-coded stages: parsing (blue) / segmentation (orange) / extraction (purple) / finalization (green)
- Animated spinning icon for the active stage, checkmark for completed stages
- **Expandable details panel** shows:
  - Key metrics grid (document size, sections found, rules found/unique)
  - Section titles identified (as chips)
  - Processing timeline showing all four stages with status badges
  - Full event log with timestamps
- Error state: red border, warning icon, error message
- **Production-ready**: Streams actual extraction events from backend

**Demo Route**: `http://localhost:5173/demo/extraction-progress`
- Run Success Scenario — realistic full pipeline simulation (~18 seconds)
- Run Error Scenario — failure handling demonstration
- Useful for testing UI without backend or reviewing component behavior

### Routing
React Router v6 with two routes:
- `/` → `Phase1` page (main application flow)
- `/demo/extraction-progress` → `ExtractionProgressDemo` page

### Component Architecture
- **DocumentUploadForm**: Reusable component accepting `phase` prop for multi-phase support
- **RuleCard**: Editable rule with expand/collapse for conditions and evidence
- **RulesList**: Stateful list with search, filter, and CRUD operations
- **ConfirmationDialog**: Reusable modal for destructive actions
- **ExtractionProgress**: Real-time SSE event display with collapsible details
- Material UI theme applied globally via `ThemeProvider`

### Services & Utilities
- **apiClient.js**: Axios instance with baseURL and error interceptor
- **documentService.js**: 
  - `extractRules()` — sync extraction endpoint (for future use)
  - `extractRulesStream()` — **SSE streaming endpoint** for real-time progress (currently in use by Phase1)
  - `auditDocument()` / `auditDocumentWithText()` — Phase 2 audit endpoints
- **fileValidator.js**: Validation for file type, size, and text length
- **documentTypes.js**: Constants for MIME types, extensions, limits
- **extractionSimulator.js**: Async generator functions for UI demo/testing without backend

### TypeScript Types
- **types/extraction.ts**: Full TypeScript interface definitions for the SSE event schema
  - `ExtractionEvent` — top-level event interface (matches Python `ExtractionEvent` Pydantic model)
  - `ExtractionEventType` — union of all 10 valid event type strings
  - `ExtractionStage` — pipeline stage union
  - `ExtractionProgress` — `current`, `total`, `percent`
  - `ExtractionEventData` — all contextual data fields

### Build & Run
```bash
cd frontend
npm install
npm run dev              # Runs on http://localhost:5173
npm run build           # Production build
```

Vite config includes proxy to `http://localhost:8000` for seamless API calls.

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
1. **Configuration** (`config.py`): Pydantic BaseSettings, LRU-cached singleton
2. **Logging** (`core/logger.py`): Structured logging, configurable level
3. **Exceptions** (`core/exceptions.py`): `InvalidInputException` (400), `FileParseFailed` (422), `ExtractionFailed` (500), `AuditFailed` (500)
4. **Validation** (`utils/validators.py`): `validate_file()`, `validate_text()`

**Build & Run**:
```bash
cd backend
pip install -r requirements.txt
python main.py                    # Runs on http://localhost:8000
```

Access Swagger at `http://localhost:8000/docs`

### Provider Abstraction Layer

**Pattern**: Abstract Factory with Python ABC (Abstract Base Classes)

**Core Architecture**:
1. **`app/providers/base.py`**: `LLMProvider` and `EmbeddingProvider` ABCs
2. **`app/providers/schemas.py`**: `LLMRequest`/`LLMResponse`, `EmbeddingRequest`/`EmbeddingResponse`
3. **`app/providers/factory.py`**: `ProviderFactory` with `ProviderType` enum (DUMMY, OPENAI, ANTHROPIC, GOOGLE, GROK)
4. **`app/providers/dummy_provider.py`**: `DummyLLMProvider` — detects extraction prompts and returns realistic JSON rule candidates; `DummyEmbeddingProvider` — returns fixed-dimension float vectors

**Pending**: Concrete implementations for OPENAI, ANTHROPIC, GOOGLE, GROK (only DUMMY is active; factory raises `ValueError` for others until implemented)

**Configuration**:
```env
LLM_PROVIDER=dummy        # dummy | openai | anthropic | google | grok
LLM_API_KEY=              # API key for chosen provider
LLM_MODEL=dummy-model     # Model identifier for chosen provider
EMBEDDING_PROVIDER=dummy
EMBEDDING_API_KEY=
EMBEDDING_MODEL=dummy-embedding
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
- **`parse_llm_response(content, segment_index)`**: Strips markdown fences, extracts JSON array, validates and constructs `RuleCandidate` objects
- **`deduplicate_rules(candidates)`**: Removes duplicates by normalized title

#### SSE Event Schema (`app/agents/events.py`)
Pydantic models that mirror the TypeScript types in `frontend/src/types/extraction.ts`:
- **`ExtractionEventType`** (str Enum): `parsing_started`, `parsing_complete`, `segmentation_started`, `segmentation_complete`, `extraction_started`, `extraction_progress`, `extraction_complete`, `finalization_started`, `finalization_complete`, `error`
- **`ExtractionStage`** (str Enum): `parsing`, `segmentation`, `extraction`, `finalization`
- **`ExtractionProgress`**: current, total, percent
- **`ExtractionEventData`**: char_count, page_count, section_count, section_titles, segment_index, segment_title, rules_in_segment, total_rules_so_far, total_rules, unique_rules, extracted_rules (only in `finalization_complete`)
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
- `orchestrate_extraction`: Dispatches `asyncio.gather` fan-out of worker tasks; emits `extraction_started`, one `extraction_progress` per segment (with `asyncio.Lock` for safe concurrent counter), `extraction_complete`
- `finalize_rules`: Deduplicates, assigns `rule_NNN` IDs; emits `finalization_started`, `finalization_complete` (with full `extracted_rules` list in event data)

**Event emission**: `_emit_event()` calls `asyncio.Queue.put_nowait()` — non-blocking, safe from both sync and async nodes

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
- **Provider-agnostic LLM integration** — abstract factory, config-driven, no vendor lock-in
- **Two endpoint modes**: `/extract-rules` (sync JSON) and `/extract-rules-stream` (SSE) — same pipeline, different execution paths (`run()` vs `stream()`)
- **Circular import prevention**: pipeline layer (`app/pipeline/`) never imports from API layer (`app/api/`); pipeline returns `list[dict]`, API layer owns Pydantic conversion
- `sse-starlette==1.6.5` pinned for compatibility with FastAPI 0.104.1 (starlette<0.28, anyio<4)

**Frontend**:
- **SSE Integration** (`documentService.extractRulesStream()`):
  - Uses native `fetch()` API with `ReadableStream` instead of `EventSource` (which only supports GET)
  - Handles streaming response by reading chunks, splitting on newlines, and parsing `data: ` lines as JSON events
  - Calls `onEvent` callback for each event, allowing real-time UI updates without accumulating in memory
  - Properly handles multi-line events and partial buffers during streaming
- `ExtractionProgress` component is driven entirely by an `events` prop — no internal fetching, making it reusable and fully testable with the simulator
- SSE event schema is defined in both Python (Pydantic) and TypeScript (interfaces) to keep the contract explicit and type-safe on both ends
- React Router added to support the demo route without affecting the main application flow
- Simulator (`extractionSimulator.js`) uses async generator pattern, mirroring the backend's `stream()` async generator — the frontend component works identically with simulated or real events
- Phase1 component manages extraction state (`extractionEvents`, `extractionError`) and automatically transitions to review step when `finalization_complete` event arrives with `extracted_rules`

## Standards & Conventions

**Backend**:
- SOLID principles throughout (Dependency Inversion, Open/Closed, Single Responsibility)
- Abstract Factory pattern for provider abstraction
- Structured logging with appropriate levels (DEBUG / INFO / WARNING / ERROR)
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

## Environment Variables

**Backend** (`backend/.env.example`):
- `APP_ENV` - Environment (development/production)
- `LOG_LEVEL` - Logging level (DEBUG/INFO/WARNING/ERROR)
- `LLM_PROVIDER` - LLM provider type (dummy, openai, anthropic, google, grok)
- `LLM_API_KEY` - API key for LLM provider
- `LLM_MODEL` - Model to use (provider-specific)
- `EMBEDDING_PROVIDER` - Embedding provider type
- `EMBEDDING_API_KEY` - API key for embedding provider
- `EMBEDDING_MODEL` - Embedding model to use
- File limits: `MAX_FILE_SIZE_MB`, `MAX_TEXT_LENGTH`, `MAX_RULES`
- CORS: `CORS_ORIGINS` (allowed origins)

**Frontend** (`frontend/.env.example`):
- `VITE_API_BASE_URL` - Backend API URL (default: http://localhost:8000)
- `VITE_APP_ENV` - Environment

## Next Steps

### Backend (Priority)
1. **Implement a concrete LLM provider** (OpenAI, Anthropic, Google, or Grok) to replace the dummy provider for production rule extraction — add provider file, register in factory, update `.env`
   - Currently: Phase 1 backend generates realistic dummy rules to test frontend integration
   - Once concrete provider is ready: will perform real LLM extraction on document segments
2. Set up vector database (Chroma / FAISS / Pinecone) for Phase 2
3. Implement Phase 2 RAG-based audit pipeline (`app/agents/`, `app/pipeline/`)
4. Implement Phase 2 SSE streaming endpoint for audit progress
5. Write test suite (`backend/tests/`)

### Frontend (Priority)
1. ✅ **COMPLETE**: Phase 1 SSE integration — Phase1.jsx now streams extraction progress in real-time
   - Upload document → SSE endpoint processes it → ExtractionProgress displays live events → Rules displayed in review step
2. Build Phase 2 frontend (Audit Document upload and results view)
3. Add user feedback via toast notifications (Snackbar) for non-critical events
4. Add error recovery UI (retry button when extraction fails)

### Integration & Testing
- End-to-end test: upload a real PDF, verify rules extracted and displayed correctly in real-time
- Test with concrete LLM provider once implemented (currently using dummy provider)
- Performance tuning (LLM concurrency, segment size optimization)
- Comprehensive test coverage (unit, integration, E2E)

## Future Improvements
- Persistent storage for extracted rules (session or DB)
- Human-in-the-loop review via LangGraph checkpointing
- Citations linking rules to specific evidence passages
- Full compliance dashboard with visual reporting
- Export rules and reports (PDF, CSV)
- Bulk rule management (import/export)
- Phase 2 SSE streaming for audit progress
