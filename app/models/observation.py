from pydantic import BaseModel, Field
from typing import Optional

class RatingDistribution(BaseModel):
    five: Optional[int] = Field(None, alias="5")
    four: Optional[int] = Field(None, alias="4")
    three: Optional[int] = Field(None, alias="3")
    two: Optional[int] = Field(None, alias="2")
    one: Optional[int] = Field(None, alias="1")

class Observation(BaseModel):
    observation_id: str
    product_id: str
    run_id: str
    scraped_at: str
    current_price: Optional[float]
    original_price: Optional[float] = None
    currency: str = "USD"
    availability_status: str
    rating: Optional[float] = None
    review_count: Optional[int] = None
    rating_distribution: Optional[RatingDistribution] = None
    seller_name: Optional[str] = None
    extraction_status: str
