import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np  

def generate_table(dataframe, max_rows=5):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))],
        style={'margin':'40px'}
    )

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
df = pd.read_csv("gdplifeexp2007.csv")

data_dict = [dict(
            x=df[df['continent'] == i]['gdp per capita'],
            y=df[df['continent'] == i]['life expectancy'],
            text=df[df['continent'] == i]['country'],
            mode='markers',
            opacity=0.7,
            marker={
                'size': 15,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name=i
        ) for i in df.continent.unique()
    ]
#print(mice)
app.layout = html.Div(children=[
        html.H1(children='Power Analysis',
                    style={
                        'textAlign':'center'
                        }
                    ),
        html.Div(children=[                    
            html.Label('Variable range'),
            dcc.Input(id='id_var_range', value='9-12', type='text'),
            
            html.Label('Range of sample sizes'),
            dcc.Input( id='id_var_samples', value='0:100:500'),
            html.Label('Range of effect sizes'),
            dcc.Input( id='id_var_effects', value= '0.05:0.05:0.7'),
            html.Label('Number of repeats'),
            dcc.Input( id='id_var_repeats', value= '10'),
            html.Label('0 = classification; 1 = regression; 2 = both'),
            dcc.Input( id='id_var_analysis', value= '4'),
            html.Label('Number of cpus'),
            dcc.Input( id='id_var_cpus', value= '1'),
            ], style={'columnCount': 3}),
        
            html.Br(),        
            generate_table(df),
            html.Br(),
            
        dcc.Graph(
        id='example-graph',
        figure={
            'data': data_dict,
            'layout': dict(
                xaxis={'type': 'log', 'title': 'GDP Per Capita'},
                yaxis={'title': 'Life Expectancy'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
        }
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)