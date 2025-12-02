import pickle

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.spatial import ConvexHull

import plotly.io as pio
pio.renderers.default = "browser"

zone_hour_stats = pd.read_csv('zone_data.csv')
df_small = pd.read_csv('plot_df.csv')

with open("nearest_zones.pkl", "rb") as f:
    nearest_zones = pickle.load(f)


def get_plot(current_zone, suggested_zone):

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
        opacity=0.6,
        zoom=11,
        center={"lat": 37.7749, "lon": -122.4194},
        hover_data=["zone_id"],
        color_discrete_map={
            "Current Zone": "blue",
            "Suggested Zone": "green",
            "Other Zones": '#F29AAE'
        }
    )

    # ✅ ADD BOUNDARIES PER ZONE
    for zone in df_plot['zone_id'].unique():
        zone_df = df_plot[df_plot['zone_id'] == zone]

        if len(zone_df) > 10:
            points = np.vstack((
                zone_df['pickup_location_longitude'].values,
                zone_df['pickup_location_latitude'].values
            )).T

            hull = ConvexHull(points)
            hull_points = points[hull.vertices]

            fig.add_trace(go.Scattermapbox(
                lon=hull_points[:, 0],
                lat=hull_points[:, 1],
                mode='lines',
                line=dict(width=2, color='black'),
                showlegend=False
            ))

    fig.update_layout(
        mapbox_style="carto-positron",
        margin={"r": 0, "t": 30, "l": 0, "b": 0}
    )

    fig.show()


def recommend_from_zone(current_zone, hour, metric, top_n=3):

    allowed_zones = nearest_zones.get(current_zone, [])

    hour_df = zone_hour_stats[
        (zone_hour_stats['Start_Hour'] == hour) &
        (zone_hour_stats['zone_id'].isin(allowed_zones))
    ]

    return hour_df.sort_values(metric, ascending=False).head(top_n)

driver_zone = 9
# driver_zone: 0-14
metric = 'avg_trip_time_min'
# metric:avg_fare,  avg_trip_time_min,  demand,  income_per_min
hour_of_the_day = 5
# hour_of_the_day: 0-23

res = recommend_from_zone(driver_zone, 5, metric)
print(res)
get_plot(driver_zone, res.zone_id.tolist())