import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Universal Orlando Food Guide", layout="wide")

@st.cache_data
def load_data():
    file_path = 'universal_food_data.csv'
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        if 'Price' in df.columns:
            df['Price'] = df['Price'].replace('[\$,]', '', regex=True).astype(float)
        return df
    return pd.DataFrame()

df = load_data()

st.title("🍔 Universal Orlando Food Guide")

if not df.empty:
    st.sidebar.header("Filters")
    
    search_query = st.sidebar.text_input("Search for food items", "")

    # Park Filter
    parks = ["All"] + sorted(df['Park'].unique().tolist())
    selected_park = st.sidebar.selectbox("Select Park", parks)

    # NEW: Meal Period Filter (scans the 'Details' column)
    meal_periods = ["All", "Breakfast", "Lunch", "Dinner"]
    selected_period = st.sidebar.selectbox("Select Meal Period", meal_periods)

    # --- FILTER LOGIC ---
    filtered_df = df.copy()

    if search_query:
        filtered_df = filtered_df[filtered_df['Item'].str.contains(search_query, case=False, na=False)]

    if selected_park != "All":
        filtered_df = filtered_df[filtered_df['Park'] == selected_park]

    # Logical scan for Breakfast/Lunch/Dinner keywords in 'Details'
    if selected_period != "All":
        filtered_df = filtered_df[filtered_df['Details'].str.contains(selected_period, case=False, na=False)]

    filtered_df = filtered_df.sort_values(by='Price')

    # --- DISPLAY ---
    st.dataframe(
        filtered_df[['Park', 'Restaurant', 'Item', 'Price', 'Details']], 
        use_container_width=True, 
        hide_index=True
    )
else:
    st.error("Could not find universal_food_data.csv.")
