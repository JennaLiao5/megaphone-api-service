from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.cruds.sync import sync_all_campaigns, sync_all_advertisers
from app.schemas.sync_response import SyncResponse

router = APIRouter(prefix="/sync", tags=["Sync"])

def generate_sync_response(resource: str, upserted: int, failed: int, deleted: int):
    total = upserted + failed + deleted
    if failed == 0:
        status = "success"
        message = f"{resource} sync completed successfully"
    elif total != 0 and total == failed:
        status = "complete_failure"
        message = f"{resource} sync failed completely"
    else:
        status = "partial_failure"
        message = f"{resource} sync completed with some failures"

    return {
        "status": status,
        "message": message,
        "total": total,
        "upserted": upserted,
        "failed": failed,
        "deleted": deleted
    }

@router.post("/advertisers", response_model=SyncResponse)
def sync_advertisers(db: Session = Depends(get_db)):
    res = sync_all_advertisers(db)
    return generate_sync_response("Advertisers", res.get("upserted"), res.get("failed"), res.get("deleted"))

@router.post("/campaigns", response_model=SyncResponse)
def sync_campaigns(db: Session = Depends(get_db)):
    res = sync_all_campaigns(db)
    return generate_sync_response("Campaigns", res.get("upserted"), res.get("failed"), res.get("deleted"))

