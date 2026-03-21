"""
Streamlit app for Sentral Ayam product comparison dashboard
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Sentral Ayam - Product Comparison",
    page_icon="🐔",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #ee4d2d;
            text-align: center;
            margin-bottom: 2rem;
        }
        .metric-card {
            background-color: #f0f2f6;
            border-radius: 10px;
            padding: 1rem;
            margin: 0.5rem;
        }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load scraped product data"""
    data_path = Path(__file__).parent.parent / "data" / "raw_products.csv"
    
    if not data_path.exists():
        st.error("Data file not found! Please run scraper first: `python run.py`")
        return pd.DataFrame()
    
    df = pd.read_csv(data_path)
    
    # Clean price strings (remove 'Rp' prefix and convert to numeric)
    def clean_price(value):
        if pd.isna(value):
            return None
        if isinstance(value, str):
            value = value.replace('Rp', '').replace(',', '').strip()
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    # Convert price to numeric
    df['current_price'] = df['current_price'].apply(clean_price)
    df['original_price'] = df['original_price'].apply(clean_price)
    df['sold_count'] = pd.to_numeric(df['sold_count'], errors='coerce')
    df['weight_kg'] = pd.to_numeric(df['weight_kg'], errors='coerce')
    df['price_per_kg'] = pd.to_numeric(df['price_per_kg'], errors='coerce')
    
    return df


def main():
    # Header
    st.markdown('<h1 class="main-header">🐔 Sentral Ayam - Product Comparison</h1>', unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    
    if df.empty:
        st.warning("No data available. Please run scraper first.")
        st.info("To scrape data, run: `python run.py`")
        return
    
    # Check if we have valid price data
    valid_prices = df['current_price'].notna()
    if not valid_prices.any():
        st.error("No valid price data found in the CSV file.")
        return
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Filter by price range
    valid_prices = df[df['current_price'].notna()]['current_price']
    if len(valid_prices) > 0:
        min_price = float(valid_prices.min())
        max_price = float(valid_prices.max())
    else:
        min_price = 0
        max_price = 100000
    
    price_range = st.sidebar.slider(
        "Price Range (Rp)",
        min_value=int(min_price),
        max_value=int(max_price),
        value=(int(min_price), int(max_price))
    )
    
    # Filter by weight
    has_weight = df['weight_kg'].notna().any()
    if has_weight:
        min_weight = float(df['weight_kg'].min())
        max_weight = float(df['weight_kg'].max())
        weight_range = st.sidebar.slider(
            "Weight Range (kg)",
            min_value=float(min_weight),
            max_value=float(max_weight),
            value=(float(min_weight), float(max_weight))
        )
    
    # Filter by sold count
    min_sold = int(df['sold_count'].min()) if df['sold_count'].notna().any() else 0
    max_sold = int(df['sold_count'].max()) if df['sold_count'].notna().any() else 10000
    sold_range = st.sidebar.slider(
        "Sold Count Range",
        min_value=min_sold,
        max_value=max_sold,
        value=(min_sold, max_sold)
    )
    
    # Apply filters
    filtered_df = df[
        (df['current_price'] >= price_range[0]) &
        (df['current_price'] <= price_range[1]) &
        (df['sold_count'] >= sold_range[0]) &
        (df['sold_count'] <= sold_range[1])
    ]
    
    if has_weight:
        filtered_df = filtered_df[
            (filtered_df['weight_kg'] >= weight_range[0]) &
            (filtered_df['weight_kg'] <= weight_range[1])
        ]
    
    # Key metrics
    st.subheader("📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Products", len(filtered_df))
    
    with col2:
        avg_price = filtered_df['current_price'].mean()
        st.metric("Avg Price", f"Rp{avg_price:,.0f}")
    
    with col3:
        total_sold = filtered_df['sold_count'].sum()
        st.metric("Total Sold", f"{total_sold:,.0f}")
    
    with col4:
        discounted = filtered_df[filtered_df['original_price'].notna()]
        discount_pct = len(discounted) / len(filtered_df) * 100 if len(filtered_df) > 0 else 0
        st.metric("Discounted Products", f"{discount_pct:.1f}%")
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Product Table", "📈 Price Analysis", "⚖️ Price per Kg", "🔗 Links"])
    
    # Tab 1: Product Table
    with tab1:
        st.subheader("All Products")
        
        # Sort options
        sort_by = st.selectbox(
            "Sort by:",
            ["Price (Low to High)", "Price (High to Low)", "Sold Count", "Weight"],
            index=0
        )
        
        display_df = filtered_df.copy()
        
        if sort_by == "Price (Low to High)":
            display_df = display_df.sort_values('current_price', ascending=True)
        elif sort_by == "Price (High to Low)":
            display_df = display_df.sort_values('current_price', ascending=False)
        elif sort_by == "Sold Count":
            display_df = display_df.sort_values('sold_count', ascending=False)
        elif sort_by == "Weight":
            display_df = display_df.sort_values('weight_kg', ascending=True)
        
        # Format for display
        display_df['current_price'] = display_df['current_price'].apply(lambda x: f"Rp{x:,.0f}" if pd.notna(x) else "N/A")
        display_df['original_price'] = display_df['original_price'].apply(lambda x: f"Rp{x:,.0f}" if pd.notna(x) else "-")
        display_df['sold_count'] = display_df['sold_count'].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A")
        display_df['weight_kg'] = display_df['weight_kg'].apply(lambda x: f"{x:.2f} kg" if pd.notna(x) else "-")
        
        # Select columns to display
        display_columns = ['product_name', 'current_price', 'original_price', 'weight_kg', 'sold_count']
        
        st.dataframe(
            display_df[display_columns],
            use_container_width=True,
            hide_index=True
        )
    
    # Tab 2: Price Analysis
    with tab2:
        st.subheader("Price Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Price Distribution**")
            fig_price = px.histogram(
                filtered_df,
                x='current_price',
                nbins=20,
                title="Product Price Distribution",
                labels={'current_price': 'Price (Rp)', 'count': 'Number of Products'},
                color_discrete_sequence=['#ee4d2d']
            )
            st.plotly_chart(fig_price, use_container_width=True)
        
        with col2:
            st.write("**Price vs Sold Count**")
            fig_scatter = px.scatter(
                filtered_df,
                x='current_price',
                y='sold_count',
                hover_data=['product_name'],
                title="Price vs Popularity",
                labels={'current_price': 'Price (Rp)', 'sold_count': 'Sold Count'},
                color='current_price',
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Price range bar chart
        st.write("**Price Comparison**")
        top_products = filtered_df.nlargest(10, 'current_price')
        fig_bar = px.bar(
                top_products,
                x='product_name',
                y='current_price',
                title="Top 10 Most Expensive Products",
                labels={'product_name': 'Product', 'current_price': 'Price (Rp)'},
                color='current_price',
                color_continuous_scale='Reds'
            )
        fig_bar.update_xaxes(tickangle=45)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Tab 3: Price per Kg
    with tab3:
        st.subheader("Price per Kilogram Comparison")
        
        # Filter products with weight data
        weighted_df = filtered_df[filtered_df['price_per_kg'].notna()].copy()
        
        if weighted_df.empty:
            st.info("No products with weight data available for price/kg comparison.")
        else:
            # Price per kg chart
            fig_price_kg = px.bar(
                    weighted_df.sort_values('price_per_kg'),
                    x='product_name',
                    y='price_per_kg',
                    hover_data=['weight_kg'],
                    title="Price per Kilogram (Lower is Better)",
                    labels={'product_name': 'Product', 'price_per_kg': 'Price per Kg (Rp)'},
                    color='price_per_kg',
                    color_continuous_scale='RdYlGn_r'  # Red (high) to Green (low)
                )
            fig_price_kg.update_xaxes(tickangle=45)
            st.plotly_chart(fig_price_kg, use_container_width=True)
            
            # Price per kg table
            st.write("**Best Value (Lowest Price per Kg)**")
            best_value = weighted_df.nsmallest(10, 'price_per_kg')[['product_name', 'current_price', 'weight_kg', 'price_per_kg', 'sold_count']].copy()
            best_value['current_price'] = best_value['current_price'].apply(lambda x: f"Rp{x:,.0f}")
            best_value['price_per_kg'] = best_value['price_per_kg'].apply(lambda x: f"Rp{x:,.0f}/kg")
            best_value['weight_kg'] = best_value['weight_kg'].apply(lambda x: f"{x:.2f} kg")
            best_value['sold_count'] = best_value['sold_count'].apply(lambda x: f"{x:,.0f}")
            
            st.dataframe(best_value, use_container_width=True, hide_index=True)
    
    # Tab 4: Links
    with tab4:
        st.subheader("Product Links")
        
        for _, row in filtered_df.iterrows():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"**{row['product_name']}**")
                price = f"Rp{row['current_price']:,.0f}" if pd.notna(row['current_price']) else "N/A"
                st.markdown(f"{price}")
            
            with col2:
                if pd.notna(row['product_url']):
                    st.markdown(f"[🔗 View on Shopee]({row['product_url']})")
                else:
                    st.text("No link available")
            
            st.markdown("---")
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #666;'>
            <p>Data scraped from Sentral Ayam Shopee store • Built with Streamlit</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
