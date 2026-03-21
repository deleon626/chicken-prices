#!/usr/bin/env python3
"""
Parse product images using OCRSpace API (free OCR service)
"""
import sys
import base64
import requests
from pathlib import Path

# Free OCR API endpoint
OCR_API_URL = "https://api.ocr.space/parse/image"

def parse_image_with_api(img_path, api_key):
    """Use OCRSpace API to extract text"""
    try:
        # Convert image to base64
        with open(img_path, 'rb') as f:
            img_data = f.read()

        # Prepare payload
        payload = {
            'base64Image': base64.b64encode(img_data).decode(),
            'language': 'eng',  # English (Indonesian not supported on free tier)
            'isTable': 'false',
            'scale': 'true',
            'detectOrientation': 'true',
            'OCREngine': '2'  # OCR Engine 2 is more accurate
        }

        # Make request
        response = requests.post(
            OCR_API_URL,
            data=payload,
            headers={
                'apikey': api_key
            },
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            if result.get('IsErroredOnProcessing'):
                return None, result.get('ErrorMessage', 'Unknown error')
            return result.get('ParsedText'), None
        else:
            return None, f"HTTP {response.status_code}: {response.text}"

    except Exception as e:
        return None, str(e)

def main():
    # Get API key from user or use demo key
    api_key = sys.argv[1] if len(sys.argv) > 1 else "helloworld"

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

    print("🔍 Parsing product images with OCRSpace API...")
    print("=" * 70)

    results = []
    for i, img_path in enumerate(image_files, 1):
        print(f"\n📸 Image {i}: {Path(img_path).name}")
        print("-" * 70)

        text, error = parse_image_with_api(img_path, api_key)

        if error:
            print(f"❌ Error: {error}")
            continue

        print(f"✅ OCR Successful!")
        print(f"\n📄 Extracted Text:")
        print(text)

        results.append({
            'image': Path(img_path).name,
            'text': text
        })

    print("\n" + "=" * 70)
    print(f"✅ Successfully parsed {len(results)}/{len(image_files)} images")

    # Save results
    import json
    output_path = Path(__file__).parent / "data" / "ocr_results.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"📄 Results saved to: {output_path}")

if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════╗
║  OCRSpace API - Free Online OCR Service                       ║
╚═══════════════════════════════════════════════════════════╝

Usage:
  python3 parse_with_api.py [your_api_key]

Get your free API key:
  1. Go to https://ocr.space/ocrapi
  2. Register for free account
  3. Copy your API key
  4. Run: python3 parse_with_api.py YOUR_API_KEY

Or run with demo key (limited):
  python3 parse_with_api.py helloworld

""")

    main()
