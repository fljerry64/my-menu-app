import streamlit as st
import pandas as pd
import os

# --- PAGE CONFIG & CUSTOM STYLING ---
st.set_page_config(page_title="Frank's Universal Food Guide", page_icon="🎢", layout="centered")

# Professional UI styling
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

st.title("🍔 Frank's Universal Food Guide")
st.markdown("---")

# --- HELPER FUNCTIONS ---
def get_stars(rating):
    """Converts numeric rating string to star emojis."""
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
    st.error("📂 No CSV file found in your GitHub repository!")
else:
    target_file = files[0]
    try:
        # Load and clean data headers/content
        df = pd.read_csv(target_file, keep_default_na=False)
        df.columns = [c.strip() for c in df.columns]
        
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace(['nan', 'NaN', 'N/A', 'n/a', 'None', 'null'], '')

        # Create numeric price for sorting
        if 'Price' in df.columns:
            df['numeric_price'] = (
                df['Price'].str.replace('[\$,]', '', regex=True)
                .replace('', '0')
                .apply(pd.to_numeric, errors='coerce').fillna(0)
            )
        else:
            df['numeric_price'] = 0

        # --- SEARCH & FILTER UI ---
        query = st.text_input("🔍 What are you craving?", placeholder="Search by item name (e.g. 'Egg', 'Taco', 'Burger')")
        
        c1, c2 = st.columns(2)
        with c1:
            if 'Park' in df.columns:
                park_list = sorted([p for p in df['Park'].unique() if p])
                selected_park = st.selectbox("📍 Filter by Park", ["All Parks"] + park_list)
            else:
                selected_park = "All Parks"
        with c2:
            sort_option = st.selectbox("⚖️ Sort results", ["Lowest Price", "Highest Rating"])

        # --- FILTERING LOGIC ---
        filtered = df.copy()
        
        # 1. Park Filter
        if selected_park != "All Parks" and 'Park' in filtered.columns:
            filtered = filtered[filtered['Park'] == selected_park]
        
        # 2. Targeted Search (Fixes the "Egg" issue)
        if query:
            search_words = query.lower().split()
            # This line specifically checks the 'Item' column ONLY
            mask = filtered['Item'].str.lower().apply(lambda x: all(word in str(x) for word in search_words))
            filtered = filtered[mask]

        # 3. Sorting
        if sort_option == "Lowest Price":
            filtered = filtered.sort_values(by='numeric_price', ascending=True)
        elif sort_option == "Highest Rating" and 'Rating' in filtered.columns:
            filtered['temp_rate'] = pd.to_numeric(filtered['Rating'], errors='coerce').fillna(0)
            filtered = filtered.sort_values(by='temp_rate', ascending=False)

        st.write(f"Found **{len(filtered)}** items matching your search.")

        # --- DISPLAY RESULTS ---
        for index, row in filtered.iterrows():
            item_name = row.get('Item', 'Unknown Item')
            price = row.get('Price', '')
            rating_val = row.get('Rating', '')
            star_text = get_stars(rating_val)
            
            # Header label for the expander
            label = f"{item_name}  |  {price} {star_text}"
            
            with st.expander(label):
                # Photo Section
                if 'Image_URL' in row and row['Image_URL'].strip() != "":
                    try:
                        # Displays photo if URL is valid
                        st.image(row['Image_URL'], use_container_width=True)
                    except:
                        st.caption("📷 Photo link detected but could not be loaded.")
                
                # Info Section
                col_left, col_right = st.columns([2, 1])
                with col_left:
                    st.markdown(f"🏠 **{row.get('Restaurant', 'N/A')}**")
                    if row.get('Details'):
                        st.info(row['Details'])
                with col_right:
                    park_name = row.get('Park', '')
                    if park_name:
                        st.markdown(f'<span class="park-badge">{park_name}</span>', unsafe_allow_html=True)
                
                # Feedback Section
                st.write("---")
                user_rate = st.slider(f"Your rating for {item_name}", 1.0, 5.0, 5.0, 0.5, key=f"s_{index}")
                
                admin_email = "YOUR_EMAIL@gmail.com" # <--- Update this to your email
                email_subject = f"Review for {item_name}"
                email_body = f"Rating: {user_rate}/5 stars for {item_name} at {row.get('Restaurant')}. %0D%0A%0D%0A(Attach photo here!)"
                mailto_link = f"mailto:{admin_email}?subject={email_subject}&body={email_body}"
                
                st.markdown(f'''
                    <a href="{mailto_link}" style="text-decoration:none;">
                        <div style="background: linear-gradient(90deg, #007bff 0%, #0056b3 100%); 
                        color: white; text-align: center; padding: 12px; border-radius: 8px; 
                        font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                            📧 Submit Rating & Attach Photo
                        </div>
                    </a>
                ''', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"⚠️ App Error: {e}")
