import streamlit as st
import pandas as pd
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Universal Menu", page_icon="🎢", layout="centered")
st.title("🎢 Universal Menu & Photo Guide")

# --- HELPER FUNCTIONS ---
def get_stars(rating):
    """Turns a numeric rating into star emojis."""
    try:
        r = float(rating)
        if r <= 0: return ""
        full_stars = int(r)
        half_star = 1 if (r - full_stars) >= 0.5 else 0
        return "⭐" * full_stars + ("½" if half_star else "")
    except: return ""

# --- DATA LOADING ---
files = [f for f in os.listdir('.') if f.endswith('.csv')]

if not files:
    st.error("📂 No CSV file found in the directory!")
else:
    target_file = files[0]
    try:
        # Load data with keep_default_na=False to prevent 'nan' from appearing automatically
        df = pd.read_csv(target_file, keep_default_na=False)
        
        # AGGRESSIVE CLEANING: Strip spaces and remove 'nan' strings
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace(['nan', 'NaN', 'N/A', 'n/a', 'None', 'null'], '')

        # CREATE NUMERIC PRICE: For accurate sorting (strips '$' and ',')
        df['numeric_price'] = (
            df['Price'].str.replace('[\$,]', '', regex=True)
            .replace('', '0')
            .apply(pd.to_numeric, errors='coerce').fillna(0)
        )

        # --- UI SEARCH & FILTERS ---
        query = st.text_input("🔍 Search for a menu item (e.g. 'Taco', 'Beer')").lower().strip()
        
        col1, col2 = st.columns(2)
        with col1:
            # Filter out empty park names for the dropdown
            park_list = sorted([p for p in df['Park'].unique() if p])
            selected_park = st.selectbox("📍 Park", ["All Parks"] + park_list)
        with col2:
            sort_option = st.selectbox("⚖️ Sort by", ["Lowest Price", "Highest Rating"])

        # --- FILTERING LOGIC ---
        filtered = df.copy()
        if selected_park != "All Parks":
            filtered = filtered[filtered['Park'] == selected_park]
        
        if query:
            search_words = query.split()
            mask = filtered['Item'].apply(lambda x: all(word in str(x).lower() for word in search_words))
            filtered = filtered[mask]

        # --- SORTING LOGIC ---
        if sort_option == "Lowest Price":
            filtered = filtered.sort_values(by='numeric_price', ascending=True)
        elif sort_option == "Highest Rating":
            if 'Rating' in filtered.columns:
                # Temporary column to handle math sorting
                filtered['temp_rate'] = pd.to_numeric(filtered['Rating'], errors='coerce').fillna(0)
                filtered = filtered.sort_values(by='temp_rate', ascending=False)

        st.divider()
        
        # --- DISPLAY RESULTS ---
        if len(filtered) == 0:
            st.warning("No items found matching your search.")
        else:
            st.caption(f"Showing {len(filtered)} items")
            for index, row in filtered.iterrows():
                # Build the Header
                item_name = row['Item']
                price_val = row['Price']
                price_display = f" — {price_val}" if price_val != "" else ""
                
                star_display = ""
                if 'Rating' in row and row['Rating'] != "":
                    star_display = f" {get_stars(row['Rating'])}"

                # Header Label
                item_label = f"{item_name}{price_display}{star_display}"
                
                with st.expander(item_label):
                    # 1. SHOW PHOTO (If Image_URL exists)
                    if 'Image_URL' in row and row['Image_URL'].strip() != "":
                        st.image(row['Image_URL'], use_container_width=True, caption=f"Customer photo of {item_name}")

                    # 2. SHOW RATING & REVIEWS
                    if star_display:
                        try:
                            r_count = row['Review_Count']
                            rev_text = f"({int(float(r_count))} reviews)" if r_count != "" and float(r_count) > 0 else ""
                            st.subheader(f"{star_display} {rev_text}")
                        except:
                            st.subheader(star_display)
                    
                    # 3. SHOW DETAILS
                    st.write(f"🏠 **Restaurant:** {row['Restaurant']}")
                    st.caption(f"🌍 **Park:** {row['Park']}")
                    
                    if row['Details'] != "":
                        st.info(row['Details'])

                    # 4. SUBMIT RATING & PHOTO SECTION
                    st.write("---")
                    st.write("📸 **Have a photo or rating?**")
                    user_rate = st.slider(f"Your score for {item_name}", 1.0, 5.0, 5.0, 0.5, key=f"slide_{index}")
                    
                    # EMAIL CONFIGURATION
                    admin_email = "YOUR_EMAIL@gmail.com" # <--- REPLACE THIS WITH YOUR EMAIL
                    email_subject = f"Rating & Photo for {item_name}"
                    email_body = (
                        f"I would like to rate {item_name} at {row['Restaurant']} a {user_rate} stars. %0D%0A%0D%0A"
                        "I have attached a photo of this meal for the app!"
                    )
                    mailto_link = f"mailto:{admin_email}?subject={email_subject}&body={email_body}"
                    
                    btn_html = f'''
                        <a href="{mailto_link}" target="_blank">
                            <button style="
                                background-color: #007bff; 
                                color: white; 
                                border: none; 
                                padding: 10px 20px; 
                                border-radius: 5px; 
                                cursor: pointer;
                                font-weight: bold;
                                width: 100%;">
                                📧 Submit Rating & Attach Photo
                            </button>
                        </a>
                    '''
                    st.markdown(btn_html, unsafe_allow_html=True)
                    st.caption("This will open your email app. Don't forget to attach your photo before sending!")

    except Exception as e:
        st.error(f"⚠️ App Error: {e}")
