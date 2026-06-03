from pydantic import BaseModel
from typing import Optional


class RiskRequest(BaseModel):
    ticker: str
    user_query: Optional[str] = None


class TraceStep(BaseModel):
    step_number: int
    thought: str
    tool_name: str
    tool_input: dict
    tool_output_summary: str
    timestamp: str


class RiskResponse(BaseModel):
    ticker: str
    risk_score: Optional[int]
    risk_label: str
    explanation: str
    tools_called: list[str]
    trace: list[TraceStep]