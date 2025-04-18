from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.db import get_db
from app.cruds.sync import sync_campaign, sync_advertiser
from app import megaphone_client
from app.schemas.sync_response import SyncResponse

router = APIRouter(tags=["Sync"])

def generate_sync_response(resource: str, success: int, failed: int):
    total = success + failed
    if failed == 0:
        status = "success"
        message = f"{resource} sync completed successfully"
    elif success == 0:
        status = "complete_failure"
        message = f"{resource} sync failed completely"
    else:
        status = "partial_failure"
        message = f"{resource} sync completed with some failures"

    return {
        "status": status,
        "message": message,
        "total": total,
        "success": success,
        "failed": failed
    }

@router.post("/campaigns/sync", response_model=SyncResponse)
def sync_campaigns(db: Session = Depends(get_db)):
    campaigns = megaphone_client.list_campaigns()
    success = 0
    failed = 0
    for c in campaigns:
        result = sync_campaign(db, c)
        if result:
            success += 1
        else:
            failed += 1

    db.commit()
    return generate_sync_response("Campaigns", success, failed)


@router.post("/advertisers/sync", response_model=SyncResponse)
def sync_advertisers(db: Session = Depends(get_db)):
    advertisers = megaphone_client.list_advertisers()
    success = 0
    failed = 0
    for adv in advertisers:
        result = sync_advertiser(db, adv)
        if result:
            success += 1
        else:
            failed += 1
    db.commit()
    return generate_sync_response("Advertisers", success, failed)
