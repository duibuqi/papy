import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table
import pandas as pd
import numpy as np  
import base64
import io
import datetime
import plotly.express as px
import pa

def generate_table(dataframe, max_rows=5):
    if dataframe is not None:
        return html.Table(
            # Header
            [html.Tr([html.Th(col) for col in dataframe.columns])] +
            [html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))],
            style={'margin':'40px'}
        )
    else:
         return html.Div('Empty dataframe')

def parse_contents(contents, filename, date):
   
    df = None
    content_type, content_string = contents.split(',')  
    decoded = base64.b64decode(content_string) 
    try:
        if 'csv' in filename:            
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), header=None)
        elif 'xls' in filename:          
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        return None
    
    return df

app = dash.Dash(__name__)
#plotly_df = px.data.gapminder().query("country=='Canada'")
global_df = None

app.layout = html.Div(className='col-sm-12', children=[
    
        html.H3('Power Analysis', className='page-header'),
     
        html.Div(className="col-sm-6", children=[
            
            html.Div(className="panel panel-success", children=[
                html.Div('Input data file', className="panel-heading"),
                html.Div(className="panel-body", children=[
                    html.Div(className="row", children=[
                        html.Div('Upload data:', className='tablelabel col-xs-3'),
                        html.Div(className='tablevalue col-xs-5', 
                                 children=dcc.Upload(id='upload-data', children=html.Div(html.Button('Choose CSV file')))),
                        html.Div(className='tablelabel col-xs-4', id='output-data-upload')
                    ]),
                    html.Div(className='row', children=[
                        html.Div(className='tablevalue col-xs-12', children=[
                            dcc.Checklist(id='id_var_analysis',
                                options=[
                                    {'label': 'Classification', 'value': 0},
                                    {'label': 'Regression', 'value': 1}
                                ],
                                value=[0,1],
                                labelStyle={'padding':'10px'}
                            )  
                            ])
                    ]),
                    html.Div(className='row', children=[
       
                        html.Div(className='tablelabel col-xs-12', children=html.Button('Run analysis', className='btn-primary', id='submit-button', n_clicks=0))
                    ])
                ])
            ]),
            
            html.Div(id='output-state')
        ]),
        html.Div(className="col-sm-6", children=[
            
            html.Div(className="panel panel-success", children=[
                html.Div('Default parameters', className="panel-heading"),
                html.Div(className="panel-body", children=[
                    html.Div(className='row', children=[                    
                        html.Div(className='tablelabel col-xs-5', children='Variable range'),
                        html.Div(className='tablevalue col-xs-5', children=dcc.Input(id='id_var_range', value='9-12'))
                    ]),
                    html.Div(className='row', children=[    
                        html.Div(className='tablelabel col-xs-5', children='Range of sample sizes'),
                        html.Div(className='tablevalue col-xs-5', children=dcc.Input( id='id_var_samples', value='0:100:500'))
                    ]),
                    html.Div(className='row', children=[ 
                        html.Div(className='tablelabel col-xs-5', children='Range of effect sizes'),
                        html.Div(className='tablevalue col-xs-5', children=dcc.Input( id='id_var_effects', value= '0.05:0.05:0.7'))
                    ]),
                    html.Div(className='row', children=[ 
                        html.Div(className='tablelabel col-xs-5', children='Number of repeats'),
                        html.Div(className='tablevalue col-xs-5', children=dcc.Input( id='id_var_repeats', value= '10'))
                    ]),
                    html.Div(className='row', children=[ 
                        html.Div(className='tablelabel col-xs-5', children='Number of cpus'),
                        html.Div(className='tablevalue col-xs-5', children=dcc.Input( id='id_var_cpus', value= '1'))
                    ])
                ]),
            ])
        ]),
       
        html.Br(),
        html.Div(id='show-data-table'),
        html.Hr()
])

@app.callback(Output('output-state', 'children'),
              [Input('submit-button', 'n_clicks')],
              [State('id_var_range', 'value'), 
               State('id_var_samples', 'value'),
               State('id_var_effects', 'value'),
               State('id_var_repeats', 'value'),
               State('id_var_cpus', 'value'),
               State('id_var_analysis', 'value')
               ])
def run_analysis(n_clicks,range,samples,effects,repeats,cpus,analysis):
    if global_df is None:
        return html.Div('no data to process')
    else:
        print('running main function')
        pa.main_ui(global_df, ranges, samples, effects, repeats, analysis, cpus)

@app.callback([Output('output-data-upload', 'children'),Output('show-data-table', 'children')],
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'), State('upload-data', 'last_modified')])
def load_data_file(contents, file_name, mod_date):
    children = [ html.Div('An error occurred opening file')]
    df = None
    if contents is not None:
        df = parse_contents(contents, file_name, mod_date)  
        if df is not None:     
            children=[html.Div(file_name)]
    return children, generate_table(df)

if __name__ == '__main__':
    app.run_server(debug=True)