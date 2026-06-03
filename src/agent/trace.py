from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import json


@dataclass
class AgentStep:
    step_number: int
    thought: str
    tool_name: str
    tool_input: dict
    tool_output_summary: str
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))


class AgentTrace:
    def __init__(self, ticker: str = "", query: str = ""):
        self.ticker = ticker
        self.query = query
        self.steps: list[AgentStep] = []
        self.final_answer: str = ""
        self.risk_score: Optional[int] = None
        self.started_at: str = datetime.now().isoformat()
        self.completed_at: Optional[str] = None

    def add_step(self, thought: str, tool_name: str, tool_input: dict, tool_output_summary: str):
        step = AgentStep(
            step_number=len(self.steps) + 1,
            thought=thought,
            tool_name=tool_name,
            tool_input=tool_input,
            tool_output_summary=tool_output_summary,
        )
        self.steps.append(step)

    def complete(self, final_answer: str, risk_score: Optional[int] = None):
        self.final_answer = final_answer
        self.risk_score = risk_score
        self.completed_at = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "ticker": self.ticker,
            "query": self.query,
            "risk_score": self.risk_score,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "total_steps": len(self.steps),
            "tools_called": [s.tool_name for s in self.steps],
            "final_answer": self.final_answer,
        }

    def save(self, path="evaluation_log.jsonl"):
        with open(path, "a") as f:
            f.write(json.dumps(self.to_dict()) + "\n")