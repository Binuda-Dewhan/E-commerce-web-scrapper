import asyncio
from typing import List
from app.scraper.base_scraper import BaseScraper


class EbayScraper(BaseScraper):
    """
    Discovers product URLs from eBay search/category pages.
    Warm-up strategy: starts from eBay homepage to acquire session cookies,
    then navigates to the target search page to avoid bot detection.
    """

    HOMEPAGE = "https://www.ebay.com/"

    async def _warmup_session(self):
        """Navigates to eBay homepage first to get session cookies."""
        self.logger.info("Warming up session on eBay homepage...")
        try:
            await self.page.goto(self.HOMEPAGE, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(3)
            # Simulate brief human-like mouse movement
            await self.page.mouse.move(400, 300)
            await asyncio.sleep(1)
            await self.page.mouse.wheel(0, 200)
            await asyncio.sleep(1)
        except Exception as e:
            self.logger.warning(f"Homepage warmup failed (non-fatal): {e}")

    async def discover_products(self, search_url: str, max_products: int) -> List[str]:
        """
        Discovers product URLs from an eBay search results page.
        Paginates through results until max_products is reached.
        """
        self.logger.info(f"Starting eBay product discovery: {search_url}")
        await self.check_robots_txt(search_url)

        # Warm up session first
        await self._warmup_session()

        discovered_urls: set = set()
        page_num = 1
        current_url = search_url

        while len(discovered_urls) < max_products:
            self.logger.info(f"Scraping page {page_num}: {current_url}")
            try:
                await self.page.goto(current_url, wait_until="domcontentloaded", timeout=30000)
                await asyncio.sleep(3)

                # Scroll to trigger lazy loading of product cards
                for _ in range(5):
                    await self.page.mouse.wheel(0, 700)
                    await asyncio.sleep(0.8)
                await asyncio.sleep(2)

                # Extract all /itm/ links (eBay product URLs)
                raw_links = await self.page.evaluate("""
                    () => Array.from(document.querySelectorAll('a'))
                        .map(a => a.href)
                        .filter(h => h && h.includes('ebay.com/itm/'))
                """)

                # Clean and deduplicate
                new_count = 0
                for link in raw_links:
                    clean = link.split('?')[0].split('#')[0].rstrip('/')
                    if clean and clean not in discovered_urls:
                        discovered_urls.add(clean)
                        new_count += 1
                        if len(discovered_urls) >= max_products:
                            break

                self.logger.info(
                    f"Page {page_num}: found {new_count} new URLs. Total: {len(discovered_urls)}"
                )
                
                if new_count == 0:
                    self.logger.warning(f"Zero URLs found on page {page_num}. Saving screenshot for debugging.")
                    await self.page.screenshot(path=f"data/debug_page_{page_num}.png")

                if len(discovered_urls) >= max_products:
                    break

                # Pagination: eBay uses a simple page counter in the URL
                # e.g. &_pgn=2 or appends it
                if "_pgn=" in current_url:
                    current_url = current_url.replace(f"_pgn={page_num}", f"_pgn={page_num + 1}")
                else:
                    sep = "&" if "?" in current_url else "?"
                    current_url = f"{current_url}{sep}_pgn={page_num + 1}"

                page_num += 1
                await self.wait_random()

            except Exception as e:
                self.logger.error(f"Error on discovery page {page_num}: {e}")
                break

        final_list = list(discovered_urls)[:max_products]
        self.logger.info(f"Discovery complete. Returning {len(final_list)} URLs.")

        # Checkpoint
        if final_list:
            self.save_checkpoint("discovery_latest", {
                "discovered_urls": final_list,
                "search_url": search_url,
                "total_found": len(final_list)
            }, "discovered_urls.json")

        return final_list
