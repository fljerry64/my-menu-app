import streamlit as st
import pandas as pd
import os
import streamlit.components.v1 as components

# 1. Page Configuration
st.set_page_config(page_title="Universal Orlando Food Guide", layout="wide")

# Custom CSS with a special injection for the table scrollbar
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    h1 { margin-top: 0rem; font-size: 2rem !important; }
    
    /* 1. Global scrollbar (the main page) */
    ::-webkit-scrollbar { width: 14px; height: 14px; display: block; }
    ::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 10px; }
    ::-webkit-scrollbar-thumb { background: #FF0000 !important; border-radius: 10px; border: 2px solid #f1f1f1; }

    /* 2. Target the Streamlit Dataframe specifically */
    [data-testid="stDataFrame"] > div:first-child {
        scrollbar-color: #FF0000 #f1f1f1 !important;
        scrollbar-width: thick !important;
    }

    /* 3. Aggressive injection for Webkit browsers (Chrome/Safari) inside the table */
    [data-testid="stDataFrame"] ::-webkit-scrollbar {
        width: 14px !important;
        height: 14px !important;
        display: block !important;
    }
    [data-testid="stDataFrame"] ::-webkit-scrollbar-thumb {
        background-color: #FF0000 !important;
        border-radius: 10px !important;
    }

    #MainMenu, footer, header {visibility: hidden;}
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
    meal_periods = ["All", "Breakfast", "Lunch/Dinner"]
    selected_period = st.sidebar.selectbox("Meal Period", meal_periods)

    # 4. Filter Logic
    filtered_df = df.copy()
    breakfast_keywords = 'Breakfast|Egg|Pancake|Waffle|Toast|Croissant|Oatmeal|Yogurt|Fruit'

    if search_query:
        filtered_df = filtered_df[filtered_df['Item'].str.contains(search_query, case=False, na=False)]
    if selected_park != "All":
        filtered_df = filtered_df[filtered_df['Park'] == selected_park]
    if selected_restaurant != "All":
        filtered_df = filtered_df[filtered_df['Restaurant'] == selected_restaurant]

    if selected_period == "Breakfast":
        mask = (filtered_df['Details'].str.contains(breakfast_keywords, case=False, na=False) | 
                filtered_df['Item'].str.contains(breakfast_keywords, case=False, na=False))
        filtered_df = filtered_df[mask]
    elif selected_period == "Lunch/Dinner":
        is_breakfast = (filtered_df['Details'].str.contains(breakfast_keywords, case=False, na=False) | 
                        filtered_df['Item'].str.contains(breakfast_keywords, case=False, na=False))
        filtered_df = filtered_df[~is_breakfast]

    filtered_df = filtered_df.sort_values(by='Price')

    # 5. Display Data
    if not filtered_df.empty:
        st.dataframe(
            filtered_df[['Item', 'Price', 'Details']], 
            use_container_width=True, 
            hide_index=True,
            height=650, 
            column_config={
                "Item": st.column_config.TextColumn("Item", width="medium"),
                "Price": st.column_config.NumberColumn("Price", format="$%.2f", width="small"),
                "Details": st.column_config.TextColumn("Details", width="large")
            }
        )
    else:
        st.warning("No items found matching those filters.")
else:
    st.error("Could not find universal_food_data.csv.")
