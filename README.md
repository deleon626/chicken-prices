# Sentral Ayam Shopee Store Analysis

A web scraping and analytics project for Sentral Ayam's Shopee store.

## Project Structure

```
sentralayam_analysis/
├── README.md
├── requirements.txt
├── scraper/
│   ├── __init__.py
│   ├── playwright_scraper.py    # Main scraping logic
│   └── utils.py                 # Helper functions
├── data/
│   └── raw_products.csv         # Scraped data (created after run)
├── app/
│   ├── __init__.py
│   └── streamlit_app.py         # Streamlit comparison dashboard
└── run.py                       # Entry point: python run.py
```

## Installation

### Prerequisites
- Python 3.8+
- System libraries for Playwright (libnspr4, libnss3, etc.)

### Option 1: With System Libraries (Full Scraping)
1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright Chromium:
```bash
playwright install chromium
```

3. Install system dependencies:
```bash
apt-get update && apt-get install -y libnspr4 libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libgbm1 libasound2 libatspi2.0-0
```

### Option 2: Without System Libraries (Sample Data Only)
If you're in a restricted container environment, you can still use the Streamlit app with the provided sample data.

## Usage

### Run the Scraper
```bash
python run.py
```
This will scrape the Sentral Ayam Shopee store and save data to `data/raw_products.csv`.
- Note: Shopee has strong anti-bot measures, so the scraper may be blocked
- Sample data is included in `data/raw_products.csv` for testing

### Run the Streamlit App
```bash
streamlit run app/streamlit_app.py
```
This opens the comparison dashboard in your browser at http://localhost:8501

### Customize Max Products
```bash
python run.py 50  # Scrape up to 50 products
```

## Features

- Scrapes Sentral Ayam Shopee store products
- Extracts: product name, current price, original price, sold count, product URL
- Handles anti-bot measures with delays and user-agent rotation
- Filters for chicken products
- Compares price per kg where possible
- Handles pagination
- Streamlit dashboard with price comparison charts and tables

## Notes

- The scraper uses headless Chromium with stealth options
- Random delays between actions to avoid detection
- Data is saved in CSV format for easy analysis
- Streamlit app provides interactive visualization

## Troubleshooting

### Browser Library Errors
If you see errors like `libnspr4.so: cannot open shared object file`, install system dependencies:
```bash
apt-get install -y libnspr4 libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libgbm1 libasound2 libatspi2.0-0
```

### Scraper Blocked
If Shopee blocks the scraper (403 errors, captchas):
- Increase delays in `scraper/playwright_scraper.py`
- Use a VPN or proxy
- Try different user agents in `scraper/utils.py`

### Data Not Found
If Streamlit shows "Data file not found":
- Make sure you've run the scraper first
- Check that `data/raw_products.csv` exists
- Sample data is included for testing
