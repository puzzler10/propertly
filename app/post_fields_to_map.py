import requests, folium,  sys, pickle,re
from IPython.core.debugger import set_trace
sys.path.append("./app/")  # path contains python_file.py
from helper import *
from references import DOMAIN_CREDS, SUBURBS, path_data
path_assets = './assets/'

img_h = 200
img_w = 250

### Read data
pickle_in = open("post_fields.pickle","rb")
post_fields = pickle.load(pickle_in)
warning_txt = ''

# Check if any locations were specified
if len(post_fields['locations']) == 0:
    warning_txt += 'no_places_detected\n'
    state = open(path_data + 'state.txt').read()
    post_fields['locations'] = [{'state': state}]
else:
    # Check if any locations are invalid
    for o in post_fields['locations']:
        sub = o['suburb']
        if sub not in SUBURBS:
            warning_txt += 'place_not_found <' + sub + '>\n'

### Set up credentials
# Get these details from https://developer.domain.com.au project portal
response = requests.post("https://auth.domain.com.au/v1/connect/token",
                    data=DOMAIN_CREDS)
token = response.json()
access_token = token['access_token']
auth = {"Authorization": "Bearer " + access_token}


### Post request
url = "https://api.domain.com.au/v1/listings/residential/_search"
request = requests.post(url,headers=auth,json=post_fields)
l = request.json()

if len(l) == 200: warning_txt += 'prop_limit_hit\n'

if len(l) == 2:  # error time potentially
    if 'errors' in l.keys():  raise Exception(l)

if len(l) !=     0:
    ### Find place to center the map
    # hack: use first property in results as map center.
    # could defs improve this. Average of lat/lon, zoom etc
    if 'listings' in l[0].keys(): o = dict({'listing':l[0]['listings'][0]})
    else:                         o = l[0]
    lat,lon = get_attribute(o, 'latitude'),get_attribute(o, 'longitude')
    m = folium.Map(location = [lat, lon], zoom_start = 12,
                  tiles='OpenStreetMap')

    def format_num(x):
        """x is result of `get_attribute` function
        Can be a float, an int, or say smth like "Not Found"
        """
        if x == "Not Found": return '0'
        else:
            try:    return str(int(float(x)))
            except: raise ValueError("String found that wasn't 'Not Found': ", x)

    ### Plot markers with formatted HTML
    for i,o in enumerate(l):
        if 'listings' in o.keys():
            print('listings triggered', i)
            # Listings refers to multiple selling at one physical location, like
            # a block of apartments.
            # HACK: just pick the first one of the listings for now. Deal with it later
            o = dict({'listing':o['listings'][0]})
        lat,lon = get_attribute(o, 'latitude'),get_attribute(o, 'longitude')
        url = "https://www.domain.com.au/" + o['listing']['listingSlug']

        try:
            # better images are too big than too small, probably
            pic_url = o['listing']['media'][0]['url'] + '/'+str(img_h*2) + 'x' + str(img_w*2)
        except:
            pic_url = path_assets + 'default_house_pic.jpg'
        beds = format_num(get_attribute(o, 'bedrooms'))
        baths = format_num(get_attribute(o, 'bathrooms'))
        cars = format_num(get_attribute(o, 'carspaces'))
        popup_text = '<img src="' + pic_url +'" width="' + str(img_w) + '" height="' + str(img_h) + '"><br>' + \
        '<a href="' + url + '/" target="_blank">' + get_attribute(o, 'displayableAddress').replace('`',"'") +"</a><br>" + \
         "<b>Property Type:</b> " + get_attribute(o, 'propertyType') + "<br>" + \
         "<b>" + get_attribute(o, 'displayPrice', 'priceDetails') + "</b><br>" + \
          "<b>Bedrooms:</b> " + beds + "<br>" + \
          "<b>Bathrooms:</b> " + baths + "<br>" + \
          "<b>Carspaces:</b> " + cars + "<br>"
        popup = folium.Popup(html=popup_text, max_width = 1000)
        add_marker(m, lat, lon, popup)
    # used to determine error message or not in main dash app
    warning_txt += 'found_properties\n'
    m.fit_bounds(m.get_bounds())
    m.save('property_map.html')
else:
    warning_txt += 'no_properties_found\n'

with open('warnings.txt', 'w') as file: file.write(warning_txt)
########## MAPBOX SOLUTION
#
#
#mapbox_access_token = 'pk.eyJ1IjoidG9tcm90aCIsImEiOiJjanhsNmc3YXMwMnh5M3BtdGJ4anVkNXRsIn0.Gxemf9vJi2b4DIu1K2BjGQ'
#
## hack: use first property in results as map center.
## could defs improve this. Average of lat/lon, zoom etc
#lat,lon = get_attribute(l[0], 'latitude'),get_attribute(l[0], 'longitude')
#
#map_layout = dict(
#    autosize=True,
#    automargin=True,
#    margin=dict(l=30, r=30, b=20, t=40),
#    hovermode="closest",
#    plot_bgcolor="#F9F9F9",
#    paper_bgcolor="#F9F9F9",
#    legend=dict(font=dict(size=10), orientation='h'),
#    title='Satellite Overview',
#    mapbox=dict(accesstoken=mapbox_access_token,
#        style="light",
#        center=dict(lon=lon, lat=lat),
#        zoom=7))
#
#data = []
#for o in l:
#    lat,lon = get_attribute(o, 'latitude'),get_attribute(o, 'longitude')
#    url = "https://www.domain.com.au/" + o['listing']['listingSlug']
#    pic_url = o['listing']['media'][0]['url']
#    popup_text = """
#    '<img src="' + pic_url +'" width="250" height="200"><br>' +
#    '<a href="' + url + '/" target="_blank">' + get_attribute(o, 'displayableAddress') +"</a><br>" +
#    "<b>Property Type:</b> " + get_attribute(o, 'propertyType') + "<br>" +
#    "<b>Rent:</b> " + get_attribute(o, 'displayPrice', 'priceDetails') + "<br>" +
#    "<b>Bedrooms:</b> " + get_attribute(o, 'bedrooms') + "<br>" +
#    "<b>Bathrooms:</b> " + get_attribute(o, 'bathrooms') + "<br>" +
#    "<b>Carspaces:</b> " + get_attribute(o, 'carspaces') + "<br>"  """
#
#    trace = dict(type='scattermapbox',lat=lat,lon=lon, text=popup_text,
#                 marker=dict(size=15))
#    data.append(trace)
#
##    pt =  [go.Scattermapbox(lat=[lat],lon=[lon],mode='markers',
##            marker=go.scattermapbox.Marker(size=14),text=[popup_text])]
##    data.append(pt)
#
#fig = dict(data=data, layout=map_layout)

