import requests, folium,  sys, pickle
from IPython.core.debugger import set_trace
sys.path.append("./app/")  # path contains python_file.py
from helper import *
from references import DOMAIN_CREDS

### Read data
pickle_in = open("post_fields.pickle","rb")
post_fields = pickle.load(pickle_in)

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


### Find place to center the map
# hack: use first property in results as map center.
# could defs improve this. Average of lat/lon, zoom etc
lat,lon = get_attribute(l[0], 'latitude'),get_attribute(l[0], 'longitude')
m = folium.Map(location = [lat, lon], zoom_start = 13,
              tiles='OpenStreetMap')

### Plot markers with formatted HTML
for o in l:
    lat,lon = get_attribute(o, 'latitude'),get_attribute(o, 'longitude')
    url = "https://www.domain.com.au/" + o['listing']['listingSlug']
    pic_url = o['listing']['media'][0]['url']
    popup_text = '<img src="' + pic_url +'" width="250" height="200"><br>' + \
    '<a href="' + url + '/" target="_blank">' + get_attribute(o, 'displayableAddress') +"</a><br>" + \
     "<b>Property Type:</b> " + get_attribute(o, 'propertyType') + "<br>" + \
     "<b>Rent:</b> " + get_attribute(o, 'displayPrice', 'priceDetails') + "<br>" + \
      "<b>Bedrooms:</b> " + get_attribute(o, 'bedrooms') + "<br>" + \
      "<b>Bathrooms:</b> " + get_attribute(o, 'bathrooms') + "<br>" + \
      "<b>Carspaces:</b> " + get_attribute(o, 'carspaces') + "<br>"
    popup = folium.Popup(html=popup_text, max_width = 1000)
    add_marker(m, lat, lon, popup)
#print(sen)
m.save('property_map.html')



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

