import pytest
from fastapi.testclient import TestClient
from app.models import Advertiser

# Test fetching advertisers
def test_list_advertisers(client, db_session):
    adv = Advertiser(id="adv-1", megaphone_id="m-adv-1", name="Adv1")
    db_session.add(adv)
    db_session.commit()
    resp = client.get("/advertisers")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert any(a["id"] == "adv-1" for a in data)

# Test advertiser required for campaign creation
def test_create_campaign_without_advertiser(client):
    data = {
        "title": "No Adv",
        "advertiser_id": "nonexistent",
        "organization_id": "org-x"
    }
    resp = client.post("/campaigns", json=data)
    assert resp.status_code == 400
    assert "Advertiser not found" in resp.text
