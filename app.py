import streamlit as st
from modules.nav import sidebar

def main():
    # builds the sidebar menu
    sidebar()

    st.title(f'395T MIMIC III Visualizations')

    st.subheader(f'Task')
    st.write('''
        Develop 5 figures to create a visual gallery based on MIMIC data using python.
    ''')

    st.subheader(f'Learning Outcomes')

    st.markdown('''
        After finishing this assignment, you should be able to say: 
        * I know how to use some visualization libraries.
        * I know how EHR data is structured.
        * I can tell a good story about healthcare using EHR data.
    ''')

    st.subheader(f'Rationale')

    st.markdown('''
        The goal of this assignment is to get familiar with the data structure of EHR data, \
        including patient, diagnosis, admission, medication and so on. \
        It also shows what kinds of simple statistics we can draw from these datasets. \
        AI in health starts from data. This is the data we are going to analyze using \
        machine learning or deep learning methods to derive valuable outputs for risk \
        prediction and better care. This assignment will help us know the details of the \
        EHR data.
    ''')

    st.subheader(f'Instructions')

    st.markdown('''
        Select from the MIMIC III dataset. If you do not have full access yet, you can use \
        demo dataLinks to an external site.. Use it to create 5 different visualizations in \
        Python. You saw examples of how to create these visualizations in Lecture \
        Series 4.2.Links to an external site. You will receive partial credit for \
        recreating exactly the same examples from the lecture. You will get full credit for \
        using different tables, visualizations, and analyses. See the rubric for more \
        information. 

        Once you complete your visualizations in Python, create a set of slides that \
        explains each one. The slides should have enough detail so that your peers could \
        rebuild your work. You can use Google Slides or PowerPoint to create these. \
        Office 365Links to an external site. is free for all UT Austin students. 
    ''')

    st.subheader(f'Submission')

    st.markdown('''
        1. Your python code file (with the link to your Github, Colab, or other codebase)  
        2. Slides with detailed instructions on how you built these visualizations

    ''')

if __name__ == '__main__':
    main()