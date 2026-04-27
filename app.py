import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Universal Menu", layout="centered")
st.title("🎢 Universal Menu Search")

# 1. FIND THE CSV FILE
# This part looks for any CSV file in your folder so names don't have to be perfect
files = [f for f in os.listdir('.') if f.endswith('.csv')]

if not files:
    st.error("📂 No CSV file found in your GitHub folder! Please upload 'Universal_Master_Menu.csv'.")
    st.write("Files found:", os.listdir('.'))
else:
    # Pick the first CSV file found
    target_file = files[0]
    
    try:
        df = pd.read_csv(target_file).fillna("")
        st.success(f"✅ Loaded {len(df)} items from {target_file}")

        # 2. SEARCH INTERFACE
        query = st.text_input("🔍 Search for food (e.g. 'Pizza', 'Vegan', 'Taco')")
        
        # 3. FILTERING
        filtered = df.copy()
        if query:
            # This looks through all text columns
            mask = filtered.apply(lambda row: query.lower() in row.astype(str).str.lower().values, axis=1)
            filtered = filtered[mask]

        # 4. RESULTS
        st.divider()
        if len(filtered) == 0:
            st.warning("No items found matching that search.")
        else:
            for _, row in filtered.iterrows():
                with st.expander(f"**{row['Item']}** — {row['Price']}"):
                    st.write(f"📍 **{row['Restaurant']}** ({row['Park']})")
                    if row['Details']:
                        st.info(row['Details'])

    except Exception as e:
        st.error(f"⚠️ Error reading the CSV: {e}")
