# backend/app/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class STTResult(BaseModel):
    text: str
    confidence: float = Field(ge=0.0, le=1.0)

class PronunciationDetails(BaseModel):
    segments: Optional[List[Dict[str, Any]]] = []

class PronResult(BaseModel):
    overall: float = Field(ge=0, le=100)
    fluency: float = Field(ge=0, le=100)
    details: Optional[PronunciationDetails] = None

class EvaluationScores(BaseModel):
    fluency: float = Field(ge=0, le=4)
    pronunciation: float = Field(ge=0, le=4)
    content: float = Field(ge=0, le=4)
    grammar: float = Field(ge=0, le=4)
    total: float = Field(ge=0, le=4)

class EvalResult(BaseModel):
    scores: EvaluationScores
    feedback: str
    tips: List[str]

class SpeechAnalyzeResponse(BaseModel):
    task_id: int
    stt: STTResult
    pronunciation: PronResult
    evaluation: EvalResult

class ErrorResponse(BaseModel):
    detail: str
