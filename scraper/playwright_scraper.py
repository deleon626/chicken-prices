"""
Playwright-based scraper for Sentral Ayam Shopee store
"""
import asyncio
import csv
import random
from pathlib import Path
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from .utils import (
    get_random_user_agent,
    random_delay,
    extract_price,
    extract_sold_count,
    extract_weight,
    calculate_price_per_kg,
    is_chicken_product
)

class SentralAyamScraper:
    """Scraper for Sentral Ayam Shopee store"""
    
    BASE_URL = "https://shopee.co.id/shop"
    SHOP_NAME = "sentralayam"
    SHOP_URL = f"{BASE_URL}/{SHOP_NAME}"
    
    def __init__(self, output_path: str = None):
        self.output_path = output_path or Path(__file__).parent.parent / "data" / "raw_products.csv"
        self.products: List[Dict] = []
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        # Ensure data directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
    
    async def init_browser(self):
        """Initialize browser with stealth settings"""
        playwright = await async_playwright().start()
        
        # Launch browser with anti-detection settings
        self.browser = await playwright.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
            ]
        )
        
        # Create context with realistic user agent
        self.context = await self.browser.new_context(
            user_agent=get_random_user_agent(),
            viewport={'width': 1920, 'height': 1080},
            locale='id-ID',
            timezone_id='Asia/Jakarta',
        )
        
        # Add stealth scripts
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['id-ID', 'id', 'en-US', 'en']
            });
        """)
        
        self.page = await self.context.new_page()
        
        # Set default timeout
        self.page.set_default_timeout(30000)
    
    async def close_browser(self):
        """Close browser and cleanup"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
    
    async def navigate_to_shop(self):
        """Navigate to the Sentral Ayam shop page"""
        print(f"Navigating to {self.SHOP_URL}...")
        
        await self.page.goto(self.SHOP_URL, wait_until='networkidle')
        await asyncio.sleep(random_delay(2, 4))
        
        # Wait for shop to load
        await self.page.wait_for_selector('[class*="shop-product"]', timeout=15000)
        
        print("Shop page loaded successfully")
    
    async def extract_product_data(self, product_element) -> Optional[Dict]:
        """Extract product data from a product element"""
        try:
            # Product name
            name_elem = await product_element.query_selector('[class*="item-card"]')
            if not name_elem:
                name_elem = await product_element.query_selector('a[class*="product-item"]')
            
            name = None
            if name_elem:
                name = await name_elem.inner_text()
                name = name.strip()
            
            # Product URL
            url_elem = await product_element.query_selector('a')
            url = None
            if url_elem:
                url = await url_elem.get_attribute('href')
                if url and not url.startswith('http'):
                    url = 'https://shopee.co.id' + url
            
            # Current price
            price_elem = await product_element.query_selector('[class*="price"]')
            current_price = None
            if price_elem:
                price_text = await price_elem.inner_text()
                current_price = extract_price(price_text)
            
            # Original price (if discounted)
            original_price_elem = await product_element.query_selector('[class*="original"]')
            original_price = None
            if original_price_elem:
                orig_price_text = await original_price_elem.inner_text()
                original_price = extract_price(orig_price_text)
            
            # Sold count
            sold_elem = await product_element.query_selector('[class*="sold"]')
            sold_count = None
            if sold_elem:
                sold_text = await sold_elem.inner_text()
                sold_count = extract_sold_count(sold_text)
            
            # Extract weight if available
            weight_kg = extract_weight(name) if name else None
            
            # Calculate price per kg
            price_per_kg = calculate_price_per_kg(current_price, weight_kg) if current_price and weight_kg else None
            
            # Check if it's a chicken product
            is_chicken = is_chicken_product(name) if name else True
            
            return {
                'product_name': name,
                'current_price': current_price,
                'original_price': original_price,
                'sold_count': sold_count,
                'product_url': url,
                'weight_kg': weight_kg,
                'price_per_kg': price_per_kg,
                'is_chicken': is_chicken
            }
            
        except Exception as e:
            print(f"Error extracting product data: {e}")
            return None
    
    async def scrape_products(self, max_products: int = 50):
        """
        Scrape all products from the shop
        max_products: Maximum number of products to scrape (default 50)
        """
        print("Starting to scrape products...")
        
        await self.navigate_to_shop()
        
        scraped_count = 0
        page_num = 1
        
        while scraped_count < max_products:
            print(f"\nScraping page {page_num}...")
            
            # Wait for products to load
            await asyncio.sleep(random_delay(2, 3))
            
            # Find all product elements
            # Try multiple selectors for product cards
            products = await self.page.query_selector_all('[class*="item-card"]')
            if not products:
                products = await self.page.query_selector_all('[class*="product-item"]')
            if not products:
                products = await self.page.query_selector_all('.shop-search-result-view__item')
            
            if not products:
                print("No products found on this page")
                break
            
            print(f"Found {len(products)} product(s) on page {page_num}")
            
            # Extract data from each product
            for i, product in enumerate(products):
                if scraped_count >= max_products:
                    break
                
                product_data = await self.extract_product_data(product)
                
                if product_data and product_data['product_name']:
                    # Filter for chicken products
                    if product_data['is_chicken']:
                        self.products.append(product_data)
                        scraped_count += 1
                        print(f"  [{scraped_count}] {product_data['product_name']} - Rp{product_data['current_price']:,.0f}")
                    else:
                        print(f"  [SKIP] Not a chicken product: {product_data['product_name']}")
                
                # Small delay between each product
                await asyncio.sleep(random_delay(0.3, 0.8))
            
            # Try to find next page button
            if scraped_count >= max_products:
                break
            
            try:
                next_button = await self.page.query_selector('button[aria-label="Next Page"]')
                if not next_button:
                    next_button = await self.page.query_selector('button[class*="next"]')
                
                if next_button:
                    is_disabled = await next_button.is_disabled()
                    if is_disabled:
                        print("Reached last page")
                        break
                    
                    # Click next page
                    await next_button.click()
                    await asyncio.sleep(random_delay(2, 4))
                    page_num += 1
                else:
                    print("No next page button found")
                    break
                    
            except Exception as e:
                print(f"Error navigating to next page: {e}")
                break
        
        print(f"\nScraping complete! Total products scraped: {len(self.products)}")
    
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
    
    async def run(self, max_products: int = 50):
        """Main run method"""
        try:
            await self.init_browser()
            await self.scrape_products(max_products=max_products)
            self.save_to_csv()
        finally:
            await self.close_browser()


async def main():
    """Main entry point for async execution"""
    scraper = SentralAyamScraper()
    await scraper.run(max_products=50)


if __name__ == "__main__":
    asyncio.run(main())
