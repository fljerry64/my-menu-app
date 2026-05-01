import streamlit as st
import pandas as pd
import os

# Page Configuration
st.set_page_config(page_title="Universal Food Guide", layout="wide")

# Load Data
@st.cache_data
def load_data():
    if os.path.exists('universal_food_data.csv'):
        return pd.read_csv('universal_food_data.csv')
    return pd.DataFrame(columns=['name', 'park', 'meal_type', 'price', 'rating'])

df = load_data()

st.title("🍔 Universal Orlando Food Guide")
st.write("Find the best eats and track your favorites.")

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filters")
search_query = st.sidebar.text_input("Search for food or restaurant", "")

# Use unique values from the CSV for filters
parks = ["All"] + sorted(df['park'].unique().tolist())
selected_park = st.sidebar.selectbox("Select Park", parks)

meals = ["All"] + sorted(df['meal_type'].unique().tolist())
selected_meal = st.sidebar.selectbox("Meal Type", meals)

# --- FILTER LOGIC ---
filtered_df = df.copy()

if search_query:
    filtered_df = filtered_df[filtered_df['name'].str.contains(search_query, case=False)]

if selected_park != "All":
    filtered_df = filtered_df[filtered_df['park'] == selected_park]

if selected_meal != "All":
    filtered_df = filtered_df[filtered_df['meal_type'] == selected_meal]

# Sort by price by default for value tracking
filtered_df = filtered_df.sort_values(by='price')

# --- MAIN DISPLAY ---
if not filtered_df.empty:
    # Display results in a nice table or grid
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    
    # Optional: Visual Cards
    st.divider()
    cols = st.columns(2)
    for index, row in filtered_df.iterrows():
        with cols[index % 2]:
            st.subheader(row['name'])
            st.caption(f"📍 {row['park']} | 🍴 {row['meal_type']}")
            st.write(f"**Price:** ${row['price']:.2f} | **Rating:** {row['rating']} ⭐")
else:
    st.warning("No food items found matching those filters.")

# --- FEEDBACK SECTION ---
st.divider()
st.subheader("📸 Submit a Review")
with st.form("review_form", clear_on_submit=True):
    food_name = st.selectbox("Which item did you try?", df['name'].tolist())
    user_rating = st.slider("Rating", 1, 5, 5)
    uploaded_photo = st.file_uploader("Upload a photo", type=['png', 'jpg', 'jpeg'])
    submitted = st.form_submit_button("Submit Feedback")
    
    if submitted:
        # In Streamlit, we can display success immediately
        st.success(f"Thank you for rating the {food_name}!")
        if uploaded_photo:
            st.image(uploaded_photo, caption="Your uploaded photo", width=200)