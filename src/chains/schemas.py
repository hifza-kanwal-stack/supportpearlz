from typing import List, Literal
from pydantic import BaseModel, Field

class SupportResponseSchema(BaseModel):
    answer: str = Field(description="The grounded support answer.")
    sources: List[str] = Field(description="List of sources used.")
    confidence: Literal["high", "partial", "none"] = Field(description="Confidence level.")
    answered: bool = Field(description="True if answered, False if refused.")
