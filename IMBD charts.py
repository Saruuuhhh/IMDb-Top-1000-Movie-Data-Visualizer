# -*- coding: utf-8 -*-
"""
Created on Fri Dec  6 17:42:30 2024

@author: Sharfan
"""

# Importing Required Libraries
import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import base64

# Read and Preprocess the Data
file_path = r"C:\Users\HP\Desktop\HND\Dash\lce mat\imdb_top_1000.csv"  # Replace with the correct dataset path
imdb_df = pd.read_csv(file_path)

# Data Cleaning
imdb_df['Released_Year'] = pd.to_numeric(imdb_df['Released_Year'], errors='coerce')
imdb_df['Gross'] = imdb_df['Gross'].str.replace(',', '').astype(float, errors='ignore').fillna(0)
imdb_df['No_of_Votes'] = imdb_df['No_of_Votes'].fillna(0)
imdb_df['IMDB_Rating'] = imdb_df['IMDB_Rating'].fillna(imdb_df['IMDB_Rating'].mean())

# Genre Count Data
genre_count = imdb_df['Genre'].value_counts().reset_index()
genre_count.columns = ['Genre', 'Count']

# Top 10 Directors by Average IMDb Rating
top_directors = imdb_df.groupby('Director')['IMDB_Rating'].mean().nlargest(10).reset_index()

# Top 10 Movies by Gross Revenue
top_gross_movies = imdb_df.nlargest(10, 'Gross')[['Series_Title', 'Gross']]

# Yearly Trends
yearly_avg_rating = imdb_df.groupby("Released_Year")['IMDB_Rating'].mean().reset_index()
yearly_total_gross = imdb_df.groupby("Released_Year")['Gross'].sum().reset_index()

# Generate Word Cloud
movie_titles = " ".join(imdb_df['Series_Title'].dropna().tolist())
wordcloud = WordCloud(width=800, height=400, background_color="white").generate(movie_titles)
img = io.BytesIO()
plt.figure(figsize=(8, 4))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.savefig(img, format='png')
img.seek(0)
wordcloud_img = base64.b64encode(img.getvalue()).decode()

# App Initialization
app = dash.Dash(__name__)
app.title = "IMDb Data Visualizer"

# Layout
app.layout = html.Div([
    html.H1("IMDb Top 1000 Movie Data Visualizer", style={'textAlign': 'center'}),
    dcc.Tabs([
        # Scatter Plots
        dcc.Tab(label="Scatter Plots", children=[
            dcc.Graph(figure=px.scatter(
                imdb_df, x="IMDB_Rating", y="No_of_Votes", size="Gross", color="Genre",
                hover_name="Series_Title", title="IMDb Ratings vs Number of Votes"
            )),
            dcc.Graph(figure=px.scatter(
                imdb_df, x="Released_Year", y="IMDB_Rating", color="Genre",
                hover_name="Series_Title", title="Released Year vs IMDb Rating"
            ))
        ]),

        # Bar Charts
        dcc.Tab(label="Bar Charts", children=[
            dcc.Graph(figure=px.bar(genre_count, x="Genre", y="Count", title="Top Genres by Count")),
            dcc.Graph(figure=px.bar(top_directors, x="Director", y="IMDB_Rating", title="Top 10 Directors by Average IMDb Rating")),
            dcc.Graph(figure=px.bar(top_gross_movies, x="Series_Title", y="Gross", title="Top 10 Movies by Gross Revenue"))
        ]),

        # Histograms
        dcc.Tab(label="Histograms", children=[
            dcc.Graph(figure=px.histogram(imdb_df, x="IMDB_Rating", nbins=20, title="Distribution of IMDb Ratings")),
            dcc.Graph(figure=px.histogram(imdb_df, x="Gross", nbins=20, title="Distribution of Gross Revenue"))
        ]),

        # Line Charts
        dcc.Tab(label="Line Charts", children=[
            dcc.Graph(figure=px.line(yearly_avg_rating, x="Released_Year", y="IMDB_Rating", title="Yearly Trend of Average IMDb Rating")),
            dcc.Graph(figure=px.line(yearly_total_gross, x="Released_Year", y="Gross", title="Yearly Trend of Total Gross Revenue"))
        ]),

        # Pie Charts
        dcc.Tab(label="Pie Charts", children=[
            dcc.Graph(figure=px.pie(imdb_df, names="Genre", title="Genre Breakdown", hole=0.4))
        ]),

        # Box Plots
        dcc.Tab(label="Box Plots", children=[
            dcc.Graph(figure=px.box(imdb_df, x="Genre", y="IMDB_Rating", title="IMDb Rating by Genre")),
            dcc.Graph(figure=px.box(imdb_df, x="Genre", y="Gross", title="Gross Revenue by Genre"))
        ]),

        # Heatmaps
        dcc.Tab(label="Heatmap", children=[
            dcc.Graph(figure=px.imshow(
                imdb_df[['IMDB_Rating', 'No_of_Votes', 'Gross']].corr(), text_auto=True,
                title="Correlation Heatmap", labels={"color": "Correlation Coefficient"}
            ))
        ]),

        # Bubble Charts
        dcc.Tab(label="Bubble Charts", children=[
            dcc.Graph(figure=px.scatter(
                imdb_df, x="IMDB_Rating", y="Gross", size="No_of_Votes", color="Genre",
                hover_name="Series_Title", title="IMDb Rating vs Gross Revenue (Bubble Size: Votes)"
            ))
        ]),

        # Tree Maps
        dcc.Tab(label="Tree Maps", children=[
            dcc.Graph(figure=px.treemap(
                imdb_df, path=["Genre"], values="Gross",
                title="Revenue Distribution by Genre"
            ))
        ]),

        # Sunburst Charts
        dcc.Tab(label="Sunburst Charts", children=[
            dcc.Graph(figure=px.sunburst(
                imdb_df, path=["Genre", "Director", "Series_Title"], values="Gross",
                title="Hierarchy of Genre -> Director -> Movie"
            ))
        ]),

        # Word Cloud
        dcc.Tab(label="Word Cloud", children=[
            html.Img(src=f"data:image/png;base64,{wordcloud_img}", style={"width": "100%"})
        ]),

        # Grouped Bar Charts
        dcc.Tab(label="Grouped Bar Charts", children=[
            dcc.Graph(figure=px.bar(
                imdb_df.groupby("Genre").agg({"IMDB_Rating": "mean", "Gross": "mean"}).reset_index(),
                x="Genre", y=["IMDB_Rating", "Gross"], barmode="group",
                title="Comparison of Average IMDb Rating and Gross Revenue by Genre"
            ))
        ])
    ])
])

# Run the App
if __name__ == "__main__":
    app.run_server(debug=True, port=8059)
