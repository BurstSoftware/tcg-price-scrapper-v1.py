import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
import altair as alt
from datetime import datetime

# Scraper function
def scrape_tcg_prices(url="https://www.tcgplayer.com/search/all/product?q=yugioh&view=grid", max_pages=5):
    all_cards = []
    page = 1
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    while page <= max_pages:
        try:
            # Add page parameter to URL
            page_url = f"{url}&page={page}"
            response = requests.get(page_url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all card listings based on TCGPlayer's structure
            card_listings = soup.select('.search-result')
            
            if not card_listings:
                break
                
            for card in card_listings:
                try:
                    # Extract data using TCGPlayer-specific selectors
                    name_elem = card.select_one('.search-result__title')
                    name = name_elem.text.strip() if name_elem else 'Unknown'
                    
                    price_elem = card.select_one('.price--direct')
                    price = price_elem.text.strip() if price_elem else '0'
                    
                    condition_elem = card.select_one('.search-result__condition')
                    condition = condition_elem.text.strip() if condition_elem else 'Near Mint'
                    
                    # Clean price (remove $ and convert to float)
                    price = float(price.replace('$', '').replace(',', '').replace('N/A', '0'))
                    
                    all_cards.append({
                        'name': name,
                        'price': price,
                        'condition': condition,
                        'date_scraped': datetime.now().strftime('%Y-%m-%d')
                    })
                except Exception as e:
                    continue
                    
            page += 1
            
        except requests.RequestException as e:
            st.error(f"Error fetching page {page}: {str(e)}")
            break
            
    return pd.DataFrame(all_cards)

# Streamlit application
def main():
    st.title("Yu-Gi-Oh! Price Scraper and Visualizer")
    
    # Preset URL with option to modify
    default_url = "https://www.tcgplayer.com/search/all/product?q=yugioh&view=grid"
    url = st.text_input("TCGPlayer URL", value=default_url)
    
    # Scrape button
    if st.button("Scrape Prices"):
        if url:
            with st.spinner("Scraping data from TCGPlayer..."):
                # Scrape data
                df = scrape_tcg_prices(url)
                
                # Store in session state for persistence
                st.session_state['df'] = df
                
                if not df.empty:
                    st.success(f"Scraped {len(df)} Yu-Gi-Oh! card listings!")
                else:
                    st.warning("No data was scraped. Check the URL or site structure.")
        else:
            st.error("Please enter a URL")
    
    # If data exists in session state, show visualization
    if 'df' in st.session_state and not st.session_state['df'].empty:
        df = st.session_state['df']
        
        # Filters
        st.sidebar.header("Filters")
        
        # Name filter
        name_filter = st.sidebar.text_input("Search by Card Name")
        if name_filter:
            df = df[df['name'].str.contains(name_filter, case=False, na=False)]
        
        # Price range filter
        min_price = float(df['price'].min())
        max_price = float(df['price'].max())
        price_range = st.sidebar.slider(
            "Price Range",
            min_price,
            max_price,
            (min_price, max_price)
        )
        df = df[(df['price'] >= price_range[0]) & (df['price'] <= price_range[1])]
        
        # Condition filter
        conditions = st.sidebar.multiselect(
            "Condition",
            options=df['condition'].unique(),
            default=df['condition'].unique()
        )
        df = df[df['condition'].isin(conditions)]
        
        # Visualization
        chart = alt.Chart(df).mark_circle(size=60).encode(
            x=alt.X('price:Q', title='Price ($)'),
            y=alt.Y('name:N', title='Card Name'),
            color='condition:N',
            tooltip=['name', 'price', 'condition', 'date_scraped']
        ).properties(
            width=700,
            height=500,
            title='Yu-Gi-Oh! Card Prices by Name and Condition'
        ).interactive()
        
        st.altair_chart(chart, use_container_width=True)
        
        # Show raw data
        if st.checkbox("Show raw data"):
            st.dataframe(df)

if __name__ == "__main__":
    main()
