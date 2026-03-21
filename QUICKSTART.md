# Quick Start Guide

## Prerequisites
- Python 3.8+
- System libraries for Playwright (for full scraping)

## Installation Options

### Option 1: Full Installation (With Scraping)
```bash
cd /home/node/.openclaw/workspace/sentralayam_analysis

# Install Python packages
pip install -r requirements.txt

# Install Playwright Chromium
playwright install chromium

# Install system dependencies (Linux)
apt-get update && apt-get install -y \
    libnspr4 libnss3 libatk-bridge2.0-0 libdrm2 \
    libxkbcommon0 libgbm1 libasound2 libatspi2.0-0
```

### Option 2: Sample Data Only (No System Dependencies)
```bash
# Streamlit app works with included sample data
pip install streamlit pandas plotly python-dotenv
```

## Running the Application

### 1. Test the Scraper
```bash
# Scrape up to 50 products
python run.py

# Custom limit
python run.py 100
```

### 2. Run the Dashboard
```bash
# Launch Streamlit app
streamlit run app/streamlit_app.py

# The app opens at http://localhost:8501
```

## Project Structure

```
sentralayam_analysis/
├── scraper/
│   ├── __init__.py              # Module init
│   ├── playwright_scraper.py    # Main scraper (285 lines)
│   └── utils.py                 # Helper functions (125 lines)
├── app/
│   ├── __init__.py              # Module init
│   └── streamlit_app.py         # Dashboard (290 lines)
├── data/
│   └── raw_products.csv         # Scraped data
├── run.py                       # Entry point (52 lines)
├── requirements.txt             # Dependencies
└── README.md                    # Full documentation
```

## Key Features

### Scraper (`scraper/playwright_scraper.py`)
- **Anti-bot measures**: Random user agents, delays, stealth scripts
- **Data extraction**: Name, price, original price, sold count, URL
- **Smart filtering**: Chicken product detection
- **Price analysis**: Weight extraction and price/kg calculation
- **Pagination**: Handles multiple pages

### Dashboard (`app/streamlit_app.py`)
- **Interactive filters**: Price, weight, sold count ranges
- **Key metrics**: Total products, avg price, total sold, discount rate
- **4 tabs**:
  1. Product Table - Sortable list with prices
  2. Price Analysis - Histograms and scatter plots
  3. Price per Kg - Value comparison (lower is better)
  4. Links - Direct Shopee product links

### Utilities (`scraper/utils.py`)
- **Price parsing**: Handles "Rp50.000", "Rp 100.000", etc.
- **Sold count**: Parses "10RB Terjual", "500 Terjual", "1RB+"
- **Weight extraction**: Detects "1kg", "500gr", "0.5 kg"
- **Price per kg**: Automatic calculation
- **Chicken detection**: Keyword-based filtering

## Troubleshooting

### "libnspr4.so: cannot open shared object file"
Install system dependencies:
```bash
apt-get install -y libnspr4 libnss3 libatk-bridge2.0-0 libdrm2 \
    libxkbcommon0 libgbm1 libasound2 libatspi2.0-0
```

### Scraper blocked (403, captcha)
- Increase delays in `scraper/playwright_scraper.py`
- Modify user agents in `scraper/utils.py`
- Use VPN/proxy if available

### Streamlit shows "Data file not found"
Run the scraper first:
```bash
python run.py
```

Sample data is included in `data/raw_products.csv` for testing.

## Sample Data

The project includes sample data with 20 chicken products:
- Fresh chicken (1kg)
- Fillet cuts (500gr)
- Wings, legs, drumsticks
- Pre-cooked options (fried, grilled, curry)
- Price range: Rp12,000 - Rp68,000

## Next Steps

1. Run the scraper to get real data from Sentral Ayam store
2. Explore the Streamlit dashboard features
3. Customize filters and charts in `app/streamlit_app.py`
4. Add more products to scrape by increasing the limit
5. Implement proxy rotation for better anti-bot protection

## Code Statistics

- **Total lines of code**: ~858 lines
- **Scraper**: 410 lines (playwright_scraper + utils)
- **Dashboard**: 290 lines
- **Entry point**: 52 lines
- **Documentation**: 104 lines (README)
