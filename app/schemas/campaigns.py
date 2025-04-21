from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime
from app.validators import campaigns as v

class Agency(BaseModel):
    id: str
    megaphone_id: str
    name: str

class Advertiser(BaseModel):
    id: str
    megaphone_id: str
    name: str
    agency: Optional[Agency] = None

class CampaignCreate(BaseModel):
    title: str = Field(..., description="Title of the campaign")
    advertiser_id: str = Field(..., description="Advertiser UUID")
    total_budget_cents: Optional[int] = Field(None, description="Total budget in cents")
    total_budget_currency: Optional[str] = Field(None, description="Currency code (e.g. USD)")
    
    @field_validator("total_budget_cents", mode="before")
    @classmethod
    def validate_budget(cls, val):
        return v.validate_budget_cents(val, field_name="total_budget_cents")

    @field_validator("total_budget_currency", mode="before")
    @classmethod
    def validate_currency(cls, val):
        return v.validate_currency_code(val, field_name="total_budget_currency")

class CampaignUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Title of the campaign")
    advertiser_id: Optional[str] = Field(None, description="Advertiser UUID")
    total_budget_cents: Optional[int] = Field(None, description="Total budget in cents")
    total_budget_currency: Optional[str] = Field(None, description="Currency code (e.g. USD)")

    @model_validator(mode="after")
    def check_at_least_one_field(self):
        if not any([
            self.title,
            self.advertiser_id,
            self.total_budget_cents,
            self.total_budget_currency
        ]):
            raise ValueError("At least one field must be provided.")
        return self
    
    @field_validator("total_budget_cents", mode="before")
    @classmethod
    def validate_budget(cls, val):
        return v.validate_budget_cents(val, field_name="total_budget_cents")

    @field_validator("total_budget_currency", mode="before")
    @classmethod
    def validate_currency(cls, val):
        return v.validate_currency_code(val, field_name="total_budget_currency")


class CampaignLocalOut(BaseModel):
    id: str
    megaphone_id: str
    external_id: Optional[str] = None
    title: str
    organization_id: str
    advertiser: Optional[Advertiser] = None
    total_budget_cents: Optional[int]
    total_budget_currency: Optional[str]
    total_revenue_cents: Optional[int]
    total_revenue_currency: Optional[str]
    duration_in_seconds: Optional[int]
    copy_needed: Optional[bool]
    booking_source: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    synced_at: Optional[datetime]
    archived: Optional[bool]

    class Config:
        from_attributes = True