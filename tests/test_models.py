import pytest
from app.models import Campaign, Advertiser
from app.schemas.campaigns import CampaignUpdate
from pydantic import ValidationError
import uuid

def test_campaign_model_fields():
    adv_id = str(uuid.uuid4())
    camp = Campaign(
        id=str(uuid.uuid4()),
        megaphone_id="m-camp-xyz",
        title="Model Test",
        advertiser_id=adv_id,
        organization_id="org-xyz",
        total_budget_cents=5000,
        total_budget_currency="USD",
        archived=False
    )
    assert camp.title == "Model Test"
    assert camp.total_budget_cents == 5000
    assert camp.archived is False

def test_advertiser_model_repr():
    adv = Advertiser(id="aid", megaphone_id="mid", name="AdvName")
    assert "AdvName" in repr(adv)

def test_campaign_update_validator():
    # At least one updatable field required
    with pytest.raises(ValidationError):
        CampaignUpdate()
    # Valid update
    upd = CampaignUpdate(title="New Title")
    assert upd.title == "New Title"
