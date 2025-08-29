from pydantic import BaseModel, Field
from typing import Any, Dict, Optional

class ToolCall(BaseModel):
    tool: str = Field(..., description="Registered tool name, e.g., 'web.search'")
    input: Dict[str, Any] = Field(default_factory=dict)

class Observation(BaseModel):
    tool: str
    output: Any
    error: Optional[str] = None
