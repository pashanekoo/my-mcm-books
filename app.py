import streamlit as st
import pandas as pd
import datetime
import re
import os

# Page Configuration
st.set_page_config(page_title="MCM Reading Hub", page_icon="📚", layout="wide")

# CSS Styling
st.markdown("""
    <style>
    .stApp { background-color: #FDFBF7; color: #2C221E; }
    h1, h2, h3 { color: #C85A32 !important; font-weight: 700; }
    .book-card { background-color: #F4EFEB; border-left: 5px solid #6B705C; padding: 12px; margin-bottom: 12px; border-radius: 8px; }
    .book-title { font-size: 1.05rem; font-weight: bold; color: #2C221E; }
    .book-author { font-size: 0.85rem; color: #6B705C; }
    .shelf-container { display: flex; gap: 10px; overflow-x: auto; padding: 10px; background: #EADBC8; border-radius: 10px; }
    .book-thumb { width: 100px; flex-shrink: 0; }
    </style>
""", unsafe_allow_html=True)

st.title("📺 MCM Reading Hub")

# Persistent Data Storage
DATA_FILE = "books.csv"
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = None

tab_home, tab_next, tab_timeline, tab_shelves, tab_upload = st.tabs([
    "🏠 Home", "🎯 Mix", "📊 Timeline", "📚 Shelves", "⚙️ Settings"
])

with tab_upload:
    st.subheader("⚙️ Data & App Settings")
    uploaded_file = st.file_uploader("Upload your Goodreads CSV", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        df.to_csv(DATA_FILE, index=False)
        st.success("CSV saved!")
    st.link_button("🔗 Edit Code on GitHub", "https://github.com/", use_container_width=True)

if df is not None:
    tbr = df[df['Exclusive Shelf'] == 'to-read'].copy()
    read = df[df['Exclusive Shelf'] == 'read'].copy()
    
    with tab_home:
        st.subheader("Your Reading Snapshot")
        progress = min(len(read) / 50, 1.0)
        col1, col2, col3 = st.columns(3)
        col1.metric("Read", len(read))
        col2.metric("Goal", f"{int(progress*100)}%")
        col3.metric("TBR", len(tbr))
        st.progress(progress)
        
        st.subheader("Your Next Reads")
        st.markdown('<div class="shelf-container">', unsafe_allow_html=True)
        for _, book in tbr.head(3).iterrows():
            isbn = str(book.get('ISBN13', '')).replace('=', '').replace('"', '')
            st.markdown(f'<div class="book-thumb"><img src="https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg" style="width:100%; border-radius:5px;"></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_next:
        st.subheader("🎯 Custom Mix Queue")
        # Logic to pick 1 classic, 1 owned, 1 filler...
        for idx, row in tbr.head(5).iterrows():
            st.markdown(f'<div class="book-card"><div class="book-title">{row["Title"]}</div><div class="book-author">by {row["Author"]}</div></div>', unsafe_allow_html=True)

    with tab_timeline:
        st.subheader("📊 Timeline Calculator")
        pace = st.slider("Pages/Day", 10, 150, 35)
        days = int(tbr['Number of Pages'].fillna(300).sum() / pace)
        st.metric("Projected Finish", (datetime.date.today() + datetime.timedelta(days=days)).strftime("%b %Y"))

    with tab_shelves:
        st.subheader("📚 Shelf Breakdown")
        shelf = st.selectbox("Select Shelf:", df['Bookshelves'].dropna().unique())
        st.write(df[df['Bookshelves'].str.contains(shelf, na=False)][['Title', 'Author']])
else:
    st.info("Upload your CSV in the Settings tab to begin!")
    
