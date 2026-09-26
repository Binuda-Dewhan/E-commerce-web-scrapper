import pandas as pd
import json
from pathlib import Path
from typing import Dict, Any, List
from app.utils.timestamps import get_current_iso_timestamp

class ProductStore:
    def __init__(self, config: dict, logger):
        self.config = config
        self.logger = logger
        self.data_dir = Path(self.config.get("paths", {}).get("data_dir", "data")) / "observations"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.filepath = self.data_dir / "products.csv"
        
    def _load_existing(self) -> pd.DataFrame:
        if self.filepath.exists():
            return pd.read_csv(self.filepath, dtype={'product_id': str})
        return pd.DataFrame()
        
    def upsert_products(self, products: List[Dict[str, Any]]):
        """Creates or updates products in the master catalog."""
        if not products:
            return
            
        new_df = pd.DataFrame(products)
        # Ensure product_id is string
        new_df['product_id'] = new_df['product_id'].astype(str)
        
        # We need to flatten the specifications dict if present
        if 'specifications' in new_df.columns:
            new_df['specifications'] = new_df['specifications'].apply(
                lambda x: json.dumps(x) if isinstance(x, dict) else x
            )
            
        existing_df = self._load_existing()
        
        if existing_df.empty:
            self.logger.info(f"Creating new products catalog with {len(products)} items")
            new_df.to_csv(self.filepath, index=False)
            return
            
        self.logger.info(f"Updating products catalog. Current size: {len(existing_df)}")
        
        # For existing products, we update last_updated_at but keep first_seen_at
        now = get_current_iso_timestamp()
        
        # Convert existing to dictionary for faster/easier updating
        existing_records = existing_df.set_index('product_id').to_dict('index')
        
        for _, row in new_df.iterrows():
            pid = row['product_id']
            row_dict = row.to_dict()
            del row_dict['product_id']
            
            if pid in existing_records:
                # Update existing record
                existing_record = existing_records[pid]
                row_dict['first_seen_at'] = existing_record.get('first_seen_at', now)
                row_dict['last_updated_at'] = now
                existing_records[pid] = row_dict
            else:
                # Add new record
                row_dict['first_seen_at'] = row_dict.get('first_seen_at', now)
                row_dict['last_updated_at'] = row_dict.get('last_updated_at', now)
                existing_records[pid] = row_dict
                
        # Reconstruct DataFrame
        final_df = pd.DataFrame.from_dict(existing_records, orient='index').reset_index()
        final_df = final_df.rename(columns={'index': 'product_id'})
        
        # Ensure product_id is first column
        cols = ['product_id'] + [c for c in final_df.columns if c != 'product_id']
        final_df = final_df[cols]
        
        final_df.to_csv(self.filepath, index=False)
        self.logger.info(f"Catalog updated. New size: {len(final_df)}")
