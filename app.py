import streamlit as st
import pandas as pd
import os

# 1. Page Configuration - Force wide layout and compact padding
st.set_page_config(page_title="Universal Orlando Food Guide", layout="wide")

# Custom CSS to reduce top padding and make the title fit better
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    h1 { margin-top: 0rem; font-size: 2rem !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Data Loading Function
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

# 3. Main Title
st.title("🍔 Universal Orlando Food Guide")

if not df.empty:
    # 4. Sidebar Filters
    st.sidebar.header("Filters")
    search_query = st.sidebar.text_input("Search", "")
    parks = ["All"] + sorted(df['Park'].unique().tolist())
    selected_park = st.sidebar.selectbox("Park", parks)
    restaurants = ["All"] + sorted(df['Restaurant'].unique().tolist())
    selected_restaurant = st.sidebar.selectbox("Restaurant", restaurants)
    meal_periods = ["All", "Breakfast", "Lunch", "Dinner"]
    selected_period = st.sidebar.selectbox("Meal Period", meal_periods)

    # 5. Filter Logic
    filtered_df = df.copy()
    if search_query:
        filtered_df = filtered_df[filtered_df['Item'].str.contains(search_query, case=False, na=False)]
    if selected_park != "All":
        filtered_df = filtered_df[filtered_df['Park'] == selected_park]
    if selected_restaurant != "All":
        filtered_df = filtered_df[filtered_df['Restaurant'] == selected_restaurant]
    
    if selected_period == "Breakfast":
        breakfast_keywords = 'Breakfast|Egg|Pancake|Waffle|Toast|Croissant|Oatmeal|Yogurt|Fruit'
        mask = (filtered_df['Details'].str.contains(breakfast_keywords, case=False, na=False) | 
                filtered_df['Item'].str.contains(breakfast_keywords, case=False, na=False))
        filtered_df = filtered_df[mask]
    elif selected_period != "All":
        filtered_df = filtered_df[filtered_df['Details'].str.contains(selected_period, case=False, na=False)]

    filtered_df = filtered_df.sort_values(by='Price')

    # 6. Display Data with specific Height and Formatting
    if not filtered_df.empty:
        # 'height' parameter controls the vertical space of the table
        # 'use_container_width' ensures it uses the full screen width
        st.dataframe(
            filtered_df[['Park', 'Restaurant', 'Item', 'Price', 'Details']], 
            use_container_width=True, 
            hide_index=True,
            height=600,  # Adjust this number to fit your specific screen resolution
            column_config={
                "Price": st.column_config.NumberColumn("Price", format="$%.2f"),
                "Details": st.column_config.TextColumn("Details", width="large")
            }
        )
    else:
        st.warning("No items found.")
else:
    st.error("Could not find universal_food_data.csv.")
