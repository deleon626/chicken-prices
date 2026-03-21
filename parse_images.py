#!/usr/bin/env python3
"""
Parse product data from receipt/product images using OCR
"""
import sys
import re
from pathlib import Path

try:
    from PIL import Image
    import pytesseract
except ImportError as e:
    print(f"❌ Missing required packages: {e}")
    print("Install with: pip install pytesseract pillow tesseract-ocr")
    sys.exit(1)

def parse_image(img_path):
    """Extract product info from image"""
    img = Image.open(img_path)

    # OCR with Indonesian language support
    text = pytesseract.image_to_string(img, lang='eng+ind')

    # Extract prices (Rp followed by numbers)
    prices = re.findall(r'Rp[\d.,]+', text)

    # Clean price strings to numbers
    def clean_price(p):
        return float(p.replace('Rp', '').replace(',', '').strip())

    # Extract product name (first meaningful line)
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    product_name = "Unknown"
    for line in lines:
        # Skip lines that are just numbers or prices
        if line and not re.match(r'^[\d.,]+$', line) and 'Rp' not in line:
            product_name = line
            break

    # Extract sold count (look for "sold", "terjual", or patterns like "100+")
    sold_match = re.search(r'(?:sold|terjual|)[:\s]*([\d+,\+K]+)', text, re.IGNORECASE)
    sold_count = sold_match.group(1) if sold_match else None

    # Extract weight (look for kg, gr, grams)
    weight_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:kg|gr|gram)', text, re.IGNORECASE)
    weight = weight_match.group(0) if weight_match else None

    return {
        'product_name': product_name,
        'prices': prices,
        'clean_prices': [clean_price(p) for p in prices],
        'sold_count': sold_count,
        'weight': weight,
        'raw_text': text
    }

def main():
    image_files = [
        "/home/node/.openclaw/media/inbound/file_4---9a8337e5-4828-4b95-a133-644da8e95ac3.jpg",
        "/home/node/.openclaw/media/inbound/file_5---2654ced7-0665-4bef-904c-f9e81f9da0f3.jpg",
        "/home/node/.openclaw/media/inbound/file_6---b76f8abc-e549-4cb3-a887-8270a57ec04b.jpg",
        "/home/node/.openclaw/media/inbound/file_7---37736947-ed82-4ca8-aa18-653421f729e9.jpg",
        "/home/node/.openclaw/media/inbound/file_8---3a06effe-5bb8-4b11-b2bf-9d0afeb26e67.jpg",
        "/home/node/.openclaw/media/inbound/file_9---b52e1afe-02fe-4423-a08c-445464497f60.jpg",
        "/home/node/.openclaw/media/inbound/file_10---2d4c9431-a806-4e2a-bc03-629dd7dfe4e6.jpg",
        "/home/node/.openclaw/media/inbound/file_11---d4001869-003d-4230-afec-9b9825359a75.jpg"
    ]

    print("🔍 Parsing product images...")
    print("=" * 70)

    results = []
    for i, img_path in enumerate(image_files, 1):
        print(f"\n📸 Image {i}: {Path(img_path).name}")
        print("-" * 70)

        try:
            data = parse_image(img_path)
            results.append(data)

            print(f"Product: {data['product_name']}")
            print(f"Prices: {', '.join(data['prices'])}")
            if data['sold_count']:
                print(f"Sold: {data['sold_count']}")
            if data['weight']:
                print(f"Weight: {data['weight']}")
            print(f"\nDetected Text:\n{data['raw_text'][:300]}...")

        except Exception as e:
            print(f"❌ Error: {e}")

    print("\n" + "=" * 70)
    print("✅ Parsing complete!")
    print(f"\nFound {len(results)} images")

    # Export to CSV
    import pandas as pd
    csv_data = []
    for r in results:
        price = r['clean_prices'][0] if r['clean_prices'] else None
        csv_data.append({
            'product_name': r['product_name'],
            'current_price': price,
            'sold_count': r['sold_count'],
            'weight_kg': r['weight'],
            'prices_found': ', '.join(r['prices'])
        })

    df = pd.DataFrame(csv_data)
    output_path = Path(__file__).parent / "data" / "parsed_products.csv"
    df.to_csv(output_path, index=False)
    print(f"\n📄 CSV saved to: {output_path}")

if __name__ == "__main__":
    main()
