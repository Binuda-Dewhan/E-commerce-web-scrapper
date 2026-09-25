# E-commerce Product Data & Price Intelligence System

## Architecture & Feasibility Review Request

### Important Instruction

Do NOT start implementation yet.

Act as a senior software engineer and solution architect. First review this project concept, identify architectural/technical problems, improve the design where necessary, and recommend the best practical approach for a portfolio-quality implementation.

We will review your recommendations before writing implementation code.

The goal is to build a realistic client-style e-commerce data extraction and price intelligence system — not just a quick product scraper.

---

## 1. Project Concept

We are building a reusable browser-based system for collecting publicly available product information from an e-commerce website.

### Fictional Client

A US-based e-commerce research and marketing company wants to monitor products from an online marketplace/store.

The client wants to:
- discover products by category/search
- collect product information
- track prices over time
- understand discounts
- collect ratings and review counts
- capture rating distribution when publicly available
- monitor availability
- collect product specifications
- clean and validate the data
- compare products and prices
- export analysis-ready datasets

### Example Scenario

The client wants to monitor laptop products from an online e-commerce marketplace.

The system should NOT be hardcoded only for laptops. The architecture should allow categories such as smartphones, TVs, cameras, appliances, gaming products, and home products later.

---

## 2. Main Objective

The objective is NOT simply “Build an e-commerce scraper.”

The objective is:

> Build a reusable browser-based e-commerce product data collection and price intelligence pipeline that transforms online product listings into clean, analysis-ready datasets and preserves historical observations for comparison over time.

Proposed flow:

Client Requirement
→ Website / Category Configuration
→ Product Discovery
→ Product Detail Extraction
→ Raw Data
→ Cleaning & Normalization
→ Deduplication & Validation
→ Historical Snapshot Storage
→ Price / Product Analysis
→ Final Dataset
→ CSV / Excel / JSON

---

## 3. Critical Requirement: Date / Historical Data

Every extraction must include a timestamp.

At minimum:
- scraped_at
- scraped_date
- scraped_time

Prefer a proper ISO 8601 timestamp.

The purpose is to support time-based product and price comparison.

Example:

Day 1: Product A = $999
Day 7: Product A = $949
Day 14: Product A = $1,029

The system should support:
- price change
- previous price
- current price
- percentage change
- lowest observed price
- highest observed price
- number of observations
- first observed date
- latest observed date

### Senior Architecture Question

Evaluate whether the system should separate:

### Product Master
Stable information:
- product_id
- product_name
- brand
- product_url
- category
- SKU/model

### Product Observation / Snapshot
Time-dependent information:
- scraped_at
- price
- original_price
- discount
- availability
- rating
- review_count
- rating_distribution
- seller
- shipping information where available

A separate historical observation dataset/table is preferred if it keeps the design simple and maintainable.

---

## 4. Website Selection — IMPORTANT

Choose ONE primary e-commerce website for V1.

Candidate platforms may include:
- eBay
- Walmart
- Amazon
- other suitable large e-commerce marketplaces

Evaluate candidates based on:
1. Public accessibility
2. Website structure
3. Product page consistency
4. Category/search structure
5. Pagination
6. Dynamic content
7. Product variants
8. Price availability
9. Rating/review availability
10. Rating distribution availability
11. Seller information
12. Availability information
13. International relevance
14. Product/catalog variety
15. Browser automation feasibility
16. Selector reliability
17. Likelihood of blocking/challenges
18. Terms/access restrictions
19. Portfolio value
20. Responsible scraping feasibility

Do not choose based only on popularity.

If a platform is popular but technically unsuitable for responsible browser automation, do not force it.

eBay is attractive because it has many international marketplaces, categories, and sellers. Verify whether its product/listing structure and rating/review information are suitable.

Walmart may also be considered because of its broad catalog and marketplace model, but evaluate actual public product-page structure and international relevance.

Do NOT implement multiple websites in V1.

The architecture may support another website later through a source-specific adapter/scraper.

---

## 5. Product Data

Potential standard fields:

### Product
- product_name
- brand
- category
- subcategory
- product_url
- product_id
- SKU
- model_number
- description

### Pricing
- current_price
- original_price
- discount_amount
- discount_percentage
- currency
- price_type
- sale_status

### Availability
- availability_status
- in_stock

### Reputation
- rating
- review_count

### Seller
- seller_name
- seller_url
- seller_rating
- seller_review_count

### Media
- primary_image_url
- additional_image_urls

### Metadata
- source_url
- scraped_at
- extraction_status

Review the schema and remove fields that are unreliable or unnecessary. Never invent missing information.

---

## 6. Rating Distribution — IMPORTANT

If the target website publicly displays a rating breakdown, collect it.

Example:

5 stars → 300 reviews
4 stars → 80 reviews
3 stars → 25 reviews
2 stars → 10 reviews
1 star → 5 reviews

Prefer a structured representation such as:

rating_distribution:
  5: 300
  4: 80
  3: 25
  2: 10
  1: 5

Recommend a better representation if appropriate.

Validate, when possible:

sum(rating_distribution) ≈ review_count

Some websites may round or display incomplete data. Record discrepancies rather than silently changing the data.

If the website does not expose rating distribution publicly, leave it null. Do not infer it from the average rating.

---

## 7. Product Specifications

Specifications vary by category.

For laptops:
- processor
- RAM
- storage
- screen size
- resolution
- GPU
- operating system

For phones:
- storage
- RAM
- screen
- camera
- battery
- operating system

Do NOT create hundreds of category-specific columns.

Evaluate a flexible structure such as:

specifications:
  processor: ...
  ram: ...
  storage: ...
  screen_size: ...

Keep common fields standard and category-specific attributes structured.

---

## 8. Product Variants

Evaluate:
- size
- color
- storage
- configuration
- model variants

Possible approaches:
A. Each variant is its own product/observation record.
B. Parent product contains variants.
C. Hybrid approach.

Recommend the simplest reliable V1 approach.

If price differs by variant, do not accidentally overwrite one variant's price with another.

---

## 9. Price Intelligence

Calculate:
- discount_amount
- discount_percentage
- price_change
- price_change_percentage
- lowest_observed_price
- highest_observed_price
- first_observed_price
- latest_price
- number_of_price_observations

Example:

Product A
2026-09-01 → $999
2026-09-08 → $949
2026-09-15 → $979

Derived:
- latest_price = $979
- lowest_observed_price = $949
- highest_observed_price = $999
- price_change_from_previous = +$30
- price_change_percentage = +3.16%

Do not claim a product is “best” or “cheapest” without a clearly defined comparison scope.

---

## 10. Product Comparison

Support descriptive comparisons such as:
- products within a category
- price vs category average
- rating vs category average
- review count
- discount percentage
- availability
- historical price movement

Potential derived fields:
- category_average_price
- price_difference_from_category_average
- price_position
- rating_vs_category_average

Use transparent calculations. Avoid arbitrary “best product” scores.

---

## 11. Data Pipeline

Use:

Raw
→ Cleaned
→ Validated
→ Historical Observations
→ Analysis
→ Final

Cleaning may include:
- price parsing
- currency normalization
- rating normalization
- review count conversion
- whitespace cleanup
- URL normalization
- availability normalization
- text normalization
- specification normalization

Examples:
"$1,299.00" → 1299.00
"4.6 out of 5 stars" → 4.6
"1,245 ratings" → 1245

---

## 12. Deduplication

Possible duplicates:
- multiple search results
- pagination
- category pages
- sponsored listings
- repeated crawls
- variants

Use reliable identifiers in this order where available:
1. Product ID / SKU
2. Canonical URL
3. Model number + brand
4. Normalized product name + brand

Do not rely only on product name.

Historical observations must NOT be deduplicated simply because they refer to the same product.

Product A on September 1 and Product A on September 8 should remain two observations.

---

## 13. Data Model Recommendation

Evaluate a normalized design:

### products.csv
Stable information:
- product_id
- product_name
- brand
- category
- product_url
- SKU
- model_number

### product_observations.csv
Time-dependent information:
- product_id
- scraped_at
- current_price
- original_price
- discount_amount
- discount_percentage
- currency
- availability_status
- rating
- review_count
- rating_distribution
- seller_name
- seller_rating

### product_analysis.csv
Derived information:
- product_id
- latest_price
- lowest_observed_price
- highest_observed_price
- price_change
- price_change_percentage
- category_average_price
- price_difference_from_average
- observation_count

Review whether this is appropriate for V1 or whether a simpler design is better.

---

## 14. Browser Automation

Use browser automation as the main collection mechanism for V1.

Candidates:
- Playwright
- Selenium

Evaluate both before implementation.

Consider:
- dynamic JavaScript content
- pagination
- infinite scrolling
- product detail pages
- multiple tabs/pages
- waiting strategies
- browser sessions
- selectors
- reliability
- debugging
- performance
- maintainability

Initial preference is Playwright because Project 1 already uses it, but still perform an objective comparison.

Do not use:
- CAPTCHA bypass
- anti-bot bypass
- authentication bypass
- access-control circumvention
- coordinate-based clicking

If the website presents a challenge/block, record the failure and stop/skip appropriately.

---

## 15. Reliability

Support:
- retries for temporary failures
- timeouts
- checkpointing
- resume
- failure isolation
- structured logging

Useful statuses:
- success
- partial
- failed
- skipped

Useful logs:
- search started
- category started
- product discovered
- product processed
- price extracted
- rating extracted
- variant processed
- duplicate detected
- analysis completed
- export completed
- failure

---

## 16. Configuration

Example:
- target_website
- category
- search_term
- max_products
- browser_mode
- headless/headed
- output_format
- delay settings
- timeout settings

No complicated UI initially.

Use YAML/JSON/CLI configuration.

---

## 17. Proposed Project Structure

ecommerce-product-intelligence/
│
├── app/
│   ├── scraper/
│   │   ├── listing_scraper.py
│   │   └── product_scraper.py
│   │
│   ├── processing/
│   │   ├── cleaner.py
│   │   ├── deduplicator.py
│   │   └── validator.py
│   │
│   ├── analysis/
│   │   ├── price_analysis.py
│   │   └── product_analysis.py
│   │
│   ├── models/
│   │   └── product.py
│   │
│   └── exporters/
│       ├── csv_exporter.py
│       ├── excel_exporter.py
│       └── json_exporter.py
│
├── config/
│   └── settings.yaml
│
├── data/
│   ├── raw/
│   ├── cleaned/
│   ├── observations/
│   ├── analyzed/
│   └── final/
│
├── logs/
├── tests/
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md

This is only a starting proposal. Improve it if necessary.

---

## 18. Technology Stack

Expected candidates:
- Python 3.12+
- Playwright OR Selenium
- Pandas
- Pydantic
- OpenPyXL
- PyYAML
- pytest
- Python logging

Outputs:
- CSV
- JSON
- Excel

Use only necessary libraries.

---

## 19. Testing

Plan tests for:
- price parsing
- currency parsing
- rating parsing
- review count parsing
- rating distribution parsing
- discount calculation
- price-change calculation
- duplicate detection
- variant handling
- missing fields
- malformed URLs
- export generation
- historical observation storage

Test realistic edge cases.

---

## 20. Security

Do not commit:
- credentials
- cookies
- browser profiles
- authentication data
- API keys
- .env secrets

Use .env, .env.example, and .gitignore.

---

## 21. Responsible Scraping

This is a portfolio project.

Use only publicly accessible information.

Respect:
- website Terms of Service
- applicable laws
- access restrictions
- reasonable request rates
- privacy considerations

Do not collect sensitive personal information.

Do not bypass CAPTCHA, authentication, technical access controls, or anti-bot protections.

Do not design aggressive bulk scraping.

Before selecting the target website, assess whether the project can be demonstrated responsibly.

---

## 22. Future UI

After the data pipeline is stable, a Streamlit UI could allow:
- select website
- select category
- enter search term
- set maximum products
- start collection
- view summary
- view price changes
- download Excel/CSV

Do NOT implement UI in the first phase.

---

## 23. Fiverr Portfolio Goal

The project should demonstrate:
- E-commerce web scraping
- Product data extraction
- Browser automation
- Data cleaning
- Data validation
- Historical price tracking
- Product comparison
- Data analysis
- Excel/CSV/JSON reporting
- Automation

Portfolio title candidate:

**E-commerce Product Data & Price Intelligence System**

Alternative:

**E-commerce Product Scraping & Price Tracking System**

The project should look like a realistic client solution rather than a tutorial scraper.

---

## 24. Expected Portfolio Deliverables

After implementation:
1. GitHub repository
2. Actual sample dataset
3. Raw dataset
4. Cleaned dataset
5. Historical price observation dataset
6. Final Excel report
7. CSV
8. JSON
9. Product comparison/price analysis output
10. Screenshots
11. Short demo video
12. Fiverr portfolio description

All statistics shown in the portfolio must come from actual runs. Do not fabricate results.

---

# 25. Required Architecture Review

Before implementation, provide these sections:

### A. Overall Architecture Review
- What is good?
- What is unnecessary?
- What is missing?
- What should change?

### B. Website Selection
Evaluate eBay, Walmart, Amazon, and any other strong candidate.

Compare:
- accessibility
- product structure
- categories
- sellers
- pricing
- reviews
- rating distribution
- variants
- international relevance
- browser automation feasibility
- responsible scraping feasibility
- portfolio value

Recommend ONE primary website for V1 and explain why.

Do not recommend multi-site implementation for V1.

### C. Browser Automation
Playwright vs Selenium. Recommend one.

### D. Historical Data Architecture
Evaluate Product Master + Product Observation/Snapshot design and explain repeated-run behavior.

### E. Product Schema
Review all fields and remove unreliable/unnecessary fields.

### F. Rating Distribution
Explain how to store and validate 1–5 star review counts.

### G. Product Variants
Recommend a practical V1 strategy.

### H. Price Intelligence
Review price history and comparison calculations.

### I. Data Pipeline
Review Raw → Cleaned → Validated → Observations → Analysis → Final.

### J. Deduplication
Review product identity and historical observations.

### K. Reliability
Review retries, timeout, checkpoint, resume, logging, and failure isolation.

### L. Testing
Recommend important tests.

### M. Security & Responsible Scraping
Review risks and safeguards.

### N. Project Structure
Improve the proposed structure if necessary.

### O. Implementation Roadmap
Break implementation into clear stages:
Phase 1 → project setup
Phase 2 → website discovery
Phase 3 → product extraction
Phase 4 → processing
Phase 5 → historical snapshots
Phase 6 → analysis
Phase 7 → exports
Phase 8 → testing
Phase 9 → documentation

### P. Alternative Ideas
Suggest useful improvements that add real portfolio value without unnecessary complexity.

---

# 26. Final Instruction

Do NOT write implementation code yet.

Do NOT create the UI yet.

Do NOT start scraping yet.

First perform the architecture and feasibility review.

We will review your response together and then finalize the architecture before implementation.
