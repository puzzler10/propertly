

### Overview 

App translates spoken queries to real estate property searches. In your spoken query, you can specify 

- min and max ranges on bedrooms, bathrooms and carparks
- Apartments or houses
- Suburb
- Rent or buy 

Technologies used in the app

* dash and React
* Python
* Google Cloud API 
* Domain API 
* HTML 
* CSS





### Instructions 

Main page for the app is `app.py`. Run the app by opening up a command line, navigating to `app.py`, and running `python app.py`. This opens up the app at a local port, by default 8050, so you can see it by going to http://localhost:8050/

Important files: 

* `app.py`: entry point for the app, and main logic 
* `speech_to_text.py`, `text_to_post_fields.py`, and `post_fields_to_map.py`: three scripts called by `app.py` to do the translation procedure. 
* `txt` files are used by the app as an easy place to store variables 

Styling and assets used in the app are in `/assets`. `/audio` contains example files you can test the app with. 





#### TODO

* update GCP credentials in `speech_to_text.py`. **app won’t work until this is done**. Requires creating GCP account (with \$300 free credits ideally), perhaps a GCP project, and setting up a service account for the app. 
* get microphone working instead of upload button 
* put online with netlify at the domain *propert.ly*



#### Current bugs

- error on "houses for rent with two bedrooms more than one bathroom and a carspace in Mosman”. problem with “a carspace”? regex?
  - “Anything available for rent in Pyrmont with a car park?” carpark not being picked up 
- Newtown not detected in “Newtown apartments with two or three bedrooms and one or two bathrooms”. problem with sentence ordering?
- make coloring less confusing 
- Add instructions, some example sentences so user is guided
- redesign UI to look better 



#### Extra features 

* Implement being able to search for areas as Domain define them, like “Inner West”
- multiple listings at one address. Currently just picks the first one in the ‘listings’ API object. Could do some nice scroll bar thing. Pair with [markerClusters](https://medium.com/@bobhaffner/folium-markerclusters-and-fastmarkerclusters-1e03b01cb7b1)

