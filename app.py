import streamlit as st
import pandas as pd
import os

# --- PAGE CONFIG & CUSTOM STYLING ---
st.set_page_config(page_title="Universal Menu Guide", page_icon="🎢", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stExpander {
        background-color: white !important;
        border-radius: 10px !important;
        border: 1px solid #e0e0e0 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    .park-badge {
        background-color: #007bff;
        color: white;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎢 Universal Food & Photo Guide")
st.markdown("---")

def get_stars(rating):
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
    st.error("📂 No CSV file found!")
else:
    target_file = files[0]
    try:
        # Load data safely
        df = pd.read_csv(target_file, keep_default_na=False)
        
        # Clean all column names (removes hidden spaces)
        df.columns = [c.strip() for c in df.columns]
        
        # Clean data cells
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace(['nan', 'NaN', 'N/A', 'n/a', 'None', 'null'], '')

        # Numeric Price for sorting
        if 'Price' in df.columns:
            df['numeric_price'] = (
                df['Price'].str.replace('[\$,]', '', regex=True)
                .replace('', '0')
                .apply(pd.to_numeric, errors='coerce').fillna(0)
            )
        else:
            df['numeric_price'] = 0

        # --- UI ---
        query = st.text_input("🔍 What are you craving?", placeholder="Search items, restaurants, or parks...")
        
        c1, c2 = st.columns(2)
        with c1:
            # Check if Park column exists
            if 'Park' in df.columns:
                park_list = sorted([p for p in df['Park'].unique() if p])
                selected_park = st.selectbox("📍 Filter by Park", ["All Parks"] + park_list)
            else:
                selected_park = "All Parks"
        with c2:
            sort_option = st.selectbox("⚖️ Sort results", ["Lowest Price", "Highest Rating"])

        # FILTERING
        filtered = df.copy()
        if selected_park != "All Parks" and 'Park' in filtered.columns:
            filtered = filtered[filtered['Park'] == selected_park]
        
        if query:
            search_words = query.lower().split()
            mask = filtered.apply(lambda row: all(word in str(row).lower() for word in search_words), axis=1)
            filtered = filtered[mask]

        # SORTING
        if sort_option == "Lowest Price" and 'numeric_price' in filtered.columns:
            filtered = filtered.sort_values(by='numeric_price', ascending=True)
        elif sort_option == "Highest Rating":
            # Only sort by rating if the column actually exists
            if 'Rating' in filtered.columns:
                filtered['temp_rate'] = pd.to_numeric(filtered['Rating'], errors='coerce').fillna(0)
                filtered = filtered.sort_values(by='temp_rate', ascending=False)

        st.write(f"Found **{len(filtered)}** items matching your search.")

        # --- DISPLAY ---
        for index, row in filtered.iterrows():
            item_name = row.get('Item', 'Unknown Item')
            price = row.get('Price', '')
            rating_val = row.get('Rating', '')
            star_text = get_stars(rating_val)
            
            label = f"{item_name}  |  {price} {star_text}"
            
            with st.expander(label):
                # 1. Image
                if 'Image_URL' in row and row['Image_URL'] != "":
                    try:
                        st.image(row['Image_URL'], use_container_width=True)
                    except:
                        st.caption("📷 Image link found but could not be loaded.")
                
                # 2. Details
                col_left, col_right = st.columns([2, 1])
                with col_left:
                    st.markdown(f"🏠 **{row.get('Restaurant', 'N/A')}**")
                    if row.get('Details'):
                        st.info(row['Details'])
                with col_right:
                    park_name = row.get('Park', '')
                    if park_name:
                        st.markdown(f'<span class="park-badge">{park_name}</span>', unsafe_allow_html=True)
                
                # 3. Rating & Photo submission
                st.write("---")
                user_rate = st.slider(f"Rate {item_name}", 1.0, 5.0, 5.0, 0.5, key=f"s_{index}")
                
                admin_email = "YOUR_EMAIL@gmail.com" 
                mailto_link = f"mailto:{admin_email}?subject=Review:{item_name}&body=Rating: {user_rate}/5. Attached is my photo!"
                
                st.markdown(f'''
                    <a href="{mailto_link}" style="text-decoration:none;">
                        <div style="background: linear-gradient(90deg, #007bff 0%, #0056b3 100%); 
                        color: white; text-align: center; padding: 12px; border-radius: 8px; 
                        font-weight: bold;">
                            📸 Submit Photo & Rating
                        </div>
                    </a>
                ''', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"⚠️ App Error: {e}")
