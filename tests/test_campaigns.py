import pytest
from fastapi.testclient import TestClient
from app.models import Advertiser

# Helper to create an advertiser
@pytest.fixture
def advertiser(db_session):
    adv = db_session.query(Advertiser).filter_by(megaphone_id="9a22ee30-1a9f-11f0-b531-1b59096fa63d").first()
    if not adv:
        adv = Advertiser(
            id="adv-2",
            megaphone_id="9a22ee30-1a9f-11f0-b531-1b59096fa63d",
            name="Jenna Test Advertiser 1"
        )
        db_session.add(adv)
        db_session.commit()
    return adv

# Test campaign creation
def test_create_campaign(client, db_session, advertiser):
    data = {
        "title": "Jenna's Test Campaign (unit test)",
        "advertiser_id": advertiser.id,
        "total_budget_cents": 10,
        "total_budget_currency": "USD"
    }
    resp = client.post("/campaigns", json=data)
    assert resp.status_code == 201
    result = resp.json()
    assert result["title"] == "Jenna's Test Campaign (unit test)"
    assert result["advertiser"]["id"] == advertiser.id
    assert result["total_budget_cents"] == 10
    assert result["total_budget_currency"] == "USD"

# Test invalid budget
def test_budget_validator(client, db_session, advertiser):
    data = {
        "title": "Jenna's Test Campaign (unit test - Invalid Budget Campaign)",
        "advertiser_id": advertiser.id,
        "total_budget_cents": -10,
        "total_budget_currency": "USD"
    }
    resp = client.post("/campaigns", json=data)
    assert resp.status_code == 400
    assert "positive integer" in resp.text

# Test invalid currency
def test_currency_validator(client, db_session, advertiser):
    data = {
        "title": "Jenna's Test Campaign (unit test - Invalid Currency Campaign)",
        "advertiser_id": advertiser.id,
        "total_budget_cents": 100,
        "total_budget_currency": "US"
    }
    response = client.post("/campaigns", json=data)
    assert response.status_code == 400
    assert "valid 3-letter uppercase code" in response.text

# Test campaign listing, search, pagination, and sorting
@pytest.mark.parametrize("search,expected_count", [("Jenna's Test Campaign (unit test)", 1), ("Nonexistent", 0)])
def test_list_campaigns(client, advertiser, search, expected_count):
    params = {"search": search, "page": 1, "per_page": 10}
    resp = client.get("/campaigns", params=params)
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) == expected_count

# Test campaign update
def test_update_campaign(client, db_session, advertiser):
    # Create campaign
    resp = client.post("/campaigns", json={
        "title": "Jenna's Test Campaign (Unit Test - To Update)",
        "advertiser_id": advertiser.id,
        "total_budget_cents": 0,
        "total_budget_currency": "USD"
    })
    cid = resp.json()["id"]
    # Update
    update = {
        "title": "Jenna's Test Campaign Updated Title",
        "total_budget_cents": 10,
        "total_budget_currency": "JPY"
    }
    resp2 = client.put(f"/campaigns/{cid}", json=update)
    assert resp2.status_code == 200
    assert resp2.json()["title"] == "Jenna's Test Campaign Updated Title"
    assert resp2.json()["total_budget_cents"] == 10
    assert resp2.json()["total_budget_currency"] == "JPY"

# Test archiving and unarchiving
def test_archive_unarchive_campaign(client, db_session, advertiser):
    resp = client.post("/campaigns", json={
        "title": "Jenna's Test Campaign (Unit Test - To Archive)",
        "advertiser_id": advertiser.id,
        "total_budget_cents": 0,
        "total_budget_currency": "USD"
    })
    cid = resp.json()["id"]
    # Archive
    resp2 = client.put(f"/campaigns/{cid}/archive", json={"archived": True})
    assert resp2.status_code == 200
    assert resp2.json()["archived"] is True
    # Unarchive
    resp3 = client.put(f"/campaigns/{cid}/archive", json={"archived": False})
    assert resp3.status_code == 200
    assert resp3.json()["archived"] is False

# Test filtering by archived status
def test_filter_archived(client, db_session, advertiser):
    # Create archived campaign
    resp = client.post("/campaigns", json={
        "title": "Jenna's Test Campaign (Unit Test - Archived)",
        "advertiser_id": advertiser.id,
        "total_budget_cents": 0,
        "total_budget_currency": "USD"
    })
    cid = resp.json()["id"]
    client.put(f"/campaigns/{cid}/archive", json={"archived": True})
    # List archived only
    resp2 = client.get("/campaigns", params={"archived": True})
    assert resp2.status_code == 200
    items = resp2.json()["items"]
    assert all(c["archived"] is True for c in items)
    # List unarchived only
    resp3 = client.get("/campaigns", params={"archived": False})
    assert resp3.status_code == 200
    items = resp3.json()["items"]
    assert all(c["archived"] is False for c in items)
