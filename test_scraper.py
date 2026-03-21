#!/usr/bin/env python3
"""Test script for simple scraper"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from scraper.simple_scraper import SimpleShopeeScraper

scraper = SimpleShopeeScraper()
count = scraper.run(max_products=3)
print(f"Total products found: {count}")
