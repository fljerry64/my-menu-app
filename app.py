import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Universal Menu", page_icon="🎢", layout="centered")
st.title("🎢 Universal Menu Search")

# Helper to turn numbers into star icons
def get_stars(rating):
    try:
        r = float(rating)
        if r <= 0: return ""
        full_stars = int(r)
        half_star = 1 if (r - full_stars) >= 0.5 else 0
        return "⭐" * full_stars + ("½" if half_star else "")
    except: return ""

files = [f for f in os.listdir('.') if f.endswith('.csv')]

if not files:
    st.error("📂 No CSV file found!")
else:
    target_file = files[0]
    try:
        df = pd.read_csv(target_file).fillna("")
        
        # Clean Price for sorting
        df['numeric_price'] = (
            df['Price'].replace('[\$,]', '', regex=True)
            .replace('N/A', '0').apply(pd.to_numeric, errors='coerce').fillna(0)
        )

        # UI Controls
        query = st.text_input("🔍 Search for a menu item").lower().strip()
        
        col1, col2 = st.columns(2)
        with col1:
            selected_park = st.selectbox("📍 Park", ["All Parks"] + sorted(list(df['Park'].unique())))
        with col2:
            sort_option = st.selectbox("⚖️ Sort by", ["Lowest Price", "Highest Rating"])

        # Filtering
        filtered = df.copy()
        if selected_park != "All Parks":
            filtered = filtered[filtered['Park'] == selected_park]
        
        if query:
            search_words = query.split()
            mask = filtered['Item'].apply(lambda x: all(word in str(x).lower() for word in search_words))
            filtered = filtered[mask]

        # Sorting Logic
        if sort_option == "Lowest Price":
            filtered = filtered.sort_values(by='numeric_price', ascending=True)
        elif sort_option == "Highest Rating":
            if 'Rating' in filtered.columns:
                filtered['temp_rate'] = pd.to_numeric(filtered['Rating'], errors='coerce').fillna(0)
                filtered = filtered.sort_values(by='temp_rate', ascending=False)

        st.divider()
        
        # Display
        if len(filtered) == 0:
            st.warning("No items found.")
        else:
            st.write(f"Showing {len(filtered)} items:")
            for index, row in filtered.iterrows():
                # 1. Create the star string
                star_text = ""
                if 'Rating' in row and str(row['Rating']).strip() != "":
                    stars = get_stars(row['Rating'])
                    star_text = f" {stars}"

                # 2. FIXED LABEL: This puts the price back in the header!
                item_label = f"{row['Item']} — {row['Price']}{star_text}"
                
                with st.expander(item_label):
                    # Big star display inside if available
                    if star_text:
                        rev_count = f"({int(row['Review_Count'])} reviews)" if 'Review_Count' in row and str(row['Review_Count']) != "" else ""
                        st.subheader(f"{star_text} {rev_count}")
                    
                    st.write(f"🏠 **Restaurant:** {row['Restaurant']}")
                    st.caption(f"🌍 **Park:** {row['Park']}")
                    if row['Details'] and str(row['Details']).lower() != "nan":
                        st.info(row['Details'])

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
