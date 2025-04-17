from pydantic import BaseModel, Field, validator, model_validator
from typing import Optional
from datetime import datetime
import re


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

    @validator("totalBudgetCents", pre=True)
    def validate_total_budget_cents(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            if not v.strip().isdigit():
                raise ValueError("Total budget cents must be a valid integer")
            return int(v.strip())
        if not isinstance(v, int):
            raise ValueError("Total budget cents must be a valid integer")
        return v
    
    @validator("totalBudgetCurrency", pre=True)
    def validate_currency(cls, v):
        if v is None:
            return v
        if isinstance(v, str) and not v.strip():
            raise ValueError("Total budget currency must not be empty")
        if not re.fullmatch(r"^[A-Z]{3}$", v.strip()):
            raise ValueError("Total budget currency must be a valid 3-letter uppercase code (e.g. USD)")
        return v.strip()
 
class CampaignCreate(CampaignBase):
    pass

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
