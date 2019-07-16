#!/usr/bin/env python
# coding: utf-8

# # Setup

# In[1]:


# !pip install --upgrade google-cloud-storage
# !pip install --upgrade google-cloud-speech
# !pip install spacy
# !python -m spacy download en_core_web_sm
# !pip install requests
# !pip install folium
# !pip install text2digits


# In[2]:

get_ipython().run_line_magic('load_ext', 'autoreload')
get_ipython().run_line_magic('autoreload', '2')
import io, os, base64, requests, folium, spacy, glob, sys
from spacy import displacy
from google.cloud import speech_v1p1beta1 as speech, storage
from google.cloud.speech_v1p1beta1 import enums, types
from text2digits import text2digits
from IPython.core.debugger import set_trace

sys.path.append("./app/")  # path contains python_file.py

from helper import *
path_audio = './audio/flac/'
path = "./data/"



# ## Mapping

# In[16]:


# Get these details from https://developer.domain.com.au project portal
creds = {'client_id':'client_c3bcd20a4906487ba71bc2394ad5d978',
         "client_secret":"secret_0b307b7200ab553e4b586d6bd156f77e",
         "grant_type":"client_credentials",
         "scope":"api_listings_read",
         "Content-Type":"text/json"}
response = requests.post("https://auth.domain.com.au/v1/connect/token",
                        data=creds)
token = response.json()
access_token = token['access_token']
auth = {"Authorization": "Bearer " + access_token}

url = "https://api.domain.com.au/v1/listings/residential/_search"
request = requests.post(url,headers=auth,json=post_fields)
l = request.json()



def get_attribute(o,field_name, dict_name='propertyDetails' ):
    if field_name not in o['listing'][dict_name].keys():   return "Not Found"
    else: return str(o['listing'][dict_name][field_name])



def add_marker(m, lat, lon, popup):  folium.Marker(location=[lat, lon], popup=popup).add_to(m)


# In[21]:


# hack: use first property in results as map center.
# could defs improve this. Average of lat/lon, zoom etc
lat,lon = get_attribute(l[0], 'latitude'),get_attribute(l[0], 'longitude')
m = folium.Map(location = [lat, lon], zoom_start = 13,
              tiles='OpenStreetMap')


# In[22]:


for o in l:
    lat,lon = get_attribute(o, 'latitude'),get_attribute(o, 'longitude')
    url = "https://www.domain.com.au/" + o['listing']['listingSlug']
    pic_url = o['listing']['media'][0]['url']
    popup_text = '<img src="' + pic_url +'" width="250" height="200"><br>' +     '<a href="' + url + '/" target="_blank">' + get_attribute(o, 'displayableAddress') +"</a><br>" +         "<b>Property Type:</b> " + get_attribute(o, 'propertyType') + "<br>" +         "<b>Rent:</b> " + get_attribute(o, 'displayPrice', 'priceDetails') + "<br>" +         "<b>Bedrooms:</b> " + get_attribute(o, 'bedrooms') + "<br>" +         "<b>Bathrooms:</b> " + get_attribute(o, 'bathrooms') + "<br>" +         "<b>Carspaces:</b> " + get_attribute(o, 'carspaces') + "<br>"
    popup = folium.Popup(html=popup_text, max_width = 1000)
    add_marker(m, lat, lon, popup)
print(sen)
m

