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
ICU_MAP = {'CCU':'Coronary care unit', 
        'CSRU': 'Cardiac surgery recovery unit', 
        'CMICU': 'Medical intensive care unit',
        'NICU': 'Neonatal intensive care unit',
        'NWARD': 'Neonatal ward',
        'SICU': 'Surgical intensive care unit',
        'TSICU': 'Trauma/surgical intensive care unit'
        }

@st.cache_data
def load_data() -> pd.DataFrame:

    # Load ICUSTAYS data
    data = pd.read_csv(os.path.join(dir, 'TRANSFERS.csv.gz'), compression='gzip')
    
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)

    for COL in DATE_COLUMNS:
        data[COL] = pd.to_datetime(data[COL])

    data = data[data['eventtype'] == 'transfer'].dropna()
    data = data[['subject_id', 'hadm_id', 'eventtype','prev_careunit', 'curr_careunit', 'intime', 'outtime']]
    #data = data.groupby(['prev_careunit','curr_careunit'])['subject_id'].count().reset_index()
    
    return data

def get_nodes(data :pd.DataFrame) -> list:

    nodes = list(pd.unique(data[['prev_careunit', 'curr_careunit']].values.ravel('K')))

    return nodes

def aggregate_data(data, unit, yr):

    agg = data[data['intime'].dt.year == yr]
    agg = agg.groupby(['prev_careunit','curr_careunit'])['subject_id'].count().reset_index()
    agg.columns = ['prev_careunit', 'curr_careunit', 'value']
    agg = agg[agg['prev_careunit'] != agg['curr_careunit']]
    agg = agg[agg['prev_careunit'] == unit]

    return agg

def get_chart(agg : pd.DataFrame) -> go:

    agg['prev_careunit'] = agg['prev_careunit'].map(ICU_MAP)
    agg['curr_careunit'] = agg['curr_careunit'].map(ICU_MAP)
    nodes = get_nodes(agg)
    mapping_dict = {k: v for v, k in enumerate(nodes)}

    #mapping of full data
    agg['prev_careunit'] = agg['prev_careunit'].map(mapping_dict)
    agg['curr_careunit'] = agg['curr_careunit'].map(mapping_dict)

    links_dict = agg.to_dict(orient='list')

    #Sankey Diagram Code 
    fig = go.Figure(data=[go.Sankey(
        node = dict(
        pad = 15,
        thickness = 20,
        line = dict(color = "black", width = 0.5),
        label = nodes,
        
        ),
        link = dict(
        source = links_dict["prev_careunit"],
        target = links_dict["curr_careunit"],
        value = links_dict["value"],
    
    ))])

    
    return fig

def main():

    sidebar()

    st.title('MIMIC III Visualization #3')
    st.header(f'ICU Transfer Flow')
    data_load_state = st.text('Loading data...')
    data = load_data()
    data_load_state.text('')

    nodes = get_nodes(data) 

    unit = st.selectbox('ICU Type', nodes)
    yr = st.number_input("Year", min_value=min(data['intime'].dt.year), max_value=max(data['intime'].dt.year))

    agg = aggregate_data(data, unit, yr)

    fig = get_chart(agg)

    st.plotly_chart(fig)

    if st.checkbox('Show raw data'):
        st.subheader('Raw data')
        st.write(agg)
    

    

if __name__ == '__main__':
    main()