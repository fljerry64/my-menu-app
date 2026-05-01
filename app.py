import streamlit as st
import pandas as pd
import os

# 1. Page Configuration - Wide layout and custom compact CSS
st.set_page_config(page_title="Universal Orlando Food Guide", layout="wide")

# 2. Custom CSS - Permanent RED scrollbar on the custom HTML container
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    h1 { margin-top: 0rem; font-size: 2rem !important; }

    /* The container for the HTML table */
    .table-container {
        height: 650px;
        overflow-y: scroll !important;
        border: 1px solid #ddd;
    }

    /* FORCED RED SCROLLBAR */
    .table-container::-webkit-scrollbar {
        width: 18px !important;
        display: block !important;
    }
    .table-container::-webkit-scrollbar-track {
        background: #f1f1f1 !important;
    }
    .table-container::-webkit-scrollbar-thumb {
        background: #FF0000 !important; /* RED */
        border-radius: 5px !important;
    }
    
    /* Style for the HTML table */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        font-family: sans-serif;
    }
    .styled-table thead tr {
        background-color: #f0f2f6;
        text-align: left;
    }
    .styled-table th, .styled-table td {
        padding: 12px 15px;
        border-bottom: 1px solid #ddd;
    }
    .styled-table tbody tr:nth-of-type(even) {
        background-color: #f9f9f9;
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
        
        # CLEANUP: Standardize Restaurant names to Title Case
        if 'Restaurant' in df.columns:
            df['Restaurant'] = df['Restaurant'].str.title()
            
        # Clean Price column for sorting
        if 'Price' in df.columns:
            df['Price'] = df['Price'].replace('[\$,]', '', regex=True).astype(float)
            
        # Standardize Meal column (Grouping Dessert into Other)
        if 'Meal' in df.columns:
            df['Meal'] = df['Meal'].replace({'Dessert': 'Other'})
            
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
    
    # Updated Meal Period options to include 'Other'
    meal_options = ["All", "Breakfast", "Lunch/Dinner", "Other"]
    selected_period = st.sidebar.selectbox("Meal Period", meal_options)

    # 5. Filter Logic
    filtered_df = df.copy()

    if search_query:
        filtered_df = filtered_df[filtered_df['Item'].str.contains(search_query, case=False, na=False)]
    
    if selected_park != "All":
        filtered_df = filtered_df[filtered_df['Park'] == selected_park]
    
    if selected_restaurant != "All":
        filtered_df = filtered_df[filtered_df['Restaurant'] == selected_restaurant]

    # DIRECT FILTER using the Meal column from universal_food_data.csv
    if selected_period != "All":
        filtered_df = filtered_df[filtered_df['Meal'] == selected_period]

    filtered_df = filtered_df.sort_values(by='Price')

    # 6. Display Data as Styled HTML Table
    if not filtered_df.empty:
        display_df = filtered_df[['Item', 'Price', 'Details']].copy()
        display_df['Price'] = display_df['Price'].map('${:,.2f}'.format)
        
        html_table = display_df.to_html(index=False, classes='styled-table')
        full_html = f'<div class="table-container">{html_table}</div>'
        st.markdown(full_html, unsafe_allow_html=True)
    else:
        st.warning("No items found matching those filters.")
else:
    st.error("Could not find universal_food_data.csv.")
