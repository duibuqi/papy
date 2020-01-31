import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table
import pandas as pd
import numpy as np  
import base64
import io
import os
import datetime
import plotly.express as px
import pa

UPLOAD_DIRECTORY = 'user/'

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

def save_file(contents, file_name, date):
   
    df = None
    content_type, content_string = contents.split(',')  
    decoded = base64.b64decode(content_string) 
    try:
        if 'csv' in file_name:            
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), header=None)
        elif 'xls' in file_name:          
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        return None
    print('saving file', file_name)
    user_dir_path = os.path.join(UPLOAD_DIRECTORY, str(int(datetime.datetime.now().timestamp())) )
    if not os.path.exists(user_dir_path):
        print('making directory', user_dir_path)
        os.makedirs(user_dir_path)

    new_file = os.path.join(user_dir_path, file_name)
    print('saving', new_file)
    df.to_csv(new_file)
    return new_file


app = dash.Dash(__name__)
#plotly_df = px.data.gapminder().query("country=='Canada'")

app.layout = html.Div(className='col-sm-12', children=[
    
        html.H3('Power Analysis', className='page-header'),
        dcc.Store(id='store', storage_type='session'),
        html.Div(className="col-sm-6", children=[
            
            html.Div(className="panel panel-success", children=[
                html.Div('Input data file', className="panel-heading"),
                html.Div(className="panel-body", children=[
                    html.Div(className="row", children=[
                        html.Div('Upload data:', className='tablelabel col-xs-3'),
                        html.Div(className='tablevalue col-xs-5', children=dcc.Upload(id='upload-data', children=html.Div(html.Button('Choose CSV file')))),
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
            html.Div(id='output-variables')
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

@app.callback([Output('output-data-upload', 'children'), Output('store', 'data')],
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'), State('upload-data', 'last_modified')])
def load_data_file(contents, file_name, mod_date):
    children = [ html.Div('No file supplied')]
    saved_file = None
    print('loading', file_name)
    if contents is not None and file_name is not None:
        #df = parse_contents(contents, file_name, mod_date)    
        children=[html.Div(file_name)]
        print("about to save", file_name)
        saved_file = save_file(contents, file_name, mod_date)
    return children, saved_file

@app.callback(Output('output-variables', 'children'),
              [Input('submit-button', 'n_clicks')],
              [State('id_var_range', 'value'), 
               State('id_var_samples', 'value'),
               State('id_var_effects', 'value'),
               State('id_var_repeats', 'value'),
               State('id_var_cpus', 'value'),
               State('id_var_analysis', 'value'),
               State('store', 'data')
               ])
def run_analysis(n_clicks,range,samples,effects,repeats,cpus,analysis,data):
    print('running main function with data', data)
    df = None
    if data is not None:
        df = pd.read_csv(data)
    return generate_table(df)
    #pa.main_ui(data, ranges, samples, effects, repeats, analysis, cpus)



if __name__ == '__main__':
    app.run_server(debug=True)