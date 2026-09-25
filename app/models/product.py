from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict

class Product(BaseModel):
    product_id: str
    product_name: str
    brand: str
    category: str
    product_url: HttpUrl | str
    model_number: Optional[str] = None
    description: Optional[str] = None
    primary_image_url: Optional[HttpUrl | str] = None
    specifications: Optional[Dict[str, str]] = None
    first_seen_at: str
    last_updated_at: str
