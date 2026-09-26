# E-Commerce Price Intelligence Scraper

Welcome to the **E-Commerce Price Intelligence Scraper**, a robust, resilient Python-based pipeline designed to extract product data and track price changes over time. 

Initially aimed at Best Buy, this scraper has been successfully migrated to **eBay** to bypass aggressive enterprise bot mitigation (Akamai Bot Manager) and to leverage eBay's rich structured data.

## 📌 What is this?
This project is an automated data pipeline that:
1. **Discovers** products based on a search query (e.g., Laptops on eBay).
2. **Extracts** detailed product information, including price, specifications, images, and seller details.
3. **Validates & Cleans** the extracted data to ensure it is structured and safe for storage.
4. **Tracks** historical pricing over time. If a product price drops or increases, it logs the change.
5. **Exports** the final analyzed data into rich CSV and JSON reports.

## 🛒 What are we scraping?
We are currently scraping **eBay Laptop Listings**. The scraper extracts the following information for each product:
- **Core Info:** Product ID, Name, Brand, Category, URL, and Primary Image.
- **Price Intelligence:** Current Price, Original Price, Currency, and Availability (In Stock/Out of Stock).
- **Metadata:** Seller Name, Condition, Rating, and Review Count.

## ⚙️ How does it work?

The system is built on a modular architecture using **Playwright** (for browser automation) and **Pydantic** (for strict data validation). It operates in the following phases:

1. **Session Warm-up (`EbayScraper`):**
   - The browser opens the eBay homepage first. This mimics human behavior and acquires necessary session cookies, tricking basic bot detection mechanisms.
2. **Product Discovery (`EbayScraper`):**
   - The scraper navigates to the search results page (e.g., searching for "Laptops").
   - It scrolls down the page to trigger lazy-loaded product cards.
   - It extracts all valid product URLs (`/itm/...`) and automatically paginates to the next page until the target `max_products` is reached.
3. **Data Extraction (`EbayExtractor`):**
   - The scraper visits each individual product URL using the same "warmed-up" browser session.
   - **Layer 1 (Primary):** It searches the page's HTML for hidden `JSON-LD` structured data (Schema.org/Product). This is the most reliable way to extract data.
   - **Layer 2 (Fallback):** If JSON-LD is missing, it falls back to parsing the visual DOM using CSS selectors to find the price and title.
4. **Processing (`DataCleaner` & `DataValidator`):**
   - The raw data is flattened into a standardized format by the `DataCleaner`.
   - `DataValidator` enforces strict data typing using Pydantic models (`Product` and `Observation`). If a price isn't a number or an ID is missing, the bad data is rejected.
5. **Storage & Analytics (`RunManager`):**
   - New products are added to `data/catalog/products.csv`.
   - Prices for the current run are logged in `data/observations/products.csv`.
   - The system compares current prices against historical prices to calculate average category prices, discounts, and price fluctuations.
6. **Export:**
   - A final merged report is generated at `data/final/full_report.csv` containing both the product details and the latest price intelligence analytics.

## 🚀 How to Run It

### Prerequisites
Make sure you have Python installed, your virtual environment activated, and Playwright browsers installed.
```bash
# Activate your virtual environment (Windows)
.\venv\Scripts\activate

# (First time only) Install playwright browsers
playwright install chromium
```

### Configuration
You can configure the behavior of the scraper in `config/settings.yaml`.
```yaml
target_website: ebay
run:
  max_products: 25      # Change this to scrape more or fewer products
  headless: false       # Set to true to hide the browser while running
```

### Execution
To run the full pipeline, simply execute the main script:
```bash
python main.py
```

Watch the terminal logs! The scraper will:
1. Open the browser and warm up the session.
2. Search for laptops and gather URLs.
3. Visit each URL to extract data.
4. Save the final output to the `data/final/` folder.

### Viewing the Results
Once the run is complete, open `data/final/full_report.csv` in Excel, Google Sheets, or a text editor to view your newly extracted price intelligence data!
