import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Universal Menu", layout="centered")
st.title("🎢 Universal Menu Search")

# Check if file exists
file_name = 'Universal_Master_Menu.csv'

if not os.path.exists(file_name):
    st.error(f"❌ File not found: {file_name}")
    st.write("Files currently in your folder:", os.listdir())
else:
    try:
        df = pd.read_csv(file_name).fillna("")
        
        # Search UI
        query = st.text_input("🔍 Search for food (e.g. 'Pizza', 'Vegan')")
        park = st.selectbox("Filter by Park", ["All"] + list(df['Park'].unique()))

        filtered = df.copy()
        if park != "All":
            filtered = filtered[filtered['Park'] == park]
            
        if query:
            # This searches across ALL columns
            mask = filtered.apply(lambda row: query.lower() in row.astype(str).str.lower().values, axis=1)
            filtered = filtered[mask]

        st.write(f"Showing {len(filtered)} items")

        for _, row in filtered.iterrows():
            with st.expander(f"**{row['Item']}** - {row['Price']}"):
                st.write(f"📍 **{row['Restaurant']}** ({row['Park']})")
                if row['Details']:
                    st.info(row['Details'])
                    
    except Exception as e:
        st.error(f"⚠️ Error loading data: {e}")
