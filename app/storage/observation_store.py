import pandas as pd
import json
from pathlib import Path
from typing import Dict, Any, List

class ObservationStore:
    def __init__(self, config: dict, logger):
        self.config = config
        self.logger = logger
        self.data_dir = Path(self.config.get("paths", {}).get("data_dir", "data")) / "observations"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.filepath = self.data_dir / "observations.csv"
        
    def append_observations(self, observations: List[Dict[str, Any]]):
        """Appends new observations to the historical dataset."""
        if not observations:
            return
            
        df = pd.DataFrame(observations)
        
        # Flatten rating_distribution dict
        if 'rating_distribution' in df.columns:
            df['rating_distribution'] = df['rating_distribution'].apply(
                lambda x: json.dumps(x) if isinstance(x, dict) else x
            )
            
        # Append mode
        file_exists = self.filepath.exists()
        df.to_csv(self.filepath, mode='a', header=not file_exists, index=False)
        
        self.logger.info(f"Appended {len(observations)} observations to historical store")
