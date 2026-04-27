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
        
        # 3. SEARCH & FILTER UI
        query = st.text_input("🔍 Search for a menu item (e.g. 'Burger', 'Crepe')").lower().strip()
        
        parks = ["All Parks"] + sorted(list(df['Park'].unique()))
        selected_park = st.selectbox("📍 Filter by Park", parks)

        # 4. FILTERING LOGIC
        filtered = df.copy()
        
        if selected_park != "All Parks":
            filtered = filtered[filtered['Park'] == selected_park]
        
        if query:
            # Targeted search ONLY on the 'Item' column
            filtered = filtered[filtered['Item'].str.lower().str.contains(query)]

        st.divider()
        
        # 5. DISPLAY
        if len(filtered) == 0:
            st.warning(f"No menu items found matching '{query}'.")
        else:
            st.write(f"Showing {len(filtered)} items:")
            for index, row in filtered.iterrows():
                # Item name and price as the header
                label = f"**{row['Item']}** — {row['Price']}"
                with st.expander(label):
                    st.markdown(f"🏠 **Restaurant:** {row['Restaurant']}")
                    st.markdown(f"🌍 **Park:** {row['Park']}")
                    if row['Details'] and str(row['Details']).lower() != "nan":
                        st.info(row['Details'])

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
