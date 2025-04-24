from pydantic import BaseModel

class SyncResponse(BaseModel):
    status: str  # "success", "partial_failure", "complete_failure"
    message: str
    total: int
    upserted: int
    failed: int
    deleted: int