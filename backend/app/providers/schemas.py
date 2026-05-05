from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List


class LLMRequest(BaseModel):
    """Standardized request model for LLM operations"""
    prompt: str = Field(..., description="The prompt to send to the LLM")
    model: Optional[str] = Field(None, description="Specific model to use")
    temperature: float = Field(default=0.7, description="Temperature for response diversity (0-1)")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens in response")
    system_prompt: Optional[str] = Field(None, description="System message/context")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class LLMResponse(BaseModel):
    """Standardized response model from LLM"""
    content: str = Field(..., description="The response content from the LLM")
    model: str = Field(..., description="Model that generated the response")
    provider: str = Field(..., description="Provider name (openai, anthropic, google, etc.)")
    tokens_used: Optional[int] = Field(None, description="Tokens consumed by the request")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class EmbeddingRequest(BaseModel):
    """Standardized request model for embedding operations"""
    text: str = Field(..., description="Text to embed")
    model: Optional[str] = Field(None, description="Specific embedding model to use")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class EmbeddingResponse(BaseModel):
    """Standardized response model from embedding provider"""
    embedding: List[float] = Field(..., description="Vector embedding of the text")
    model: str = Field(..., description="Model that generated the embedding")
    provider: str = Field(..., description="Provider name")
    text_length: int = Field(..., description="Number of tokens/characters in input")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
