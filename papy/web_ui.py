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
import pa
import shutil
from collections import deque
import plotly
import random
import plotly.graph_objs as go

UPLOAD_DIRECTORY = 'user/'
X = deque(maxlen=20)
X.append(1)
Y = deque(maxlen=20)
Y.append(1)

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(children=[
    html.Div(className="hero-wrap container-fluid px-0", children=[
        html.Div(className="row d-md-flex no-gutters slider-text align-items-end js-fullheight justify-content-end", children=[         
            html.Div(className="one-forth", children=[
                 html.Div(className="text mt-5", children=[
                    html.H1('Statistical Power Analysis Tool', className='mb-5'),     
                    
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
                                                html.Div(className="form-group", children=[
                                                    html.Div(className="form-field", children=[
                                                    
                                                        dcc.Input(type="text", className="form-control",placeholder="eg. Garphic. Web Developer")
                                                    ])
                                                ])
                                            ]),
                                            html.Div(className="col-md mr-md-2", children=[
                                                html.Div(className="form-group", children=[
                                                    html.Div(className="form-field", children=[
                                                        dcc.Input(type="text", className="form-control",placeholder="eg. Garphic. Web Developer")
                                                    ])
                                                ])
                                            ]),
                                            html.Div(className="col-md", children=[
                                                html.Div(className="form-group", children=[
                                                    html.Div(className="form-field", children=[
                                                        html.Button('Run analysis', type="submit", className="form-control btn btn-secondary")
                                                    ])
                                                ])
                                            ])
                                        ])
                                    ])
                                ])
                            ])
                        ])
                    ]),
                    
                              
                    dcc.Store(id='store', storage_type='memory'),
                    dcc.Input(id='id_hidden_results', type='hidden'),
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
                                     children=[html.Button('Run analysis', className='btn-primary', id='submit-button'),
                                               html.Button('Plot', className='btn-default', id='plot-button', n_clicks=0)])
                        ]),  
                        html.Div(className='row', children=[              
                            html.Div(className = 'tablevalue col-xs-12', id='output-variables')
                        ]),            
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
        html.Section(className="ftco-section ftco-candidates bg-primary", children=[
            html.Div(className="container", children=[
                html.Div(className="row justify-content-center pb-3", children=[
                    html.Div(className="col-md-10 heading-section heading-section-white text-center",children=[                     
                        html.H2('Results', className="mb-4")
                ])
            ])
        ]),
        dcc.Loading(id="loading-1", children=[html.Div(id="pretty-spinner")], type='dot', color='#006600'),
        html.Div(id='display-results', children=[
            dcc.Graph(id='pa-graph')
        ])
    ])
])


@app.callback(Output('pa-graph', 'figure'),
              [Input('plot-button', 'n_clicks')])
def update_graph_scatter(clicked):
    X.append(X[-1]+clicked)
    Y.append(Y[-1]+Y[-1]*random.uniform(-0.1,0.1))

    data = plotly.graph_objs.Scatter(
            x=list(X),
            y=list(Y),
            name='Scatter',
            mode= 'lines+markers'
            )

    return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                yaxis=dict(range=[min(Y),max(Y)]),)}


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
    return  html.Div(className="pull-right post-it green", children=[
                html.Span(error_msg, className="error-message")
                ])
   
def make_download_button(folder, f_name):
    uri = os.path.join(folder, f_name)
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
    print('running main function with n-clicks, data', n_clicks, data)
    if n_clicks is not None:
        df = None
        if data is None:
            return post_it('No data file supplied!'), ''
        if len(analysis)==0:
            return post_it('Please choose analysis type(s)'), ''
        try:
            df = pd.read_csv(data)
            data_dir = os.path.dirname(data)
            f = pa.main_ui(df, range, samples, effects, repeats, analysis, cpus, data_dir)
            return make_download_button(data_dir, f), ''
            #return make_download_link(data_dir, f), None
        except Exception as e:
            return post_it(str(e)), ''
    return [None, None]

if __name__ == '__main__':
    app.run_server(debug=True)