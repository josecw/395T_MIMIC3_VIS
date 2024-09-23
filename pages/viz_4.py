import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import plotly.graph_objects as go
import numpy as np
import random
import plotly.express as px
import os, warnings

from modules.nav import sidebar
DIR = os.getenv('DIR')
warnings.filterwarnings("ignore")

load_dotenv('.env')
DIR = os.getenv('DIR')
warnings.filterwarnings("ignore")


@st.cache_data
def get_lab_items():

    lab_items = pd.read_csv(os.path.join(DIR, 'D_LABITEMS.csv.gz'), compression='gzip')
  
    lab_items.drop(['ROW_ID'], axis=1, inplace=True)
    lab_items['DISPLAY'] = lab_items['CATEGORY'] + ': ' + lab_items['FLUID'] + ' - ' + lab_items['LABEL']

    return lab_items

@st.cache_data
def get_lab_readings(sampling_size: float):

    labs = pd.read_csv(os.path.join(DIR, 'LABEVENTS.csv.gz'), 
                       compression='gzip', skiprows=lambda i: i>0 and random.random() > (sampling_size/100))
    labs = labs[labs['HADM_ID'].notnull() & labs['VALUENUM'].notnull()]

    patients = pd.read_csv(os.path.join(DIR, 'PATIENTS.csv.gz'), compression='gzip')

    labs = pd.merge(labs, patients, on='SUBJECT_ID')
    
    labs_desc = pd.read_csv(os.path.join(DIR, 'D_LABITEMS.csv.gz'), compression='gzip')

    labs = pd.merge(labs, labs_desc, on='ITEMID')
    labs['DISPLAY'] = labs['CATEGORY'] + ' : ' \
                        + labs['FLUID'] + ' - ' \
                        + labs['LABEL']
    
    labs['COLOR'] = np.where(
        labs['GENDER'] == 'M', '#636EFA', '#EF553B'
    )
    
    return labs

def get_result(labs: pd.DataFrame, itemID: int):

    labs = labs[labs['ITEMID'] == itemID]

    return labs

def main():

    sidebar()

    st.title('MIMIC III Visualization #4')
    st.header(f'Diagnoses and Lab Readings')
    
    data_load_state = st.text('Loading data...')
    
    lab_options = get_lab_items().to_dict("records")

    with st.expander("Query Parameter", expanded=True):

        sampling_size = st.number_input('Sampling Size (%)', value=5, max_value=100, min_value=1)
       
        selected_item = st.selectbox("Lab Type", options=lab_options,
                     format_func=lambda items: f'{items['DISPLAY']}')

    labs = get_lab_readings(sampling_size)
    
    data_load_state.text('')

    data = get_result(labs, selected_item.get('ITEMID'))

    if len(data) == 0:
        st.write(f'No Data for {selected_item.get('DISPLAY')}')
    else:
        st.write('')

    fig = px.box(data, x="GENDER", y="VALUENUM", color="GENDER",
             notched=False, # used notched shape
             title=f'Reading of {selected_item.get('DISPLAY')}',
             points='all',
             color_discrete_sequence=px.colors.qualitative.G10,
             hover_data=["VALUEUOM"],
             log_y=False
            )

    fig.update_layout(
    yaxis=dict(
            autorange=True,
            showgrid=False,
            zeroline=True,
            dtick=5,
            gridcolor='rgb(255, 255, 255)',
            gridwidth=1,
            zerolinecolor='rgb(255, 255, 255)',
            zerolinewidth=2,
        ),
        margin=dict(
            l=40,
            r=30,
            b=80,
            t=100,
        ),
        # paper_bgcolor='rgb(243, 243, 243)',
        # plot_bgcolor='rgb(243, 243, 243)',
        showlegend=True
    )

    st.plotly_chart(fig)

    if st.checkbox('Show raw data'):
        st.subheader('Raw data')
        st.write(data)

if __name__ == '__main__':
    main()