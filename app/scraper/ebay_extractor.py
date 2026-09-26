import asyncio
import json
import re
import html
from typing import Optional, Dict, Any
from playwright.async_api import Page
from playwright_stealth import Stealth


class EbayExtractor:
    """
    Extracts product data from eBay item pages.
    Primary: JSON-LD structured data (schema.org/Product).
    Fallback: CSS selectors for each field.
    """

    STEALTH = Stealth()

    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

    async def extract_product(self, url: str, run_id: str, browser=None, page: Optional[Page] = None) -> Optional[Dict[str, Any]]:
        """
        Extracts structured product data from an eBay product page.
        If a page object is provided, navigates with it directly.
        """
        self.logger.info(f"Extracting: {url}")

        # Extract item ID from URL (e.g. .../itm/158322714380)
        match = re.search(r'/itm/(\d+)', url)
        item_id = match.group(1) if match else url.split('/')[-1]

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(4)

            page_title = await page.title()
            if "Error" in page_title or "Access Denied" in page_title:
                self.logger.warning(f"Blocked on {url}: title = {page_title}")
                return None

            # --- Primary: JSON-LD extraction ---
            data = await self._extract_from_jsonld(page, item_id, url)
            if data:
                self.logger.info(f"JSON-LD extraction success for item {item_id}")
                return data

            # --- Fallback: CSS selector extraction ---
            self.logger.warning(f"JSON-LD failed, using CSS fallback for {url}")
            data = await self._extract_from_selectors(page, item_id, url)
            return data

        except Exception as e:
            self.logger.error(f"Extraction failed for {url}: {e}")
            return None

    async def _extract_from_jsonld(self, page: Page, item_id: str, url: str) -> Optional[Dict]:
        """Parse schema.org/Product from embedded JSON-LD scripts."""
        try:
            blocks = await page.evaluate("""
                () => Array.from(document.querySelectorAll('script[type="application/ld+json"]'))
                    .map(s => s.textContent)
            """)

            for block in blocks:
                try:
                    data = json.loads(block)
                    if data.get("@type") != "Product":
                        continue

                    # Offers can be a dict or list
                    offers = data.get("offers", {})
                    if isinstance(offers, list):
                        offers = offers[0] if offers else {}

                    # Decode HTML entities in name
                    name = html.unescape(data.get("name", ""))

                    # Seller info
                    seller = offers.get("seller", {})
                    seller_name = seller.get("name", "") if isinstance(seller, dict) else ""

                    # Aggregate rating
                    agg = data.get("aggregateRating", {})

                    # Images
                    images = data.get("image", [])
                    if isinstance(images, list) and images:
                        img = images[0]
                        image_url = img.get("url", "") if isinstance(img, dict) else img
                    elif isinstance(images, str):
                        image_url = images
                    else:
                        image_url = ""

                    return {
                        "product_id": item_id,
                        "product_name": name,
                        "brand": data.get("brand", {}).get("name", "") if isinstance(data.get("brand"), dict) else data.get("brand", ""),
                        "category": "Laptops",
                        "product_url": url,
                        "price": offers.get("price", ""),
                        "original_price": offers.get("highPrice", ""),
                        "currency": offers.get("priceCurrency", "USD"),
                        "condition": offers.get("itemCondition", "").replace("https://schema.org/", ""),
                        "availability": offers.get("availability", "").replace("https://schema.org/", ""),
                        "seller_name": seller_name,
                        "rating": agg.get("ratingValue", ""),
                        "rating_count": agg.get("reviewCount", ""),
                        "description": data.get("description", ""),
                        "primary_image_url": image_url,
                        "source": "ebay",
                        "extraction_method": "json_ld",
                    }
                except (json.JSONDecodeError, Exception):
                    continue

        except Exception as e:
            self.logger.debug(f"JSON-LD parse error: {e}")

        return None

    async def _extract_from_selectors(self, page: Page, item_id: str, url: str) -> Optional[Dict]:
        """CSS selector fallback when JSON-LD is unavailable."""
        try:
            result = await page.evaluate("""
                () => {
                    const get = (selectors) => {
                        for (const s of selectors) {
                            const el = document.querySelector(s);
                            if (el && el.innerText && el.innerText.trim()) return el.innerText.trim();
                        }
                        return '';
                    };

                    const name = get([
                        '.x-item-title__mainTitle span',
                        'h1[class*="title"]',
                        'h1'
                    ]);

                    const price = get([
                        '.x-price-primary',
                        '#prcIsum',
                        '[itemprop="price"]',
                        '.mainPrice',
                    ]).replace(/\\n|or Best Offer|or best offer/gi, '').trim();

                    const condition = get([
                        '.ux-label',
                        '.u-cbx-condition',
                        '[class*="condition"]'
                    ]);

                    const seller = get([
                        '.x-sellercard-atf__info__about-seller a',
                        '.mbg-nw',
                        '.seller-persona'
                    ]);

                    const image = (() => {
                        const img = document.querySelector('.ux-image-carousel-item.active img, .imgTag');
                        return img ? (img.getAttribute('data-zoom-src') || img.src || '') : '';
                    })();

                    return { name, price, condition, seller, image };
                }
            """)

            if not result.get("name"):
                return None

            return {
                "product_id": item_id,
                "product_name": result.get("name", ""),
                "brand": "",
                "category": "Laptops",
                "product_url": url,
                "price": result.get("price", ""),
                "original_price": "",
                "currency": "USD",
                "condition": result.get("condition", ""),
                "availability": "",
                "seller_name": result.get("seller", ""),
                "rating": "",
                "rating_count": "",
                "description": "",
                "primary_image_url": result.get("image", ""),
                "source": "ebay",
                "extraction_method": "css_selectors",
            }

        except Exception as e:
            self.logger.error(f"CSS selector extraction failed: {e}")
            return None
