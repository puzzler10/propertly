
# !pip install pyaudio
# !pip install wave

#%%
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash.dependencies import Input, Output, State
import pickle
import runpy
import base64
from IPython.core.debugger import set_trace

#%%
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

radio_options = [
    {'label': 'Yes', 'value': 'Yes'},
    {'label': 'No', 'value': 'No'}
]
no_input_msg = "You haven't said anything yet"


# add map
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1('Find your dream home. Just ask for it.'),
    html.Br(),
    html.H2("Upload an audio file here"),
    html.Div(id='upload-div', children=[
        dcc.Upload(id='upload-data', children=[
            html.Button(id='upload_button', children='Upload File', n_clicks=0)
        ])
    ]),
    dcc.Loading(id="loading-1", children=[
        html.Div(id="loading-output-1")
    ], type="default"),
    html.Div(id='sen_div', children = [
        html.H3(id='output_intro', children="Here's what we understood"),
        html.H4(id='output_sen'),
        html.Div(id='radio_div', children = [
            html.H4(children="Want to edit your speech results?"),
            dcc.RadioItems(id='edit_radio', options=radio_options, value='No'),
        ]),
    ], style={'display':'none'}),
    html.Div(id='edit_speech_div', children = [
        dcc.Input(id='edit_speech_input', style={'width': '75%'}),
        html.Button(id='edit_button', children = "Submit"),
    ], style= {'display': 'block'}),
    html.Div(id='map_div', children = [
        html.H3("Here's your search results"),
        html.Iframe(id='map', srcDoc = open('property_map.html', 'r').read(),
            width ='50%', height='600')
    ])
], id='everything-div', n_clicks=0)

@app.callback([Output('output_sen', 'children'),
               Output('edit_speech_input', 'value'),
               Output("loading-output-1", "children")],
              [Input('upload-data', 'contents'),
               Input('edit_button', 'n_clicks')],
              [State('upload_button', 'n_clicks'),
               State('upload_button', 'n_clicks_timestamp'),
               State('edit_button', 'n_clicks_timestamp'),
               State('edit_speech_input', 'value')])
def parse_upload(contents, n_clicks_edit, n_clicks_upload,
                 upload_ts, edit_ts, input_value):
    # Case that the page is just loading
    if upload_ts is None:    upload_ts = 0
    if edit_ts   is None:    edit_ts = 0
    if n_clicks_upload==0 or contents is None:      return (no_input_msg,"","")
    # Upload button press
    if upload_ts > edit_ts:
        if contents is not None:
            # Parse the upload
            pickle_out = open("contents.pickle","wb")
            pickle.dump(contents, pickle_out)
            pickle_out.close()
            contents_bytes = str.encode(contents)
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            runpy.run_path(path_name='speech_to_text.py')
            pickle_in = open("sen.pickle","rb")
            sen = pickle.load(pickle_in)
    # Edit button press
    elif edit_ts > upload_ts:
        sen = input_value
        pickle_out = open("sen.pickle","wb")
        pickle.dump(sen, pickle_out)
        pickle_out.close()
    else:                      sen = no_input_msg
    return (sen, sen, "")

@app.callback(Output('map_div', 'children'),
              [Input('output_sen', 'children')])
def update_map(sen):
    if sen == no_input_msg or sen is None:          return ""
    else:
        runpy.run_path(path_name='text_to_post_fields.py')
        runpy.run_path(path_name='post_fields_to_map.py')
        return html.Iframe(id='map', srcDoc = open('property_map.html', 'r').read(),
                width ='50%', height='600')



#### Hiding and showing div's. #####
@app.callback(Output('edit_speech_div', "style" ),
        [Input('edit_radio', 'value')])
def show_editable_input(radio_value):
    if radio_value == "Yes":     return {'display': 'block'}
    else:                        return {'display': 'none'}


@app.callback(Output('sen_div', "style"),
            [Input('output_sen', 'children')])
def show_sen(sen):
    if sen == no_input_msg:          return {'display': 'none'}
    else:                            return {'display': 'block'}



#%%
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)



