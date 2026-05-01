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
        # Clean the Price column to handle '$' signs for proper sorting
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
    
    # Text Search
    search_query = st.sidebar.text_input("Search for food items", "")

    # Park Dropdown
    parks = ["All"] + sorted(df['Park'].unique().tolist())
    selected_park = st.sidebar.selectbox("Select Park", parks)

    # Restaurant Dropdown (Fixed the NameError from image_4a5341.png)
    restaurants = ["All"] + sorted(df['Restaurant'].unique().tolist())
    selected_restaurant = st.sidebar.selectbox("Select Restaurant", restaurants)

    # Meal Period Dropdown
    meal_periods = ["All", "Breakfast", "Lunch", "Dinner"]
    selected_period = st.sidebar.selectbox("Select Meal Period", meal_periods)

    # 4. Filter Logic
    filtered_df = df.copy()

    # Apply search query
    if search_query:
        filtered_df = filtered_df[filtered_df['Item'].str.contains(search_query, case=False, na=False)]

    # Apply Park filter
    if selected_park != "All":
        filtered_df = filtered_df[filtered_df['Park'] == selected_park]

    # Apply Restaurant filter
    if selected_restaurant != "All":
        filtered_df = filtered_df[filtered_df['Restaurant'] == selected_restaurant]

    # Apply Smarter Meal Period filter
    if selected_period == "Breakfast":
        # Broadens search to include common breakfast items even if "Breakfast" isn't in Details
        breakfast_keywords = 'Breakfast|Egg|Pancake|Waffle|Toast|Croissant|Oatmeal|Yogurt|Fruit'
        mask = (filtered_df['Details'].str.contains(breakfast_keywords, case=False, na=False) | 
                filtered_df['Item'].str.contains(breakfast_keywords, case=False, na=False))
        filtered_df = filtered_df[mask]
    elif selected_period != "All":
        # Standard filter for Lunch or Dinner
        filtered_df = filtered_df[filtered_df['Details'].str.contains(selected_period, case=False, na=False)]

    # Sort results by price (Low to High)
    filtered_df = filtered_df.sort_values(by='Price')

    # 5. Display the Data
    if not filtered_df.empty:
        st.dataframe(
            filtered_df[['Park', 'Restaurant', 'Item', 'Price', 'Details']], 
            use_container_width=True, 
            hide_index=True
        )
    else:
        st.warning("No items found matching your current filters.")

else:
    # Error state if the CSV isn't found in the GitHub repo
    st.error("Could not find universal_food_data.csv. Please ensure the file is in your main GitHub folder.")
