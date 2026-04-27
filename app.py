import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Universal Menu", page_icon="🎢", layout="centered")
st.title("🎢 Universal Menu Search")

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
        # 1. LOAD DATA
        df = pd.read_csv(target_file)
        
        # 2. CLEAN DATA (Removing the 'nan' issue)
        # We fill empty cells with an empty string so they don't show 'nan'
        df = df.fillna("")
        df = df.applymap(lambda x: str(x).strip() if isinstance(x, str) else x)
        
        # 3. CLEAN PRICE FOR SORTING
        df['numeric_price'] = (
            df['Price'].replace('[\$,]', '', regex=True)
            .replace(['N/A', '', 'nan'], '0')
            .apply(pd.to_numeric, errors='coerce').fillna(0)
        )

        # 4. UI CONTROLS
        query = st.text_input("🔍 Search for a menu item").lower().strip()
        
        col1, col2 = st.columns(2)
        with col1:
            selected_park = st.selectbox("📍 Park", ["All Parks"] + sorted(list(df['Park'].unique())))
        with col2:
            sort_option = st.selectbox("⚖️ Sort by", ["Lowest Price", "Highest Rating"])

        # 5. FILTERING
        filtered = df.copy()
        if selected_park != "All Parks":
            filtered = filtered[filtered['Park'] == selected_park]
        
        if query:
            search_words = query.split()
            mask = filtered['Item'].apply(lambda x: all(word in str(x).lower() for word in search_words))
            filtered = filtered[mask]

        # 6. SORTING
        if sort_option == "Lowest Price":
            filtered = filtered.sort_values(by='numeric_price', ascending=True)
        elif sort_option == "Highest Rating":
            if 'Rating' in filtered.columns:
                filtered['temp_rate'] = pd.to_numeric(filtered['Rating'], errors='coerce').fillna(0)
                filtered = filtered.sort_values(by='temp_rate', ascending=False)

        st.divider()
        
        # 7. DISPLAY
        if len(filtered) == 0:
            st.warning("No items found.")
        else:
            for index, row in filtered.iterrows():
                # Get Star String
                star_text = ""
                if 'Rating' in row and str(row['Rating']).strip() not in ["", "nan"]:
                    star_text = f" {get_stars(row['Rating'])}"

                # Header Label Fix
                raw_price = str(row['Price']).strip()
                # If price is missing or 'nan', we'll just show the item name
                price_display = f" — {raw_price}" if raw_price and raw_price.lower() != "nan" else ""
                
                item_label = f"{row['Item']}{price_display}{star_text}"
                
                with st.expander(item_label):
                    if star_text:
                        try:
                            rev_val = int(float(row['Review_Count']))
                            rev_count = f"({rev_val} reviews)"
                        except:
                            rev_count = ""
                        st.subheader(f"{star_text} {rev_count}")
                    
                    st.write(f"🏠 **Restaurant:** {row['Restaurant']}")
                    st.caption(f"🌍 **Park:** {row['Park']}")
                    if row['Details'] and str(row['Details']).lower() not in ["nan", ""]:
                        st.info(row['Details'])

    except Exception as e:
        st.error(f"⚠️ Error: {e}")
