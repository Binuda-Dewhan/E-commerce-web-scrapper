import pandas as pd
from pathlib import Path

class CsvExporter:
    def __init__(self, config: dict, logger):
        self.logger = logger
        self.final_dir = Path(config.get("paths", {}).get("data_dir", "data")) / "final"
        self.final_dir.mkdir(parents=True, exist_ok=True)
        
    def export(self, final_df: pd.DataFrame, filename: str = "full_report.csv"):
        """Exports the fully analyzed dataset to CSV."""
        if final_df.empty:
            self.logger.warning("Export DataFrame is empty. Skipping CSV export.")
            return
            
        filepath = self.final_dir / filename
        final_df.to_csv(filepath, index=False)
        self.logger.info(f"Exported CSV report to {filepath} with {len(final_df)} products")
