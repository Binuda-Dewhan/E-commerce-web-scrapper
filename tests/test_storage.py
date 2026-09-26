import pytest
import os
import pandas as pd
from pathlib import Path
import logging
from app.storage.product_store import ProductStore
from app.storage.observation_store import ObservationStore
from app.storage.checkpoint import RunManager

# Setup dummy logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test")

@pytest.fixture
def temp_config(tmp_path):
    return {
        "paths": {
            "data_dir": str(tmp_path / "data")
        }
    }

def test_product_store_upsert(temp_config):
    store = ProductStore(temp_config, logger)
    
    products_run1 = [
        {
            "product_id": "111",
            "product_name": "Laptop A",
            "category": "Laptops",
            "first_seen_at": "2026-09-01T00:00:00Z",
            "last_updated_at": "2026-09-01T00:00:00Z"
        }
    ]
    
    # First run
    store.upsert_products(products_run1)
    
    df1 = pd.read_csv(store.filepath, dtype={'product_id': str})
    assert len(df1) == 1
    assert df1.iloc[0]['product_name'] == "Laptop A"
    
    # Second run: updating 111, adding 222
    products_run2 = [
        {
            "product_id": "111",
            "product_name": "Laptop A (Updated)",
            "category": "Laptops",
        },
        {
            "product_id": "222",
            "product_name": "Laptop B",
            "category": "Laptops"
        }
    ]
    
    store.upsert_products(products_run2)
    
    df2 = pd.read_csv(store.filepath, dtype={'product_id': str})
    assert len(df2) == 2
    
    # Check that 111 was updated
    prod111 = df2[df2['product_id'] == "111"].iloc[0]
    assert prod111['product_name'] == "Laptop A (Updated)"
    assert prod111['first_seen_at'] == "2026-09-01T00:00:00Z" # Preserved
    assert prod111['last_updated_at'] > "2026-09-01T00:00:00Z" # Updated to now
    
def test_observation_store_append(temp_config):
    store = ObservationStore(temp_config, logger)
    
    obs1 = [
        {
            "observation_id": "obs1",
            "product_id": "111",
            "current_price": 999.0
        }
    ]
    
    obs2 = [
        {
            "observation_id": "obs2",
            "product_id": "111",
            "current_price": 949.0
        }
    ]
    
    store.append_observations(obs1)
    store.append_observations(obs2)
    
    df = pd.read_csv(store.filepath, dtype={'product_id': str})
    assert len(df) == 2
    assert df.iloc[0]['observation_id'] == "obs1"
    assert df.iloc[1]['observation_id'] == "obs2"

def test_run_manager(temp_config):
    manager = RunManager(temp_config, logger, "test_run")
    
    meta = manager.create_run(category="Test Category")
    assert meta["status"] == "in_progress"
    
    manager.update_stats(discovered=5, extracted=4, failed=1)
    
    updated = manager.load_run()
    assert updated["products_discovered"] == 5
    assert updated["products_extracted"] == 4
    
    manager.complete_run(status="success")
    final = manager.load_run()
    assert final["status"] == "success"
    assert final["completed_at"] is not None
