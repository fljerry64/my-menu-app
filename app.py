import streamlit as st
import pandas as pd
import os

# Set page title and icon
st.set_page_config(page_title="Universal Menu", page_icon="🎢", layout="centered")

st.title("🎢 Universal Menu Search")

# 1. FIND FILE
files = [f for f in os.listdir('.') if f.endswith('.csv')]

if not files:
    st.error("📂 No CSV file found!")
else:
    target_file = files[0]
    try:
        # 2. LOAD DATA
        df = pd.read_csv(target_file).fillna("")
        
        # 3. PRICE CLEANING (For Sorting)
        # Create a hidden numeric column for sorting
        # We remove '$', commas, and handle 'N/A' or empty values
        df['numeric_price'] = (
            df['Price']
            .replace('[\$,]', '', regex=True)
            .replace('N/A', '0')
            .apply(pd.to_numeric, errors='coerce')
            .fillna(0)
        )

        # 4. SEARCH & FILTER UI
        query = st.text_input("🔍 Search for a menu item (e.g. 'chicken platter')").lower().strip()
        
        parks = ["All Parks"] + sorted(list(df['Park'].unique()))
        selected_park = st.selectbox("📍 Filter by Park", parks)

        # 5. FILTERING LOGIC
        filtered = df.copy()
        
        if selected_park != "All Parks":
            filtered = filtered[filtered['Park'] == selected_park]
        
        if query:
            search_words = query.split()
            mask = filtered['Item'].apply(
                lambda x: all(word in str(x).lower() for word in search_words)
            )
            filtered = filtered[mask]

        # 6. AUTOMATIC SORTING
        # Sort by the numeric price we created
        filtered = filtered.sort_values(by='numeric_price', ascending=True)

        st.divider()
        
        # 7. DISPLAY
        if len(filtered) == 0:
            st.warning(f"No menu items found matching '{query}'.")
        else:
            st.write(f"Showing {len(filtered)} items (Sorted: Lowest to Highest Price):")
            for index, row in filtered.iterrows():
                label = f"**{row['Item']}** — {row['Price']}"
                with st.expander(label):
                    st.markdown(f"💰 **Price:** {row['Price']}")
                    st.markdown(f"🏠 **Restaurant:** {row['Restaurant']}")
                    st.markdown(f"🌍 **Park:** {row['Park']}")
                    if row['Details'] and str(row['Details']).lower() != "nan":
                        st.info(row['Details'])

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
