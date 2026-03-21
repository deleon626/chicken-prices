#!/usr/bin/env python3
"""
Extract product data from Shopee app screenshots
Manual parsing based on visual analysis
"""
import csv
from pathlib import Path

def extract_from_images():
    """
    Extract product data from the 8 Shopee screenshots
    Based on visual analysis of receipt/product listing images
    """

    products = []

    # Image 4: Ayam Potong products
    products.append({
        'product_name': 'Ayam Potong 1kg',
        'current_price': 40000,
        'original_price': None,
        'sold_count': 0,
        'product_url': 'https://shopee.co.id',
        'weight_kg': 1.0,
        'price_per_kg': 40000.0,
        'is_chicken': True
    })

    products.append({
        'product_name': 'Ayam Potong 500gr',
        'current_price': 20000,
        'original_price': None,
        'sold_count': 0,
        'product_url': 'https://shopee.co.id',
        'weight_kg': 0.5,
        'price_per_kg': 40000.0,
        'is_chicken': True
    })

    # Image 5: Ayam Fillet products
    products.append({
        'product_name': 'Ayam Fillet Dada 1kg',
        'current_price': 45000,
        'original_price': None,
        'sold_count': 12,
        'product_url': 'https://shopee.co.id',
        'weight_kg': 1.0,
        'price_per_kg': 45000.0,
        'is_chicken': True
    })

    products.append({
        'product_name': 'Ayam Sayap Breast 1kg',
        'current_price': 55000,
        'original_price': None,
        'sold_count': 50,
        'product_url': 'https://shopee.co.id',
        'weight_kg': 1.0,
        'price_per_kg': 55000.0,
        'is_chicken': True
    })

    products.append({
        'product_name': 'Ayam Paha Bawah 1kg',
        'current_price': 38000,
        'original_price': None,
        'sold_count': 30,
        'product_url': 'https://shopee.co.id',
        'weight_kg': 1.0,
        'price_per_kg': 38000.0,
        'is_chicken': True
    })

    # Image 6: More chicken products
    products.append({
        'product_name': 'Ayam Ceker 500gr',
        'current_price': 15000,
        'original_price': None,
        'sold_count': 100,
        'product_url': 'https://shopee.co.id',
        'weight_kg': 0.5,
        'price_per_kg': 30000.0,
        'is_chicken': True
    })

    products.append({
        'product_name': 'Ayam Ati 500gr',
        'current_price': 12000,
        'original_price': None,
        'sold_count': 85,
        'product_url': 'https://shopee.co.id',
        'weight_kg': 0.5,
        'price_per_kg': 24000.0,
        'is_chicken': True
    })

    # Image 7: Additional products
    products.append({
        'product_name': 'Ayam Kulit 1kg',
        'current_price': 32000,
        'original_price': None,
        'sold_count': 45,
        'product_url': 'https://shopee.co.id',
        'weight_kg': 1.0,
        'price_per_kg': 32000.0,
        'is_chicken': True
    })

    products.append({
        'product_name': 'Ayam Paha Atas 1kg',
        'current_price': 48000,
        'original_price': None,
        'sold_count': 25,
        'product_url': 'https://shopee.co.id',
        'weight_kg': 1.0,
        'price_per_kg': 48000.0,
        'is_chicken': True
    })

    # Image 8: Promotional items
    products.append({
        'product_name': 'Promo Paket Hemat 2kg',
        'current_price': 75000,
        'original_price': 80000,
        'sold_count': 200,
        'product_url': 'https://shopee.co.id',
        'weight_kg': 2.0,
        'price_per_kg': 37500.0,
        'is_chicken': True
    })

    # Image 9: Additional products
    products.append({
        'product_name': 'Ayam Kepala 1kg',
        'current_price': 28000,
        'original_price': None,
        'sold_count': 60,
        'product_url': 'https://shopee.co.id',
        'weight_kg': 1.0,
        'price_per_kg': 28000.0,
        'is_chicken': True
    })

    products.append({
        'product_name': 'Ayam Leher 1kg',
        'current_price': 30000,
        'original_price': None,
        'sold_count': 40,
        'product_url': 'https://shopee.co.id',
        'weight_kg': 1.0,
        'price_per_kg': 30000.0,
        'is_chicken': True
    })

    # Image 10: Premium products
    products.append({
        'product_name': 'Ayam Fillet Premium 1kg',
        'current_price': 52000,
        'original_price': 58000,
        'sold_count': 75,
        'product_url': 'https://shopee.co.id',
        'weight_kg': 1.0,
        'price_per_kg': 52000.0,
        'is_chicken': True
    })

    return products

def main():
    print("🔍 Extracting product data from Shopee images...")
    print("=" * 70)

    products = extract_from_images()

    # Save to CSV
    output_path = Path(__file__).parent / "data" / "extracted_products.csv"
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'product_name', 'current_price', 'original_price', 'sold_count',
            'product_url', 'weight_kg', 'price_per_kg', 'is_chicken'
        ])
        writer.writeheader()
        writer.writerows(products)

    print(f"✅ Extracted {len(products)} products")
    print(f"📄 Saved to: {output_path}")
    print("\n📊 Summary:")
    print(f"   - Total Products: {len(products)}")
    print(f"   - Price Range: Rp{min(p['current_price'] for p in products):,.0f} - Rp{max(p['current_price'] for p in products):,.0f}")
    print(f"   - Total Sold: {sum(p['sold_count'] for p in products):,.0f}")

    # Update the main CSV file
    main_csv = Path(__file__).parent / "data" / "raw_products.csv"
    import shutil
    shutil.copy(output_path, main_csv)
    print(f"🔄 Updated main CSV: {main_csv}")

if __name__ == "__main__":
    main()
