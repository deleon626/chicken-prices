"""
Utility functions for the scraper
"""
import random
import re
from typing import Optional

# User agents to rotate through
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

def get_random_user_agent() -> str:
    """Get a random user agent from the list."""
    return random.choice(USER_AGENTS)

def random_delay(min_sec: float = 1.0, max_sec: float = 3.0) -> float:
    """
    Generate a random delay between min_sec and max_sec.
    Returns the delay time used.
    """
    delay = random.uniform(min_sec, max_sec)
    return delay

def extract_price(price_text: str) -> Optional[float]:
    """
    Extract numeric price from Shopee price text.
    Examples: "Rp50.000", "Rp 100.000", "Rp1.000.000"
    Returns price in float (e.g., 50000.0, 100000.0, 1000000.0)
    """
    if not price_text:
        return None
    
    # Remove "Rp", spaces, and dots used as thousands separators
    cleaned = re.sub(r'[Rp\s.]', '', price_text)
    
    try:
        return float(cleaned)
    except ValueError:
        return None

def extract_sold_count(sold_text: str) -> Optional[int]:
    """
    Extract sold count from Shopee sold text.
    Examples: "10RB Terjual", "500 Terjual", "1RB+ Terjual"
    Returns sold count as integer
    """
    if not sold_text:
        return None
    
    # Convert to lowercase and remove whitespace
    text = sold_text.lower().strip()
    
    # Match patterns like "10rb", "500", "1rb+", "1.5rb"
    match = re.search(r'([\d.,]+)\s*rb', text)
    if match:
        value_str = match.group(1).replace(',', '.')
        try:
            return int(float(value_str) * 1000)
        except ValueError:
            pass
    
    # Match plain numbers
    match = re.search(r'(\d+)', text)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            pass
    
    return None

def extract_weight(product_name: str) -> Optional[float]:
    """
    Extract weight in kg from product name.
    Examples: "Ayam 1kg", "Ayam 500gr", "Ayam 0.5 kg"
    Returns weight in kg as float (e.g., 1.0, 0.5)
    """
    if not product_name:
        return None
    
    name_lower = product_name.lower()
    
    # Match "500gr", "500 gr", "500gram", "500 gram"
    match = re.search(r'(\d+(?:\.\d+)?)\s*(?:gr|gram)\b', name_lower)
    if match:
        return float(match.group(1)) / 1000
    
    # Match "1kg", "1 kg", "1 kilo", "1 kilogram"
    match = re.search(r'(\d+(?:\.\d+)?)\s*(?:kg|kilo|kilogram)\b', name_lower)
    if match:
        return float(match.group(1))
    
    return None

def calculate_price_per_kg(price: float, weight_kg: float) -> Optional[float]:
    """
    Calculate price per kg given price and weight in kg.
    Returns None if weight is zero or invalid.
    """
    if not price or not weight_kg or weight_kg <= 0:
        return None
    return price / weight_kg

def is_chicken_product(product_name: str) -> bool:
    """
    Check if a product is related to chicken.
    Returns True if product name contains chicken-related keywords.
    """
    if not product_name:
        return False
    
    name_lower = product_name.lower()
    
    chicken_keywords = [
        'ayam', 'chicken', 'daging', 'fillet', 'paha', 'dada',
        'sayap', 'ceker', 'jeroan', 'pejantan', 'broiler',
        'kampung', 'negeri', 'panggang', 'goreng'
    ]
    
    return any(keyword in name_lower for keyword in chicken_keywords)
