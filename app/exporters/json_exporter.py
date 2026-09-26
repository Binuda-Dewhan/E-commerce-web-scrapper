import json
import pandas as pd
from pathlib import Path
import math

class JsonExporter:
    def __init__(self, config: dict, logger):
        self.logger = logger
        self.final_dir = Path(config.get("paths", {}).get("data_dir", "data")) / "final"
        self.final_dir.mkdir(parents=True, exist_ok=True)
        
    def export(self, final_df: pd.DataFrame, filename: str = "full_report.json"):
        """Exports the fully analyzed dataset to JSON format."""
        if final_df.empty:
            self.logger.warning("Export DataFrame is empty. Skipping JSON export.")
            return
            
        filepath = self.final_dir / filename
        
        clean_df = final_df.copy()
        
        # Convert to records
        records = clean_df.to_dict('records')
        
        # Clean NaN/floats to make it valid JSON
        def clean_record(d):
            new_d = {}
            for k, v in d.items():
                if isinstance(v, float) and math.isnan(v):
                    new_d[k] = None
                else:
                    new_d[k] = v
            return new_d
            
        records = [clean_record(r) for r in records]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=2)
            
        self.logger.info(f"Exported JSON report to {filepath}")
