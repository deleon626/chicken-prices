# Sentral Ayam Analysis Project

## 📁 Project Structure

```
sentralayam_analysis/
├── README.md
├── requirements.txt
├── scraper/
│   ├── __init__.py
│   ├── utils.py
│   ├── playwright_scraper.py
│   ├── simple_scraper.py
│   ├── selenium_scraper.py
│   └── browser_scraper.py
├── data/
│   └── raw_products.csv
├── app/
│   ├── __init__.py
│   └── streamlit_app.py
├── run.py
└── test_scraper.py
```

## 📄 Files Created

| File | Status | Description |
|------|--------|-------------|
| `README.md` | ✅ | Project documentation |
| `requirements.txt` | ✅ | Python dependencies (playwright, streamlit, pandas, plotly) |
| `scraper/utils.py` | ✅ | Helper functions (price, sold, weight parsing) |
| `scraper/playwright_scraper.py` | ✅ | Full Playwright scraper (blocked by missing system libs) |
| `scraper/simple_scraper.py` | ✅ | Simple requests scraper (JS-rendered site limitation) |
| `scraper/selenium_scraper.py` | ✅ | Selenium scraper (Chrome not available in container) |
| `scraper/browser_scraper.py` | ⚠️ | Browser tool scraper (complex, syntax issues with async) |
| `app/streamlit_app.py` | ✅ | Streamlit dashboard with charts and filters |
| `app/__init__.py` | ✅ | App module |
| `run.py` | ✅ | Entry point (updated for browser scraper) |
| `data/raw_products.csv` | ✅ | Mock data with 8 sample chicken products |

## 📊 Mock Data Included

The CSV file has 8 sample chicken products for testing the dashboard:

| # | Product Name | Price (Rp) | Sold Count | Weight (kg) | Price/Kg |
|---|--------------|------------|----------|----------|
| 1 | Ayam Potong 1kg | Rp40,000.0 | 0 | 1.0 | Rp40,000.0 |
| 2 | Ayam Potong 500gr | Rp20,000.0 | 0 | 0.5 | Rp40,000.0 |
| 3 | Ayam Fillet Dada 1kg | Rp45,000.0 | 12 | 1.0 | Rp45,000.0 |
| 4 | Ayam Sayap Breast 1kg | Rp55,000.0 | 50 | 1.0 | Rp55,000.0 |
| 5 | Ayam Paha 1kg | Rp50,000.0 | 0 | 1.0 | Rp50,000.0 |
| 6 | Ayam Daging 1kg | Rp48,000.0 | 0 | 1.0 | Rp48,000.0 |
| 7 | Ayam Ceker 1kg | Rp52,000.0 | 0 | 1.0 | Rp52,000.0 |
| 8 | Ayam Jeroan 1kg | Rp51,000.0 | 0 | 1.0 | Rp51,000.0 |

## 🎯 What Works

**✅ Streamlit Dashboard** - Ready to visualize data
- Product table with sorting
- Price distribution chart
- Price vs sold count scatter plot
- Top 10 most expensive products
- Price per kilogram comparison
- Direct product links
- Filters for price range, weight range, sold count

**✅ Mock Data** - CSV file has realistic sample data
- 8 chicken products (Ayam Potong, Fillet, Sayap Breast, etc.)
- Prices ranging from Rp40,000 to Rp55,000
- Weights from 0.5kg to 1kg
- Some products have sold counts (0, 12, 50)

## ⚠️ Known Issues

1. **Shopee Anti-Bot Protection** - Shopee renders products via JavaScript
   - Playwright/Selenium fail because initial HTML is empty
   - Simple requests only gets shell HTML (redirects to login)

2. **Browser Tool Complexity** - Browser scraper has async/await issues
   - Tool calls run in subagent context (plaid-lo, delta-pine, etc.)
   - Complex to implement correctly

3. **Missing System Libraries** - Playwright requires libnspr4.so, libnss3.so
   - These aren't available in this containerized environment

## 🚀 Ready to Test

You can now test the dashboard without needing real scraper to work!

**To test the dashboard:**

1. Start the Streamlit app:
   ```bash
   streamlit run app/streamlit_app.py --server.port 8502
   ```

2. Access in browser:
   - Local: `http://localhost:8502`
   - External: `http://217.15.164.63:8502` (if Cloudflare tunnel is running)

3. Test features:
   - View product table
   - Try different filters (price range, weight range)
   - Sort by price (low to high, high to low, sold count, weight)
   - Check price analysis charts
   - Click product links
   - Check price/kg calculations

The mock data has 8 realistic chicken products with prices, weights, and sold counts for testing all dashboard features!
