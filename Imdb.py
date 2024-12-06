# -*- coding: utf-8 -*-
"""
Created on Fri Dec  6 17:02:11 2024

@author: HP
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 10:34:00 2024

@author: Sharfan
"""

import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import base64
from io import BytesIO
from PIL import Image
from plotly import graph_objects as go
from plotly import express as px
import numpy as np
import pandas as pd

# Load dataset
file_path = r"C:\Users\HP\Desktop\HND\Dash\lce mat\imdb_top_1000.csv"  # Replace with your file path
imdb_df = pd.read_csv(file_path)

# Preprocess the dataset
imdb_df['Released_Year'] = pd.to_numeric(imdb_df['Released_Year'], errors='coerce')
imdb_df['Gross'] = imdb_df['Gross'].str.replace(',', '').astype(float, errors='ignore')

# Handle NaN values in 'Gross' column for scatter plot
imdb_df['Gross'] = imdb_df['Gross'].fillna(0)  # Replace NaN with 0

# Scatter plot for IMDb Rating vs Votes
fig_scatter = px.scatter(
    imdb_df,
    x="IMDB_Rating",
    y="No_of_Votes",
    size="Gross",  # 'Gross' now has no NaN values
    color="Genre",
    hover_name="Series_Title",
    title="IMDb Ratings vs Number of Votes",
    labels={"IMDB_Rating": "IMDb Rating", "No_of_Votes": "Number of Votes"}
)


app = dash.Dash()
app.title = "IMDb Dashboard"

# Tabs layout
tab_1 = html.Div([
    html.H2("Input Section", className='head_section'),
    html.Div([
        html.Div("Name: "),
        dcc.Input(id='name_input', type='text', placeholder='Type your name here')
    ]),
    html.Div([
        html.Div("Favorite Genre: "),
        dcc.Input(id='genre_input', type='text', placeholder='Type your favorite genre here')
    ]),
    html.Div(id='output_name'),
    html.Div(id='output_genre')
])

upload_comp = dcc.Upload(
    id='upload-image',
    children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
    style={
        'width': '100%',
        'height': '60px',
        'lineHeight': '60px',
        'borderWidth': '1px',
        'borderStyle': 'dashed',
        'borderRadius': '5px',
        'textAlign': 'center',
        'margin': '10px'
    },
    multiple=False
)

tab_2 = html.Div([
    upload_comp,
    html.Div(id='graph_output_container'),
    dcc.Slider(0, 100, 10, value=0, id='image_brightness_slider'),
    dcc.Store(id='numpy_image_matrix')
])

tab_3 = html.Div([
    html.H1("Movie Trends"),
    dcc.Graph(id='scatter_plot', figure=fig_scatter),
    html.Div("Select Genre:"),
    dcc.Dropdown(
        id='genre_dropdown',
        options=[{"label": genre, "value": genre} for genre in imdb_df['Genre'].unique()],
        value=None,
        multi=True,
        placeholder="Filter by genre"
    ),
    dcc.Graph(id='genre_trend_plot')
])

app.layout = html.Div([
    html.H1("IMDb Movie Dashboard", className='head_section'),
    html.Div("A Dash Application for IMDb Top 1000 Movies"),
    dcc.Tabs(id='tabs', value='profile', children=[
        dcc.Tab(label='Profile', value='profile', children=tab_1),
        dcc.Tab(label='Visualizer', value='visualizer', children=tab_2),
        dcc.Tab(label='Charts', value='charts', children=tab_3)
    ])
])

# Callbacks for interactivity
@app.callback(
    [Output('output_name', 'children'),
     Output('output_genre', 'children')],
    [Input('genre_input', 'value')],
    State('name_input', 'value')
)
def greet_user(favorite_genre, name):
    greeting = f"Hi {name}, welcome to the IMDb Dashboard!"
    genre_msg = f"Your favorite genre is {favorite_genre}."
    return greeting, genre_msg

@app.callback(
    [Output('graph_output_container', 'children'),
     Output('numpy_image_matrix', 'data')],
    [Input('upload-image', 'contents')],
    [State('upload-image', 'filename')]
)
def display_image(uploaded_file, filename):
    if uploaded_file:
        binary_file_content = uploaded_file.split(',')[1]
        decoded_file = base64.b64decode(binary_file_content)
        bytes_file = BytesIO(decoded_file)
        img = Image.open(bytes_file).convert('RGB')
        img_matrix = np.array(img).tolist()
        fig = go.Figure(go.Image(z=np.array(img)))
        fig.update_layout(title=filename)
        fig.update_xaxes(showticklabels=False)
        fig.update_yaxes(showticklabels=False)
        return dcc.Graph(figure=fig), {"img_matrix": img_matrix, "filename": filename}
    return None, None

@app.callback(
    Output('scatter_plot', 'figure'),
    Input('genre_dropdown', 'value')
)
def update_scatter_plot(selected_genres):
    filtered_df = imdb_df if not selected_genres else imdb_df[imdb_df['Genre'].isin(selected_genres)]
    return px.scatter(
        filtered_df,
        x="IMDB_Rating",
        y="No_of_Votes",
        size="Gross",
        color="Genre",
        hover_name="Series_Title",
        title="IMDb Ratings vs Number of Votes"
    )

if __name__ == '__main__':
    app.run_server(port=2303)