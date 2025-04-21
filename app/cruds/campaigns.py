from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, asc
from fastapi import HTTPException
import requests

from app import models, megaphone_client
from app.schemas.campaigns import CampaignLocalOut, CampaignCreate, CampaignUpdate
from app.schemas.pagination import PaginatedResponse, PaginationMeta
from app.cruds.sync import sync_campaign


def get_advertisers(db: Session):
    return db.query(models.Advertiser).options(joinedload(models.Advertiser.agency)).all()


def list_campaigns(db: Session, search, advertiser_id, sort_by, sort_order, page, per_page):
    query = db.query(models.Campaign).options(
        joinedload(models.Campaign.advertiser).joinedload(models.Advertiser.agency)
    )

    if search:
        query = query.filter(models.Campaign.title.ilike(f"%{search}%"))

    if advertiser_id:
        query = query.filter(models.Campaign.advertiser_id == advertiser_id)

    sort_column = getattr(models.Campaign, sort_by)
    query = query.order_by(desc(sort_column) if sort_order == "desc" else asc(sort_column))

    total = query.count()
    db_items = query.offset((page - 1) * per_page).limit(per_page).all()
    items = [CampaignLocalOut.model_validate(obj, from_attributes=True) for obj in db_items]

    return PaginatedResponse[CampaignLocalOut](
        items=items,
        meta=PaginationMeta(page=page, per_page=per_page, total=total)
    )


def create_campaign(db: Session, campaign: CampaignCreate):
    advertiser = db.query(models.Advertiser).filter_by(id=campaign.advertiser_id).first()
    if not advertiser:
        raise HTTPException(status_code=400, detail="Advertiser not found")
    try:
        campaign_data = campaign.model_dump(exclude_none=True)
        campaign_data["advertiserId"] = advertiser.megaphone_id

        remote = megaphone_client.create_campaign(campaign_data)

        local = sync_campaign(db, remote)
        db.commit()

        return CampaignLocalOut.model_validate(local, from_attributes=True)

    except requests.exceptions.HTTPError as e:
        db.rollback()
        try:
            error_detail = e.response.json()
        except Exception:
            error_detail = e.response.text
        raise HTTPException(
            status_code=e.response.status_code,
            detail={"error": "Remote API failed", "reason": error_detail}
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


def get_campaign_by_id(db: Session, campaign_id: str):
    campaign = db.query(models.Campaign).options(
        joinedload(models.Campaign.advertiser).joinedload(models.Advertiser.agency)
    ).filter(models.Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return CampaignLocalOut.model_validate(campaign, from_attributes=True)


def update_campaign(db: Session, campaign_id: str, campaign: CampaignUpdate):
    local_campaign = db.query(models.Campaign).filter_by(id=campaign_id).first()
    if not local_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    advertiser_megaphone_id = None
    if campaign.advertiser_id:
        advertiser = db.query(models.Advertiser).filter_by(id=campaign.advertiser_id).first()
        if not advertiser:
            raise HTTPException(status_code=400, detail="Advertiser not found")
        advertiser_megaphone_id = advertiser.megaphone_id

    try:
        update_data = campaign.model_dump(exclude_none=True)
        if advertiser_megaphone_id:
            update_data["advertiserId"] = advertiser_megaphone_id

        remote = megaphone_client.update_campaign(local_campaign.megaphone_id, update_data)

        local = sync_campaign(db, remote)
        db.commit()
        return CampaignLocalOut.model_validate(local, from_attributes=True)

    except requests.exceptions.HTTPError as e:
        db.rollback()
        try:
            error_detail = e.response.json()
        except Exception:
            error_detail = e.response.text
        raise HTTPException(
            status_code=e.response.status_code,
            detail={"error": "Remote API failed", "reason": error_detail}
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

