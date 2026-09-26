import pytest
from app.processing.cleaner import DataCleaner
from app.processing.validator import DataValidator
from app.processing.deduplicator import Deduplicator

def test_cleaner():
    raw_data = {
        "sku": "12345",
        "url": "https://www.bestbuy.com/site/laptop/12345.p?skuId=12345",
        "jsonld": {
            "name": "Test Laptop",
            "brand": {"name": "TestBrand"},
            "model": "TL-1",
            "offers": {
                "price": 999.99,
                "priceCurrency": "USD",
                "availability": "InStock"
            },
            "aggregateRating": {
                "ratingValue": 4.5,
                "reviewCount": 100
            }
        },
        "dom": {
            "specifications": {"RAM": "16GB"},
            "rating_distribution": {"5": 50, "4": 30, "3": 10, "2": 5, "1": 5}
        }
    }
    
    cleaned = DataCleaner.clean(raw_data, "Laptops")
    
    assert cleaned["product_id"] == "12345"
    assert cleaned["product_name"] == "Test Laptop"
    assert cleaned["brand"] == "TestBrand"
    assert cleaned["category"] == "Laptops"
    assert cleaned["product_url"] == "https://www.bestbuy.com/site/laptop/12345.p"
    assert cleaned["current_price"] == 999.99
    assert cleaned["availability_status"] == "in_stock"
    assert cleaned["rating"] == 4.5
    assert cleaned["review_count"] == 100
    assert cleaned["rating_distribution"]["5"] == 50
    assert cleaned["specifications"]["RAM"] == "16GB"

def test_validator():
    cleaned_data = {
        "product_id": "12345",
        "product_name": "Test Laptop",
        "brand": "TestBrand",
        "category": "Laptops",
        "product_url": "https://www.bestbuy.com/site/laptop/12345.p",
        "model_number": "TL-1",
        "description": "A test laptop",
        "primary_image_url": "http://example.com/img.png",
        "specifications": {"RAM": "16GB"},
        "current_price": 999.99,
        "currency": "USD",
        "availability_status": "in_stock",
        "rating": 4.5,
        "review_count": 100,
        "rating_distribution": {"5": 50, "4": 30, "3": 10, "2": 5, "1": 5},
        "seller_name": "Best Buy"
    }
    
    is_valid, prod, obs, err = DataValidator.validate(cleaned_data, "run_123")
    
    assert is_valid is True
    assert prod["product_id"] == "12345"
    assert obs["current_price"] == 999.99
    assert obs["run_id"] == "run_123"
    assert obs["extraction_status"] == "success"
    
def test_validator_failure():
    # Test with missing required field
    cleaned_data = {
        "product_id": None, # Missing!
        "product_name": "Test Laptop",
        "brand": "TestBrand",
        "category": "Laptops",
        "product_url": "https://www.bestbuy.com/site/laptop/12345.p"
    }
    
    is_valid, prod, obs, err = DataValidator.validate(cleaned_data, "run_123")
    assert is_valid is False
    assert "validation error" in err.lower() or "1 validation error" in err

def test_deduplicator():
    products = [
        {"product": {"product_id": "123"}},
        {"product": {"product_id": "123"}}, # duplicate
        {"product": {"product_id": "456"}}
    ]
    
    deduped = Deduplicator.deduplicate_run(products)
    
    assert len(deduped) == 2
    assert deduped[0]["product"]["product_id"] == "123"
    assert deduped[1]["product"]["product_id"] == "456"
