from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl

class CandidateGiveaway(BaseModel):
    title: str
    sponsor: str
    prize_description: str = "Premio descrito en las reglas oficiales"
    prize_value_usd: Optional[float] = None
    entry_url: HttpUrl
    official_rules_url: HttpUrl
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    eligible_regions: list[str] = Field(default_factory=list)
    minimum_age: Optional[int] = None
    entry_method: Optional[str] = None

    requires_purchase: bool = False
    entry_fee_usd: float = 0
    requires_financial_info: bool = False
    requires_ssn: bool = False
    requires_government_id_at_entry: bool = False
    requires_third_party_registration: bool = False
    requires_offer_completion: bool = False
    requires_app_install: bool = False
    requires_newsletter: bool = False
    requires_account_creation: bool = False
    required_fields: list[str] = Field(default_factory=list)

    sponsor_domain_verified: bool = False
    rules_verified: bool = False
    cross_source_verified: bool = False

class DeviceRegistration(BaseModel):
    token: str
    platform: str = "ios"
