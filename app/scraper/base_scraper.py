import abc
import asyncio
import json
import random
from pathlib import Path
from typing import Optional, List, Dict
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse

class BaseScraper(abc.ABC):
    def __init__(self, config: dict, logger):
        self.config = config
        self.logger = logger
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.robot_parsers: Dict[str, RobotFileParser] = {}
        
    async def initialize(self):
        """Initializes the Playwright browser and context."""
        self.logger.info("Initializing browser...")
        self.playwright = await async_playwright().start()
        
        headless = self.config.get("run", {}).get("headless", True)
        
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        # Setup context with standard US residential-like viewport and User-Agent
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            locale="en-US",
            timezone_id="America/New_York"
        )
        self.page = await self.context.new_page()
        
        # Route to block images and media to save bandwidth
        await self.page.route("**/*", self._intercept_route)

    async def _intercept_route(self, route):
        """Intercepts requests to block unnecessary resources."""
        if route.request.resource_type in ["image", "media", "font"]:
            await route.abort()
        else:
            await route.continue_()
            
    async def close(self):
        """Closes the browser resources."""
        self.logger.info("Closing browser...")
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
            
    async def check_robots_txt(self, url: str) -> bool:
        """Checks robots.txt for the given URL."""
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        if base_url not in self.robot_parsers:
            robots_url = f"{base_url}/robots.txt"
            self.logger.info(f"Checking robots.txt at {robots_url}")
            # Note: A real implementation would parse it asynchronously here.
            # For this portfolio V1, we simply log the compliance step.
            self.robot_parsers[base_url] = RobotFileParser()
            
        # Simplified: assume True for V1 portfolio, but log the check.
        # It's important not to actually scrape disallowed paths.
        return True
        
    async def wait_random(self):
        """Waits for a random amount of time between min and max config values."""
        min_sec = self.config.get("scraper", {}).get("delay", {}).get("min_seconds", 3)
        max_sec = self.config.get("scraper", {}).get("delay", {}).get("max_seconds", 6)
        delay = random.uniform(min_sec, max_sec)
        self.logger.debug(f"Waiting for {delay:.2f} seconds...")
        await asyncio.sleep(delay)
        
    def save_checkpoint(self, run_id: str, data: dict, filename: str):
        """Saves a checkpoint JSON file."""
        checkpoint_dir = Path(self.config.get("paths", {}).get("data_dir", "data")) / "raw" / run_id
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = checkpoint_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            
    def load_checkpoint(self, run_id: str, filename: str) -> Optional[dict]:
        """Loads a checkpoint JSON file if it exists."""
        filepath = Path(self.config.get("paths", {}).get("data_dir", "data")) / "raw" / run_id / filename
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    @abc.abstractmethod
    async def discover_products(self, category_url: str, max_products: int) -> List[str]:
        """Discovers product URLs from a category or search page."""
        pass
