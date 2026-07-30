import streamlit as st
import pandas as pd
import datetime
import re

# Page Configuration for Mobile
st.set_page_config(
    page_title="MCM Reading Hub",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Mid-Century Modern Styling
st.markdown("""
    <style>
    .stApp {
        background-color: #FDFBF7;
        color: #2C221E;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    h1, h2, h3 {
        color: #C85A32 !important;
        font-weight: 700;
        margin-bottom: 4px;
    }
    
    /* Navigation Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #F4EFEB;
        padding: 6px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 42px;
        border-radius: 8px;
        color: #2C221E;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .stTabs [aria-selected="true"] {
        background-color: #C85A32 !important;
        color: #FFFFFF !important;
    }

    /* Summary Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #F4EFEB;
        border-radius: 10px;
        padding: 12px;
        border-top: 4px solid #DDA15E;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    div[data-testid="stMetricValue"] {
        color: #C85A32 !important;
        font-size: 1.5rem !important;
        font-weight: bold;
    }

    /* Book Display Cards */
    .book-card {
        background-color: #F4EFEB;
        border-left: 5px solid #6B705C;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 12px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.04);
    }
    .book-title {
        font-size: 1.05rem;
        font-weight: bold;
        color: #2C221E;
    }
    .book-author {
        font-size: 0.85rem;
        color: #6B705C;
        margin-bottom: 6px;
    }
    .badge-sooner {
        background-color: #C85A32;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.72rem;
        font-weight: bold;
    }
    .badge-owned {
        background-color: #DDA15E;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.72rem;
        font-weight: bold;
    }
    .badge-normal {
        background-color: #6B705C;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.72rem;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📺 MCM Reading Hub")
st.caption("Warm Teak • Burnt Sienna • Muted Sage")

# Define App Tabs (Home Summary First!)
tab_home, tab_next, tab_timeline, tab_shelves, tab_upload = st.tabs([
    "🏠 Home Overview", 
    "🎯 Custom Mix", 
    "📊 Finish Calculator", 
    "📚 Priority Shelves", 
    "⚙️ Settings & Upload"
])

# Helper function to extract series number
def extract_series_num(title):
    match = re.search(r'#(\d+)', str(title))
    return int(match.group(1)) if match else 1

# Tab 5: Settings & File Upload
with tab_upload:
    st.subheader("⚙️ Data & App Settings")
    uploaded_file = st.file_uploader("Upload your Goodreads CSV file (`books.csv`)", type=["csv"])
    if uploaded_file is not None:
        st.session_state['df'] = pd.read_csv(uploaded_file)
        st.success("CSV loaded successfully! Your home overview has updated.")
        
    st.markdown("---")
    st.caption("🛠️ Developer Shortcuts:")
    st.link_button("🔗 Edit App Code on GitHub", "https://github.com/", use_container_width=True)

# Process Data if available in Session State
if 'df' in st.session_state:
    df = st.session_state['df']
    
    tbr_df = df[df['Exclusive Shelf'] == 'to-read'].copy()
    read_df = df[df['Exclusive Shelf'] == 'read'].copy()
    
    tbr_df['Pages'] = pd.to_numeric(tbr_df['Number of Pages'], errors='coerce').fillna(300)
    tbr_df['Series_Num'] = tbr_df['Title'].apply(extract_series_num)
    
    def calc_priority(row):
        shelves = str(row['Bookshelves']).lower()
        if 'sooner' in shelves: return 1
        if 'soon' in shelves: return 2
        if any(x in shelves for x in ['home-library', 'kindle']): return 3
        return 4

    tbr_df['Priority_Rank'] = tbr_df.apply(calc_priority, axis=1)
    
    valid_tbr = []
    read_titles = " ".join(read_df['Title'].dropna().tolist()).lower()
    
    for idx, row in tbr_df.iterrows():
        if row['Series_Num'] == 1:
            valid_tbr.append(row)
        else:
            series_title = row['Title'].split('(')[0].strip().lower()
            if series_title in read_titles:
                valid_tbr.append(row)

    valid_tbr_df = pd.DataFrame(valid_tbr) if valid_tbr else tbr_df

    # TAB 1: HOME OVERVIEW
    with tab_home:
        total_books = len(valid_tbr_df)
        sooner_count = len(valid_tbr_df[valid_tbr_df['Priority_Rank'] == 1])
        owned_count = len(valid_tbr_df[valid_tbr_df['Priority_Rank'] <= 3])
        
        c1, c2, c3 = st.columns(3)
        c1.metric("TBR Library", f"{total_books} Books")
        c2.metric("🔥 High Priority", f"{sooner_count} Soon(er)")
        c3.metric("🏠 Owned Copies", f"{owned_count} Print/Kindle")
        
        st.markdown("---")
        st.subheader("🌟 Top Priority Read Next")
        
        top_picks = valid_tbr_df.sort_values(by=['Priority_Rank', 'Pages']).head(3)
        
        for idx, row in top_picks.iterrows():
            title = row['Title']
            author = row['Author']
            pages = int(row['Pages'])
            rank = row['Priority_Rank']
            isbn = str(row['ISBN13']).replace('="', '').replace('"', '').strip()
            cover_url = f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg" if isbn and isbn != "nan" else None
            
            col_cov, col_det = st.columns([1, 3])
            with col_cov:
                if cover_url:
                    st.image(cover_url, use_column_width=True)
                else:
                    st.write("📷 *No Cover*")
            with col_det:
                badge_class = "badge-sooner" if rank == 1 else ("badge-owned" if rank <= 3 else "badge-normal")
                badge_label = "🔥 Sooner Priority" if rank == 1 else ("🏠 Owned Copy" if rank <= 3 else "📌 TBR Pick")
                
                st.markdown(f"""
                    <div class="book-card">
                        <span class="{badge_class}">{badge_label}</span>
                        <div class="book-title" style="margin-top:6px;">{title}</div>
                        <div class="book-author">by {author}</div>
                        <span style="font-size:0.8rem; color:#6B705C;">📖 {pages} pages</span>
                    </div>
                """, unsafe_allow_html=True)

    # TAB 2: CUSTOM MIX QUEUE
    with tab_next:
        st.subheader("🎨 Your Balanced Mix Queue")
        sorted_mix = valid_tbr_df.sort_values(by=['Priority_Rank', 'Pages'])
        
        prio_pick = sorted_mix[sorted_mix['Priority_Rank'] <= 2].head(2)
        persian_pick = sorted_mix[sorted_mix['Bookshelves'].str.contains('persian', case=False, na=False)].head(1)
        filler_pick = sorted_mix[sorted_mix['Pages'] < 300].head(1)
        classic_pick = sorted_mix[sorted_mix['Bookshelves'].str.contains('classic', case=False, na=False)].head(1)
        
        mix_df = pd.concat([prio_pick, persian_pick, filler_pick, classic_pick]).drop_duplicates().head(5)
        
        for idx, row in mix_df.iterrows():
            isbn = str(row['ISBN13']).replace('="', '').replace('"', '').strip()
            cover_url = f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg" if isbn and isbn != "nan" else None
            
            col1, col2 = st.columns([1, 3])
            with col1:
                if cover_url: st.image(cover_url, use_column_width=True)
                else: st.write("📷 *No Cover*")
            with col2:
                st.markdown(f"""
                    <div class="book-card">
                        <div class="book-title">{row['Title']}</div>
                        <div class="book-author">by {row['Author']}</div>
                        <span class="badge-owned">{int(row['Pages'])} pages</span>
                    </div>
                """, unsafe_allow_html=True)

    # TAB 3: TIMELINE CALCULATOR
    with tab_timeline:
        st.subheader("📊 Projected TBR Timeline")
        pace = st.slider("Daily Reading Speed (Pages / Day):", 10, 150, 35, 5)
        
        total_pgs = int(valid_tbr_df['Pages'].sum())
        days = int(total_pgs / pace)
        finish_date = datetime.date.today() + datetime.timedelta(days=days)
        
        m1, m2 = st.columns(2)
        m1.metric("Total Pages Left", f"{total_pgs:,}")
        m2.metric("Projected Finish Date", finish_date.strftime("%b %Y"))

    # TAB 4: PRIORITY SHELVES
    with tab_shelves:
        st.subheader("📚 Shelf Breakdown")
        shelf = st.radio("Choose Category:", ["🔥 Priorities ((soon)/(sooner))", "🏠 Owned (Print/Kindle)", "🇮🇷 Persian Collection"], horizontal=True)
        
        filtered = valid_tbr_df.copy()
        if "Priorities" in shelf:
            filtered = filtered[filtered['Bookshelves'].str.contains('soon', case=False, na=False)]
        elif "Owned" in shelf:
            filtered = filtered[filtered['Bookshelves'].str.contains('home-library|kindle', case=False, na=False)]
        elif "Persian" in shelf:
            filtered = filtered[filtered['Bookshelves'].str.contains('persian', case=False, na=False)]
            
        for idx, row in filtered.head(10).iterrows():
            st.markdown(f"""
                <div class="book-card">
                    <div class="book-title">{row['Title']}</div>
                    <div class="book-author">by {row['Author']} ({int(row['Pages'])} pgs)</div>
                </div>
            """, unsafe_allow_html=True)

else:
    with tab_home:
        st.info("👆 Welcome! Please go to the **'⚙️ Settings & Upload'** tab and upload your Goodreads CSV file (
            
