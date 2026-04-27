import streamlit as st
import pandas as pd
import os

# Set page title and icon
st.set_page_config(page_title="Universal Menu", page_icon="🎢", layout="centered")

st.title("🎢 Universal Menu Search")

# 1. FIND THE CSV FILE AUTOMATICALLY
files = [f for f in os.listdir('.') if f.endswith('.csv')]

if not files:
    st.error("📂 No CSV file found in your GitHub folder! Please upload your 'Universal_Master_Menu.csv' file.")
else:
    # Use the first CSV file found in the folder
    target_file = files[0]
    
    try:
        # Load the data
        df = pd.read_csv(target_file).fillna("")
        
        # 2. SEARCH INTERFACE
        query = st.text_input("🔍 Search for food (e.g. 'Pizza', 'Vegan', 'Taco')")
        
        # 3. FILTERING LOGIC
        filtered = df.copy()
        if query:
            # Search across all columns (Item, Restaurant, Park, Details)
            mask = filtered.apply(lambda row: query.lower() in row.astype(str).str.lower().values, axis=1)
            filtered = filtered[mask]

        # 4. RESULTS DISPLAY
        st.divider()
        
        if len(filtered) == 0:
            st.warning("No items found matching that search.")
        else:
            # Show how many items were found
            if query:
                st.write(f"Found {len(filtered)} items for '{query}':")
            else:
                st.write(f"Showing first 20 of {len(df)} total items. Use the search box to find more!")

            # Limit display to 20 items if no search is active to keep the app fast
            display_limit = len(filtered) if query else 20
            
            for i, (index, row) in enumerate(filtered.iterrows()):
                if i >= display_limit:
                    break
                
                # Each item is a clickable dropdown
                with st.expander(f"**{row['Item']}** — {row['Price']}"):
                    st.write(f"📍 **{row['Restaurant']}**")
                    st.caption(f"Park: {row['Park']}")
                    if row['Details']:
                        st.info(row['Details'])

    except Exception as e:
        st.error(f"⚠️ Error reading the CSV: {e}")
