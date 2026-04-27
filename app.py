import streamlit as st
import pandas as pd

st.set_page_config(page_title="Universal Menu", layout="centered")
st.title("🎢 Universal Menu Search")

# Load the data
df = pd.read_csv('Universal_Master_Menu.csv').fillna("")

# Mobile-friendly search bar
query = st.text_input("🔍 Search for food (e.g. 'Pizza', 'Vegan', 'Egg')")

# Park Filter
park = st.selectbox("Filter by Park", ["All"] + list(df['Park'].unique()))

filtered = df.copy()
if park != "All":
    filtered = filtered[filtered['Park'] == park]
if query:
    mask = filtered.apply(lambda row: query.lower() in row.astype(str).str.lower().values, axis=1)
    filtered = filtered[mask]

# Display as clean cards for mobile scrolling
st.write(f"Showing {len(filtered)} items")
for _, row in filtered.iterrows():
    with st.expander(f"**{row['Item']}** - {row['Price']}"):
        st.write(f"📍 **{row['Restaurant']}** ({row['Park']})")
        if row['Details']:
            st.info(row['Details'])