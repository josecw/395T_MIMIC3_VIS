import streamlit as st
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import plotly.express as px
import os, random
from datetime import datetime

from modules.nav import sidebar

load_dotenv('.env')
DIR = os.getenv('DIR')
ICU_MAP = {'CCU':'Coronary care unit', 
        'CSRU': 'Cardiac surgery recovery unit', 
        'CMICU': 'Medical intensive care unit',
        'NICU': 'Neonatal intensive care unit',
        'NWARD': 'Neonatal ward',
        'SICU': 'Surgical intensive care unit',
        'TSICU': 'Trauma/surgical intensive care unit'
        }
SEED = random.randint(2100, 2210)

@st.cache_data
def load_data(yr_start: int, 
              yr_end: int,
              wards: list[str]) -> pd.DataFrame:
    
    patients = pd.read_csv(os.path.join(DIR, 'PATIENTS.csv.gz'), compression='gzip')
    icustays = pd.read_csv(os.path.join(DIR, 'ICUSTAYS.csv.gz'), compression='gzip')

    data =  pd.merge(patients, icustays, on='SUBJECT_ID')
    data.drop(['ROW_ID_x','ROW_ID_y'], axis=1, inplace=True)

    DATE_COLS = ['DOB','DOD','INTIME']

    for col in DATE_COLS:
        data[col] = pd.to_datetime(data[col])

    data = data[data['DOB'].dt.year >=2000]

    # Apply calculate_age function to create "age" column
    data["AGE"] = data.apply(lambda row: calculate_age(row["DOB"], 
                                                       row["DOD"], 
                                                       row['EXPIRE_FLAG'],
                                                       row['INTIME']), 
                                    axis=1)

    # Filter out rows with age greater than or equal to 120
    data = data[data["AGE"] < 120]

    data = data[(data['INTIME'].dt.year >= yr_start) & 
                (data['INTIME'].dt.year <= yr_end)]

    data = data[data['FIRST_CAREUNIT'].isin(wards)]

    return data

def calculate_age(dob, dod, expire, MAX_TS: datetime):

    if expire and dod is not None:
        age = (dod - dob).days // 365
    else:
        age = (MAX_TS - dob).days // 365
    return age

def main():

    sidebar()

    st.title('MIMIC III Visualization #5')
    st.header(f'Correlation between Age and Length Of Stay')

    with st.expander("Query Parameter", expanded=True):
        yr_start, yr_end = st.slider('Admission Year', value=[2100,2200], 
                                     min_value=2100, max_value=2200)
        container = st.container()
        all = st.checkbox("Select all", value=True)
        
        if all:
            selected_units = container.multiselect("WARD",
                ICU_MAP,ICU_MAP)
        else:
            selected_units =  container.multiselect("WARD",
                ICU_MAP)


    data_load_state = st.text('Loading data...')
    data = load_data(yr_start, yr_end, selected_units)
    data_load_state.text('')

    fig = px.scatter(data,
                     x='AGE',
                     y='LOS',
                     title=f'Correlation between {yr_start} and {yr_end}',
                     color='FIRST_CAREUNIT',
                     facet_row='GENDER',
                     #marginal_x='histogram',
                     width=1400,
                     height=800,
                     log_y=True,
                     labels=dict(FIRST_CAREUNIT='Ward', 
                                 LOS='Lenght of Stay',
                                 AGE='Age'),
                     
        )

    fig.update_xaxes(nticks=10)

    st.plotly_chart(fig)

    if st.checkbox('Show raw data'):
        st.subheader('Raw data')
        st.write(data)
    

if __name__ == '__main__':
    main()