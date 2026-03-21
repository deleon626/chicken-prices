"""
Selenium-based scraper for Sentral Ayam Shopee store
Uses real Chrome browser to bypass JS rendering issues
"""
import csv
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from pathlib import Path
from typing import List, Dict, Optional
from .utils import (
    extract_price,
    extract_sold_count,
    extract_weight,
    calculate_price_per_kg,
    is_chicken_product,
    random_delay
)


class SeleniumShopeeScraper:
    """Selenium scraper for Sentral Ayam Shopee store"""
    
    BASE_URL = "https://shopee.co.id/shop"
    SHOP_NAME = "sentralayam"
    SHOP_URL = f"{BASE_URL}/{SHOP_NAME}"
    
    def __init__(self, output_path: str = None, headless: bool = True):
        self.output_path = output_path or Path(__file__).parent.parent / "data" / "raw_products.csv"
        self.products: List[Dict] = []
        self.headless = headless
        
        # Set up Chrome options
        self.chrome_options = Options()
        if headless:
            self.chrome_options.add_argument("--headless")
            self.chrome_options.add_argument("--no-sandbox")
            self.chrome_options.add_argument("--disable-dev-shm-usage")
            self.chrome_options.add_argument("--disable-gpu")
            self.chrome_options.add_argument("--window-size=1920,1080")
        
        # Ensure data directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
    
    def init_driver(self):
        """Initialize Chrome driver"""
        # Try to use chromedriver-auto, otherwise fall back to standard ChromeDriver
        try:
            service = Service(executable_path='/usr/bin/chromedriver')
            driver = webdriver.Chrome(service=service, options=self.chrome_options)
            print("✅ Chrome driver initialized successfully")
            return driver
        except Exception as e:
            print(f"⚠️  Error initializing Chrome driver: {e}")
            # Try without service (may use system chromedriver)
            try:
                driver = webdriver.Chrome(options=self.chrome_options)
                print("✅ Chrome driver initialized (fallback mode)")
                return driver
            except Exception as e2:
                print(f"❌ Failed to initialize Chrome driver: {e2}")
                raise
    
    def scrape_products(self, driver, max_products: int = 50):
        """Scrape products from Shopee store using Selenium"""
        print(f"Navigating to {self.SHOP_URL}...")
        
        try:
            driver.get(self.SHOP_URL, timeout=30)
            
            # Wait for page to load
            time.sleep(random_delay(3, 5))
            
            # Try to scroll to load all products (infinite scroll)
            for _ in range(3):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random_delay(1, 2))
            
            # Get page source after scrolling
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Find product cards (try multiple selectors)
            product_cards = []
            
            selectors = [
                '.shopee-search-item-result__item',
                '.shop-search-result-view__item',
                '[class*="item-card"]',
                '[class*="product-item"]',
                'div[class*="shop-search-result-view__item"]',
                'div[class*="product-item"]'
            ]
            
            for selector in selectors:
                cards = soup.select(selector)
                if cards:
                    print(f"Found {len(cards)} products with selector: {selector}")
                    product_cards.extend(cards)
                    break
            
            if not product_cards:
                print("No products found with standard selectors")
                # Try to find any elements that look like products
                print("Looking for any product-related elements...")
                
                # Look for links that match product pattern
                all_links = soup.find_all('a', href=True)
                product_links = [a for a in all_links if '/product/' in a.get('href', '')]
                
                print(f"Found {len(product_links)} potential product links")
                
                # Visit first few product pages directly
                scraped_count = 0
                for i, link in enumerate(product_links[:min(max_products, 10)]):
                    if scraped_count >= max_products:
                        break
                    
                    try:
                        print(f"Visiting product {i+1}: {link.get('href', '')}")
                        driver.get(link['href'], timeout=20)
                        time.sleep(random_delay(2, 3))
                        
                        product_page_source = driver.page_source
                        product_soup = BeautifulSoup(product_page_source, 'html.parser')
                        
                        # Try to extract product data from this page
                        product_data = self.parse_product_page(product_soup)
                        
                        if product_data:
                            self.products.append(product_data)
                            scraped_count += 1
                            print(f"  [{scraped_count}] {product_data['product_name']} - Rp{product_data['current_price']:,.0f}")
                        else:
                            print(f"  [SKIP] No product data found")
                    
                        # Go back to shop page
                        driver.back()
                        time.sleep(random_delay(1, 2))
                        
                    except Exception as e:
                        print(f"Error visiting product {i+1}: {e}")
                        continue
            
        except Exception as e:
            print(f"Error during scraping: {e}")
        
        print(f"\nScraping complete! Total products scraped: {len(self.products)}")
    
    def parse_product_page(self, soup) -> Optional[Dict]:
        """Parse product data from a product page"""
        try:
            # Product name
            name_elem = soup.find(['h1', 'h2', 'h3', 'h4', 'div'], class_=lambda x: x and 'name' in str(x).lower())
            name = name_elem.get_text(strip=True) if name_elem else None
            
            # Price
            price = None
            for price_class in ['price', 'current-price', 'product-price', 'shopee-price']:
                price_elem = soup.find(class_=lambda x: price_class in str(x).lower())
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    price = extract_price(price_text)
                    if price:
                        break
            
            # Product URL (from current page if different)
            url = None
            link_elem = soup.find('a', href=True)
            if link_elem:
                url = link_elem.get('href')
                if url and not url.startswith('http'):
                    url = 'https://shopee.co.id' + url
            
            # Sold count
            sold = None
            for sold_class in ['sold', 'sold-count', 'items-sold', 'shopee-sold']:
                sold_elem = soup.find(class_=lambda x: sold_class in str(x).lower())
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
            print(f"Error parsing product page: {e}")
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
                "weight_kg",
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
        print("🐔 Sentral Ayam Shopee Store Scraper (Selenium)")
        print("=" * 60)
        print()
        
        driver = None
        try:
            driver = self.init_driver()
            
            try:
                self.scrape_products(driver, max_products=max_products)
            finally:
                driver.quit()
            
            self.save_to_csv()
            
        finally:
            if driver:
                driver.quit()
        
        print("-" * 60)
        print("✅ Scraping completed!")
        print()
        print("Next steps:")
        print("  1. View data: cat data/raw_products.csv")
        print("  2. Run dashboard: streamlit run app/streamlit_app.py")
        print()


def main():
    """Main entry point"""
    scraper = SeleniumShopeeScraper(headless=True)
    scraper.run(max_products=32)


if __name__ == "__main__":
    main()
