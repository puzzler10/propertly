

# !pip install pyaudio
# !pip install wave

#%%
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash.dependencies import Input, Output, State
import pickle, re, runpy, base64
import pandas as pd
from IPython.core.debugger import set_trace
from references import path_data
#%%
toggle_opts = [
    {'label': 'Yes'},
    {'label': 'No'}
]
rent_or_buy_opts = [
    {'label': 'Rent'},
    {'label': 'Buy'}
]
states = []
for state in ['NSW', "QLD",'VIC', "SA", "WA", "NT", "ACT", "TAS"]:  states.append({'label': state, 'value': state})
no_input_msg = "You haven't said anything yet"


# add map
external_stylesheets =["/assets/css/ionicons.min.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#app.css.append_css({'external_url': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css'})

app.layout = html.Div([
    html.Header(id='header', children=[
        html.H1("propert.ly"),
        html.Span(className='avatar', children=[
            html.Img(src='/assets/images/avatar_house.png', alt='')
        ]),
        html.H2('Find your dream home. Just ask for it.'),
    ]),
    html.Hr(),
    dcc.Loading(id="loading_sen", children=[
         html.Div(id="loading_sen_div")
    ], type="default"),
    html.Div(id='main_container', children = [
        html.Section(id='sidebar_div', className='main_item', children = [
            html.Div(id='state_div', className='sidebar_item', children= [
                html.H2(className='text', children='What state are you looking in?'),
                dcc.Dropdown(id='state_dropdown', options=states, value='NSW',
                             searchable=False, multi=False, clearable=False,
                             style={"color":"black","width":"70%"}),
                 html.H3(id='output_state', children='', style={"display":'none'} )
            ]),
            html.Div(id='rent_or_buy_div', children=[
                html.H2(className='text', children="Default to rent or buy?"),
                daq.BooleanSwitch(id='rent_or_buy_switch', on=False, className='toggle',
                                          label=rent_or_buy_opts, labelPosition='bottom',
                                          color="#FF6382")
            ]),
            html.Div(id='upload_div', className='sidebar_item', children=[
                html.H2(className='text', children="Upload an audio file to get started: "),
                dcc.Upload(id='upload_data', children=[
                    html.Button(id='upload_button', children='Upload File', n_clicks=0)
                ])
            ]),
            html.Div(id='sen_div', className='sidebar_item', children = [
                html.H3(id='output_intro', children="Here's what we understood:"),
                html.H3(id='output_sen', className='bold'),
                html.Div(id='toggle_div', children = [
                    html.Label(id='edit_label', htmlFor='edit_switch', children=[
                        "Happy with your transcription?",
                        daq.BooleanSwitch(id='edit_switch', on=False, className='toggle',
                                          label=toggle_opts, labelPosition='bottom',
                                          color="#FF6382")
                    ]),
                ]),
            ], style={'display':'none'}),
            html.Div(id='edit_speech_div',className='sidebar_item', children = [
                html.H3("Edit until you are happy!"),
                dcc.Textarea(id='edit_speech_input', style={'width': '100%'},
                          placeholder="Put your query here!"),
                html.Button(id='edit_button', type='submit', children = "Submit"),
            ]),
        ]),
        dcc.Loading(id="loading_map", children=[
                html.Div(id="loading_map_div"),
                html.Div(id='warning_div', style={'white-space': 'pre'}),
                html.Div(id='map_div', className='main_item', children = [
                        html.Iframe(id='map', srcDoc = open('property_map.html', 'r').read())
            ])
        ], type="default")
    ])

], id='wrapper', n_clicks=0)



@app.callback([Output('output_state', 'children')],
              [Input('state_dropdown', 'value')])
def update_areas(state):
    # create temp file with areas in the state
    pd.read_csv(path_data + "areas.csv").query("state == @state").to_csv(path_data + "areas_tmp.csv",index=False)
    # dump state to file
    with open(path_data + 'state.txt', 'w') as file:
        file.write(state)
    return [state]

@app.callback([Output('output_sen', 'children'),
               Output('edit_speech_input', 'value'),
               Output("loading_sen_div", "children")],
              [Input('upload_data', 'contents'),
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
        print("edited")
        sen = input_value
        pickle_out = open("sen.pickle","wb")
        pickle.dump(sen, pickle_out)
        pickle_out.close()
    else:                      sen = no_input_msg
    return (sen, sen, "")

@app.callback([Output('map_div', 'children'),
               Output("loading_map_div", "children"),
               Output('warning_div', 'children')],
              [Input('output_sen', 'children'),
               Input('state_dropdown', 'value'),
               Input('rent_or_buy_switch', 'on')])
def update_map(sen, state, rent_switch):
    if sen == no_input_msg or sen is None:          return ("","","")
    else:
        if rent_switch: rent_msg = 'buy'
        else:           rent_msg = 'rent'
        with open(path_data + 'rent_default.txt', 'w') as file: file.write(rent_msg)
        runpy.run_path(path_name='text_to_post_fields.py')
        runpy.run_path(path_name='post_fields_to_map.py')
        warnings = ''
        # determine warnings and messages
        warning_txt = open('warnings.txt').read()
        if 'no_places_detected' in warning_txt:
            warnings += "No specific locations detected in your search: searching in " + state + ".\n"
        if 'prop_limit_hit' in warning_txt:
            warnings += "Showing a maximum of 200 results. Refine your search to see other properties.\n"
        if 'place_not_found' in warning_txt:
            missing_places = re.findall("\<([A-Za-z\- ]*)\>", warning_txt)
            if len(missing_places) == 1:
                warnings += 'Location "' + '", "'.join(missing_places) +'" probably isn\'t a valid suburb.'
            else:
                warnings += 'Locations "' + '", "'.join(missing_places) +'" probably arent\'t valid suburbs.'
        if 'no_properties_found' not in warning_txt:
            return (html.Iframe(id='map', srcDoc = open('property_map.html', 'r').read(),
                                width ='50%', height='600'), "",warnings)
        else:
            warnings += """
            Check you were understood and that suburb names are spelt correctly. Also check that the right state is selected.
            If that didn't work, try separating suburb names with commas; like "Chatswood, West Ryde" instead of "Chatswood West Ryde".
            Finally, perhaps your search was too specific? Try making it broader.
            """
            return(html.H2('No properties found. Try a different search.'),"",warnings)


#### Hiding and showing divs. #####
@app.callback(Output('edit_speech_div', "style" ),
        [Input('edit_switch', 'on')])
def show_editable_input(radio_value):
    if radio_value:     return {'display': 'block'}
    else:               return {'display': 'none'}


@app.callback(Output('sen_div', "style"),
            [Input('output_sen', 'children')])
def show_sen(sen):
    if sen == no_input_msg:          return {'display': 'none'}
    else:                            return {'display': 'block'}



#%%
if __name__ == '__main__':
    app.run_server(debug=True, port=8050, dev_tools_hot_reload_interval=1)

