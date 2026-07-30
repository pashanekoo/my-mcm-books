import streamlit as st
import pandas as pd
import datetime
import re

# Page Configuration
st.set_page_config(page_title="MCM Reading Hub", page_icon="📚", layout="wide")

# CSS Styling
st.markdown("""
    <style>
    .stApp { background-color: #FDFBF7; color: #2C221E; }
    h1, h2, h3 { color: #C85A32 !important; font-weight: 700; }
    .book-card { background-color: #F4EFEB; border-left: 5px solid #6B705C; border-radius: 10px; padding: 12px; margin-bottom: 12px; }
    .book-title { font-size: 1.05rem; font-weight: bold; color: #2C221E; }
    .book-author { font-size: 0.85rem; color: #6B705C; }
    </style>
""", unsafe_allow_html=True)

st.title("📺 MCM Reading Hub")

# Tabs
tab_home, tab_next, tab_timeline, tab_shelves, tab_upload = st.tabs([
    "🏠 Home", "🎯 Mix", "📊 Timeline", "📚 Shelves", "⚙️ Settings"
])

def extract_series_num(title):
    match = re.search(r'#(\d+)', str(title))
    return int(match.group(1)) if match else 1

with tab_upload:
    st.subheader("⚙️ Data & App Settings")
    uploaded_file = st.file_uploader("Upload your Goodreads CSV", type=["csv"])
    if uploaded_file is not None:
        st.session_state['df'] = pd.read_csv(uploaded_file)
        st.success("CSV loaded!")
    st.link_button("🔗 Edit Code on GitHub", "https://github.com/", use_container_width=True)

if 'df' in st.session_state:
    df = st.session_state['df']
    tbr_df = df[df['Exclusive Shelf'] == 'to-read'].copy()
    read_df = df[df['Exclusive Shelf'] == 'read'].copy()
    
    tbr_df['Pages'] = pd.to_numeric(tbr_df['Number of Pages'], errors='coerce').fillna(300)
    tbr_df['Series_Num'] = tbr_df['Title'].apply(extract_series_num)
    tbr_df['Priority_Rank'] = tbr_df['Bookshelves'].apply(lambda x: 1 if 'sooner' in str(x).lower() else (2 if 'soon' in str(x).lower() else (3 if any(y in str(x).lower() for y in ['home-library', 'kindle']) else 4)))
    
    valid_tbr = []
    read_titles = " ".join(read_df['Title'].dropna().tolist()).lower()
    for idx, row in tbr_df.iterrows():
        if row['Series_Num'] == 1 or row['Title'].split('(')[0].strip().lower() in read_titles:
            valid_tbr.append(row)
    valid_tbr_df = pd.DataFrame(valid_tbr) if valid_tbr else tbr_df

    with tab_home:
        c1, c2, c3 = st.columns(3)
        c1.metric("Books", f"{len(valid_tbr_df)}")
        c2.metric("Priority", f"{len(valid_tbr_df[valid_tbr_df['Priority_Rank']==1])}")
        c3.metric("Owned", f"{len(valid_tbr_df[valid_tbr_df['Priority_Rank']<=3])}")
        st.subheader("🌟 Top Priority")
        for idx, row in valid_tbr_df.sort_values('Priority_Rank').head(3).iterrows():
            st.markdown(f'<div class="book-card"><div class="book-title">{row["Title"]}</div><div class="book-author">by {row["Author"]}</div></div>', unsafe_allow_html=True)

    with tab_next:
        st.subheader("🎨 Balanced Mix")
        for idx, row in valid_tbr_df.sort_values('Priority_Rank').head(5).iterrows():
            st.markdown(f'<div class="book-card"><div class="book-title">{row["Title"]}</div></div>', unsafe_allow_html=True)

    with tab_timeline:
        st.subheader("📊 Timeline")
        pace = st.slider("Pages/Day", 10, 150, 35)
        days = int(valid_tbr_df['Pages'].sum() / pace)
        st.metric("Projected Finish", (datetime.date.today() + datetime.timedelta(days=days)).strftime("%b %Y"))

    with tab_shelves:
        st.subheader("📚 Shelf Breakdown")
        if st.checkbox("Show Owned Books"):
            st.write(valid_tbr_df[valid_tbr_df['Priority_Rank'] <= 3][['Title', 'Author']])
            
