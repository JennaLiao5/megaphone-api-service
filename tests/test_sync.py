import pytest
from unittest.mock import patch
from app.cruds.sync import sync_campaign, sync_advertiser
from app.cruds.sync import parse_datetime_safe
from datetime import datetime

# Test parse_datetime_safe edge cases
def test_parse_datetime_safe_valid():
    dt = parse_datetime_safe("2024-04-22T09:00:00Z")
    assert isinstance(dt, datetime)
    assert dt.year == 2024

def test_parse_datetime_safe_none():
    assert parse_datetime_safe(None) is None

def test_parse_datetime_safe_invalid():
    assert parse_datetime_safe("not-a-date") is None

# Test sync_advertiser creates and updates
@patch("app.cruds.sync.sync_agency", return_value=None)
def test_sync_advertiser_create(mock_agency, db_session):
    data = {"id": "m-adv-3", "name": "Sync Adv", "createdAt": "2024-01-01T00:00:00Z"}
    adv = sync_advertiser(db_session, data)
    assert adv.megaphone_id == "m-adv-3"
    assert adv.name == "Sync Adv"
    assert adv.created_at.year == 2024

@patch("app.cruds.sync.sync_agency", return_value=None)
def test_sync_advertiser_update(mock_agency, db_session):
    # Create first
    data = {"id": "m-adv-4", "name": "Sync Adv4", "createdAt": "2024-01-01T00:00:00Z"}
    adv = sync_advertiser(db_session, data)
    # Update
    data2 = {"id": "m-adv-4", "name": "Updated Name", "updatedAt": "2024-02-01T00:00:00Z"}
    adv2 = sync_advertiser(db_session, data2)
    assert adv2.megaphone_id == "m-adv-4"
    assert adv2.name == "Updated Name"
    assert adv2.updated_at.year == 2024

# Test sync_campaign creates and updates
@patch("app.cruds.sync.sync_advertiser", return_value=None)
def test_sync_campaign_create(mock_sync_adv, db_session):
    data = {
        "title": "Sync Camp",
        "advertiserId": "adv-2",
        "totalBudgetCents": 0,
        "totalBudgetCurrency": "USD",
        "id": "m-camp-1",
        "externalId": None,
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-01T00:00:00Z",
        "organizationId": "org-1",
        "totalRevenueCents": 0,
        "totalRevenueCurrency": "USD",
        "durationInSeconds": 0,
        "copyNeeded": True,
        "advertiser": {
            "id": "adv-2",
            "name": "Sync Adv",
            "agency": None
        },
        "bookingSource": None
    }
    camp = sync_campaign(db_session, data)
    assert camp.megaphone_id == "m-camp-1"
    assert camp.title == "Sync Camp"
    assert camp.created_at.year == 2024

@patch("app.cruds.sync.sync_advertiser", return_value=None)
def test_sync_campaign_update(mock_sync_adv, db_session):
    data = {
        "title": "Sync Camp",
        "advertiserId": "adv-2",
        "totalBudgetCents": 0,
        "totalBudgetCurrency": "USD",
        "id": "m-camp-1",
        "externalId": None,
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-01T00:00:00Z",
        "organizationId": "org-1",
        "totalRevenueCents": 0,
        "totalRevenueCurrency": "USD",
        "durationInSeconds": 0,
        "copyNeeded": True,
        "advertiser": {
            "id": "adv-2",
            "name": "Sync Adv",
            "agency": None
        },
        "bookingSource": None
    }
    camp = sync_campaign(db_session, data)
    data2 = {
        "title": "Updated Title",
        "advertiserId": "adv-2",
        "totalBudgetCents": 0,
        "totalBudgetCurrency": "USD",
        "id": "m-camp-2",
        "externalId": None,
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2025-01-01T00:00:00Z",
        "organizationId": "org-1",
        "totalRevenueCents": 0,
        "totalRevenueCurrency": "USD",
        "durationInSeconds": 0,
        "copyNeeded": True,
        "advertiser": {
            "id": "adv-2",
            "name": "Sync Adv",
            "agency": None
        },
        "bookingSource": None
    }
    camp2 = sync_campaign(db_session, data2)
    assert camp2.megaphone_id == "m-camp-2"
    assert camp2.title == "Updated Title"
    assert camp2.updated_at.year == 2025
