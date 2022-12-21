import streamlit as st
import pandas as pd
import json
import folium
from streamlit_folium import st_folium
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

import irceline_api 
from point import Point

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

## prepare the map
m = folium.Map(location=[50.7, 5], zoom_start=7.3)

for index, row in measurements_phenomenon.iterrows():
    popup = folium.Popup(f"""
                  {row['location-name'].split(' - ')[1]} <br>
                  {row['phenomenon']}: {row['measurement']} <br>
                  #measurements in past 3 hours: {row['num-measurements']}
                  """,
                  max_width = 250)

    folium.CircleMarker(
        location = [row['latitude'], row['longitude']], 
        popup=popup,
        fill = True,
        fillOpacity=1,
        radius = 5,
        weight = 1,
        color = 'black',
        fillColor = row['reference-value-color']
    ).add_to(m)

map = st_folium(m, width = 800, height=400)

## Visualize additional statistics for the selected point
try:
    point_clicked = Point.from_dict(map["last_object_clicked"])

    if point_clicked is not None:
        for index, row in measurements_phenomenon.iterrows():
            if Point(row["latitude"], row["longitude"]).is_close_to(point_clicked):
                
                selected_location = row['location-name']
                data_location = (
                    measurements[measurements['location-name'] == selected_location].
                    filter(['phenomenon', 'measurement', 'num-measurements', 'reference-value-color']).
                    rename(columns= {'reference-value-color': 'reference'}))

                st.text(f"All measurements for {selected_location.split(' - ')[1]} averaged over the last 3 hours")

                options = GridOptionsBuilder.from_dataframe(data_location)
                options.configure_columns('reference', hide = True)

                jscode = JsCode("""
                            function(params) {
                                    return {
                                        'color': `${params.data.reference}`,
                                        'backgroundColor': "#EEE"
                                    }
                            };
                            """)

                # ${params.data.reference}
                options = options.build()
                options['getRowStyle'] = jscode

                AgGrid(
                    data_location,
                    enable_enterprise_modules = False,
                    gridOptions = options,
                    fit_columns_on_grid_load = True,
                    height = min(50 + 35 * len(data_location), 300),
                    allow_unsafe_jscode = True
                )

except TypeError:
    point_clicked = None




