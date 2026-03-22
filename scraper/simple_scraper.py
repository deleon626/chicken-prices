"""
Simple Shopee scraper using requests + BeautifulSoup
This avoids extra dependencies and works better for JS-rendered sites
"""
import csv
import re
import time
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from typing import List, Dict
from .utils import (
    extract_price,
    extract_sold_count,
    extract_weight,
    calculate_price_per_kg,
    is_chicken_product,
    random_delay
)


class SimpleShopeeScraper:
    """Simple scraper for Sentral Ayam Shopee store"""
    
    BASE_URL = "https://shopee.co.id/shop"
    SHOP_NAME = "sentralayam"
    SHOP_URL = f"{BASE_URL}/{SHOP_NAME}"
    
    def __init__(self, output_path: str = None):
        self.output_path = output_path or Path(__file__).parent.parent / "data" / "raw_products.csv"
        self.products: List[Dict] = []
        
        # Headers to mimic browser
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Ensure data directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
    
    def scrape_products(self, max_products: int = 50):
        """Scrape products from Shopee store"""
        print(f"Fetching {self.SHOP_URL}...")
        
        try:
            response = self.session.get(self.SHOP_URL, timeout=30)
            response.raise_for_status()
            print(f"Response status: {response.status_code}")
            print(f"Page size: {len(response.text)} bytes")
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find product cards (try multiple selectors)
            product_cards = []
            
            selectors = [
                '.shopee-search-item-result__item',
                '.shop-search-result-view__item',
                '[class*="item-card"]',
                '[class*="product-item"]'
            ]
            
            for selector in selectors:
                cards = soup.select(selector)
                if cards:
                    print(f"Found {len(cards)} products with selector: {selector}")
                    product_cards.extend(cards)
                    break
            
            if not product_cards:
                print("No products found. This site may require JavaScript to render products.")
            
            # Parse products from cards
            for i, card in enumerate(product_cards):
                if i >= max_products:
                    break
                
                product_data = self.parse_product_card(card)
                
                if product_data and product_data['product_name']:
                    # Filter for chicken products
                    if product_data['is_chicken']:
                        self.products.append(product_data)
                        print(f"  [{len(self.products)}] {product_data['product_name']} - Rp{product_data['current_price']:,.0f}")
                    else:
                        print(f"  [SKIP] Not a chicken product: {product_data['product_name']}")
                
                # Small delay between requests
                time.sleep(random_delay(0.2, 0.5))
        
        except Exception as e:
            print(f"Error scraping: {e}")
        
        print(f"\nScraping complete! Total products: {len(self.products)}")
        return len(self.products)
    
    def parse_product_card(self, card) -> Optional[Dict]:
        """Parse product data from a product card element"""
        try:
            # Product name
            name_elem = card.find(['h3', 'h4', 'div'], class_=re.compile(r'name|title', re.I))
            name = name_elem.get_text(strip=True) if name_elem else None
            
            # Product URL (from link elements)
            link_elem = card.find('a', href=True)
            url = None
            if link_elem:
                url = f"https://shopee.co.id{link_elem['href']}" if link_elem['href'].startswith('/') else link_elem['href']
            
            # Current price
            price = None
            for price_class in ['price', 'current-price', 'product-price']:
                price_elem = card.find(class_=re.compile(price_class, re.I))
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    price = extract_price(price_text)
                    if price:
                        break
            
            # Sold count
            sold = None
            for sold_class in ['sold', 'sold-count', 'items-sold']:
                sold_elem = card.find(class_=re.compile(sold_class, re.I))
                if sold_elem:
                    sold_text = sold_elem.get_text(strip=True)
                    sold = extract_sold_count(sold_text)
                    if sold:
                        break
            
            # Extract weight
            weight_kg = extract_weight(name) if name else None
            
            # Calculate price per kg
            price_per_kg = calculate_price_per_kg(price, weight_kg) if price and weight_kg else None
            
            # Check if chicken
            is_chicken = is_chicken_product(name) if name else True
            
            return {
                'product_name': name,
                'current_price': price,
                'original_price': None,
                'sold_count': sold,
                'product_url': url,
                'weight_kg': weight_kg,
                'price_per_kg': price_per_kg,
                'is_chicken': is_chicken
            }
        except Exception as e:
            print(f"Error parsing product card: {e}")
            return None
    
    def save_to_csv(self):
        """Save scraped products to CSV file"""
        if not self.products:
            print("No products to save")
            return
        
        with open(self.output_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'product_name',
                'current_price',
                'original_price',
                'sold_count',
                'product_url',
                'weight_kg',
                'price_per_kg',
                'is_chicken'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.products)
        
        print(f"Data saved to {self.output_path}")
    
    def run(self, max_products: int = 50):
        """Main run method"""
        print("=" * 60)
        print("🐔 Sentral Ayam Shopee Store Scraper (Simple - requests)")
        print("=" * 60)
        print()
        
        # Create scraper and run
        scraper = SimpleShopeeScraper()
        count = scraper.run(max_products=max_products)
        
        print("-" * 60)
        print("✅ Scraping completed!")
        print()
        print(f"Total products found: {count}")
        print()
        print("Next steps:")
        print("  1. View data: cat data/raw_products.csv")
        print("  2. Run dashboard: streamlit run app/streamlit_app.py")
        print()


def main():
    """Main entry point"""
    scraper = SimpleShopeeScraper()
    scraper.run(max_products=10)


if __name__ == "__main__":
    main()
