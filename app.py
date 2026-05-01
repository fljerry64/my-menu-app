import streamlit as st
import pandas as pd
import os

# 1. Page Configuration
st.set_page_config(page_title="Universal Orlando Food Guide", layout="wide")

# 2. Custom CSS - This creates a scrollable area with a FORCED RED SCROLLBAR
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    h1 { margin-top: 0rem; font-size: 2rem !important; }

    /* This targets the custom 'scroll-container' we create below */
    .scroll-container {
        height: 650px;
        overflow-y: scroll !important;
        border: 1px solid #ddd;
        padding-right: 5px;
    }

    /* FORCED RED SCROLLBAR logic for the container */
    .scroll-container::-webkit-scrollbar {
        width: 16px !important;
        display: block !important;
    }
    .scroll-container::-webkit-scrollbar-track {
        background: #f1f1f1 !important;
    }
    .scroll-container::-webkit-scrollbar-thumb {
        background: #FF0000 !important; /* BRIGHT RED */
        border-radius: 10px !important;
        border: 2px solid #f1f1f1 !important;
    }
    .scroll-container::-webkit-scrollbar-thumb:hover {
        background: #CC0000 !important;
    }

    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. Data Loading
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
    # 4. Sidebar Filters
    st.sidebar.header("Filters")
    search_query = st.sidebar.text_input("Search", "")
    parks = ["All"] + sorted(df['Park'].unique().tolist())
    selected_park = st.sidebar.selectbox("Park", parks)
    restaurants = ["All"] + sorted(df['Restaurant'].unique().tolist())
    selected_restaurant = st.sidebar.selectbox("Restaurant", restaurants)
    meal_periods = ["All", "Breakfast", "Lunch/Dinner"]
    selected_period = st.sidebar.selectbox("Meal Period", meal_periods)

    # 5. Filter Logic
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

    # 6. Display Data using a Custom Scrollable HTML Div
    if not filtered_df.empty:
        # Format the price column for the table
        display_df = filtered_df[['Item', 'Price', 'Details']].copy()
        display_df['Price'] = display_df['Price'].map('${:,.2f}'.format)
        
        # We wrap the table in a div with the class 'scroll-container'
        st.markdown('<div class="scroll-container">', unsafe_allow_html=True)
        st.table(display_df)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("No items found matching those filters.")
else:
    st.error("Could not find universal_food_data.csv.")
