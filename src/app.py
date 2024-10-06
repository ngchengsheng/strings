import streamlit as st
import pydeck as pdk
from datetime import datetime
import time
from api import WeatherAPI
from config import API_BASE_URL, REFRESH_INTERVAL
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Singapore Rainfall Map", page_icon="🌧️", layout="wide")

def main():
    st.title("Singapore Rainfall Map")

    api = WeatherAPI(API_BASE_URL)

    if 'last_update' not in st.session_state:
        st.session_state.last_update = None

    map_placeholder = st.empty()

    while True:
        current_time = datetime.now()

        if st.session_state.last_update is None or (current_time - st.session_state.last_update).total_seconds() >= REFRESH_INTERVAL:
            with st.spinner("Fetching latest rainfall data..."):
                rainfall_data = api.get_rainfall_data()
                parsed_data = api.parse_rainfall_data(rainfall_data)

            if parsed_data:
                st.session_state.last_update = current_time

                data = [
                    {
                        "name": info["name"],
                        "lat": info["lat"],
                        "lon": info["lon"],
                        "rainfall": info["value"]
                    }
                    for info in parsed_data.values()
                ]

                if data:
                    layer = pdk.Layer(
                        "ScatterplotLayer",
                        data,
                        get_position=["lon", "lat"],
                        get_color=[255, 0, 0, 150],
                        get_radius="rainfall * 100",
                        pickable=True,
                        opacity=0.8,
                        stroked=True,
                        filled=True,
                        radius_scale=6,
                        radius_min_pixels=3,
                        radius_max_pixels=30,
                    )

                    view_state = pdk.ViewState(
                        latitude=1.3521,
                        longitude=103.8198,
                        zoom=10,
                        pitch=0,
                    )

                    tooltip = {
                        "html": "<b>{name}</b><br/>{rainfall} mm",
                        "style": {"background": "grey", "color": "white", "font-family": '"Helvetica Neue", Arial', "z-index": "10000"},
                    }

                    r = pdk.Deck(
                        layers=[layer],
                        initial_view_state=view_state,
                        map_style="mapbox://styles/mapbox/light-v9",
                        tooltip=tooltip
                    )

                    map_placeholder.pydeck_chart(r)
                    st.write(f"Last updated: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    st.warning("No rainfall data available at the moment. The map will update when data becomes available.")
            else:
                st.error("Failed to fetch or parse rainfall data. Please check the logs for more information.")

        time.sleep(60)

if __name__ == "__main__":
    main()