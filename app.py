import streamlit as st
import pandas as pd
import os

# 1. Page Configuration
st.set_page_config(page_title="Universal Orlando Food Guide", layout="wide")

# 2. Data Loading Function
@st.cache_data
def load_data():
    file_path = 'universal_food_data.csv'
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        # Clean the Price column to ensure it is numeric for sorting/formatting
        if 'Price' in df.columns:
            df['Price'] = df['Price'].replace('[\$,]', '', regex=True).astype(float)
        return df
    return pd.DataFrame()

# Load the data into the app
df = load_data()

st.title("🍔 Universal Orlando Food Guide")

if not df.empty:
    # 3. Sidebar Filters
    st.sidebar.header("Filters")
    
    search_query = st.sidebar.text_input("Search for food items", "")

    parks = ["All"] + sorted(df['Park'].unique().tolist())
    selected_park = st.sidebar.selectbox("Select Park", parks)

    restaurants = ["All"] + sorted(df['Restaurant'].unique().tolist())
    selected_restaurant = st.sidebar.selectbox("Select Restaurant", restaurants)

    meal_periods = ["All", "Breakfast", "Lunch", "Dinner"]
    selected_period = st.sidebar.selectbox("Select Meal Period", meal_periods)

    # 4. Filter Logic
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

    # Sort results by price (Low to High)
    filtered_df = filtered_df.sort_values(by='Price')

    # 5. Display the Data with Currency Formatting
    if not filtered_df.empty:
        st.dataframe(
            filtered_df[['Park', 'Restaurant', 'Item', 'Price', 'Details']], 
            use_container_width=True, 
            hide_index=True,
            # This config adds the '$' symbol and keeps the number sortable
            column_config={
                "Price": st.column_config.NumberColumn(
                    "Price",
                    format="$%.2f",
                )
            }
        )
    else:
        st.warning("No items found matching your current filters.")

else:
    st.error("Could not find universal_food_data.csv.")
