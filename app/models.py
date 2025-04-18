import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Agency(Base):
    __tablename__ = "agencies"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    megaphone_id = Column(String, unique=True, nullable=True)
    name = Column(String, nullable=False)

    def __repr__(self):
        return f"<Agency(id={self.id}, name={self.name})>"

class Advertiser(Base):
    __tablename__ = "advertisers"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    megaphone_id = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    agency_id = Column(String(36), ForeignKey("agencies.id"), nullable=True)
    agency = relationship("Agency", backref="advertisers")
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    competitive_categories = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Advertiser(id={self.id}, name={self.name})>"

class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    megaphone_id = Column(String, unique=True, nullable=False)
    external_id = Column(String, nullable=True)
    title = Column(String, nullable=False)
    advertiser_id = Column(String(36), ForeignKey("advertisers.id"))
    advertiser = relationship("Advertiser", backref="campaigns")
    organization_id = Column(String, nullable=False)
    total_budget_cents = Column(Integer, nullable=True)
    total_budget_currency = Column(String, nullable=True)
    total_revenue_cents = Column(Integer, nullable=True)
    total_revenue_currency = Column(String, nullable=True)
    duration_in_seconds = Column(Integer, nullable=True)
    copy_needed = Column(Boolean, default=False)
    booking_source = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    synced_at = Column(DateTime, default=datetime.utcnow)
    archived = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Campaign(id={self.id}, title={self.title})>"