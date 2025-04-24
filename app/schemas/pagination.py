from pydantic import BaseModel, ConfigDict
from typing import Generic, TypeVar, List, Literal

T = TypeVar("T")

class PaginationMeta(BaseModel):
    page: int
    per_page: int
    total: int

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    meta: PaginationMeta

    model_config = ConfigDict(from_attributes=True)


# Sorting Field Restrictions (Based on the Campaign Field)
SortByField = Literal[
    "title",
    "created_at",
    "updated_at",
    "organization_id",
    "total_budget_cents",
    "total_budget_currency",
    "total_revenue_cents",
    "total_revenue_currency",
    "duration_in_seconds",
    "copy_needed",
    "booking_source",
    "synced_at",
    "archived"
]

SortOrder = Literal["asc", "desc"]