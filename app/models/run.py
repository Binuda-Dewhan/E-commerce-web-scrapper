from pydantic import BaseModel
from typing import Optional

class RunMetadata(BaseModel):
    run_id: str
    started_at: str
    completed_at: Optional[str] = None
    category: str
    search_term: Optional[str] = None
    products_discovered: int = 0
    products_extracted: int = 0
    products_failed: int = 0
    status: str = "in_progress"
