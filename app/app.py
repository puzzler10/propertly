
# !pip install pyaudio
# !pip install wave

#%%
from google.cloud import speech_v1p1beta1 as speech
from google.cloud.speech_v1p1beta1 import types
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash.dependencies import Input, Output, State
import pickle
import runpy
import ipdb
import base64
import plotly.plotly as py
import plotly.graph_objs as go
from IPython.core.debugger import set_trace

#%%

# Workflow
#import speech_to_text
#import text_to_post_fields
#import post_fields_to_map

# Load sentence to display it
#pickle_in = open("sen.pickle","rb")
#sen = pickle.load(pickle_in)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

sen = ''

# add map
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1('Find your dream home. Just ask for it.'),
    html.Br(),
    html.H2("Upload an audio file here"),
   # dcc.Upload(html.Button('Upload File'),id='upload-button'),
   # html.P('upload_string'),
   html.Div([
    dcc.Upload(id='upload-data', children = html.Button(id='upload_button',
                                                        children='Upload File',
                                                        n_clicks=0))
   # dcc.Upload(id='upload-data',
  #             children=html.Div(['Drag and Drop or ',html.A('Select Files')]),
  #            style={'width': '100%','height': '60px', 'lineHeight': '60px',
  #                    'borderWidth': '1px', 'borderStyle': 'dashed',
  #                    'borderRadius': '5px','textAlign': 'center', 'margin': '10px'}),
    ], id='upload-div'),
    html.H3(id='output-data-upload'),
    html.H3("Here's your search results" ),
   # dcc.Graph(figure=fig)
    html.Iframe(id='map', srcDoc = open('property_map.html', 'r').read(),
                width ='50%', height='600')
], id='everything-div', n_clicks=0)


#@app.callback(Output('upload_string', 'children'),
#              [Input('upload-data', 'contents')])
#def parse_upload_button(contents):
#    print("the button works")
#    print(' ')
#    print("contents")
#    return contents



@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents'),
               Input('upload_button', 'n_clicks')],
              [State('upload-data', 'filename')])
def parse_upload(contents, n_clicks, filename):
    #set_trace()
    if contents is None: print("Contents is none")
    if contents is not None:
        pickle_out = open("contents.pickle","wb")
        pickle.dump(contents, pickle_out)
        pickle_out.close()
        contents_bytes = str.encode(contents)
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)

#        runpy.run_path(file_path='helper.py')
        runpy.run_path(path_name='speech_to_text.py')
        runpy.run_path(path_name='text_to_post_fields.py')
        runpy.run_path(path_name='post_fields_to_map.py')

        #exec(open('speech_to_text.py').read())
        #exec(open('text_to_post_fields.py').read())
        #exec(open('.py').read())

        #import speech_to_text
        #import text_to_post_fields
        #import post_fields_to_map

    if n_clicks==0 or contents is None:
        sen = ''
        return "You haven't said anything yet"
    else:
        if contents is None: print("hello, contents is None, and n_clicks is ", n_clicks)
        print("number of clicks: " + str(n_clicks))
        pickle_in = open("sen.pickle","rb")
        sen = pickle.load(pickle_in)
        return "Here's what we understood: " + sen
# html.Pre(sen, style={'whiteSpace': 'pre-wrap','wordBreak': 'break-all'})




#@app.callback(Output('map', 'figure'))
#def make_main_figure(map_layout, data):
#    figure = dict(data=data, layout=map_layout)
#    return map_layout
#%%
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)



