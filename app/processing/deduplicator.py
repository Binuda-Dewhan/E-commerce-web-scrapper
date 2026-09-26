from typing import Dict, Any, List

class Deduplicator:
    @staticmethod
    def deduplicate_run(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Removes duplicates within a single run based on product_id (SKU)."""
        seen = set()
        deduped = []
        for p in products:
            # p should be a dictionary containing 'product' and 'observation'
            pid = p.get("product", {}).get("product_id")
            if pid and pid not in seen:
                seen.add(pid)
                deduped.append(p)
        return deduped
