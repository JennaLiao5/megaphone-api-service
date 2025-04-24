from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import List
import requests
from app import megaphone_client
from app.schemas import remote as schemas


router = APIRouter(prefix="/remote", tags=["Remote - Campaigns & Advertisers"])

@router.get("/advertisers", response_model=List[schemas.AdvertiserOut])
def fetch_remote_advertisers():
    try:
        advertisers = megaphone_client.list_advertisers()
        return advertisers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/campaigns", response_model=List[schemas.CampaignOut])
def fetch_remote_campaigns():
    try:
        campaigns = megaphone_client.list_campaigns()
        return campaigns
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post(
    "/campaigns",
    response_model=schemas.CampaignOut,
    responses={
        400: {"description": "Bad Request - Invalid input."},
    },
)
def create_remote_campaign(campaign: schemas.CampaignCreate):
    try:
        result = megaphone_client.create_campaign(campaign.dict(exclude_none=True))
        return result
    except requests.exceptions.HTTPError as e:
        # If Megaphone returns a body
        try:
            error_detail = e.response.json()
        except Exception:
            error_detail = e.response.text  # Fallback
        return JSONResponse(status_code=e.response.status_code, content={"detail": error_detail})
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/campaigns/{campaign_id}", response_model=schemas.CampaignOut)
def fetch_single_remote_campaign(campaign_id: str):
    try:
        result = megaphone_client.get_campaign(campaign_id)
        return result
    except requests.exceptions.HTTPError as e:
        try:
            return JSONResponse(status_code=e.response.status_code, content={"detail": e.response.json()})
        except Exception:
            return JSONResponse(status_code=e.response.status_code, content={"detail": e.response.text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put(
    "/campaigns/{campaign_id}",
    response_model=schemas.CampaignOut,
    responses={
        400: {"description": "Bad Request - Invalid input."},
    },
)
def update_remote_campaign(campaign_id: str, campaign: schemas.CampaignUpdate):
    try:
        result = megaphone_client.update_campaign(campaign_id, campaign.dict(exclude_none=True))
        return result
    except requests.exceptions.HTTPError as e:
        try:
            return JSONResponse(status_code=e.response.status_code, content={"detail": e.response.json()})
        except Exception:
            return JSONResponse(status_code=e.response.status_code, content={"detail": e.response.text})
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
   