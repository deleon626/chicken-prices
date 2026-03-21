# Code Review: Sentral Ayam Streamlit App

**Date:** 2026-02-04
**File:** `app/streamlit_app.py`
**Reviewer:** Optimum Pride

---

## 📋 Summary

**Overall Assessment:** ⭐⭐⭐⭐ (4/5 stars)

The code is well-structured, follows Streamlit best practices, and provides a clean, functional dashboard. However, there are several areas for improvement in error handling, data validation, and user experience.

---

## ✅ Strengths

### 1. Good Structure
- Clear separation of concerns with `load_data()` and `main()` functions
- Logical flow from data loading → filtering → visualization
- Well-organized tabs for different views

### 2. Data Caching
- Uses `@st.cache_data` for the data loading function (good for performance)
- Prevents unnecessary CSV reloads on every interaction

### 3. User Experience
- Sidebar filters provide good interactivity
- Multiple visualization options (histogram, scatter, bar charts)
- Color schemes match Shopee branding (#ee4d2d)

### 4. Error Handling Improvements Made
- Recent fixes for price string parsing (`clean_price()` function)
- Proper NaN handling in filters and calculations

---

## 🔴 Critical Issues

### 1. **Missing Weight Validation**
**Location:** Line 133-140

```python
if has_weight:
    min_weight = float(df['weight_kg'].min())
    max_weight = float(df['weight_kg'].max())
```

**Issue:** If all weight values are NaN, `min()` and `max()` will fail or return NaN, causing the slider to break.

**Fix:**
```python
if has_weight:
    valid_weights = df[df['weight_kg'].notna()]['weight_kg']
    if len(valid_weights) > 0:
        min_weight = float(valid_weights.min())
        max_weight = float(valid_weights.max())
    else:
        has_weight = False  # Disable weight filter
```

---

## ⚠️ High Priority Issues

### 2. **Sold Count NaN Issue**
**Location:** Line 143-149

```python
min_sold = int(df['sold_count'].min()) if df['sold_count'].notna().any() else 0
max_sold = int(df['sold_count'].max()) if df['sold_count'].notna().any() else 10000
```

**Issue:** If all sold counts are NaN, `.min()` and `.max()` will fail with TypeError.

**Fix:**
```python
valid_sold = df[df['sold_count'].notna()]['sold_count']
if len(valid_sold) > 0:
    min_sold = int(valid_sold.min())
    max_sold = int(valid_sold.max())
else:
    min_sold = 0
    max_sold = 10000
```

### 3. **Filter Logic Bug**
**Location:** Line 156-166

**Issue:** When applying weight filter, it doesn't check if `weight_range` exists. If `has_weight` is False, `weight_range` is undefined and will cause NameError.

**Fix:**
```python
if has_weight:
    filtered_df = filtered_df[
        (filtered_df['weight_kg'] >= weight_range[0]) &
        (filtered_df['weight_kg'] <= weight_range[1])
    ]
```

### 4. **Division by Zero Risk**
**Location:** Line 88

```python
discount_pct = len(discounted) / len(filtered_df) * 100 if len(filtered_df) > 0 else 0
```

**Issue:** The condition checks if filtered_df has any rows, but the discount calculation still happens on the full dataset before filtering.

**Fix:**
```python
if len(filtered_df) > 0:
    discounted = filtered_df[filtered_df['original_price'].notna()]
    discount_pct = len(discounted) / len(filtered_df) * 100
else:
    discount_pct = 0
```

---

## 🟡 Medium Priority Issues

### 5. **Unused Import**
**Location:** Line 7

```python
import plotly.graph_objects as go
```

**Issue:** This import is never used in the code.

**Fix:** Remove the unused import.

### 6. **Hardcoded Values**
**Location:** Multiple locations

- Default max price: 100000 (line 105)
- Default max sold: 10000 (line 146)

**Issue:** Magic numbers without context. Consider defining constants at the top:
```python
DEFAULT_MAX_PRICE = 100000
DEFAULT_MAX_SOLD = 10000
```

### 7. **Inconsistent NaN Handling**
**Location:** Throughout the file

**Issue:** Some places use `pd.notna()`, others check `if pd.notna(x)`. Should be consistent.

**Fix:** Use a helper function:
```python
def is_valid(value):
    return pd.notna(value) and value != ''
```

### 8. **Sort Function Bug**
**Location:** Line 218

```python
elif sort_by == "Weight":
    display_df = display_df.sort_values('weight_kg', ascending=True)
```

**Issue:** This will fail if some products don't have weight data (NaN values).

**Fix:**
```python
elif sort_by == "Weight":
    display_df = display_df.sort_values('weight_kg', ascending=True, na_position='last')
```

### 9. **No Loading State**
**Issue:** Large datasets might take time to filter/visualize, but there's no loading indicator.

**Fix:** Add:
```python
with st.spinner('Loading data...'):
    df = load_data()
```

### 10. **Product Links Tab Performance**
**Location:** Line 258-272

**Issue:** Iterates through all products in a loop, which can be slow for large datasets.

**Fix:** Consider using `st.dataframe` with a formatted column instead, or add pagination.

---

## 🟢 Low Priority Improvements

### 11. **CSS Not Applied**
**Location:** Line 18-28

**Issue:** `.metric-card` class is defined but never used.

**Fix:** Either apply it or remove it.

### 12. **Missing Data Refresh Button**
**Issue:** Data is cached with `@st.cache_data`, so updates to the CSV won't show until the app restarts.

**Fix:** Add a refresh button:
```python
if st.button('🔄 Refresh Data'):
    st.cache_data.clear()
    df = load_data()
```

### 13. **No Search Functionality**
**Issue:** Users can't search by product name.

**Fix:** Add a search box in the sidebar:
```python
search_query = st.sidebar.text_input('Search products:')
if search_query:
    filtered_df = filtered_df[filtered_df['product_name'].str.contains(search_query, case=False)]
```

### 14. **Accessibility**
**Issue:** Color scales might be hard to distinguish for colorblind users.

**Fix:** Use more accessible color scales or add pattern fills.

### 15. **Missing Error Logging**
**Issue:** Errors are only shown to the user, not logged for debugging.

**Fix:** Add proper logging:
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

---

## 🔒 Security Considerations

### 16. **XSS Risk in Product Names**
**Location:** Line 267, 283

```python
st.markdown(f"**{row['product_name']}**")
```

**Issue:** If product names contain HTML/JS, it could be executed.

**Fix:** Use `st.write()` instead, or sanitize input:
```python
import html
st.markdown(f"**{html.escape(row['product_name'])}**")
```

### 17. **URL Validation**
**Location:** Line 283

```python
st.markdown(f"[🔗 View on Shopee]({row['product_url']})")
```

**Issue:** No validation that URLs are from shopee.co.id (could be malicious links).

**Fix:** Add URL validation in the scraper.

---

## 📊 Performance Optimization

### 18. **Redundant Filtering**
**Location:** Line 234-242

**Issue:** Filters are applied multiple times (once for each tab), even though the filtered dataframe is the same.

**Fix:** Move filter application outside the tabs.

### 19. **Large DataFrame Copy**
**Location:** Line 213

```python
display_df = filtered_df.copy()
```

**Issue:** Creates a copy of the entire dataframe, which is unnecessary for sorting.

**Fix:** Sort in place or use `inplace=True` parameter.

---

## 🎨 UI/UX Improvements

### 20. **Mobile Responsiveness**
**Issue:** 4-column layout doesn't work well on mobile.

**Fix:** Use responsive columns:
```python
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
```

### 21. **Export Functionality**
**Issue:** Users can't export filtered data.

**Fix:** Add download button:
```python
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button('Download CSV', csv, 'products.csv', 'text/csv')
```

---

## 📝 Code Style

### 22. **Missing Type Hints**
**Issue:** Functions don't have type hints, making code harder to maintain.

**Fix:** Add type hints:
```python
def clean_price(value: Any) -> Optional[float]:
    ...

def load_data() -> pd.DataFrame:
    ...
```

### 23. **Long Function**
**Issue:** `main()` is 200+ lines, violating single responsibility principle.

**Fix:** Break into smaller functions:
```python
def render_metrics(df: pd.DataFrame) -> None:
    ...

def render_filters(df: pd.DataFrame) -> Tuple[pd.DataFrame, ...]:
    ...

def render_tabs(df: pd.DataFrame) -> None:
    ...
```

---

## ✅ Recommendations Priority

### Must Fix (Critical & High Priority)
1. Weight validation (Issue #1)
2. Sold count NaN handling (Issue #2)
3. Filter logic bug (Issue #3)
4. Division by zero (Issue #4)
5. XSS vulnerability (Issue #16)

### Should Fix (Medium Priority)
6. Remove unused import (Issue #5)
7. Add constants (Issue #6)
8. Sort NaN handling (Issue #8)
9. Add loading state (Issue #9)
10. Optimize links tab (Issue #10)

### Nice to Have (Low Priority)
11. Remove unused CSS (Issue #11)
12. Add refresh button (Issue #12)
13. Add search (Issue #13)
14. Improve accessibility (Issue #14)
15. Add logging (Issue #15)
16. Add export (Issue #21)

### Code Quality
17. Add type hints (Issue #22)
18. Refactor main() (Issue #23)

---

## 🎯 Overall Verdict

**Good foundation** but needs **error handling and data validation improvements** before production use. The critical issues could cause crashes with incomplete or malformed data.

**Estimated effort to fix all issues:** 4-6 hours

**Recommended next steps:**
1. Fix critical and high priority issues first
2. Add unit tests for data loading and filtering
3. Add integration tests for the Streamlit UI
4. Consider moving to a more modular architecture

---

**End of Code Review**
