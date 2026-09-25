import json
import re
from typing import Optional, Dict, Any

class JsonLdExtractor:
    @staticmethod
    def extract(page_content: str) -> Optional[Dict[str, Any]]:
        """Parses the JSON-LD from page content and returns the Product object if found."""
        # Look for <script type="application/ld+json"> ... </script>
        pattern = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.DOTALL | re.IGNORECASE)
        matches = pattern.findall(page_content)
        
        for match in matches:
            try:
                data = json.loads(match)
                # JSON-LD can be a list or a dict
                if isinstance(data, dict):
                    if data.get("@type") == "Product":
                        return data
                    elif "@graph" in data:
                        for item in data["@graph"]:
                            if item.get("@type") == "Product":
                                return item
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and item.get("@type") == "Product":
                            return item
            except json.JSONDecodeError:
                continue
                
        return None
