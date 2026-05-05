from pydantic import BaseModel, Field
from typing import List, Optional


class RuleCondition(BaseModel):
    """A condition within a rule"""
    text: str = Field(..., description="Condition text")


class RuleEvidence(BaseModel):
    """Expected evidence for a rule"""
    text: str = Field(..., description="Evidence description")


class Rule(BaseModel):
    """Structured rule object"""
    id: str = Field(..., description="Unique rule identifier")
    title: str = Field(..., description="Rule title")
    description: str = Field(..., description="Rule description")
    conditions: List[str] = Field(default_factory=list, description="List of conditions")
    expected_evidence: List[str] = Field(default_factory=list, description="List of expected evidence")
    section: Optional[str] = Field(default=None, description="Source section reference")
    severity: str = Field(default="medium", description="Rule severity (high/medium/low)")
    status: str = Field(default="extracted", description="Rule status")


class ExtractRulesResponse(BaseModel):
    """Response for /extract-rules endpoint"""
    document_id: str = Field(..., description="Unique document identifier")
    total_rules: int = Field(..., description="Total number of extracted rules")
    rules: List[Rule] = Field(default_factory=list, description="List of extracted rules")
    extraction_timestamp: str = Field(..., description="ISO 8601 timestamp of extraction")
    status: str = Field(default="success", description="Extraction status")


class AuditResultRule(BaseModel):
    """Individual rule audit result"""
    rule_id: str = Field(..., description="Rule identifier")
    rule_title: str = Field(..., description="Rule title")
    status: str = Field(..., description="Pass/Fail status")
    confidence: float = Field(default=0.0, description="Confidence score (0-1)")
    reasoning: str = Field(..., description="Explanation of the result")
    evidence: List[str] = Field(default_factory=list, description="Supporting evidence passages")


class AuditResponse(BaseModel):
    """Response for /audit endpoint"""
    document_id: str = Field(..., description="Unique document identifier")
    total_rules: int = Field(..., description="Total number of rules evaluated")
    passed_rules: int = Field(..., description="Number of rules that passed")
    failed_rules: int = Field(..., description="Number of rules that failed")
    compliance_score: float = Field(default=0.0, description="Overall compliance percentage")
    results: List[AuditResultRule] = Field(default_factory=list, description="Detailed audit results")
    audit_timestamp: str = Field(..., description="ISO 8601 timestamp of audit")
    status: str = Field(default="success", description="Audit status")


class ErrorResponse(BaseModel):
    """Standard error response"""
    status: str = Field(default="error", description="Status indicator")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Additional error details")
