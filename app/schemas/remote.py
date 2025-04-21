from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime
from app.validators import campaigns as v


class Agency(BaseModel):
    id: str
    name: str

class AdvertiserBase(BaseModel):
    id: str
    name: str
    agency: Optional[Agency] = None

class AdvertiserOut(AdvertiserBase):
    createdAt: datetime
    updatedAt: datetime
    competitiveCategories: Optional[str]

class CampaignBase(BaseModel):
    title: str = Field(..., description="Title of the campaign (required)")
    advertiserId: str = Field(..., description="Advertiser UUID (required)")
    totalBudgetCents: Optional[int] = Field(None, description="Total budget in cents (optional)")
    totalBudgetCurrency: Optional[str] = Field(None, description="Currency code, e.g. USD (optional)")

 
class CampaignCreate(CampaignBase):
    @field_validator("totalBudgetCents", mode="before")
    @classmethod
    def validate_budget(cls, val):
        return v.validate_budget_cents(val, field_name="totalBudgetCents")

    @field_validator("totalBudgetCurrency", mode="before")
    @classmethod
    def validate_currency(cls, val):
        return v.validate_currency_code(val, field_name="totalBudgetCurrency")

class CampaignUpdate(CampaignBase):
    title: Optional[str] = Field(None, description="Title of the campaign")
    advertiserId: Optional[str] = Field(None, description="Advertiser UUID")
    totalBudgetCents: Optional[int] = Field(None, description="Total budget in cents")
    totalBudgetCurrency: Optional[str] = Field(None, description="Currency code, e.g. USD")

    @model_validator(mode="after")
    def check_at_least_one_field(self):
        if not any([
            self.title,
            self.advertiserId,
            self.totalBudgetCents,
            self.totalBudgetCurrency
        ]):
            raise ValueError(
                "At least one of 'title', 'advertiserId', 'totalBudgetCents', or 'totalBudgetCurrency' must be provided"
            )
        return self
    
    @field_validator("totalBudgetCents", mode="before")
    @classmethod
    def validate_budget(cls, val):
        return v.validate_budget_cents(val, field_name="totalBudgetCents")

    @field_validator("totalBudgetCurrency", mode="before")
    @classmethod
    def validate_currency(cls, val):
        return v.validate_currency_code(val, field_name="totalBudgetCurrency")
    
class CampaignOut(CampaignBase):
    id: str
    externalId: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime
    organizationId: str
    totalRevenueCents: int
    totalRevenueCurrency: str
    durationInSeconds: int
    copyNeeded: bool
    advertiser: Optional[AdvertiserBase]
    bookingSource: Optional[str] = None
