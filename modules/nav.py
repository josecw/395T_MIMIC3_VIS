import streamlit as st

def sidebar():
    # builds the sidebar menu
    with st.sidebar:
        st.page_link('app.py', label='Home')
        st.page_link('pages/viz_1.py', label='Visualization #1')
        st.page_link('pages/viz_2.py', label='Visualization #2')
        st.page_link('pages/viz_3.py', label='Visualization #3')
        st.page_link('pages/viz_4.py', label='Visualization #4')
        st.page_link('pages/viz_5.py', label='Visualization #5')
        st.page_link('pages/about.py', label='About')