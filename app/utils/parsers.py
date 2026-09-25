import re
from typing import Optional

def parse_price(price_str: Optional[str]) -> Optional[float]:
    """Parses a price string like '$1,299.00' or '$1,299.00 - $1,499.00' into a float.
    In case of range, returns the lower value."""
    if not price_str:
        return None
        
    # Clean the string
    cleaned = price_str.upper().replace('$', '').replace(',', '').strip()
    
    if not cleaned or cleaned == 'N/A' or cleaned == 'NONE':
        return None
        
    # Handle ranges by splitting and taking the first part
    if '-' in cleaned:
        cleaned = cleaned.split('-')[0].strip()
        
    try:
        # Extract the first numeric match
        match = re.search(r'\d+\.?\d*', cleaned)
        if match:
            return float(match.group())
        return None
    except ValueError:
        return None

def parse_rating(rating_str: Optional[str]) -> Optional[float]:
    """Parses a rating string like '4.6 out of 5 stars' or '4.6' into a float."""
    if not rating_str:
        return None
        
    match = re.search(r'(\d+\.\d+|\d+)', rating_str)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            pass
    return None

def parse_review_count(count_str: Optional[str]) -> Optional[int]:
    """Parses a review count like '1,245 ratings' or '(1,245)' into an int."""
    if not count_str:
        return None
        
    # Remove commas and extract numbers
    cleaned = count_str.replace(',', '')
    match = re.search(r'(\d+)', cleaned)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            pass
    return None
