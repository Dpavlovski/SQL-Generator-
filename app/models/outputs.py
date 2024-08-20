from dataclasses import dataclass
from typing import List, Optional

from pydantic import BaseModel


class ValidationOutput(BaseModel):
    reason: str
    verdict: str
    missing_tables: Optional[List[str]] = None


@dataclass(frozen=True)
class SearchOutput(BaseModel):
    table_name: str
    score: float
    column_name: Optional[str] = None
    value: Optional[str] = None


class SqlGenerationOutput(BaseModel):
    reason: str
    query: str
