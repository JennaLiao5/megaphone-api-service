from sqlalchemy.orm import Session
from app.models import Campaign, Advertiser, Agency
from datetime import datetime
import logging
from app.megaphone_client import list_campaigns, list_advertisers

logger = logging.getLogger(__name__)

def parse_datetime_safe(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None

def sync_agency(db: Session, agency_data: dict) -> Agency:
    try:
        if not agency_data:
            return None
        agency = db.query(Agency).filter_by(megaphone_id=agency_data["id"]).one_or_none()
        if agency:
            agency.name = agency_data["name"]
        else:
            agency = Agency(
                megaphone_id=agency_data["id"],
                name=agency_data["name"]
            )
            db.add(agency)
            db.flush()
        return agency
    except Exception as e:
        logger.warning(f"[SYNC ERROR] agency_id={agency_data.get('id')}, title={agency_data.get('title')}")
        logger.warning(f"Data: {agency_data}")
        logger.exception(e)
        return None

def sync_advertiser(db: Session, advertiser_data: dict) -> Advertiser:
    try:
        if not advertiser_data:
            return None
        advertiser = db.query(Advertiser).filter_by(megaphone_id=advertiser_data["id"]).one_or_none()
        agency = sync_agency(db, advertiser_data.get("agency"))

        if advertiser:
            advertiser.name = advertiser_data["name"]
            advertiser.agency = agency
            advertiser.updated_at = parse_datetime_safe(advertiser_data.get("updatedAt"))
            advertiser.competitive_categories = advertiser_data.get("competitiveCategories")
        else:
            advertiser = Advertiser(
                megaphone_id=advertiser_data["id"],
                name=advertiser_data["name"],
                agency=agency,
                created_at=parse_datetime_safe(advertiser_data.get("createdAt")),
                updated_at=parse_datetime_safe(advertiser_data.get("updatedAt")),
                competitive_categories=advertiser_data.get("competitiveCategories")
            )
            db.add(advertiser)
            db.flush()
        return advertiser
    except Exception as e:
        logger.warning(f"[SYNC ERROR] advertiser_id={advertiser_data.get('id')}, title={advertiser_data.get('title')}")
        logger.warning(f"Data: {advertiser_data}")
        logger.exception(e)
        return None

def sync_campaign(db: Session, campaign_data: dict) -> Campaign:
    try:
        advertiser_data = campaign_data.get("advertiser") or {}
        advertiser = sync_advertiser(db, advertiser_data)

        created_at = parse_datetime_safe(campaign_data.get("createdAt"))
        updated_at = parse_datetime_safe(campaign_data.get("updatedAt"))

        campaign = db.query(Campaign).filter_by(megaphone_id=campaign_data["id"]).first()

        if not campaign:
            campaign = Campaign(
                megaphone_id=campaign_data["id"],
                external_id=campaign_data.get("externalId"),
                title=campaign_data["title"],
                advertiser=advertiser,
                organization_id=campaign_data["organizationId"],
                total_budget_cents=campaign_data.get("totalBudgetCents"),
                total_budget_currency=campaign_data.get("totalBudgetCurrency"),
                total_revenue_cents=campaign_data.get("totalRevenueCents"),
                total_revenue_currency=campaign_data.get("totalRevenueCurrency"),
                duration_in_seconds=campaign_data.get("durationInSeconds"),
                copy_needed=campaign_data.get("copyNeeded", False),
                booking_source=campaign_data.get("bookingSource"),
                created_at=created_at,
                updated_at=updated_at,
                synced_at=datetime.utcnow()
            )
            db.add(campaign)
        else:
            campaign.external_id = campaign_data.get("externalId")
            campaign.title = campaign_data["title"]
            campaign.advertiser = advertiser
            campaign.total_budget_cents = campaign_data.get("totalBudgetCents")
            campaign.total_budget_currency = campaign_data.get("totalBudgetCurrency")
            campaign.total_revenue_cents = campaign_data.get("totalRevenueCents")
            campaign.total_revenue_currency = campaign_data.get("totalRevenueCurrency")
            campaign.duration_in_seconds = campaign_data.get("durationInSeconds")
            campaign.copy_needed = campaign_data.get("copyNeeded", False)
            campaign.booking_source = campaign_data.get("bookingSource")
            campaign.updated_at = updated_at
            campaign.synced_at = datetime.utcnow()

        db.flush()
        return campaign

    except Exception as e:
        logger.warning(f"[SYNC ERROR] campaign_id={campaign_data.get('id')}, title={campaign_data.get('title')}")
        logger.warning(f"Data: {campaign_data}")
        logger.exception(e)
        return None

def sync_all_advertisers(db: Session):
    remote_advertisers = list_advertisers()
    remote_ids = set(c["id"] for c in remote_advertisers)
    upserted = 0
    failed = 0
    deleted = 0
    for a in remote_advertisers:
        result = sync_advertiser(db, a)
        if result:
            upserted += 1
        else:
            failed += 1
    local_advertisers = db.query(Advertiser).all()
    for advertiser in local_advertisers:
        if advertiser.megaphone_id not in remote_ids:
            db.delete(advertiser)
            deleted += 1
            logger.info(f"[SYNC] Advertiser deleted - ID: {advertiser.id}, Megaphone ID: {advertiser.megaphone_id}, Name: {advertiser.name}")
    db.commit()
    return {"upserted": upserted, "failed": failed, "deleted": deleted}

def sync_all_campaigns(db: Session):
    remote_campaigns = list_campaigns()
    remote_ids = set(c["id"] for c in remote_campaigns)
    upserted = 0
    failed = 0
    deleted = 0
    for c in remote_campaigns:
        result = sync_campaign(db, c)
        if result:
            upserted += 1
        else:
            failed += 1
    local_campaigns = db.query(Campaign).all()
    for campaign in local_campaigns:
        if campaign.megaphone_id not in remote_ids:
            db.delete(campaign)
            deleted += 1
            logger.info(f"[SYNC] Campaign deleted - ID: {campaign.id}, Megaphone ID: {campaign.megaphone_id}, Title: {campaign.title}")
    db.commit()
    return {"upserted": upserted, "failed": failed, "deleted": deleted}
