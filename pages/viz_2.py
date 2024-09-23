import streamlit as st
from dotenv import load_dotenv
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import seaborn as sns
import os

from modules.nav import sidebar

load_dotenv('.env')
dir = os.getenv('DIR')
DATE_COLUMNS = ['intime', 'outtime']
DAYS = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday', 'Sunday']

@st.cache_data
def get_dataset(name) -> pd.date_range:

    # Load ICUSTAYS data
    data = pd.read_csv(os.path.join(dir, f'{name}.csv.gz'), compression='gzip')
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)

    for COL in DATE_COLUMNS:
        data[COL] = pd.to_datetime(data[COL])

    return data

def get_pivot(data: pd.DataFrame , input_yr: int, 
              selected_units: list[str]) -> pd.date_range:

    # Load ICUSTAYS data
    filtered_data = data[data['intime'].dt.year == input_yr]

    if selected_units:
        pivot_table = filtered_data[filtered_data['first_careunit'].isin(selected_units)]
    else:
        pivot_table = filtered_data
    
    pivot_table['inweekday'] = pivot_table['intime'].dt.day_name()
    pivot_table['inhour'] = pivot_table['intime'].dt.round('h').dt.hour
    pivot_table['inyear'] = pivot_table['intime'].dt.year

    pivot_table = pivot_table.groupby([ 'inweekday','inhour',]).size().unstack().reindex(DAYS, )

    return pivot_table

def main():

    sidebar()

    data = get_dataset('ICUSTAYS')

    st.title('MIMIC III Visualization #2')

    st.header(f'ICU Admission Temporal Pattern')

    #yr = st.slider("Year", min(data['intime'].dt.year),)
    units = data['first_careunit'].unique()
    yr = st.slider("Year", min_value=min(data['intime'].dt.year), max_value=max(data['intime'].dt.year))
    container = st.container()
    all = st.checkbox("Select all", value=True)
    
    if all:
        selected_units = container.multiselect("Care units:",
            units,units)
    else:
        selected_units =  container.multiselect("Care units:",
            units)
        
    fig, ax = plt.subplots()
    s = sns.heatmap(get_pivot(data, yr, selected_units), ax=ax, cmap='YlOrBr')
    s.set_ylabel('Admission Day in Week')
    s.set_xlabel('Admission Hour')
    st.write(fig)
    
    if st.checkbox('Show raw data'):
        st.subheader('Raw data')
        st.write(data)

if __name__ == '__main__':
    main()