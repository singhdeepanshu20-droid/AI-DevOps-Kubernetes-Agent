from typing import Any, Dict, Optional, Union
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str


class InvestigationRequest(BaseModel):
    cluster_context: Optional[str] = None
    namespace: Optional[str] = None


class DiagnosisSchema(BaseModel):
    root_cause: str
    explanation: str
    fix: str
    kubectl_command: str
    prevention: Optional[str] = None
    confidence: int


class InvestigationResponse(BaseModel):
    status: str
    investigation: Dict[str, Any]
    message: Optional[str] = None
    diagnosis: Optional[Union[DiagnosisSchema, Dict[str, Any], str]] = None
