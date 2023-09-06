# Dash app to visualize scRNA-seq data quality control metrics from scanpy objects
# Shoutout to Coding-with-Adam for the initial template of the project: 
# https://github.com/Coding-with-Adam/Dash-by-Plotly/blob/master/Dash%20Components/Graph/dash-graph.py

import dash
from dash import dcc, html, Output, Input
import plotly.express as px
import pandas as pd
import dash_callback_chain
import yaml

config_path = "data/config.yaml"

# Add the read-in data from the yaml file
def read_config(filename):
    with open(filename, 'r') as yaml_file:
        config = yaml.safe_load(yaml_file)
    return config

if __name__ == "__main__":
    config = read_config(config_path)

    path_df = config.get("path_df")
    path_plotdf = config.get("path_umap")
    conditions = config.get("conditions")
    col_features = config.get("col_features")
    col_counts = config.get("col_counts")
    col_mt = config.get("col_mt")

    #print("path_df:", path_df)
    #print("path_plotdf:", path_plotdf)
    #print("conditions:", conditions)

# Import the data from .tsv files; one with QC params and one with UMAP data
df = pd.read_csv(path_df, sep="\t")
plotdf = pd.read_csv(path_plotdf, sep="\t")

# Add UMAP data of plotdf to the QC df
df["umap1"] = plotdf["X_umap-0"]
df["umap2"] = plotdf["X_umap-1"]

# Setup the app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

min_value = df[col_features].min()
max_value = df[col_features].max()

min_value_2 = df[col_counts].min()
min_value_2 = min_value_2.astype(int)
max_value_2 = df[col_counts].max()
max_value_2 = max_value_2.astype(int)

min_value_3 = df[col_mt].min()
min_value_3 = round(min_value_3, 1)
max_value_3 = df[col_mt].max()
max_value_3 = round(max_value_3, 1)

app.layout = html.Div([
    dcc.Dropdown(id='dpdn2', value=conditions, multi=True,
                 options=[{'label': x, 'value': x} for x in df.batch.unique()]),

  # Add Sliders for three QC params: N genes by counts, total amount of reads and pct MT reads
    html.Label("N Genes by Counts"),
    dcc.RangeSlider(
        id='range-slider-1',
        step=250,
        value=[min_value, max_value],
        marks={i: str(i) for i in range(min_value, max_value + 1, 250)},
    ),
    dcc.Input(id='min-slider-1', type='number', value=min_value, debounce=True),
    dcc.Input(id='max-slider-1', type='number', value=max_value, debounce=True),
    html.Label("Total Counts"),
    dcc.RangeSlider(
        id='range-slider-2',
        step=7500,
        value=[min_value_2, max_value_2],
        marks={i: str(i) for i in range(min_value_2, max_value_2 + 1, 7500)},
    ),
    dcc.Input(id='min-slider-2', type='number', value=min_value_2, debounce=True),
    dcc.Input(id='max-slider-2', type='number', value=max_value_2, debounce=True),
    html.Label("Percent Mitochondrial Genes"),
    dcc.RangeSlider(
        id='range-slider-3',
        step=0.1,
        min=0,
        max=1,
        value=[min_value_3, max_value_3],
    ),
    dcc.Input(id='min-slider-3', type='number', value=min_value_3, debounce=True),
    dcc.Input(id='max-slider-3', type='number', value=max_value_3, debounce=True),
    html.Div([
        dcc.Graph(id='pie-graph', figure={}, className='six columns'),
        dcc.Graph(id='my-graph', figure={}, clickData=None, hoverData=None,
                  config={
                      'staticPlot': False,
                      'scrollZoom': True,
                      'doubleClick': 'reset',
                      'showTips': False,
                      'displayModeBar': True,
                      'watermark': True,
                  },
                  className='six columns'
                  )
    ]),

  # Add scatter-plots that display the UMAP values
    html.Div([
        dcc.Graph(id='scatter-plot', figure={}, className='six columns')
    ]),
    html.Div([
        dcc.Graph(id='scatter-plot-2', figure={}, className='six columns')
    ]),
    html.Div([
        dcc.Graph(id='scatter-plot-3', figure={}, className='six columns')
    ]),
    html.Div([
        dcc.Graph(id='scatter-plot-4', figure={}, className='six columns')
    ]),
])

# Define the circular callback
@app.callback(
    Output("min-slider-1", "value"),
    Output("max-slider-1", "value"),
    Output("min-slider-2", "value"),
    Output("max-slider-2", "value"),
    Output("min-slider-3", "value"),
    Output("max-slider-3", "value"),
    Input("min-slider-1", "value"),
    Input("max-slider-1", "value"),
    Input("min-slider-2", "value"),
    Input("max-slider-2", "value"),
    Input("min-slider-3", "value"),
    Input("max-slider-3", "value"),
)
def circular_callback(min_1, max_1, min_2, max_2, min_3, max_3):
    return min_1, max_1, min_2, max_2, min_3, max_3

@app.callback(
    Output('range-slider-1', 'value'),
    Output('range-slider-2', 'value'),
    Output('range-slider-3', 'value'),
    Input('min-slider-1', 'value'),
    Input('max-slider-1', 'value'),
    Input('min-slider-2', 'value'),
    Input('max-slider-2', 'value'),
    Input('min-slider-3', 'value'),
    Input('max-slider-3', 'value'),
)
def update_slider_values(min_1, max_1, min_2, max_2, min_3, max_3):
    return [min_1, max_1], [min_2, max_2], [min_3, max_3]

@app.callback(
    Output(component_id='my-graph', component_property='figure'),
    Output(component_id='pie-graph', component_property='figure'),
    Output(component_id='scatter-plot', component_property='figure'),
    Output(component_id='scatter-plot-2', component_property='figure'),
    Output(component_id='scatter-plot-3', component_property='figure'),
    Output(component_id='scatter-plot-4', component_property='figure'),  # Add this new scatter plot
    Input(component_id='dpdn2', component_property='value'),
    Input(component_id='range-slider-1', component_property='value'),
    Input(component_id='range-slider-2', component_property='value'),
    Input(component_id='range-slider-3', component_property='value')
)
def update_graph_and_pie_chart(batch_chosen, range_value_1, range_value_2, range_value_3):
    dff = df[df.batch.isin(batch_chosen) &
              (df[col_features] >= range_value_1[0]) &
              (df[col_features] <= range_value_1[1]) &
              (df[col_counts] >= range_value_2[0]) &
              (df[col_counts] <= range_value_2[1]) &
              (df[col_mt] >= range_value_3[0]) &
              (df[col_mt] <= range_value_3[1])]

    fig_violin = px.violin(data_frame=dff, x='batch', y=col_features, box=True, points="all",
                            color='batch', hover_name='batch')

    # Calculate the percentage of each category for pie chart
    category_counts = dff['batch'].value_counts(normalize=True)
    labels = category_counts.index
    values = category_counts.values * 100  # Convert to percentage

    total_cells = len(dff)  # Calculate total number of cells
    pie_title = f'Percentage of Categories (Total Cells: {total_cells})'  # Include total cells in the title

    fig_pie = px.pie(names=labels, values=values, title=pie_title)

    # Create the scatter plots
    fig_scatter = px.scatter(data_frame=dff, x='umap1', y='umap2', color='batch',
                             labels={'umap1': 'UMAP 1', 'umap2': 'UMAP 2'},
                             hover_name='batch')

    fig_scatter_2 = px.scatter(data_frame=dff, x='umap1', y='umap2', color=col_mt,
                             labels={'umap1': 'UMAP 1', 'umap2': 'UMAP 2'},
                             hover_name='batch')

    fig_scatter_3 = px.scatter(data_frame=dff, x='umap1', y='umap2', color=col_features,
                             labels={'umap1': 'UMAP 1', 'umap2': 'UMAP 2'},
                             hover_name='batch')

    fig_scatter_4 = px.scatter(data_frame=dff, x='umap1', y='umap2', color=col_counts,
                             labels={'umap1': 'UMAP 1', 'umap2': 'UMAP 2'},
                             hover_name='batch')

    return fig_violin, fig_pie, fig_scatter, fig_scatter_2, fig_scatter_3, fig_scatter_4

if __name__ == '__main__':
    app.run_server(debug=True)
