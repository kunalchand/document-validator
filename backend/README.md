# Document Validator Backend

## Setup

### Prerequisites
- Python 3.10+
- pip or poetry for dependency management

### Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

4. Add your OpenAI API key to `.env`:
```
OPENAI_API_KEY=your_actual_api_key_here
```

## Running the Server

Start the development server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, access the interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Project Structure

```
backend/
├── app/
│   ├── main.py                # FastAPI application setup
│   ├── config.py              # Settings and configuration
│   ├── core/                  # Core utilities
│   │   ├── logger.py          # Structured logging
│   │   └── exceptions.py      # Custom exceptions
│   ├── api/                   # REST API layer
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── rules.py   # /extract-rules endpoint
│   │       │   └── audit.py   # /audit endpoint
│   │       └── schemas.py     # Pydantic models
│   ├── utils/
│   │   └── validators.py      # Input validation
│   ├── agents/                # LangGraph agents (Phase 2)
│   ├── parsers/               # Document parsers (Phase 2)
│   └── pipeline/              # LangGraph pipelines (Phase 2)
├── tests/                     # Test suite
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
├── .gitignore                # Git ignore file
└── main.py                   # Entry point
```

## API Endpoints

### Health Checks
- `GET /` - Root endpoint
- `GET /health` - Health check

### Rules Extraction (Phase 1)
- `POST /api/v1/extract-rules` - Extract rules from document

### Audit (Phase 2)
- `POST /api/v1/audit` - Audit document against rules

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `APP_ENV` | Environment (development/production) | development |
| `LOG_LEVEL` | Logging level (DEBUG/INFO/WARNING/ERROR) | INFO |
| `MAX_FILE_SIZE_MB` | Max file upload size | 10 |
| `MAX_TEXT_LENGTH` | Max text input length | 50000 |
| `CORS_ORIGINS` | Allowed CORS origins | ["http://localhost:3000"] |

## Development

### Error Handling

All endpoints follow a consistent error response format:
```json
{
  "status": "error",
  "message": "Error message",
  "detail": "Additional details (if available)"
}
```

### Logging

Structured logging is configured throughout the application. All errors and important events are logged with appropriate log levels.

### Next Steps

1. Implement document parsers for PDF and DOCX files
2. Integrate LangGraph agents for rules extraction
3. Implement audit pipeline with RAG
4. Add persistent storage for rules
5. Add comprehensive test suite
