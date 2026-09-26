import json
from pathlib import Path
from typing import Dict, Any, Optional
from app.utils.timestamps import get_current_iso_timestamp

class RunManager:
    def __init__(self, config: dict, logger, run_id: str):
        self.config = config
        self.logger = logger
        self.run_id = run_id
        self.data_dir = Path(self.config.get("paths", {}).get("data_dir", "data")) / "raw" / run_id
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.filepath = self.data_dir / "run_metadata.json"
        
    def create_run(self, category: str, search_term: str = None) -> Dict[str, Any]:
        """Initializes a new run."""
        metadata = {
            "run_id": self.run_id,
            "started_at": get_current_iso_timestamp(),
            "completed_at": None,
            "category": category,
            "search_term": search_term,
            "products_discovered": 0,
            "products_extracted": 0,
            "products_failed": 0,
            "status": "in_progress"
        }
        self._save(metadata)
        return metadata
        
    def update_stats(self, discovered: int = 0, extracted: int = 0, failed: int = 0):
        metadata = self.load_run()
        if metadata:
            metadata["products_discovered"] += discovered
            metadata["products_extracted"] += extracted
            metadata["products_failed"] += failed
            self._save(metadata)
            
    def complete_run(self, status: str = "success"):
        metadata = self.load_run()
        if metadata:
            metadata["completed_at"] = get_current_iso_timestamp()
            metadata["status"] = status
            self._save(metadata)
            
    def load_run(self) -> Optional[Dict[str, Any]]:
        if self.filepath.exists():
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
        
    def _save(self, metadata: dict):
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
