import re
from typing import List
from urllib.parse import urljoin
from app.scraper.base_scraper import BaseScraper

class BestBuyScraper(BaseScraper):
    async def discover_products(self, category_url: str, max_products: int) -> List[str]:
        """Discovers product URLs from a Best Buy category page."""
        self.logger.info(f"Starting product discovery on: {category_url}")
        
        await self.check_robots_txt(category_url)
        
        discovered_urls = set()
        current_url = category_url
        page_num = 1
        
        while len(discovered_urls) < max_products:
            self.logger.info(f"Navigating to page {page_num}: {current_url}")
            try:
                await self.page.goto(current_url, timeout=30000, wait_until="domcontentloaded")
                await self.wait_random()
                
                # Extract all links on the page
                links = await self.page.evaluate('''() => {
                    return Array.from(document.querySelectorAll('a')).map(a => a.href);
                }''')
                
                # Filter for product URLs
                # Best Buy product URLs typically look like: /site/product-name/1234567.p?skuId=1234567
                new_urls = 0
                for link in links:
                    if '/site/' in link and '.p?skuId=' in link:
                        # Normalize URL to avoid duplicates with different tracking params
                        clean_link = link.split('&')[0]
                        if clean_link not in discovered_urls:
                            discovered_urls.add(clean_link)
                            new_urls += 1
                            if len(discovered_urls) >= max_products:
                                break
                                
                self.logger.info(f"Found {new_urls} new product URLs on page {page_num}. Total: {len(discovered_urls)}")
                
                if len(discovered_urls) >= max_products:
                    break
                    
                # Look for the 'Next' page button
                next_button = await self.page.query_selector('a.sku-list-page-next, a.next-page, a[rel="next"]')
                
                if next_button:
                    is_disabled = await next_button.evaluate('node => node.disabled || node.classList.contains("disabled")')
                    if not is_disabled:
                        # Click it and let the page load
                        self.logger.info("Clicking next page...")
                        await next_button.click()
                        await self.page.wait_for_load_state('domcontentloaded')
                        await self.wait_random()
                        current_url = self.page.url
                        page_num += 1
                    else:
                        self.logger.info("Next page button is disabled. Reached end of pagination.")
                        break
                else:
                    self.logger.info("No next page button found. Reached end of pagination.")
                    break
                    
            except Exception as e:
                self.logger.error(f"Error during discovery on page {page_num}: {e}")
                break
                
        # Return a list of at most max_products URLs
        final_list = list(discovered_urls)[:max_products]
        
        # Save a checkpoint of discovered URLs
        if len(final_list) > 0:
            checkpoint_data = {
                "discovered_urls": final_list,
                "category_url": category_url,
                "total_found": len(final_list)
            }
            # For demonstration, we use a generic run_id 'discovery_latest' if not provided by caller
            # Real implementation would pass run_id down
            self.save_checkpoint("discovery_latest", checkpoint_data, "discovered_urls.json")
            
        return final_list
