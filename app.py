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
        # LOAD DATA - keep_default_na=False is the 'nan' killer
        df = pd.read_csv(target_file, keep_default_na=False)
        
        # CLEANING
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace(['nan', 'NaN', 'N/A', 'n/a', 'None', 'null'], '')

        # NUMERIC PRICE
        df['numeric_price'] = (
            df['Price'].str.replace('[\$,]', '', regex=True)
            .replace('', '0')
            .apply(pd.to_numeric, errors='coerce').fillna(0)
        )

        # UI CONTROLS
        query = st.text_input("🔍 Search for a menu item").lower().strip()
        
        col1, col2 = st.columns(2)
        with col1:
            selected_park = st.selectbox("📍 Park", ["All Parks"] + sorted([p for p in df['Park'].unique() if p]))
        with col2:
            sort_option = st.selectbox("⚖️ Sort by", ["Lowest Price", "Highest Rating"])

        # FILTERING
        filtered = df.copy()
        if selected_park != "All Parks":
            filtered = filtered[filtered['Park'] == selected_park]
        
        if query:
            search_words = query.split()
            mask = filtered['Item'].apply(lambda x: all(word in str(x).lower() for word in search_words))
            filtered = filtered[mask]

        # SORTING
        if sort_option == "Lowest Price":
            filtered = filtered.sort_values(by='numeric_price', ascending=True)
        elif sort_option == "Highest Rating":
            if 'Rating' in filtered.columns:
                filtered['temp_rate'] = pd.to_numeric(filtered['Rating'], errors='coerce').fillna(0)
                filtered = filtered.sort_values(by='temp_rate', ascending=False)

        st.divider()
        
        # DISPLAY
        if len(filtered) == 0:
            st.warning("No items found.")
        else:
            for index, row in filtered.iterrows():
                item_name = row['Item']
                price_val = row['Price']
                price_display = f" — {price_val}" if price_val != "" else ""
                
                star_display = ""
                if 'Rating' in row and row['Rating'] != "":
                    star_display = f" {get_stars(row['Rating'])}"

                item_label = f"{item_name}{price_display}{star_display}"
                
                with st.expander(item_label):
                    # Show current rating
                    if star_display:
                        try:
                            r_count = row['Review_Count']
                            rev_text = f"({int(float(r_count))} reviews)" if r_count != "" and float(r_count) > 0 else ""
                            st.subheader(f"{star_display} {rev_text}")
                        except:
                            st.subheader(star_display)
                    
                    st.write(f"🏠 **Restaurant:** {row['Restaurant']}")
                    st.caption(f"🌍 **Park:** {row['Park']}")
                    
                    if row['Details'] != "":
                        st.info(row['Details'])

                    # NEW: MANUAL RATING SECTION
                    st.write("---")
                    st.write("📝 **Record your own rating:**")
                    user_rate = st.slider(f"Rate {item_name}", 1.0, 5.0, 5.0, 0.5, key=f"slide_{index}")
                    
                    # Create a mailto link that pre-fills an email with the rating
                    # Replace 'YOUR_EMAIL@gmail.com' with your actual email
                    email_body = f"I want to rate {item_name} at {row['Restaurant']} a {user_rate} stars!"
                    mailto_link = f"mailto:YOUR_EMAIL@gmail.com?subject=New Rating for {item_name}&body={email_body}"
                    
                    st.markdown(f'<a href="{mailto_link}" target="_blank" style="text-decoration: none;"><button style="background-color: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;">Send Rating to Admin</button></a>', unsafe_index=True, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"⚠️ App Error: {e}")
