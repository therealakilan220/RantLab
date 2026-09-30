"""Data shapes. Must match docs/api-contract.md and frontend/lib/types.ts."""
from typing import Literal

from pydantic import BaseModel, Field

Cost = Literal["free", "cheap", "budget"]
Timeframe = Literal["today", "this_week", "this_semester"]


class Fix(BaseModel):
    title: str
    detail: str
    owner: str
    cost: Cost
    timeframe: Timeframe


class LLMOutput(BaseModel):
    problem: str
    pattern: str
    affected: str
    fixes: list[Fix] = Field(min_length=3, max_length=3)


class Card(LLMOutput):
    id: str
    created_at: str
    input_type: Literal["voice", "text"]
    transcript: str
    cluster_id: str | None = None
