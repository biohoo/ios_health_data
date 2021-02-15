import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
from dash.dependencies import Input, Output
import dash_cytoscape as cyto

'''
Learning from:

https://dash.plot.ly/datatable/interactivity

'''

fat_data = pd.read_csv('output_fat.csv')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
            ],
            'layout': {
                'title': 'Dash Data Visualization'
            }
        }
    ),

    cyto.Cytoscape(
            id='cytoscape-two-nodes',
            layout={'name': 'preset'},
            style={'width': '100%', 'height': '400px'},
            elements=[
                {'data': {'id': 'one', 'label': 'Node 1'}, 'position': {'x': 75, 'y': 75}},
                {'data': {'id': 'two', 'label': 'Node 2'}, 'position': {'x': 200, 'y': 200}},
                {'data': {'source': 'one', 'target': 'two'}}
            ]
        ),

    html.Div(children='Fat Data Table'),

    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i,"deletable": True, "selectable": True} for i in fat_data.columns],
        data=fat_data.to_dict('records'),
        sort_action='native',
        column_selectable="single"
    )
])



@app.callback(
    Output('table', 'style_data_conditional'),
    [Input('table', 'selected_columns')]
)
def update_styles(selected_columns):
    return [{
        'if': { 'column_id': i },
        'background_color': '#ffd2d2'
    } for i in selected_columns]


if __name__ == '__main__':
    app.run_server(debug=True)