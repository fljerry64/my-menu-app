import streamlit as st
import pandas as pd
import os

# 1. Page Configuration
st.set_page_config(page_title="Universal Orlando Food Guide", layout="wide")

# Custom CSS for a compact, no-scroll feel
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

st.title("🍔 Universal Orlando Food Guide")

if not df.empty:
    # 3. Sidebar Filters
    st.sidebar.header("Filters")
    search_query = st.sidebar.text_input("Search", "")
    
    parks = ["All"] + sorted(df['Park'].unique().tolist())
    selected_park = st.sidebar.selectbox("Park", parks)
    
    restaurants = ["All"] + sorted(df['Restaurant'].unique().tolist())
    selected_restaurant = st.sidebar.selectbox("Restaurant", restaurants)

    # UPDATED: Combined Meal Period options
    meal_periods = ["All", "Breakfast", "Lunch/Dinner"]
    selected_period = st.sidebar.selectbox("Meal Period", meal_periods)

    # 4. Filter Logic
    filtered_df = df.copy()

    if search_query:
        filtered_df = filtered_df[filtered_df['Item'].str.contains(search_query, case=False, na=False)]

    if selected_park != "All":
        filtered_df = filtered_df[filtered_df['Park'] == selected_park]

    if selected_restaurant != "All":
        filtered_df = filtered_df[filtered_df['Restaurant'] == selected_restaurant]

    # Combined Lunch/Dinner Logic
    if selected_period == "Breakfast":
        breakfast_keywords = 'Breakfast|Egg|Pancake|Waffle|Toast|Croissant|Oatmeal|Yogurt|Fruit'
        mask = (filtered_df['Details'].str.contains(breakfast_keywords, case=False, na=False) | 
                filtered_df['Item'].str.contains(breakfast_keywords, case=False, na=False))
        filtered_df = filtered_df[mask]
    
    elif selected_period == "Lunch/Dinner":
        # Searches for either 'Lunch' OR 'Dinner' in the Details
        lunch_dinner_keywords = 'Lunch|Dinner'
        filtered_df = filtered_df[filtered_df['Details'].str.contains(lunch_dinner_keywords, case=False, na=False)]

    # Sort by Price
    filtered_df = filtered_df.sort_values(by='Price')

    # 5. Display Data
    if not filtered_df.empty:
        st.dataframe(
            filtered_df[['Park', 'Restaurant', 'Item', 'Price', 'Details']], 
            use_container_width=True, 
            hide_index=True,
            height=600, 
            column_config={
                "Price": st.column_config.NumberColumn("Price", format="$%.2f"),
                "Details": st.column_config.TextColumn("Details", width="large")
            }
        )
    else:
        st.warning("No items found matching those filters.")
else:
    st.error("Could not find universal_food_data.csv.")
