from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db import get_db
from app import models
from app.schemas.campaigns import CampaignLocalOut, CampaignCreate, CampaignUpdate, Advertiser as AdvertiserSchema
from app.schemas.pagination import PaginatedResponse, SortByField, SortOrder
from app.cruds import campaigns as crud

router = APIRouter(tags=["Local - Campaigns & Advertiser"])

@router.get("/advertisers", response_model=List[AdvertiserSchema])
def list_advertisers(db: Session = Depends(get_db)):
    return crud.get_advertisers(db)

@router.get("/campaigns", response_model=PaginatedResponse[CampaignLocalOut])
def list_local_campaigns(
    db: Session = Depends(get_db),
    search: Optional[str] = Query(None, description="Search by title"),
    advertiser_id: Optional[str] = Query(None, description="Filter by advertiser ID (exact match)"),
    sort_by: SortByField = Query("created_at", description="Field to sort by"),
    sort_order: SortOrder = Query("desc", description="Sort order: 'asc' or 'desc'"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page")
):
    return crud.list_campaigns(db, search, advertiser_id, sort_by, sort_order, page, per_page)

@router.post("/campaigns", response_model=CampaignLocalOut, status_code=status.HTTP_201_CREATED)
def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    return crud.create_campaign(db, campaign)

@router.get("/campaigns/{campaign_id}", response_model=CampaignLocalOut)
def get_campaign(campaign_id: str, db: Session = Depends(get_db)):
    return crud.get_campaign_by_id(db, campaign_id)

@router.put("/campaigns/{campaign_id}", response_model=CampaignLocalOut)
def update_campaign(campaign_id: str, campaign: CampaignUpdate, db: Session = Depends(get_db)):
    return crud.update_campaign(db, campaign_id, campaign)
