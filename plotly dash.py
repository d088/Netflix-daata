import dash
from dash import Dash, html, dcc, callback, Output, Input ,dash_table
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from plotly.offline import iplot, plot
import pandas as pd
import matplotlib as plt

# Load your data
df = pd.read_csv('IBM Data Science G2/modi_netflix_titles.csv')

# Create a Dash application
app = dash.Dash( )

Radio_options=['directors', 'shows-per-year', 'Type-distribution','countries','Ratigin_Per_Each_genre_Type']

# Calculate KPIs
total_movies = df.shape[0]
total_genres = df['genre'].nunique()
served_country=df['country'].apply(lambda x: x.split(",")[0]).value_counts().reset_index()
served_countries=served_country['country'].count()
# Define the layout of the app
app.layout = html.Div(children=[
    html.H1(children='Netflix and TV Show Data'),
    #Data table
    dash_table.DataTable(data=df.to_dict('records'), page_size=10),
    html.H1(children='Netflix and TV Show Data Dashboard'),
    #KPIs
    html.Div(children=[
        html.Div(children=[
            html.H3('Total Movies'),
            html.H2(f'{total_movies}', style={'color': 'blue'})
        ], style={'textAlign': 'center', 'padding': '20px', 'border': '1px solid black'}),
        
        html.Div(children=[
            html.H3('served countries'),
            html.H2(f'{served_countries}', style={'color': 'green'})
        ], style={'textAlign': 'center', 'padding': '20px', 'border': '1px solid black'}),
        
        html.Div(children=[
            html.H3('Total Genres'),
            html.H2(f'{total_genres}', style={'color': 'orange'})
        ], style={'textAlign': 'center', 'padding': '20px', 'border': '1px solid black'}),
    ], style={'display': 'flex', 'justifyContent': 'space-around'}),

    html.Br(),
    #Define Graphs
    dcc.RadioItems(options=Radio_options, value=Radio_options[0], id='radio'),

    dcc.Graph(figure={}, id='graph'),
    
])

@callback(
        Output(component_id='graph', component_property='figure'),
        Input(component_id='radio', component_property='value')
)
def update_graphs(selected_col):

    # Update the histogram for directories
    if selected_col== 'directors':
        directors = df.groupby(['director'])['director'].value_counts().sort_values(ascending=False).reset_index().head(15)
        directors = directors.drop(index=0).reset_index(drop=True)
        fig = px.histogram(directors, x='director',y='count', title='Distribution of director', nbins=10)

    # Update the line chart for shows per year
    elif selected_col=='shows-per-year':
        year = df.groupby(['release_year'])['release_year'].value_counts().reset_index()
        fig = px.line(year, x='release_year', y='count',markers=True, title='Shows per Year')

    # Update the pie chart for type distribution
    elif selected_col=='Type-distribution':
        fig = px.pie(df, names='type', title='Type Distribution')

    #update bar for Ratigin Per Each Show Type
    elif selected_col=='Ratigin_Per_Each_genre_Type':
        movies = df.loc[df["type"] == "Movie", "genre"].value_counts()
        tv_show = df.loc[df["type"] == "TV Show", "genre"].value_counts()

        movies_bar = go.Bar(x = movies.index, y = movies, name="Movie")
        tv_bar = go.Bar(x = tv_show.index, y = tv_show, name="Tv show")
        
        fig = make_subplots(rows=1, cols=2, shared_yaxes=True)
        fig.add_trace(movies_bar, row=1, col=1)
        fig.add_trace(tv_bar, row=1, col=2)
        fig.update_layout(height=550, width=1200, title_text="Ratigin Per Each Show Type")
        fig.update_xaxes(tickangle=90)
        iplot(fig)

    #update choropleth for ountries
    else:
        counts_country = df['country'].apply(lambda x: x.split(",")[0]).value_counts().reset_index()
        fig = px.choropleth(counts_country, locations='country',  locationmode='country names', hover_name='country', color='count',
                            color_continuous_scale='Greens', width=1200, height=500,labels={'count':'Count'})
        fig.update_layout(geo=dict(showframe=False, showcoastlines=False, projection_type='natural earth'))


    return fig
# Run the app
if __name__ == '__main__':
    app.run_server(debug=True,port=1082)