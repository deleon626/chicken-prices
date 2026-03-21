#!/usr/bin/env python3
"""
Browser-based scraper for Sentral Ayam Shopee store
Uses OpenClaw browser tool to bypass JS rendering issues
"""
import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Optional

sys.path.insert(0, str(Path(__file__).parent))

from .utils import (
    extract_price,
    extract_sold_count,
    extract_weight,
    calculate_price_per_kg,
    is_chicken_product,
    random_delay
)


class BrowserShopeeScraper:
    """Browser scraper using OpenClaw browser tool"""
    
    BASE_URL = "https://shopee.co.id/shop"
    SHOP_NAME = "sentralayam"
    SHOP_URL = f"{BASE_URL}/{SHOP_NAME}"
    
    def __init__(self, output_path: str = None):
        self.output_path = output_path or Path(__file__).parent.parent / "data" / "raw_products.csv"
        self.products: List[Dict] = []
    
    def scrape_products(self, max_products: int = 50):
        """Scrape products from Shopee store using browser tool"""
        print(f"Navigating to {self.SHOP_URL}...")
        
        try:
            # Navigate to shop
            from openclaw_toolkit import browser
            await browser.start(profile="chrome")
            
            # Navigate to shop URL
            print(f"Navigating to {self.SHOP_URL}...")
            await browser.navigate(self.SHOP_URL)
            
            # Wait for page to load
            await asyncio.sleep(random_delay(2, 3))
            
            # Scroll to load more products (if needed)
            for _ in range(3):
                # Execute JavaScript to scroll
                await browser.evaluate("""
                    window.scrollTo(0, document.body.scrollHeight);
                """)
                await asyncio.sleep(random_delay(0.5, 1))
            
            # Take snapshot to get page HTML
            snapshot = await browser.snapshot(mode="markdown")
            print(f"Page snapshot size: {len(snapshot)} bytes")
            
            # Parse products from snapshot
            if snapshot:
                products = self.parse_snapshot(snapshot, max_products=max_products)
            
            # Save to CSV
            self.save_to_csv()
            
            # Close browser
            await browser.close()
        
        except Exception as e:
            print(f"Error during scraping: {e}")
    
    def parse_snapshot(self, snapshot: str, max_products: int) -> List[Dict]:
        """Parse product data from page snapshot"""
        products = []
        
        # Simple regex patterns for product data
        # Product cards are typically in divs with specific class names
        # Try to find products by looking for patterns in text
        
        lines = snapshot.split('\n')
        current_product = None
        product_count = 0
        
        for line in lines:
            line = line.strip()
            
            # Skip non-product lines
            if not line or line.startswith('```') or line.startswith('|') or line.startswith('>'):
                continue
            
            # Try to identify product entries
            # Look for patterns that indicate a product:
            # - Contains currency (Rp) or price numbers
            # - Contains product-like text (Ayam, Potong, Fillet, etc.)
            
            if 'Ayam' in line or 'Potong' in line or 'Fillet' in line or 'Daging' in line or 'Ceker' in line or 'Paha' in line or 'Sayap' in line or 'Jeroan' in line or 'Pejantan' in line or 'Kepala' in line or 'Kepala' in line or 'Cincin' in line or 'Pop' in line:
                if current_product is None:
                    current_product = {'product_name': line, 'current_price': 0, 'original_price': None, 'sold_count': 0, 'product_url': None, 'weight_kg': 0, 'price_per_kg': 0, 'is_chicken': False}
                else:
                    # This looks like a new product entry
                    current_product['product_name'] = line
            
            # Check if this line contains price information
            if 'Rp' in line or line.count('000') >= 3:
                # Try to extract price
                import re
                price_match = re.search(r'Rp\s*([\d.,]+)', line)
                if price_match:
                    try:
                        price = float(price_match.group(1).replace('.', '').replace(',', ''))
                        if current_product:
                            current_product['current_price'] = price
                    except:
                        pass
            
            # Check for sold count indicators
            if 'Terjual' in line or ('RB' in line) or ('rb' in line.lower()):
                # Try to extract sold count
                import re
                sold_match = re.search(r'([\d.,]+)(?:RB|rb)?\s*Terjual', line)
                if sold_match:
                    try:
                        sold = int(sold_match.group(1).replace('.', '').replace(',', ''))
                        if current_product:
                            current_product['sold_count'] = sold
                    except:
                        pass
            
            # Check for weight indicators (kg, gr)
            if 'kg' in line.lower() or 'gr' in line.lower():
                # Try to extract weight
                import re
                weight_match = re.search(r'([\d.,]+)(?:kg|gram|gr)', line)
                if weight_match:
                    try:
                        weight = float(weight_match.group(1).replace('.', '').replace(',', ''))
                        # Convert to kg
                        if 'gr' in line.lower() and weight > 0:
                            weight = weight / 1000.0  # grams to kg
                        if current_product:
                            current_product['weight_kg'] = weight
                            current_product['price_per_kg'] = current_product['current_price'] / weight if weight > 0 and current_product['current_price'] > 0 else 0
                    except:
                        pass
            
            # Check if this is a complete product entry
            if current_product and current_product.get('product_name'):
                if current_product['product_name'] in line or 'Ayam' in line or 'Potong' in line:
                    # Valid product name found
                    products.append(current_product)
                    product_count += 1
                    current_product = None
                    print(f"  [{product_count}] {current_product['product_name']} - Rp{current_product.get('current_price', 0):,.0f}")
                else:
                    # This line doesn't look like product data
                    if current_product:
                        current_product = None
        
        # Limit to max_products
        if product_count >= max_products:
            break
        
        return products
    
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
        print("🐔 Sentral Ayam Shopee Store Scraper (Browser-based)")
        print("=" * 60)
        print()
        
        # Check if browser tool is available
        try:
            from openclaw_toolkit import browser
            print("✅ OpenClaw browser tool detected")
        except ImportError:
            print("❌ OpenClaw browser tool not available")
            print("Note: This scraper requires browser tool. Please ensure OpenClaw Gateway is running with browser enabled.")
            return
        
        print(f"Configuration:")
        print(f"  - Max products to scrape: {max_products}")
        print(f"  - Output: data/raw_products.csv")
        print()
        print("Starting scraper...")
        print("-" * 60)
        
        # Run async scrape
        asyncio.run(self.scrape_products(max_products=max_products))
        
        print("-" * 60)
        print("✅ Scraping completed!")
        print()
        print("Next steps:")
        print("  1. View data: cat data/raw_products.csv")
        print("  2. Run dashboard: streamlit run app/streamlit_app.py")
        print()


def main():
    """Main entry point"""
    scraper = BrowserShopeeScraper()
    scraper.run(max_products=10)


if __name__ == "__main__":
    main()
