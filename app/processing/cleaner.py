from typing import Dict, Any
from app.utils.parsers import parse_price, parse_rating, parse_review_count
from urllib.parse import urlparse


class DataCleaner:
    @staticmethod
    def clean(raw_data: Dict[str, Any], category: str) -> Dict[str, Any]:
        """
        Cleans raw extracted data into a standardized flat dictionary.
        Supports two formats:
          - Flat eBay extractor format (source='ebay' or has 'product_id')
          - Legacy nested Best Buy format (keys: jsonld, dom, sku, url)
        """
        if not raw_data:
            return {}

        cleaned = {}

        # ── eBay flat format ──────────────────────────────────────────────
        if raw_data.get("source") == "ebay" or "product_id" in raw_data:
            cleaned['product_id']        = str(raw_data.get("product_id", ""))
            cleaned['product_name']      = raw_data.get("product_name") or "Unknown Product"
            cleaned['brand']             = raw_data.get("brand") or "Unknown"
            cleaned['category']          = category
            cleaned['product_url']       = raw_data.get("product_url", "")
            cleaned['model_number']      = raw_data.get("model_number")
            cleaned['description']       = raw_data.get("description")
            cleaned['primary_image_url'] = raw_data.get("primary_image_url")
            cleaned['specifications']    = None

            # Price: may come as "US $139.99", "139.99", or "139.99 or Best Offer"
            price_raw = str(raw_data.get("price", ""))
            cleaned['current_price']     = parse_price(price_raw)

            orig_price_raw = str(raw_data.get("original_price", ""))
            cleaned['original_price']    = parse_price(orig_price_raw)

            cleaned['currency']          = raw_data.get("currency", "USD")

            avail = raw_data.get("availability", "")
            if "OutOfStock" in avail:
                cleaned['availability_status'] = "out_of_stock"
            else:
                cleaned['availability_status'] = "in_stock"

            cleaned['rating']              = parse_rating(str(raw_data.get("rating", "")))
            cleaned['review_count']        = parse_review_count(str(raw_data.get("rating_count", "")))
            cleaned['rating_distribution'] = None
            cleaned['seller_name']         = raw_data.get("seller_name", "")
            cleaned['condition']           = raw_data.get("condition", "")
            return cleaned

        # ── Legacy Best Buy nested format ─────────────────────────────────
        jsonld = raw_data.get("jsonld") or {}
        dom    = raw_data.get("dom")    or {}

        cleaned['product_id']   = str(raw_data.get("sku"))
        cleaned['product_name'] = jsonld.get("name") or "Unknown Product"

        brand_data = jsonld.get("brand")
        if isinstance(brand_data, dict):
            cleaned['brand'] = brand_data.get("name", "Unknown")
        else:
            cleaned['brand'] = str(brand_data) if brand_data else "Unknown"

        cleaned['category'] = category

        url = raw_data.get("url", "")
        parsed_url = urlparse(url)
        cleaned['product_url'] = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

        cleaned['model_number']      = jsonld.get("model") or jsonld.get("mpn")
        cleaned['description']       = jsonld.get("description")

        image_data = jsonld.get("image")
        if isinstance(image_data, list) and len(image_data) > 0:
            cleaned['primary_image_url'] = str(image_data[0])
        elif isinstance(image_data, str):
            cleaned['primary_image_url'] = image_data
        else:
            cleaned['primary_image_url'] = None

        cleaned['specifications']  = dom.get("specifications")

        offers = jsonld.get("offers", {})
        if isinstance(offers, list) and len(offers) > 0:
            offers = offers[0]

        cleaned['current_price']   = parse_price(str(offers.get("price")))
        cleaned['original_price']  = None
        cleaned['currency']        = offers.get("priceCurrency", "USD")

        avail = offers.get("availability", "")
        if "InStock" in avail:
            cleaned['availability_status'] = "in_stock"
        elif "OutOfStock" in avail:
            cleaned['availability_status'] = "out_of_stock"
        else:
            cleaned['availability_status'] = "unknown"

        agg_rating = jsonld.get("aggregateRating", {})
        cleaned['rating']              = parse_rating(str(agg_rating.get("ratingValue")))
        cleaned['review_count']        = parse_review_count(str(agg_rating.get("reviewCount")))
        cleaned['rating_distribution'] = dom.get("rating_distribution")

        seller = offers.get("seller")
        if isinstance(seller, dict):
            cleaned['seller_name'] = seller.get("name", "Best Buy")
        else:
            cleaned['seller_name'] = "Best Buy"

        cleaned['condition'] = ""
        return cleaned
