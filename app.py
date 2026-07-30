import streamlit as st
import pandas as pd
import datetime

# Set Page Configuration for Mobile
st.set_page_config(
    page_title="MCM Reading Hub",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Mid-Century Modern CSS Styling
st.markdown("""
    <style>
    /* Background & Main Page */
    .stApp {
        background-color: #FDFBF7;
        color: #2C221E;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* Header Styling */
    h1, h2, h3 {
        color: #C85A32 !important;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    /* Metric Cards */
    div[data-testid="stMetricValue"] {
        color: #DDA15E !important;
        font-size: 1.8rem !important;
        font-weight: bold;
    }
    
    /* Buttons & Controls */
    .stButton>button {
        background-color: #C85A32;
        color: #FFFFFF;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        font-weight: 600;
    }

    /* Book Cards */
    .book-card {
        background-color: #F4EFEB;
        border-left: 6px solid #6B705C;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 12px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .book-title {
        font-size: 1.1rem;
        font-weight: bold;
        color: #2C221E;
        margin-bottom: 2px;
    }
    .book-author {
        font-size: 0.9rem;
        color: #6B705C;
        margin-bottom: 6px;
    }
    .mcm-badge {
        display: inline-block;
        background-color: #DDA15E;
        color: #FFFFFF;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📺 MCM Reading Hub")
st.caption("Warm Teak • Burnt Sienna • Muted Sage")

# File Upload Section
uploaded_file = st.file_uploader("Upload your Goodreads CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # Filter TBR Books
    tbr_df = df[df['Exclusive Shelf'] == 'to-read'].copy()
    
    # Calculate Total Pages
    tbr_df['Number of Pages'] = pd.to_numeric(tbr_df['Number of Pages'], errors='coerce').fillna(300)
    total_tbr_books = len(tbr_df)
    total_tbr_pages = int(tbr_df['Number of Pages'].sum())
    
    st.markdown("---")
    
    # Controls Header
    st.subheader("⚡ Reading Speed & Timeline")
    pages_per_day = st.slider("Your Average Pace (Pages / Day):", min_value=10, max_value=150, value=35, step=5)
    
    # Calculate Days & Finish Date
    days_to_finish = int(total_tbr_pages / pages_per_day)
    completion_date = datetime.date.today() + datetime.timedelta(days=days_to_finish)
    
    # Metric Display Columns
    col1, col2, col3 = st.columns(3)
    col1.metric("TBR Books", f"{total_tbr_books}")
    col2.metric("Total Pages", f"{total_tbr_pages:,}")
    col3.metric("Est. Finish Date", completion_date.strftime("%b %d, %Y"))
    
    st.markdown("---")
    st.subheader("📖 What to Read Next")
    
    # Format Selector Filter
    shelves_list = ["All Formats"] + sorted(list(set([str(s) for s in tbr_df['Bookshelves'].dropna()])))
    selected_shelf = st.selectbox("Filter by Shelf / Format Tag:", shelves_list)
    
    display_df = tbr_df.copy()
    if selected_shelf != "All Formats":
        display_df = display_df[display_df['Bookshelves'].astype(str).str.contains(selected_shelf, case=False, na=False)]
    
    # Display Books Queue
    for idx, row in display_df.head(15).iterrows():
        title = row['Title']
        author = row['Author']
        pages = int(row['Number of Pages'])
        est_days = max(1, int(pages / pages_per_day))
        isbn = str(row['ISBN13']).replace('="', '').replace('"', '').strip()
        
        cover_url = f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg" if isbn and isbn != "nan" else None
        
        col_img, col_info = st.columns([1, 3])
        with col_img:
            if cover_url:
                st.image(cover_url, use_column_width=True)
            else:
                st.markdown("📷 *No Cover*")
        with col_info:
            st.markdown(f"""
                <div class="book-card">
                    <div class="book-title">{title}</div>
                    <div class="book-author">by {author}</div>
                    <span class="mcm-badge">{pages} pages • ~{est_days} days to read</span>
                </div>
            """, unsafe_allow_html=True)

else:
    st.info("👆 Upload your `29).csv` file above to view your personalized MCM Reading Dashboard!")
  
