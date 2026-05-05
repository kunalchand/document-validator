# Document Validator — Project Reference

## Overview
A document compliance verification system. Takes a rules document and a user document, extracts structured rules from the former, and evaluates the latter against those rules — producing a structured compliance report with pass/fail status and supporting evidence per rule.

## Tech Stack
| Layer      | Technology                           |
|------------|--------------------------------------|
| Frontend   | React.js 18 + Vite + Material UI 5   |
| Backend    | Python (FastAPI)                     |
| Pipeline   | LangGraph                            |
| LLM        | OpenAI (via LangChain)               |
| Vector DB  | TBD (Chroma / FAISS / Pinecone)      |

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
│   │   │   └── ConfirmationDialog.jsx  # Reusable confirmation modal
│   │   ├── pages/
│   │   │   └── Phase1.jsx              # Three-step flow: Upload → Review → Ready
│   │   ├── services/
│   │   │   ├── apiClient.js            # Axios client with interceptors
│   │   │   └── documentService.js      # API methods (extract-rules, audit)
│   │   ├── utils/
│   │   │   └── fileValidator.js        # File and text validation helpers
│   │   ├── constants/
│   │   │   ├── documentTypes.js        # File types, sizes, formats
│   │   │   └── dummyRules.js           # Sample extracted rules (for development)
│   │   ├── App.jsx                     # Root component with Material UI theme
│   │   └── main.jsx                    # React entry point
│   ├── index.html                      # HTML entry
│   ├── vite.config.js                  # Vite configuration with API proxy
│   ├── package.json                    # Dependencies
│   ├── .env.example                    # Environment variable template
│   └── .gitignore
│
├── backend/                            # Python / FastAPI application
│   ├── app/
│   │   ├── api/                        # Route handlers (FastAPI routers)
│   │   ├── agents/                     # LangGraph agents and nodes
│   │   ├── parsers/                    # Input parsers (PDF, DOCX, text)
│   │   ├── pipeline/                   # LangGraph graph definitions
│   │   ├── utils/                      # Shared utilities
│   │   └── constants/                  # App-wide constants
│   ├── tests/                          # Backend tests
│   ├── .env.example                    # Environment variable template
│   └── requirements.txt                # Python dependencies
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
- Currently uses dummy data (ready for API integration)

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

### Component Architecture
- **DocumentUploadForm**: Reusable component accepting `phase` prop for multi-phase support
- **RuleCard**: Editable rule with expand/collapse for conditions and evidence
- **RulesList**: Stateful list with search, filter, and CRUD operations
- **ConfirmationDialog**: Reusable modal for destructive actions (can be used anywhere)
- Material UI theme applied globally (customizable primary/secondary colors)

### Services & Utilities
- **apiClient.js**: Axios instance with baseURL and error interceptor
- **documentService.js**: Methods for `/extract-rules` and `/audit` endpoints (ready to connect to backend)
- **fileValidator.js**: Validation for file type, size, and text length
- **documentTypes.js**: Constants for MIME types, extensions, limits

### Development Data
- **dummyRules.js**: 5 sample rules (Employee Background Check, Data Confidentiality, etc.) with realistic structure
- Allows full testing of UI without backend; easily replaced with API calls

### Build & Run
```bash
cd frontend
npm install
npm run dev              # Runs on http://localhost:3000
npm run build           # Production build
```

Vite config includes proxy to `http://localhost:8000` for seamless API calls.

## Key Design Decisions
- Rules extraction is a deterministic structuring problem — no vector DB in Phase 1
- Vector DB is used only for the user document in Phase 2
- Map-reduce (fan-out / fan-in) pattern for both rule extraction and rule evaluation
- Stateless between API calls — rules are passed explicitly by the client
- No LangGraph interrupts or checkpointing in v1 (kept simple intentionally)
- All three input types (PDF, DOCX, raw text) are normalized to plain text before pipeline entry
- Frontend components are phase-agnostic where possible (DocumentUploadForm, ConfirmationDialog)
- Material UI used for consistent, professional styling and accessibility
- Dummy data approach allows full frontend development without backend dependency

## Standards & Conventions
- SOLID principles throughout frontend and backend
- Structured logging with appropriate log levels (DEBUG / INFO / WARNING / ERROR)
- Consistent HTTP error responses: `{ status, message, detail }`
- All secrets and config via environment variables — never hardcoded
- Constants file for all magic values (model names, chunk sizes, endpoint paths, etc.)
- `.env` files excluded from version control; `.env.example` documents required variables
- No directional icons (arrows) on buttons — text labels speak for themselves
- Confirmation dialogs for destructive actions (data loss, deletion)

## Environment Variables
See `frontend/.env.example` and `backend/.env.example` for required variables.

## Next Steps
- Build Phase 2 frontend (Audit Document upload and results view)
- Implement backend API for `/extract-rules` endpoint (Phase 1)
- Implement backend API for `/audit` endpoint (Phase 2)
- Connect frontend services to live backend
- Add user feedback via toast notifications (Snackbar)

## Future Improvements
- Persistent storage for extracted rules
- Human-in-the-loop review via LangGraph checkpointing
- Citations linking rules to specific evidence passages
- Real-time progress updates (WebSocket or SSE)
- Full compliance dashboard with visual reporting
- Export rules and reports (PDF, CSV)
- Bulk rule management (import/export)
