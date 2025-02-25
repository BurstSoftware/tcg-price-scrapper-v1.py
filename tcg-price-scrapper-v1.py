import pandas as pd
import streamlit as st
import altair as alt
from datetime import datetime

# Streamlit application
def main():
    st.title("Yu-Gi-Oh! Price Visualizer")

    # File upload
    uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

    # Only proceed if a file is uploaded
    if uploaded_file is not None:
        # Read the uploaded CSV into a DataFrame
        df = pd.read_csv(uploaded_file)
        st.success("File uploaded successfully!")

        # Store DataFrame in session state for persistence within the session
        st.session_state['df'] = df

        # Work with a copy of the DataFrame
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
        # Ensure default selections are valid by checking column existence
        x_axis_options = df.columns.tolist()
        y_axis_options = df.columns.tolist()
        color_by_options = df.columns.tolist()

        x_axis = st.selectbox("Select X-axis", x_axis_options, index=x_axis_options.index('price') if 'price' in x_axis_options else 0)
        y_axis = st.selectbox("Select Y-axis", y_axis_options, index=y_axis_options.index('name') if 'name' in y_axis_options else 0)
        color_by = st.selectbox("Color by", color_by_options, index=color_by_options.index('rarity') if 'rarity' in color_by_options else 0)

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
    else:
        st.warning("Please upload a CSV file to begin.")

if __name__ == "__main__":
    main()
