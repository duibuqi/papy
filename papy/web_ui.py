import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from flask import send_file
import pandas as pd
import numpy as np  
import base64, io, os, datetime, time
import pa
import shutil
from collections import deque
import plotly
import random
import plotly.graph_objs as go

UPLOAD_DIRECTORY = 'user/'

external_stylesheets = [
    'https://fonts.googleapis.com/css?family=Nunito+Sans:200,300,400,600,700,800,900',
    'https://fonts.googleapis.com/css?family=Architects+Daughter|Indie+Flower|Rock+Salt&display=swap'

]

app = dash.Dash(__name__, 
                external_stylesheets=external_stylesheets,
                routes_pathname_prefix='/pa/')
server = app.server

def post_it(error_msg, col):
    return  html.Div(className="post-it " + col, children=[
                html.Span(error_msg, className="error-message")
                ])
    
app.layout = html.Div(className='shadow-panel', children=[
    
    html.Div(className="container-fluid", children=[
        html.Div(className="row", children=[ 

            html.Div(className='col-md-8'),
            html.H3(id="user-msg", className='col-md-4')
        ]),
        html.Div(className="row no-gutters slider-text", children=[ 
          
            html.Div(className="col-md-12", children=[
                 
                 html.Div(className="", children=[

                    html.H1('Statistical Power Analysis', className='papy-heading'),     
                   

                    html.Div(className="ftco-search", children=[
                        html.Div(className="row", children=[
                            html.Div(className="col-md-12 nav-link-wrap", children=[
                                html.Div(className="nav nav-pills text-center", id="v-pills-tab", role="tablist", children=[
                                    html.A('Parameters', className="nav-link active mr-md-1", id="v-pills-1-tab", href="#v-pills-1", role="tab")
                                ])
                            ]),
                            html.Div(className="col-md-12 tab-wrap", children=[
                                html.Div(className="tab-content p-4", id="v-pills-tabContent", children=[
                                    html.Div(className="tab-pane fade show active", id="v-pills-1", role="tabpanel", children=[
                                        html.Div(className="row no-gutters", children=[
                                           
                                            html.Div(className="col-md mr-md-2", children=[
                                                html.Div(className='btn btn-primary'),
                                                html.Div(className="form-group", children=[
                                                    html.Div(className="form-field", children=[                  
                                                        dcc.Upload(id='upload-data', children=html.Div(html.Button('Upload CSV file', className='text-nowrap form-control btn btn-secondary'))),
                                                        html.Div(className='btn btn-primary', id='output-data-upload')
                                                    ])
                                                ])
                                            ]),
                                            html.Div(className="col-md mr-md-2", children=[
                                                html.Div('Range of variables:',className='papy'),
                                                html.Div(className="form-group", children=[
                                                    html.Div(className="form-field", children=[
                                                        dcc.Input(id='id_var_range', value='9-12', type="text", className="form-control")
                                                    ])
                                                ])
                                            ]),
                                            html.Div(className="col-md mr-md-2", children=[
                                                html.Div('Range of sample sizes:',className='papy'),
                                                html.Div(className="form-group", children=[
                                                    html.Div(className="form-field", children=[
                                                        dcc.Input(id='id_var_samples', value='0:100:500', type="text", className="form-control")
                                                    ])
                                                ])
                                            ]),
                                            html.Div(className="col-md mr-md-2", children=[
                                                html.Div('Range of effect sizes:',className='papy'),
                                                html.Div(className="form-group", children=[
                                                    html.Div(className="form-field", children=[
                                                        dcc.Input(id='id_var_effects', value='0.05:0.05:0.7', type="text", className="form-control")
                                                    ])
                                                ])
                                            ]),
                                            html.Div(className="col-md mr-md-2", children=[
                                                html.Div('Repeats:',className='papy'),
                                                html.Div(className="form-group", children=[
                                                    html.Div(className="form-field", children=[
                                                        dcc.Input(id='id_var_repeats', value='10', type="text", className="form-control")
                                                    ])
                                                ])
                                            ]),
                                            html.Div(className="col-md mr-md-2", children=[
                                                html.Div('Number of CPUs:',className='papy'),
                                                html.Div(className="form-group", children=[
                                                    html.Div(className="form-field", children=[
                                                        dcc.Input(id='id_var_cpus', value='1', type="text", className="form-control")
                                                    ])
                                                ])
                                            ])
                                        ]),
                                        html.Div(id="please-wait", className="row invisible", children=[ 
                                            html.Div(className='col-md-8'),
                                            html.H3(className='col-md-4', children=[
                                                post_it('Please wait! Your analysis is running...', 'yellow')
                                            ])
                                        ]),
                                        html.Div(className="row", children=[
                                             #html.H3(id='user-msg', className='col-md-3'),
                                             html.Div(className="text-right col-md-8", children=[
                                                html.Div(className="form-group", children=[
                                                    html.Div(className="form-field", children=[ 
                                                        dcc.Checklist(className='col-md-8 papy', id='id_var_analysis',
                                                        options=[
                                                            {'label': 'Classification', 'value': 0},
                                                            {'label': 'Linear regression', 'value': 1}
                                                        ],
                                                        value=[0,1],
                                                        labelStyle={'padding':'10px', 'color':'white', 'fontSize': '20px'}
                                                    )  
                                                    ])  
                                                    
                                                ])
                                            ]),
                                            
                                           
                                            html.Div(className="col-md-4", children=[
                                                html.Div(className="form-group row", children=[
                                                    html.Div(className='col-md-6', children=[html.Button('Run analysis', id='submit-button', n_clicks=0, type="submit", className="text-nowrap form-control btn btn-secondary")]),
                                                    html.Div(className='col-md-6', id="results-button")
                                                    
                                                ])
                                            ])
                                        ])
                                    ])
                                ])
                            ])
                        ])
                    ]), 
                   
                                            
                    dcc.Loading(id="loading-1", children=[html.Div(id="pretty-spinner")], type='dot', color='#001166'),                   
                    dcc.Store(id='store', storage_type='memory'),
                    dcc.Input(id='id_hidden_results', type='hidden'),        
                    html.Div(id='trigger',children=0, style=dict(display='none')),
                    html.Div(id='other-element'),
                    html.Div(className='row', children=[             
                        html.Div(className = 'tablevalue col-xs-12', id='output-variables')
                    ]),                     
                ])
            ])                    
        ])
    ]),

    html.Section(children=[
      html.Div(className="container", children=[
        html.Div(className="row mb-5", children=[
            html.Div(className="col-md", children=[
                ])
            ])
        ])
    ])
    
])
            
@app.callback(
    [Output('submit-button','disabled'),
     Output('user-msg', 'className'),
     Output('please-wait', 'className')],
    [Input('submit-button','n_clicks'),
     Input('trigger','children')])
def trigger_function(n_clicks,trigger):
   
    context = dash.callback_context.triggered[0]['prop_id'].split('.')[0]
    context_value = dash.callback_context.triggered[0]['value']
    print('trigger context', context)
    if context == 'submit-button':
        if n_clicks > 0 :
            print('button will be disabled')
            return True, 'invisible', 'row visible'      
        else:
            print('button will be enabled')
            return False, 'visible', 'row invisible'
    else:
        print('button will be enabled')
        return False, 'visible', 'row invisible'

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
        os.makedirs(user_dir_path)

    new_file = os.path.join(user_dir_path, file_name)
    print('saving', new_file)
    df.to_csv(new_file)
    return new_file
  
def make_download_button(folder=None, f_name=None, disabled=True):
    if folder is not None and f_name is not None:
        uri = os.path.join(folder, f_name)
    else:
        uri = ''
        
    button = html.Form(
        action='/' + uri,
        method="get",
        children=[
            html.Button('Download results', className="text-nowrap form-control btn btn-secondary", type="submit", disabled=disabled)
        ]
    )
    return button

@app.server.route('/user/<path:path>')
def serve_static(path):
    print('in serve_static', path)
    path = os.path.join('user', path)
    t = os.path.abspath(path)
    return send_file(t, attachment_filename='pa_results.zip', as_attachment = True)

@app.callback([Output('output-data-upload', 'children'), 
               Output('store', 'data')],
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'), 
               State('upload-data', 'last_modified')])
def load_data_file(contents, file_name, mod_date):
    children = [ html.Div(file_name)]
    saved_file = None
   
    if contents is not None and file_name is not None:
        children=[html.Div(file_name)]
       
        saved_file = save_file(contents, file_name, mod_date)
    return children, saved_file


@app.callback([Output('results-button', 'children'),
               Output("pretty-spinner", "children"),
               Output('trigger','children'),
               Output('user-msg','children') ],
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
    print('running main function with n-clicks, data', n_clicks, data)
    if n_clicks is not None:
        df = None
        if data is None:
            return (make_download_button(), '', 1, post_it('Please upload a data file to begin.', 'green'))
        if len(analysis)==0:
            return (make_download_button(), '', 1, post_it('Please choose at least one analysis type!', 'pink'))
        try:
            df = pd.read_csv(data)
            data_dir = os.path.dirname(data)
            #f = pa.main_ui(df, range, samples, effects, repeats, analysis, cpus, data)
            time.sleep(10)
            f = 'tmp'
            return (make_download_button(data_dir, f, False), '', 1, post_it('Your analysis is complete - click below to download your results.', 'yellow'))
            #return make_download_link(data_dir, f), None
        except Exception as e:
            
            return (make_download_button(), '', 1, post_it('Oh dear... ' + str(e), 'pink'))
    return make_download_button(), None, 1, ''

if __name__ == '__main__':
    app.run_server(debug=True)