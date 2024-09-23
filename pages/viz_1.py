import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from dotenv import load_dotenv
from modules.nav import sidebar
import os
import warnings

from pyvis.network import Network

load_dotenv('.env')
DIR = os.getenv('DIR')
warnings.filterwarnings("ignore")

@st.cache_data
def get_admissions() -> pd.DataFrame:

    admission = pd.read_csv(os.path.join(DIR, 'ADMISSIONS.csv.gz'), compression='gzip')
    admission['ADMITTIME'] = pd.to_datetime(admission['ADMITTIME'])
    admission.drop(['ROW_ID'], axis=1, inplace=True)

    #admission = admission[admission['ADMITTIME'].dt.year == yr]

    return admission

@st.cache_data
def get_diagnosis() -> pd.DataFrame:
    
    diagnosis = pd.read_csv(os.path.join(DIR, 'DIAGNOSES_ICD.csv.gz'), compression='gzip')
    diag_label = pd.read_csv(os.path.join(DIR, 'D_ICD_DIAGNOSES.csv.gz'), compression='gzip')

    diagnosis.drop(['ROW_ID'], axis=1, inplace=True)
    diag_label.drop(['ROW_ID'], axis=1, inplace=True)

    diagnosis = pd.merge(diagnosis, diag_label, on='ICD9_CODE')

    return diagnosis

@st.cache_data
def get_prescriptions() -> pd.DataFrame:
    
    prescriptions = pd.read_csv(os.path.join(DIR, 'PRESCRIPTIONS.csv.gz'), compression='gzip')
    prescriptions.drop(['ROW_ID'], axis=1, inplace=True)

    return prescriptions

def get_disease_in_yr(admissions: pd.DataFrame, 
                      diagnosis: pd.DataFrame,
                      yr: int):

    #disease_desc = pd.read_csv(os.path.join(DIR, 'D_ICD_DIAGNOSES.csv.gz'), compression='gzip')
    data = admissions[admissions['ADMITTIME'].dt.year == yr]
    data = pd.merge(data,diagnosis, on='HADM_ID')
    #data = pd.merge(data, disease_desc, on='ICD9_CODE')
    data.head(2)
    data = data[['ICD9_CODE', 'LONG_TITLE']]

    return data['LONG_TITLE'].unique()


def get_procs(admissions: pd.DataFrame, 
            diagnosis: pd.DataFrame,
            diagnosis_desc:str, 
            yr:int,
            top: int = 30):

    procs = pd.read_csv(os.path.join(DIR, 'PROCEDURES_ICD.csv.gz'), compression='gzip')
    procs_desc = pd.read_csv(os.path.join(DIR, 'D_ICD_PROCEDURES.csv.gz'), compression='gzip')
    
    procs.drop(['ROW_ID'], axis=1, inplace=True)
    procs_desc.drop(['ROW_ID'], axis=1, inplace=True)

    diagnosis = diagnosis[diagnosis['LONG_TITLE'].isin(diagnosis_desc)]
    admissions = admissions[admissions['ADMITTIME'].dt.year == yr]
    diagnosis = pd.merge(diagnosis, admissions, on ='HADM_ID')
    
    procs = pd.merge(procs, procs_desc, on='ICD9_CODE')
    procs = pd.merge(procs, diagnosis, on='HADM_ID')

    procs = procs.groupby(['LONG_TITLE_y','LONG_TITLE_x'])['HADM_ID'].count().reset_index()
    procs.columns = ['source','target', 'weight']
    procs['category'] = 'proc'
    procs = procs.sort_values(by='weight', ascending=False)

    return procs.head(top)


def get_drugs(admissions: pd.DataFrame, 
            diagnosis: pd.DataFrame, 
            prescriptions: pd.DataFrame,
            diagnosis_desc:str, 
            yr:int,
            top: int = 30):

    diagnosis = diagnosis[diagnosis['LONG_TITLE'].isin(diagnosis_desc)]
    
    admissions = admissions[admissions['ADMITTIME'].dt.year == yr]
    diagnosis = pd.merge(diagnosis, admissions, on ='HADM_ID')

    drugs = pd.merge(prescriptions, diagnosis, on='HADM_ID')

    drugs = drugs.groupby(['LONG_TITLE','DRUG'])['HADM_ID'].count().reset_index()
    drugs.columns = ['source','target', 'weight']
    drugs['category'] = 'drug'
    drugs = drugs.sort_values(by='weight', ascending=False)

    return drugs.head(top)

def main():

    sidebar()

    st.title('MIMIC III Visualization #1')
    st.subheader(f'Network Graph of Diseases, Drugs, and Procedures (Top 30)')
    
    data_load_state = st.text('Loading data...')
    
    adms = get_admissions()
    diags = get_diagnosis()
    prescs = get_prescriptions()

    data_load_state.text('')
    
    with st.expander("Query Parameter", expanded = True ):
        col_input_1, col_input_2 = st.columns(2)
        with col_input_1:
            yr = st.slider("Year", min_value=2100, max_value=2210)

        with col_input_2:
            max_node = st.number_input("Maximum Node", 
                                        value=30,
                                        max_value=30, 
                                        min_value=1)
        
        diag_name = st.multiselect('Diseases', 
                                   get_disease_in_yr(adms, diags, yr),
                                    max_selections=3)
        
        col_cat_1, col_cat_2 = st.columns(2)
        with col_cat_1:
            drug_ind = st.checkbox('Drugs')
                
        with col_cat_2:
            proc_ind = st.checkbox('Procedures', value=True)

    nodes = pd.DataFrame()     

    if drug_ind:
        nodes = pd.concat([
            nodes, get_drugs(adms, diags, prescs, diag_name, yr, max_node)
        ])

    if proc_ind:
        nodes = pd.concat([
            nodes, get_procs(adms, diags, diag_name, yr, max_node)
        ])

    s = nodes['source']
    t = nodes['target']
    w = nodes['weight']
    c = nodes['category']

    edges = zip(s,t,w,c)
 
    # Initiate PyVis network object
    diag_net = Network(
                       height='800px',
                       width='100%',
                       bgcolor='grey',
                       font_color='black'
                      )

    diag_net.barnes_hut() 

    for s, t, w, c in edges:
        #add nodes and edges to the graph
        diag_net.add_node(s, label=s, color='blue')
        if c == 'proc':
            diag_net.add_node(t, label=t, color='red', shape='box')
            diag_net.add_edge(s,t, color = 'red')
        else:
            diag_net.add_node(t, label=t, color='green', shape='square')
            diag_net.add_edge(s,t, color = 'green')

    # Generate network with specific layout settings
    diag_net.repulsion(
        node_distance=400,
        central_gravity=0.25,
        spring_length=100,
        spring_strength=0.20,
        damping=0.95
    )
    
    # Save and read graph as HTML file (on Streamlit Sharing)
    output = os.getenv('OUTPUT')
    diag_net.save_graph(os.path.join(output, 'pyvis_graph.html')[0:])
    HtmlFile = open(os.path.join(output, 'pyvis_graph.html'), 'r', encoding='utf-8')

    # # Load HTML file in HTML component for display on Streamlit page
    components.html(HtmlFile.read(), height=800)

    col_lg_1, col_lg_2, col_lg_3 = st.columns(3)

    with col_lg_1:
        st.markdown("""
            <span style="color:blue"> Blue Dot </span> is Diseases
        """, unsafe_allow_html=True)

    with col_lg_2:
        st.markdown("""
            <span style="color:red"> Red Rectangular </span> is Procedure
        """, unsafe_allow_html=True)

    with col_lg_3:
        st.markdown("""
            <span style="color:green"> Green Box </span> is Drug
        """, unsafe_allow_html=True)

    if st.checkbox('Show raw data'):
        st.subheader('Raw data')
        st.write(nodes)


if __name__ == '__main__':
    main()