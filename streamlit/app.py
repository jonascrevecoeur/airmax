import streamlit as st
import pandas as pd
import json

import folium
import streamlit as st
from streamlit_folium import st_folium

import irceline_api 
import ui_components

st.header("POC - realtime air quality")
st.markdown(f"""
Select a phenomenon from the list below to view its current status across Belgium. 
Data and reference levels are obtained from [IRCEL-CELINE](https://www.irceline.be/nl)
""", unsafe_allow_html=True)

phenomena_available = {
    'Nitrogen dioxide - NO₂': 'Nitrogen dioxide',
    'Nitrogen monoxide - NO': 'Nitrogen monoxide',
    'Ozone - O₃': 'Ozone',
    'Amonia': 'Amonia',
    'Black carbon': 'Black Carbon',
    'Sulpher dioxide': 'Sulphur dioxide',
    'PM10': 'Particulate Matter < 10 µm',
    'PM2.5': 'Particulate Matter < 2.5 µm'
}

phenomenon_selected = phenomena_available[st.selectbox("Phenomenon:", list(phenomena_available.keys()))]

if 'measurements_json' in st.session_state:
    measurements = pd.DataFrame(json.loads(st.session_state['measurements_json']))
else:
    with st.spinner('Loading data'):
        measurements = irceline_api.get_recent_measurements('data/metadata.csv')
        st.session_state['measurements_json'] = measurements.to_json()

measurements_phenomenon = measurements[measurements['phenomenon'] == phenomenon_selected]

map = ui_components.show_map(measurements_phenomenon)

selected_location = ui_components.get_location_clicked(map, measurements_phenomenon)

if selected_location is not None:
    ui_components.show_info_table(measurements, selected_location)