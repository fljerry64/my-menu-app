import streamlit as st
import pandas as pd
import os

# 1. Page Configuration
st.set_page_config(
    page_title="Universal Orlando Food Guide", 
    layout="wide"
)

# 2. Custom CSS - Permanent RED scrollbar
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    h1 { margin-bottom: 0.5rem; font-size: 1.8rem !important; }

    /* FORCED RED SCROLLBAR for the main page */
    ::-webkit-scrollbar {
        width: 14px !important;
    }
    ::-webkit-scrollbar-track {
        background: #f1f1f1 !important;
    }
    ::-webkit-scrollbar-thumb {
        background: #FF0000 !important;
        border-radius: 5px !important;
    }

    /* Styling for the custom 'Table' header */
    .header-row {
        display: flex;
        background-color: #f0f2f6;
        padding: 10px;
        font-weight: bold;
        border-bottom: 2px solid #ddd;
        margin-bottom: 10px;
        border-radius: 5px;
    }
    .col-item { flex: 3; }
    .col-price { flex: 1; text-align: right; }

    /* Hide standard Streamlit elements */
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. Data Loading & Cleaning
@st.cache_data
def load_data():
    # Use the specific file name you are currently working with
    file_path = 'universal_food_data.csv' 
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        
        # Standardize Restaurant names
        if 'Restaurant' in df.columns:
            df['Restaurant'] = df['Restaurant'].str.title()
        
        # Robust Price Cleaning[cite: 1]
        if 'Price' in df.columns:
            # Convert to string, remove symbols, strip whitespace, then convert to number
            df['Price'] = df['Price'].astype(str).str.replace('[\$,]', '', regex=True).str.strip()
            df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
            
        # Advanced Category Correction[cite: 1]
        if 'Meal' in df.columns:
            # Fix 1: Catch beverages and Coca-Cola cups mislabeled in the CSV
            bev_keywords = ['Water', 'Icee', 'Soda', 'Drink', 'Juice', 'Coffee', 'Tea', 
                            'Powerade', 'Milk', 'Coca-Cola', 'Cup', 'Refill']
            bev_pattern = '|'.join(bev_keywords)
            df.loc[df['Item'].str.contains(bev_pattern, case=False, na=False), 'Meal'] = 'Beverage'
            
            # Fix 2: Ensure "Dessert-like" items appear under Dessert
            dessert_keywords = ['Cake', 'Cookie', 'Brownie', 'Pie', 'Churro', 'Pastry', 'Sweet']
            dess_pattern = '|'.join(dessert_keywords)
            df.loc[(df['Item'].str.contains(dess_pattern, case=False, na=False)) & 
                   (~df['Meal'].isin(['Breakfast', 'Lunch/Dinner'])), 'Meal'] = 'Dessert'
            
        return df
    return pd.DataFrame()

df = load_data()

st.title("🍔 Universal Orlando Food Guide")

if not df.empty:
    # 4. Top-Screen Filters
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
        meal_options = ["All", "Breakfast", "Lunch/Dinner", "Beverage", "Dessert", "Snack", "Other"]
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

    # 6. Display Data using Expanders[cite: 1]
    if not filtered_df.empty:
        st.markdown(f'''
            <div class="header-row">
                <div class="col-item">Item (Restaurant)</div>
                <div class="col-price">Price</div>
            </div>
        ''', unsafe_allow_html=True)

        for index, row in filtered_df.iterrows():
            # Format price and handle missing values[cite: 1]
            if pd.isna(row['Price']):
                price_str = "Price TBD"
            else:
                price_str = f"${row['Price']:,.2f}"
            
            # The label shown in the list results[cite: 1]
            label = f"{row['Item']} ({row['Restaurant']}) — {price_str}"
            
            with st.expander(label):
                # Detailed content revealed on click[cite: 1]
                st.write(f"**Details:** {row['Details'] if pd.notna(row['Details']) else 'No details available.'}")
                st.caption(f"Park: {row['Park']}")
    else:
        st.warning("No items found matching those filters.")
else:
    st.error("Could not find universal_food_data.csv.")
