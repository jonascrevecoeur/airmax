from __future__ import annotations

import pandas as pd
import folium
import streamlit as st
from streamlit_folium import st_folium
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

from dataclasses import dataclass
from typing import Optional

@dataclass
class Point:
    lat: float
    lon: float

    @classmethod
    def from_dict(cls, data: dict) -> Point:
        if "lat" in data:
            return cls(float(data["lat"]), float(data["lng"]))
        elif "latitude" in data:
            return cls(float(data["latitude"]), float(data["longitude"]))
        else:
            raise NotImplementedError(data.keys())

    def is_close_to(self, other: Point) -> bool:
        close_lat = self.lat - 0.0001 <= other.lat <= self.lat + 0.0001
        close_lon = self.lon - 0.0001 <= other.lon <= self.lon + 0.0001
        return close_lat and close_lon

def show_map(measurements: pd.DataFrame):

    m = folium.Map(location=[50.7, 5], zoom_start=7.3) # type: ignore

    for index, row in measurements.iterrows():
        popup = folium.Popup(f"""
                    {row['location-name'].split(' - ')[1]} <br>
                    {row['phenomenon']}: {row['measurement']} <br>
                    #measurements in past 3 hours: {row['num-measurements']}
                    """,
                    max_width = str(250))

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

    return st_folium(m, width = 800, height=400)

def get_location_clicked(map, measurements: pd.DataFrame) -> Optional[str]:

    try:
        point_clicked = Point.from_dict(map["last_object_clicked"])

        if point_clicked is not None:
            for index, row in measurements.iterrows():
                if Point(row["latitude"], row["longitude"]).is_close_to(point_clicked):
                    return row['location-name']

    except:
        pass

    return None

def show_info_table(measurements: pd.DataFrame, selected_location) -> None:

    data_location = (
        measurements[measurements['location-name'] == selected_location].
        filter(['phenomenon', 'measurement', 'num-measurements', 'reference-value-color']).
        rename(columns= {'reference-value-color': 'reference'})) # type:ignore

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