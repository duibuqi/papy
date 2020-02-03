import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from flask import send_file
import pandas as pd
import numpy as np  
import base64
import io
import os
import datetime
import plotly.express as px
import pa
import shutil

UPLOAD_DIRECTORY = 'user/'

def make_download_link():
    return html.Div(className='row', children=[
                        html.Div(className='tablelabel col-xs-12', 
                                 children=html.A('Download results', id='download-zip', download="papy_output_zip.zip",href="/dash/download",target="_blank",n_clicks = 0 ))
                    ])
    
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
         return html.Div('No data available')

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
    user_dir_path = os.path.join(UPLOAD_DIRECTORY, str(datetime.datetime.now().timestamp()) )
    if not os.path.exists(user_dir_path):
        print('making directory', user_dir_path)
        os.makedirs(user_dir_path)

    new_file = os.path.join(user_dir_path, file_name)
    print('saving', new_file)
    df.to_csv(new_file)
    return new_file

def post_it(error_msg):
    return  html.Div(className="pull-right post-it yellow", children=[
                html.Span(error_msg, className="error-message")
                ])
     
app = dash.Dash(__name__)
#plotly_df = px.data.gapminder().query("country=='Canada'")

app.layout = html.Div(className='col-sm-12 palegrey', children=[
    
        html.H3('Power Analysis', className='page-header'),               
        dcc.Store(id='store', storage_type='session'),
        html.Div(className="col-sm-6", children=[
            
            html.Div(className="panel panel-success", children=[
                html.Div('Input data file', className="panel-heading"),
                html.Div(className="panel-body", children=[
                    html.Div(className="row", children=[
                        html.Div('Upload data', className='tablelabel col-xs-3'),
                        html.Div(className='tablevalue col-xs-5', children=dcc.Upload(id='upload-data', children=html.Div(html.Button('Choose CSV file')))),
                        html.Div(className='tablelabel col-xs-4', id='output-data-upload')
                    ]),
                    html.Div(className='row', children=[

                        html.Div('Analysis type', className='tablelabel col-xs-3'),
                        html.Div(className='tablevalue col-xs-9', children=[
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
                        html.Div(className='tablelabel col-xs-12', 
                                 children=html.Button('Run analysis', className='btn-primary', id='submit-button', n_clicks=0))
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
        html.Hr(),
        dcc.Loading(id="loading-1", children=[html.Div(id="pretty-spinner")], type="default")
        
])

@app.server.route('/dash/download')
def generate_report_url():
    print('sending file')
    return send_file('papy_output_zip.zip', attachment_filename = 'papy_output_zip.zip', as_attachment = True)

@app.callback([Output('output-data-upload', 'children'), Output('store', 'data')],
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'), State('upload-data', 'last_modified')])
def load_data_file(contents, file_name, mod_date):
    children = [ html.Div(file_name)]
    saved_file = None
    print('in load_data_file with', file_name)
    if contents is not None and file_name is not None:
        #df = parse_contents(contents, file_name, mod_date)    
        children=[html.Div(file_name)]
        print("about to save", file_name)
        saved_file = save_file(contents, file_name, mod_date)
    return children, saved_file

@app.callback([Output('output-variables', 'children'),Output("pretty-spinner", "children")],
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
    if data is None:
        return html.Div('Please upload a csv data file to begin'), ''
    if len(analysis)==0:
        return html.Div('Please choose analysis type(s)'), ''
    try:
        df = pd.read_csv(data)
        data_dir = os.path.dirname(data)
        #x = threading.Thread(target= pa.main_ui, args=(df, range, samples, effects, repeats, analysis, cpus))
        pa.main_ui(df, range, samples, effects, repeats, analysis, cpus, data_dir)
        
        #print('about to remove input', data_dir)
        #shutil.rmtree(data_dir)
        
    except Exception as e:
        return post_it(str(e)), ''
    #return generate_table(df),''
    return make_download_link(), ''
   

if __name__ == '__main__':
    app.run_server(debug=True)