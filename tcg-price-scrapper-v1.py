import pandas as pd
import streamlit as st
import altair as alt
from datetime import datetime

# Default data as a fallback
default_data = {
    'name': [
        'Blue-Eyes Spirit Dragon', 'Blue-Eyes White Dragon (SDWD-EN003)', 'Blue-Eyes Tyrant Dragon',
        'True Light', 'The White Stone of Ancients', 'Neo Blue-Eyes Ultimate Dragon',
        'Sage with Eyes of Blue', 'Blue-Eyes Ultimate Spirit Dragon', 'Called by the Grave',
        'Indigo-Eyes Silver Dragon', 'Wishes for Eyes of Blue', 'Majesty of the White Dragons',
        'Maiden of White', 'Neo Kaiser Sea Horse', 'Roar of the Blue-Eyed Dragons',
        'Nibiru, the Primal Being', 'Blue-Eyes Ultimate Spirit Dragon (Secret Rare)',
        'Infinite Impermanence', 'Effect Veiler', 'Maiden of White (Secret Rare)',
        'Spirit with Eyes of Blue', 'Wishes for Eyes of Blue (Secret Rare)',
        'Ash Blossom & Joyous Spring', 'Blue-Eyes White Destiny Structure Deck'
    ],
    'price': [
        0.19, 0.21, 0.15, 0.20, 0.17, 0.23, 0.20, 0.24, 0.27, 0.27, 0.42, 0.25,
        0.26, 0.22, 0.27, 0.48, 0.84, 2.54, 0.33, 1.91, 0.42, 1.16, 1.98, 15.05
    ],
    'condition': [
        'Near Mint', 'Near Mint', 'Near Mint', 'Near Mint', 'Near Mint', 'Near Mint',
        'Near Mint', 'Near Mint', 'Near Mint', 'Near Mint', 'Near Mint', 'Near Mint',
        'Near Mint', 'Near Mint', 'Near Mint', 'Near Mint', 'Near Mint', 'Near Mint',
        'Near Mint', 'Near Mint', 'Near Mint', 'Near Mint', 'Near Mint', 'Near Mint'
    ],
    'date_scraped': [datetime.now().strftime('%Y-%m-%d')] * 24,
    'rarity': [
        'Common', 'Common', 'Common', 'Common', 'Common', 'Common', 'Common', 'Ultra Rare',
        'Common', 'Ultra Rare', 'Ultra Rare', 'Super Rare', 'Ultra Rare', 'Super Rare',
        'Super Rare', 'Common', 'Secret Rare', 'Common', 'Common', 'Secret Rare',
        'Ultra Rare', 'Secret Rare', 'Common', 'N/A'
    ]
}

# Streamlit application
def main():
    st.title("Yu-Gi-Oh! Price Visualizer")

    # File upload
    uploaded_file = st.file_uploader("Upload your CSV file", type="csv")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.success("File uploaded successfully!")
    else:
        # Use default data if no file is uploaded
        df = pd.DataFrame(default_data)
        st.info("Using default dataset. Upload a CSV to use your own data.")

    # Store DataFrame in session state for persistence
    st.session_state['df'] = df

    if 'df' in st.session_state and not st.session_state['df'].empty:
        df = st.session_state['df'].copy()

        # Filters
        st.sidebar.header("Filters")

        # Search across multiple attributes
        st.sidebar.subheader("Search")
        search_query = st.sidebar.text_input("Search by Name, Price, Condition, Rarity, or Date")
        if search_query:
            # Convert price to string for searching, handle numeric search separately
            try:
                price_search = float(search_query)
                df = df[
                    (df['name'].str.contains(search_query, case=False, na=False)) |
                    (df['price'] == price_search) |
                    (df['condition'].str.contains(search_query, case=False, na=False)) |
                    (df['rarity'].str.contains(search_query, case=False, na=False)) |
                    (df['date_scraped'].str.contains(search_query, case=False, na=False))
                ]
            except ValueError:
                df = df[
                    (df['name'].str.contains(search_query, case=False, na=False)) |
                    (df['condition'].str.contains(search_query, case=False, na=False)) |
                    (df['rarity'].str.contains(search_query, case=False, na=False)) |
                    (df['date_scraped'].str.contains(search_query, case=False, na=False))
                ]

        # Dynamic filters for each column
        for column in df.columns:
            if column == 'price':
                min_val = float(df[column].min())
                max_val = float(df[column].max())
                selected_range = st.sidebar.slider(
                    f"Filter {column.capitalize()}",
                    min_val, max_val, (min_val, max_val)
                )
                df = df[(df[column] >= selected_range[0]) & (df[column] <= selected_range[1])]
            else:
                unique_values = df[column].unique()
                selected_values = st.sidebar.multiselect(
                    f"Filter {column.capitalize()}",
                    options=unique_values,
                    default=unique_values
                )
                df = df[df[column].isin(selected_values)]

        # Visualization
        st.subheader("Visualization")
        x_axis = st.selectbox("Select X-axis", df.columns, index=df.columns.get_loc('price'))
        y_axis = st.selectbox("Select Y-axis", df.columns, index=df.columns.get_loc('name'))
        color_by = st.selectbox("Color by", df.columns, index=df.columns.get_loc('rarity'))

        chart = alt.Chart(df).mark_circle(size=60).encode(
            x=alt.X(f'{x_axis}:Q' if df[x_axis].dtype in ['int64', 'float64'] else f'{x_axis}:N', title=x_axis.capitalize()),
            y=alt.Y(f'{y_axis}:N', title=y_axis.capitalize()),
            color=f'{color_by}:N',
            tooltip=list(df.columns)
        ).properties(
            width=700,
            height=500,
            title=f'Yu-Gi-Oh! Card Data: {x_axis.capitalize()} vs {y_axis.capitalize()}'
        ).interactive()

        st.altair_chart(chart, use_container_width=True)

        # Show raw data
        if st.checkbox("Show raw data"):
            st.dataframe(df)

        # Export filtered data as CSV
        st.subheader("Export Data")
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download filtered data as CSV",
            data=csv,
            file_name=f"yugioh_filtered_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
