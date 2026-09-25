from playwright.async_api import Page
from typing import Dict, Any

class DomExtractor:
    @staticmethod
    async def extract(page: Page) -> Dict[str, Any]:
        """Extracts fallback fields from the DOM."""
        data = {}
        
        # Attempt to get specifications table
        # Best Buy typically has specs in divs with specific classes
        specs = await page.evaluate('''() => {
            const specList = {};
            // Look for generic spec list items or specific Best Buy classes
            const items = document.querySelectorAll('.specs-table ul li, .spec-categories .category-wrapper li, .spec-list li');
            items.forEach(item => {
                const titleEl = item.querySelector('.title, .spec-name, .v-fw-medium');
                const valEl = item.querySelector('.val, .spec-value, .v-fw-regular');
                if (titleEl && valEl) {
                    specList[titleEl.textContent.trim()] = valEl.textContent.trim();
                }
            });
            return specList;
        }''')
        
        if specs:
            data['specifications'] = specs
            
        # Attempt to get rating distribution
        rating_dist = await page.evaluate('''() => {
            const dist = {};
            // Look for rating breakdown bars
            const bars = document.querySelectorAll('.rating-bars, .histogram-row, .review-rating-bar, .ugc-histogram-row');
            bars.forEach(bar => {
                const starLabel = bar.querySelector('.star-label, .histogram-star-label');
                const countLabel = bar.querySelector('.count-label, .histogram-count-label');
                if (starLabel && countLabel) {
                    const stars = starLabel.textContent.trim().charAt(0); // e.g. "5" from "5 stars"
                    const count = countLabel.textContent.replace(/,/g, '').trim(); // e.g. "1245"
                    if (stars && !isNaN(parseInt(stars)) && count && !isNaN(parseInt(count))) {
                        dist[stars] = parseInt(count);
                    }
                }
            });
            return dist;
        }''')
        
        if rating_dist:
            data['rating_distribution'] = rating_dist
            
        return data
