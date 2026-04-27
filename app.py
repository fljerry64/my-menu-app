import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Universal Menu", page_icon="🎢", layout="centered")
st.title("🎢 Universal Menu Search")

# 1. FIND FILE
files = [f for f in os.listdir('.') if f.endswith('.csv')]

if not files:
    st.error("📂 No CSV file found!")
else:
    target_file = files[0]
    try:
        # 2. LOAD AND CLEAN DATA
        df = pd.read_csv(target_file)
        # Convert all columns to strings and strip hidden whitespace
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
        
        # 3. SEARCH INTERFACE
        query = st.text_input("🔍 Search for food (e.g. 'Burger', 'Pizza')").lower().strip()
        
        # 4. FILTERING LOGIC (Improved)
        if query:
            # Check if query exists in ANY of these columns
            mask = (
                df['Item'].str.lower().str.contains(query) | 
                df['Restaurant'].str.lower().str.contains(query) | 
                df['Details'].str.lower().str.contains(query)
            )
            filtered = df[mask]
        else:
            filtered = df.head(20) # Show first 20 if search is empty

        # 5. DISPLAY
        st.divider()
        
        if len(filtered) == 0:
            st.warning(f"No items found matching '{query}'.")
            # Debug: show column names if search fails
            st.write("Columns available:", list(df.columns))
        else:
            st.write(f"Showing {len(filtered)} results:")
            for index, row in filtered.iterrows():
                with st.expander(f"**{row['Item']}** — {row['Price']}"):
                    st.write(f"📍 **{row['Restaurant']}**")
                    st.caption(f"Park: {row['Park']}")
                    if row['Details'] and row['Details'].lower() != "nan":
                        st.info(row['Details'])

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
