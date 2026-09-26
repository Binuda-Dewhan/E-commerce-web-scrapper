import pytest
import pandas as pd
from app.analysis.price_intelligence import PriceIntelligence
from app.analysis.category_comparison import CategoryComparison

def test_price_intelligence():
    products = pd.DataFrame([
        {"product_id": "111", "product_name": "Laptop A", "category": "Laptops"},
        {"product_id": "222", "product_name": "Laptop B", "category": "Laptops"}
    ])
    
    observations = pd.DataFrame([
        # Product 111 History
        {"observation_id": "o1", "product_id": "111", "scraped_at": "2026-09-01T00:00:00Z", "current_price": 1000.0, "original_price": 1200.0, "rating": 4.5},
        {"observation_id": "o2", "product_id": "111", "scraped_at": "2026-09-08T00:00:00Z", "current_price": 950.0, "original_price": 1200.0, "rating": 4.6},
        
        # Product 222 History
        {"observation_id": "o3", "product_id": "222", "scraped_at": "2026-09-08T00:00:00Z", "current_price": 500.0, "original_price": 500.0, "rating": 4.0}
    ])
    
    analysis = PriceIntelligence.analyze(products, observations)
    
    assert len(analysis) == 2
    
    prod111 = analysis[analysis['product_id'] == "111"].iloc[0]
    assert prod111['latest_price'] == 950.0
    assert prod111['first_observed_price'] == 1000.0
    assert prod111['lowest_observed_price'] == 950.0
    assert prod111['highest_observed_price'] == 1000.0
    assert prod111['price_change'] == -50.0
    assert prod111['discount_amount'] == 250.0
    assert prod111['observation_count'] == 2
    assert prod111['latest_rating'] == 4.6
    
    prod222 = analysis[analysis['product_id'] == "222"].iloc[0]
    assert pd.isna(prod222['price_change'])
    assert prod222['discount_amount'] == 0.0

def test_category_comparison():
    analysis = pd.DataFrame([
        {"product_id": "111", "latest_price": 950.0, "category": "Laptops", "latest_rating": 4.6},
        {"product_id": "222", "latest_price": 500.0, "category": "Laptops", "latest_rating": 4.0},
        {"product_id": "333", "latest_price": 300.0, "category": "Tablets", "latest_rating": 4.5}
    ])
    
    comp = CategoryComparison.compare(analysis)
    
    laptop_111 = comp[comp['product_id'] == "111"].iloc[0]
    laptop_222 = comp[comp['product_id'] == "222"].iloc[0]
    tablet_333 = comp[comp['product_id'] == "333"].iloc[0]
    
    # Laptop average = (950+500)/2 = 725
    assert laptop_111['category_average_price'] == 725.0
    assert laptop_111['price_vs_category_avg'] == 225.0 # 950 - 725
    assert laptop_111['price_rank_in_category'] == 2.0
    
    assert laptop_222['price_rank_in_category'] == 1.0 # 500 < 950
    
    assert tablet_333['category_average_price'] == 300.0
    assert tablet_333['price_rank_in_category'] == 1.0
