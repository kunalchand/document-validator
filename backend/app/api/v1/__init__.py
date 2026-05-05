from fastapi import APIRouter
from app.api.v1.endpoints import rules, audit

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(rules.router)
api_router.include_router(audit.router)

__all__ = ["api_router"]
