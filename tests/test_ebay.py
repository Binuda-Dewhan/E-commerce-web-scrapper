import asyncio
import logging
from app.utils.config import load_config
from app.scraper.ebay_scraper import EbayScraper
from app.scraper.ebay_extractor import EbayExtractor
from app.processing.cleaner import DataCleaner
from app.processing.validator import DataValidator

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("TestEbay")

async def test_pagination(config):
    """Test 4.2: Pagination and discovery logic."""
    logger.info("--- Starting Test 4.2: Pagination ---")
    scraper = EbayScraper(config, logger)
    await scraper.initialize()
    
    try:
        # Request 10 products to force scrolling and potentially pagination
        search_url = "https://www.ebay.com/sch/i.html?_nkw=laptop&_sop=10&_ipg=48"
        urls = await scraper.discover_products(search_url, max_products=10)
        
        assert len(urls) == 10, f"Expected 10 URLs, got {len(urls)}"
        logger.info(f"✅ Pagination test passed. Found {len(urls)} URLs.")
        return urls, scraper
    except Exception as e:
        logger.error(f"❌ Pagination test failed: {e}")
        await scraper.close()
        raise

async def test_extraction_and_cleaning(config, scraper, test_urls):
    """Test 4.1, 4.3, 4.4: Extraction, cleaning, and validation."""
    logger.info("--- Starting Test 4.1 & 4.3 & 4.4: Extraction & Data Integrity ---")
    extractor = EbayExtractor(config, logger)
    
    success_count = 0
    for url in test_urls[:3]:  # Test on the first 3 URLs to save time
        logger.info(f"Testing extraction for: {url}")
        
        # 4.1 & 4.3 Extraction
        raw_data = await extractor.extract_product(url, run_id="test_run", page=scraper.page)
        
        assert raw_data is not None, f"Extraction failed for {url}"
        assert raw_data.get("product_name"), "Product name is missing"
        assert raw_data.get("price"), "Price is missing"
        
        # 4.4 Data Integrity (Cleaning & Validation)
        cleaned_data = DataCleaner.clean(raw_data, category="Laptops")
        
        assert cleaned_data.get("current_price") is not None, "Cleaned price is missing"
        assert cleaned_data.get("product_id"), "Cleaned product ID is missing"
        
        is_valid, prod, obs, err = DataValidator.validate(cleaned_data, run_id="test_run")
        
        assert is_valid, f"Validation failed: {err}"
        
        logger.info(f"✅ Extraction & Integrity passed for {url}. Price: {obs['current_price']}")
        success_count += 1
        
    logger.info(f"✅ All {success_count} extraction tests passed.")

async def main():
    config = load_config()
    
    try:
        urls, scraper = await test_pagination(config)
        await test_extraction_and_cleaning(config, scraper, urls)
        
        logger.info("🎉 All SDLC Phase 4 tests completed successfully!")
    finally:
        if 'scraper' in locals():
            await scraper.close()

if __name__ == "__main__":
    asyncio.run(main())
