import abc
import asyncio
import json
import random
from pathlib import Path
from typing import Optional, List, Dict
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from playwright_stealth import Stealth
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
        self._stealth = Stealth()

    async def initialize(self):
        """Initializes the Playwright browser and context."""
        self.logger.info("Initializing browser...")
        self.playwright = await async_playwright().start()

        headless = self.config.get("run", {}).get("headless", True)

        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-web-security",
            ]
        )

        await self._new_context()

    async def _new_context(self):
        """Creates a fresh browser context, replacing the existing one."""
        if self.context:
            try:
                await self.context.close()
            except Exception:
                pass

        # Randomize viewport slightly to appear more human
        width = random.randint(1440, 1920)
        height = random.randint(768, 1080)

        self.context = await self.browser.new_context(
            viewport={'width': width, 'height': height},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/129.0.0.0 Safari/537.36"
            ),
            locale="en-US",
            timezone_id="America/New_York",
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "sec-ch-ua": '"Chromium";v="129", "Not=A?Brand";v="8"',
                "sec-ch-ua-platform": '"Windows"',
            }
        )

        self.page = await self.context.new_page()
        await self._stealth.apply_stealth_async(self.page)

        # Mask webdriver property via JS
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
        """)

        # Block images, fonts, media to save bandwidth
        await self.page.route("**/*", self._intercept_route)

    async def new_product_page(self) -> Page:
        """
        Opens a fresh page in a new context for product-detail scraping.
        This avoids carrying over bot-detection state from the listing context.
        """
        width = random.randint(1440, 1920)
        height = random.randint(768, 1080)

        product_context = await self.browser.new_context(
            viewport={'width': width, 'height': height},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/129.0.0.0 Safari/537.36"
            ),
            locale="en-US",
            timezone_id="America/New_York",
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Referer": "https://www.bestbuy.com/",
            }
        )

        page = await product_context.new_page()
        await self._stealth.apply_stealth_async(page)

        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
        """)

        # Block images/fonts/media
        await page.route("**/*", self._intercept_route)

        return page

    async def _intercept_route(self, route):
        """Intercepts requests to block unnecessary resources."""
        if route.request.resource_type in ["image", "media", "font"]:
            await route.abort()
        else:
            await route.continue_()

    async def close(self):
        """Closes the browser resources."""
        self.logger.info("Closing browser...")
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
            self.robot_parsers[base_url] = RobotFileParser()

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

    async def bypass_splash_screen(self, page=None, target_url: str = None):
        """Bypasses the 'Choose your country' splash screen if it appears."""
        p = page or self.page
        try:
            # Best Buy shows a country selector - find "United States" link
            # It can be text, an image link, or aria-label
            us_selectors = [
                'a[aria-label*="United States"]',
                'a[href*="intl=nosplash"]',
                'a:has-text("United States")',
                'img[alt*="United States"]',
                'a.us-link',
            ]
            for selector in us_selectors:
                try:
                    el = await p.wait_for_selector(selector, timeout=3000)
                    if el:
                        self.logger.info(f"Found country splash ({selector}). Clicking US...")
                        await el.click()
                        await p.wait_for_load_state('domcontentloaded')
                        await asyncio.sleep(2)
                        if target_url:
                            self.logger.info("Re-navigating to target URL after splash...")
                            await p.goto(target_url, timeout=60000, wait_until="domcontentloaded")
                            await asyncio.sleep(3)
                        return
                except Exception:
                    continue
        except Exception as e:
            self.logger.debug(f"Splash screen bypass check failed: {e}")

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
