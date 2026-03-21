#!/usr/bin/env python3
"""
Entry point for running Sentral Ayam scraper
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scraper.browser_scraper import BrowserShopeeScraper


async def main():
    """Main entry point"""
    print("=" * 60)
    print("🐔 Sentral Ayam Shopee Store Scraper (Browser-based)")
    print("=" * 60)
    print()
    
    # Get max products from command line or default to 50
    max_products = 10
    if len(sys.argv) > 1:
        try:
            max_products = int(sys.argv[1])
        except ValueError:
            print(f"Invalid argument: {sys.argv[1]}. Using default: 10")
    
    print(f"Configuration:")
    print(f"  - Max products to scrape: {max_products}")
    print(f"  - Output: data/raw_products.csv")
    print()
    print("Starting scraper...")
    print("-" * 60)
    
    # Create scraper and run
    scraper = BrowserShopeeScraper()
    await scraper.run(max_products=max_products)
    
    print("-" * 60)
    print("✅ Scraping completed!")
    print()
    print("Next steps:")
    print("  1. View data: cat data/raw_products.csv")
    print("  2. Run dashboard: streamlit run app/streamlit_app.py")
    print()


if __name__ == "__main__":
    asyncio.run(main())
