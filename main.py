import asyncio
import logging
import pandas as pd
from app.utils.config import load_config
from app.utils.logger import setup_logger
from app.scraper.ebay_scraper import EbayScraper
from app.scraper.ebay_extractor import EbayExtractor
from app.processing.cleaner import DataCleaner
from app.processing.validator import DataValidator
from app.processing.deduplicator import Deduplicator
from app.storage.product_store import ProductStore
from app.storage.observation_store import ObservationStore
from app.storage.checkpoint import RunManager
from app.analysis.price_intelligence import PriceIntelligence
from app.analysis.category_comparison import CategoryComparison
from app.exporters.csv_exporter import CsvExporter
from app.exporters.json_exporter import JsonExporter
from app.utils.timestamps import get_current_iso_timestamp

async def run_pipeline():
    config = load_config()
    run_id = f"run_{get_current_iso_timestamp().replace(':', '').replace('-', '').replace('Z', '').replace('T', '_')}"
    logger = setup_logger(run_id, config.get("paths", {}).get("logs_dir", "logs"))
    
    logger.info(f"Starting pipeline run: {run_id}")
    
    run_manager = RunManager(config, logger, run_id)
    # eBay laptop search - sorted by newest listings
    search_url = "https://www.ebay.com/sch/i.html?_nkw=laptop&_sop=10&_ipg=48"
    run_manager.create_run(category="Laptops")
    
    scraper = EbayScraper(config, logger)
    extractor = EbayExtractor(config, logger)
    await scraper.initialize()
    
    max_products = config.get("run", {}).get("max_products", 5)
    
    try:
        # 1. Discovery
        discovered_urls = await scraper.discover_products(search_url, max_products)
        run_manager.update_stats(discovered=len(discovered_urls))
        
        # 2. Extraction using the same warm browser page
        valid_products = []
        
        for url in discovered_urls:
            try:
                raw_data = await extractor.extract_product(
                    url, run_id, page=scraper.page
                )
                cleaned = DataCleaner.clean(raw_data, "Laptops")
                
                is_valid, prod, obs, err = DataValidator.validate(cleaned, run_id)
                if is_valid:
                    valid_products.append({"product": prod, "observation": obs})
                    run_manager.update_stats(extracted=1)
                else:
                    logger.warning(f"Validation failed for {url}: {err}")
                    run_manager.update_stats(failed=1)
            except Exception as e:
                logger.error(f"Failed to extract {url}: {e}")
                run_manager.update_stats(failed=1)
                
        # 4. Deduplication within run
        deduped = Deduplicator.deduplicate_run(valid_products)
        
        final_prods = [item["product"] for item in deduped]
        final_obs = [item["observation"] for item in deduped]
        
        # 5. Storage
        p_store = ProductStore(config, logger)
        o_store = ObservationStore(config, logger)
        
        p_store.upsert_products(final_prods)
        o_store.append_observations(final_obs)
        
        # 6. Analysis
        all_prods_df = p_store._load_existing()
        if o_store.filepath.exists():
            all_obs_df = pd.read_csv(o_store.filepath, dtype={'product_id': str})
        else:
            all_obs_df = pd.DataFrame()
            
        analysis_df = PriceIntelligence.analyze(all_prods_df, all_obs_df)
        comparison_df = CategoryComparison.compare(analysis_df)
        
        # 7. Exports
        csv_exp = CsvExporter(config, logger)
        json_exp = JsonExporter(config, logger)
        
        csv_exp.export(comparison_df, "full_report.csv")
        json_exp.export(comparison_df, "full_report.json")
        
        run_manager.complete_run(status="success")
        logger.info(f"Pipeline run {run_id} completed successfully.")
        
    finally:
        await scraper.close()

if __name__ == "__main__":
    asyncio.run(run_pipeline())
