import json
import re
from pathlib import Path
from playwright.async_api import Page
from app.scraper.extractors.jsonld_extractor import JsonLdExtractor
from app.scraper.extractors.dom_extractor import DomExtractor
from app.utils.timestamps import get_current_iso_timestamp

class ProductExtractor:
    def __init__(self, page: Page, config: dict, logger):
        self.page = page
        self.config = config
        self.logger = logger
        
    async def extract_product(self, url: str, run_id: str) -> dict:
        """Navigates to product page and extracts all possible data."""
        self.logger.info(f"Extracting product from {url}")
        
        # Navigate
        await self.page.goto(url, timeout=60000, wait_until="domcontentloaded")
        
        # We need a safe filename, grab the sku from URL
        sku_match = re.search(r'skuId=(\d+)', url)
        sku = sku_match.group(1) if sku_match else "unknown_sku"
        
        # Take a screenshot
        screenshots_dir = Path(self.config.get("paths", {}).get("data_dir", "data")) / "raw" / run_id / "screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        await self.page.screenshot(path=str(screenshots_dir / f"{sku}.png"), full_page=False)
        
        # Get page content for JSON-LD parsing
        content = await self.page.content()
        
        # 1. Parse JSON-LD
        jsonld_data = JsonLdExtractor.extract(content)
        
        # 2. Extract DOM data
        dom_data = await DomExtractor.extract(self.page)
        
        # Combine
        raw_data = {
            "url": url,
            "scraped_at": get_current_iso_timestamp(),
            "sku": sku,
            "jsonld": jsonld_data,
            "dom": dom_data
        }
        
        # Save raw JSON
        raw_dir = Path(self.config.get("paths", {}).get("data_dir", "data")) / "raw" / run_id
        raw_dir.mkdir(parents=True, exist_ok=True)
        
        with open(raw_dir / f"product_{sku}.json", 'w', encoding='utf-8') as f:
            json.dump(raw_data, f, indent=2)
            
        self.logger.info(f"Extracted and saved product {sku}")
        
        return raw_data
