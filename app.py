import streamlit as st
import pandas as pd
import os

# 1. Page Configuration
st.set_page_config(
    page_title="Universal Orlando Food Guide", 
    layout="wide"
)

# 2. Custom CSS - Permanent RED scrollbar + Optimized Header
st.markdown("""
    <style>
    /* Reduce padding for a tighter mobile look */
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    h1 { margin-bottom: 0.5rem; font-size: 1.8rem !important; }

    /* The container for the HTML table */
    .table-container {
        height: 600px;
        overflow-y: scroll !important;
        overflow-x: auto !important;
        border: 1px solid #ddd;
        margin-top: 10px;
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
        background: #FF0000 !important;
        border-radius: 5px !important;
    }
    
    /* Styled HTML table */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        font-family: sans-serif;
        font-size: 0.9rem;
    }
    .styled-table thead tr {
        background-color: #f0f2f6;
        text-align: left;
    }
    .styled-table th, .styled-table td {
        padding: 10px 8px;
        border-bottom: 1px solid #ddd;
    }
    .styled-table tbody tr:nth-of-type(even) {
        background-color: #f9f9f9;
    }

    /* Hide standard Streamlit header/footer */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Make the filter container look distinct */
    .filter-box {
        background-color: #f8f9fb;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Data Loading
@st.cache_data
def load_data():
    file_path = 'universal_food_data.csv'
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        if 'Restaurant' in df.columns:
            df['Restaurant'] = df['Restaurant'].str.title()
        if 'Price' in df.columns:
            df['Price'] = df['Price'].replace('[\$,]', '', regex=True).astype(float)
        if 'Meal' in df.columns:
            df['Meal'] = df['Meal'].replace({'Dessert': 'Other'})
        return df
    return pd.DataFrame()

df = load_data()

st.title("🍔 Universal Orlando Food Guide")

if not df.empty:
    # 4. Top-Screen Filters (No Sidebar)
    # Using columns ensures they stay side-by-side on desktop but stack on mobile
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    with col1:
        search_query = st.text_input("🔍 Search Item", "")
    
    with col2:
        parks = ["All"] + sorted(df['Park'].unique().tolist())
        selected_park = st.selectbox("Park", parks)
    
    with col3:
        restaurants = ["All"] + sorted(df['Restaurant'].unique().tolist())
        selected_restaurant = st.selectbox("Restaurant", restaurants)
    
    with col4:
        meal_options = ["All", "Breakfast", "Lunch/Dinner", "Other"]
        selected_period = st.selectbox("Meal Period", meal_options)

    # 5. Filter Logic
    filtered_df = df.copy()

    if search_query:
        filtered_df = filtered_df[filtered_df['Item'].str.contains(search_query, case=False, na=False)]
    if selected_park != "All":
        filtered_df = filtered_df[filtered_df['Park'] == selected_park]
    if selected_restaurant != "All":
        filtered_df = filtered_df[filtered_df['Restaurant'] == selected_restaurant]
    if selected_period != "All":
        filtered_df = filtered_df[filtered_df['Meal'] == selected_period]

    filtered_df = filtered_df.sort_values(by='Price')

    # 6. Display Data
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
