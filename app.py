import streamlit as st
import pd as pd
import os

st.set_page_config(page_title="Universal Menu", page_icon="🎢", layout="centered")
st.title("🎢 Universal Menu Search")

files = [f for f in os.listdir('.') if f.endswith('.csv')]

if not files:
    st.error("📂 No CSV file found!")
else:
    target_file = files[0]
    try:
        df = pd.read_csv(target_file).fillna("")
        
        # 1. SEARCH BOX (Now targeted to Item Name only)
        query = st.text_input("🔍 Search for a menu item (e.g. 'Burger', 'Crepe')").lower().strip()
        
        # 2. PARK FILTER (Optional but helpful)
        parks = ["All Parks"] + sorted(list(df['Park'].unique()))
        selected_park = st.selectbox("📍 Filter by Park", parks)

        # 3. FILTERING LOGIC
        filtered = df.copy()
        
        # Filter by Park first
        if selected_park != "All Parks":
            filtered = filtered[filtered['Park'] == selected_park]
        
        # Search ONLY in the 'Item' column
        if query:
            filtered = filtered[filtered['Item'].str.lower().str.contains(query)]

        st.divider()
        
        # 4. DISPLAY RESULTS
        if len(filtered) == 0:
            st.warning(f"No menu items found matching '{query}'.")
        else:
            st.write(f"Showing {len(filtered)} items:")
            for index, row in filtered.iterrows():
                # Display the Restaurant name in small text above the Item
                label = f"**{row['Item']}** — {row['Price']}"
                with st.expander(label):
                    st.markdown(f"🏠 **Restaurant:** {row['Restaurant']}")
                    st.markdown(f"🌍 **Park:** {row['Park']}")
                    if row['Details'] and row['Details'].lower() != "nan":
                        st.info(row['Details'])

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
