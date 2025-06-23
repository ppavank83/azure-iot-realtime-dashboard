import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from pymongo import MongoClient
from scipy.spatial.transform import Rotation as R

# MongoDB setup
client = MongoClient("your_mongodb_connection_string_here")
db = client["iot_data"]
collection = db["sensor_logs"]

# Orientation calculation
def calculate_orientation(accX, accY, accZ, magX, magY, magZ):
    norm_acc = np.sqrt(accX**2 + accY**2 + accZ**2)
    norm_mag = np.sqrt(magX**2 + magY**2 + magZ**2)

    accX, accY, accZ = accX / norm_acc, accY / norm_acc, accZ / norm_acc
    magX, magY, magZ = magX / norm_mag, magY / norm_mag, magZ / norm_mag

    pitch = np.arcsin(-accX)
    roll = np.arctan2(accY, accZ)

    magX_comp = magX * np.cos(pitch) + magZ * np.sin(pitch)
    magY_comp = magX * np.sin(roll) * np.sin(pitch) + magY * np.cos(roll) - magZ * np.sin(roll) * np.cos(pitch)

    yaw = np.arctan2(-magY_comp, magX_comp)

    return np.degrees(pitch), np.degrees(roll), np.degrees(yaw)

# 3D phone block (cuboid) visualization
def create_3d_phone_block(pitch, roll, yaw):
    r = R.from_euler('yxz', [pitch, roll, yaw], degrees=True)

    # Define a basic phone-like block centered at origin (8 corners of a cuboid)
    w, h, d = 0.2, 0.4, 0.05  # width, height, depth
    corners = np.array([
        [-w, -h, -d], [ w, -h, -d], [ w,  h, -d], [-w,  h, -d],
        [-w, -h,  d], [ w, -h,  d], [ w,  h,  d], [-w,  h,  d]
    ])

    rotated = r.apply(corners)

    x, y, z = rotated[:,0], rotated[:,1], rotated[:,2]
    i, j, k = [0, 0, 0, 1, 1, 2, 4, 5, 6, 3, 2, 6], [1, 2, 3, 5, 6, 3, 5, 6, 7, 0, 3, 7], [2, 3, 0, 6, 7, 0, 1, 2, 3, 4, 7, 4]

    fig = go.Figure(data=[
        go.Mesh3d(x=x, y=y, z=z,
                  i=i, j=j, k=k,
                  opacity=0.6,
                  color='blue')
    ])

    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[-1, 1]),
            yaxis=dict(range=[-1, 1]),
            zaxis=dict(range=[-1, 1])
        ),
        title="3D Phone Orientation Block"
    )
    return fig

# Initialize app
app = dash.Dash(__name__)
app.title = "IoT Sensor Dashboard"

# Layout
app.layout = html.Div([
    html.H1("Sensor Dashboard", style={'textAlign': 'center'}),

    dcc.Graph(id='acceleration-plot'),
    dcc.Graph(id='gyroscope-plot'),
    dcc.Graph(id='orientation-plot'),
    dcc.Graph(id='gps-map'),

    dcc.Interval(
        id='interval-component',
        interval=1000,
        n_intervals=0
    )
])

# Callback for all graphs
@app.callback(
    Output('acceleration-plot', 'figure'),
    Output('gyroscope-plot', 'figure'),
    Output('orientation-plot', 'figure'),
    Output('gps-map', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_graphs(n):
    data = list(
        collection.find({"timestamp": {"$exists": True}})
        .sort("timestamp", -1)
        .limit(100)
    )
    df = pd.DataFrame(data)

    if df.empty:
        return {}, {}, {}, {}

    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Acceleration
    acc_fig = px.line(df, x='timestamp', y=['accX', 'accY', 'accZ'], title="Acceleration (X, Y, Z)")
    acc_fig.update_layout(transition_duration=500)

    # Gyroscope
    gyro_fig = px.line(df, x='timestamp', y=['gyroX', 'gyroY', 'gyroZ'], title="Gyroscope (X, Y, Z)")
    gyro_fig.update_layout(transition_duration=500)

    # Orientation
    latest = df.iloc[0]
    pitch, roll, yaw = calculate_orientation(latest['accX'], latest['accY'], latest['accZ'], latest['magX'], latest['magY'], latest['magZ'])
    orientation_fig = create_3d_phone_block(pitch, roll, yaw)

    # GPS Map
    map_fig = px.scatter_mapbox(df, lat="gpsLat", lon="gpsLon", zoom=15, height=300, title="Phone GPS Location")
    map_fig.update_layout(mapbox_style="open-street-map")

    return acc_fig, gyro_fig, orientation_fig, map_fig

if __name__ == '__main__':
    app.run(debug=True)
