from typing import Dict, Any, Tuple
from app.models.product import Product
from app.models.observation import Observation
from app.utils.timestamps import get_current_iso_timestamp

class DataValidator:
    @staticmethod
    def validate(cleaned_data: Dict[str, Any], run_id: str) -> Tuple[bool, Dict[str, Any], Dict[str, Any], str]:
        """
        Validates cleaned data against Pydantic models.
        Returns (is_valid, product_dict, observation_dict, error_message)
        """
        now = get_current_iso_timestamp()
        
        product_data = {
            "product_id": cleaned_data.get("product_id"),
            "product_name": cleaned_data.get("product_name"),
            "brand": cleaned_data.get("brand"),
            "category": cleaned_data.get("category"),
            "product_url": cleaned_data.get("product_url"),
            "model_number": cleaned_data.get("model_number"),
            "description": cleaned_data.get("description"),
            "primary_image_url": cleaned_data.get("primary_image_url"),
            "specifications": cleaned_data.get("specifications"),
            "first_seen_at": now,
            "last_updated_at": now
        }
        
        observation_id = f"{cleaned_data.get('product_id')}_{now.replace(':', '').replace('-', '').replace('Z', '')}"
        
        observation_data = {
            "observation_id": observation_id,
            "product_id": cleaned_data.get("product_id"),
            "run_id": run_id,
            "scraped_at": now,
            "current_price": cleaned_data.get("current_price"),
            "original_price": cleaned_data.get("original_price"),
            "currency": cleaned_data.get("currency", "USD"),
            "availability_status": cleaned_data.get("availability_status", "unknown"),
            "rating": cleaned_data.get("rating"),
            "review_count": cleaned_data.get("review_count"),
            "rating_distribution": cleaned_data.get("rating_distribution"),
            "seller_name": cleaned_data.get("seller_name"),
            "extraction_status": "success" if cleaned_data.get("current_price") else "partial"
        }
        
        try:
            # Pydantic validation
            prod = Product(**product_data)
            obs = Observation(**observation_data)
            return True, prod.model_dump(), obs.model_dump(), ""
        except Exception as e:
            observation_data["extraction_status"] = "failed"
            return False, product_data, observation_data, str(e)
