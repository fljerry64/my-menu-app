import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Universal Orlando Food Guide", layout="wide")

@st.cache_data
def load_data():
    file_path = 'universal_food_data.csv'
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        # Remove '$' and convert Price to a number so we can sort it
        if 'Price' in df.columns:
            df['Price'] = df['Price'].replace('[\$,]', '', regex=True).astype(float)
        return df
    return pd.DataFrame()

df = load_data()

st.title("🍔 Universal Orlando Food Guide")

if not df.empty:
    # --- SIDEBAR FILTERS ---
    st.sidebar.header("Filters")
    
    # Search by Item Name
    search_query = st.sidebar.text_input("Search for food items", "")

    # Filter by Park
    parks = ["All"] + sorted(df['Park'].unique().tolist())
    selected_park = st.sidebar.selectbox("Select Park", parks)

    # Filter by Restaurant (New based on your CSV)
    restaurants = ["All"] + sorted(df['Restaurant'].unique().tolist())
    selected_restaurant = st.sidebar.selectbox("Select Restaurant", restaurants)

    # --- FILTER LOGIC ---
    filtered_df = df.copy()

    if search_query:
        filtered_df = filtered_df[filtered_df['Item'].str.contains(search_query, case=False, na=False)]

    if selected_park != "All":
        filtered_df = filtered_df[filtered_df['Park'] == selected_park]

    if selected_restaurant != "All":
        filtered_df = filtered_df[filtered_df['Restaurant'] == selected_restaurant]

    # Sort by Price (Low to High)
    filtered_df = filtered_df.sort_values(by='Price')

    # --- DISPLAY ---
    st.dataframe(
        filtered_df[['Park', 'Restaurant', 'Item', 'Price', 'Details']], 
        use_container_width=True, 
        hide_index=True
    )
else:
    st.error("Could not find universal_food_data.csv. Please ensure it is in the main folder on GitHub.")
