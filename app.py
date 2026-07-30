    with tab_home:
        st.subheader("Your Reading Snapshot")
        
        # Calculate stats safely
        read_count = len(read)
        annual_goal = 50
        progress_val = min(read_count / annual_goal, 1.0)
        
        # Stats display
        col1, col2, col3 = st.columns(3)
        col1.metric("Books Read", f"{read_count}")
        col2.metric("Annual Goal", f"{int(progress_val*100)}%")
        col3.metric("TBR Size", len(tbr))
        
        st.subheader("Progress towards goal")
        st.progress(progress_val)
        
        st.markdown("---")
        
        st.subheader("Your Next Reads")
        st.caption("A shelf of your high-priority books:")
        
        # Visual Shelf
        st.markdown('<div class="shelf-container">', unsafe_allow_html=True)
        # Showing only the top 3 high-priority books
        priority_queue = tbr.sort_values('Priority_Rank').head(3)
        for _, book in priority_queue.iterrows():
            isbn = str(book.get('ISBN13', '')).replace('=', '').replace('"', '')
            # Using OpenLibrary for cover art
            st.markdown(f'''
                <div class="book-thumb">
                    <img src="https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg" style="width:100%; border-radius:5px;">
                    <div style="font-size:0.7rem; margin-top:5px;">{book['Title'][:20]}...</div>
                </div>
            ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
