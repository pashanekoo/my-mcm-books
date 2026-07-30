import streamlit as st
import pandas as pd
import datetime
import os

st.set_page_config(page_title="MCM Reading Hub", page_icon="📚", layout="wide")

# Persistent Storage
DATA_FILE = "books.csv"
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = None

# Custom CSS for MCM Look
st.markdown("""
    <style>
    .stApp { background-color: #FDFBF7; color: #2C221E; }
    .shelf-container { display: flex; gap: 10px; overflow-x: auto; padding: 10px; background: #EADBC8; border-radius: 10px; }
    .book-thumb { width: 100px; flex-shrink: 0; }
    </style>
""", unsafe_allow_html=True)

st.title("📺 MCM Reading Hub")
tab_home, tab_mix, tab_timeline, tab_shelves, tab_upload = st.tabs(["🏠 Home", "🎯 Mix", "📊 Timeline", "📚 Shelves", "⚙️ Upload"])

# Upload Tab
with tab_upload:
    uploaded = st.file_uploader("Update your Goodreads CSV", type=["csv"])
    if uploaded:
        df = pd.read_csv(uploaded)
        df.to_csv(DATA_FILE, index=False)
        st.success("Library updated!")

if df is not None:
    tbr = df[df['Exclusive Shelf'] == 'to-read'].copy()
    read = df[df['Exclusive Shelf'] == 'read'].copy()

    # Home Tab
    with tab_home:
        st.subheader("Progress")
        st.progress(len(read) / 50) # Assuming 50 book annual goal
        st.write(f"**Books Read:** {len(read)} | **TBR:** {len(tbr)}")
        
        st.subheader("Your Active Shelf")
        st.markdown('<div class="shelf-container">', unsafe_allow_html=True)
        for _, book in tbr.head(5).iterrows():
            isbn = str(book.get('ISBN13', '')).replace('=', '').replace('"', '')
            st.markdown(f'<div class="book-thumb"><img src="https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg" width="90"></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Mix Tab (The Planner)
    with tab_mix:
        st.subheader("Plan Your Next Reads")
        for i in range(3):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.selectbox(f"Book {i+1}", tbr['Title'].tolist(), key=f"b{i}")
            with col2:
                st.selectbox("Format", ["Print", "Kindle", "Audiobook"], key=f"f{i}")

    # Timeline Tab
    with tab_timeline:
        st.subheader("Reading Stats")
        avg_pace = st.number_input("Pages you read per day:", value=30)
        total_pages = tbr['Number of Pages'].fillna(300).sum()
        st.metric("Est. Finish TBR", f"{(total_pages/avg_pace)/365:.1f} Years")

    # Shelves Tab
    with tab_shelves:
        selected_shelf = st.selectbox("Select Shelf:", df['Bookshelves'].dropna().unique())
        st.write(df[df['Bookshelves'].str.contains(selected_shelf, na=False)][['Title', 'Author']])

else:
    st.info("Upload your Goodreads CSV to begin.")
    
