import streamlit as st
from dotenv import load_dotenv
import os

from modules.nav import sidebar

load_dotenv('.env')

NAME = os.getenv('STUDENT')
EID = os.getenv('EID')

def main():

    sidebar()
    
    st.title('Submmitted By')

    st.subheader('Student Name')
    st.text(f'{NAME}')

    st.subheader('EID')
    st.text(f'{EID}')


if __name__ == '__main__':
    main()