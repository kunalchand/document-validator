from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import traceback

from app.config import get_settings, Settings
from app.core import get_logger
from app.core.exceptions import DocumentValidatorException
from app.api.v1 import api_router

logger = get_logger(__name__)

app = FastAPI(
    title="Document Validator",
    description="Document compliance verification system with AI-powered rules extraction and auditing",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(DocumentValidatorException)
async def document_validator_exception_handler(request: Request, exc: DocumentValidatorException):
    logger.error(f"Document Validator Exception: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.message,
            "detail": None
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected exception: {str(exc)}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "An unexpected error occurred",
            "detail": str(exc) if settings.app_env == "development" else None
        }
    )


# Include API routes
app.include_router(api_router)


@app.get("/", tags=["health"])
async def root():
    """Root endpoint for health check"""
    return {
        "status": "ok",
        "message": f"Welcome to {settings.app_name}",
        "version": "0.1.0"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.app_env
    }


if __name__ == "__main__":
    import uvicorn
    _settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=_settings.app_env == "development",
        log_level=_settings.log_level.lower()
    )
