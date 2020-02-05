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
  
app = dash.Dash(__name__)
#plotly_df = px.data.gapminder().query("country=='Canada'")

app.layout = html.Div(className='col-sm-12 palegrey', children=[
    
        html.H3('Power Analysis', className='page-header'),               
        dcc.Store(id='store', storage_type='memory'),
        dcc.Input(id='id_hidden_results', type='hidden'),

        html.Div(className="col-sm-12", children=[
            
            html.Div(className="panel panel-success", children=[
                html.Div('Parameters', className="panel-heading"),
                
                html.Div(className="panel-body", children=[
                    html.Div(className='col-sm-6', children=[
                        

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
                        ]),  
                        html.Div(className='row', children=[              
                            html.Div(className = 'tablelabel col-xs-12', id='output-variables')
                        ])                   
                    ]),
                    html.Div(className='col-sm-6', children=[
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
                            
                    ])
                    
                ])
            ])
        ]),
        html.Hr(),
        dcc.Loading(id="loading-1", children=[html.Div(id="pretty-spinner")], type='dot', color='#006600'),
        html.Div(id='display-results')
])

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
   
def make_download_button(folder, f_name):
    uri = os.path.join(folder, f_name)
    print('making button', uri)
    button = html.Form(
        action='/' + uri,
        method="get",
        children=[
            html.Button('Download results', className="btn-primary", type="submit")
        ]
    )
    return button

def make_download_link(folder, f_name):
    path = os.path.join(folder, f_name)
    print('making link', path)
    return html.Div(className='row', children=[
                        html.Div(className='tablelabel col-xs-12', 
                                 children=html.A('Download results', href='/' + path))
                    ])

@app.server.route('/user/<path:path>')
def serve_static(path):
    print('in serve_static', path)
    path = os.path.join('user', path)
    t = os.path.abspath(path)
    return send_file(t, attachment_filename='pa_results.zip', as_attachment = True)

@app.server.route('/download/results')
def generate_report_url(file_name):
    print('path', file_name)  
    return send_file(file_name, attachment_filename='results.zip', as_attachment = True)

@app.callback([Output('output-data-upload', 'children'), 
               Output('store', 'data')],
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'), 
               State('upload-data', 'last_modified')])
def load_data_file(contents, file_name, mod_date):
    children = [ html.Div(file_name)]
    saved_file = None
    print('in load_data_file with', file_name)
    if contents is not None and file_name is not None:
        children=[html.Div(file_name)]
        print("about to save", file_name)
        saved_file = save_file(contents, file_name, mod_date)
    return children, saved_file


@app.callback([Output('output-variables', 'children'),
               Output("pretty-spinner", "children") ],
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
        f = pa.main_ui(df, range, samples, effects, repeats, analysis, cpus, data_dir)
        return make_download_button(data_dir, f), ''
        #return make_download_link(data_dir, f), None
    except Exception as e:
        return post_it(str(e)), ''
   
if __name__ == '__main__':
    app.run_server(debug=True, port=1234)