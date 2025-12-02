import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy.spatial import ConvexHull


DATA_DIR = Path(__file__).parent


@st.cache_data
def load_data():
    zone_hour_stats = pd.read_csv(DATA_DIR / 'zone_data.csv')
    df_small = pd.read_csv(DATA_DIR / 'plot_df.csv')
    with open(DATA_DIR / 'nearest_zones.pkl', 'rb') as f:
        nearest_zones = pickle.load(f)
    return zone_hour_stats, df_small, nearest_zones


def get_plot(df_small, current_zone, suggested_zone):
    def zone_color(z):
        if z == current_zone:
            return "Current Zone"
        elif z in suggested_zone:
            return "Suggested Zone"
        else:
            return "Other Zones"

    df_plot = df_small.copy()
    df_plot["zone_type"] = df_plot["zone_id"].apply(zone_color)

    fig = px.scatter_mapbox(
        df_plot,
        lat="pickup_location_latitude",
        lon="pickup_location_longitude",
        color="zone_type",
        opacity=0.7,
        zoom=11,
        center={"lat": 37.7749, "lon": -122.4194},
        hover_data=["zone_id"],
        color_discrete_map={
            "Current Zone": "#1f77b4",
            "Suggested Zone": "#2ca02c",
            "Other Zones": '#F29AAE'
        }
    )

    for zone in df_plot['zone_id'].unique():
        zone_df = df_plot[df_plot['zone_id'] == zone]
        if len(zone_df) > 10:
            points = np.vstack((
                zone_df['pickup_location_longitude'].values,
                zone_df['pickup_location_latitude'].values
            )).T
            if points.shape[0] >= 3:
                try:
                    hull = ConvexHull(points)
                    hull_points = points[hull.vertices]
                    fig.add_trace(go.Scattermapbox(
                        lon=hull_points[:, 0],
                        lat=hull_points[:, 1],
                        mode='lines',
                        line=dict(width=2, color='black'),
                        showlegend=False
                    ))
                except Exception:
                    # convex hull sometimes fails for degenerate shapes
                    pass

    fig.update_layout(
        mapbox_style="carto-positron",
        margin={"r": 0, "t": 30, "l": 0, "b": 0}
    )

    return fig


def recommend_from_zone(zone_hour_stats, nearest_zones, current_zone, hour, metric, top_n=3):
    allowed_zones = nearest_zones.get(current_zone, [])
    hour_df = zone_hour_stats[
        (zone_hour_stats['Start_Hour'] == hour) &
        (zone_hour_stats['zone_id'].isin(allowed_zones))
    ]
    return hour_df.sort_values(metric, ascending=False).head(top_n)


def main():
    st.set_page_config(page_title='Driver Zone Recommender', layout='wide')

    zone_hour_stats, df_small, nearest_zones = load_data()

    st.title('Ride-hailing Driver Zone Recommender')
    st.markdown(
        'Predict which nearby zone a driver should move to based on a chosen metric, current zone, and hour.'
    )

    with st.sidebar:
        st.header('Query')
        zone_options = sorted(zone_hour_stats['zone_id'].unique().tolist())
        current_zone = st.selectbox('Current Zone', zone_options, index=0)
        hour = st.slider('Hour of Day', 0, 23, value=8)
        metric = st.selectbox('Driving Metric',
                              ['demand', 'avg_fare', 'avg_trip_time_min', 'income_per_min'],
                              index=0)
        top_n = st.slider('Number of suggestions', 1, 5, 3)
        st.markdown('')
        predict = st.button('Predict')
        reset = st.button('Reset')

    if 'result' not in st.session_state:
        st.session_state.result = None

    if reset:
        st.session_state.result = None
        st.rerun()

    if predict:
        res = recommend_from_zone(zone_hour_stats, nearest_zones, current_zone, hour, metric, top_n)
        st.session_state.result = dict(
            current_zone=int(current_zone),
            hour=int(hour),
            metric=metric,
            top_n=int(top_n),
            dataframe=res
        )

    if st.session_state.result:
        res = st.session_state.result['dataframe']
        suggested = res['zone_id'].tolist()

        st.subheader('Recommendations')
        st.dataframe(res.reset_index(drop=True))
        st.markdown('**Suggested zones:** ' + ', '.join(map(str, suggested)))

        st.subheader('Map View')
        fig = get_plot(df_small, st.session_state.result['current_zone'], suggested)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('---')
    if st.checkbox('Show raw data'):
        st.write('`zone_data.csv`')
        st.dataframe(zone_hour_stats.head(200))


if __name__ == '__main__':
    main()
