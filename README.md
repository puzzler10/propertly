Scope: 

## V1 tasks 

- ~~return default map option when nothing been done yet~~
- ~~Add initial styling and css~~ 
- ~~change carpark not found to 0~~
- ~~round off bedrooms and bathrooms to integers~~
- ~~bug with sydney and North Sydney, Ryde and West Ryde~~
- ~~bug with “The Inner West” not coming up as an area~~ 
- ~~handle “one bedroom and two bedroom apartments”~~
- ~~regex to handle “one and two bedroom apartments”~~ 
- ~~bug fix why it isn’t working properly~~ 
- ~~add state~~ 
- ~~add domain areas from other states~~
- ~~bug with ‘for sale’ searching for rentals~~
- ~~bug with lowercase suburb names not being recognised~~
- ~~bug with houses not being recognised~~
- ~~bug with houses coming up as ‘hOuses’~~
- ~~‘listings’ bugs~~
- ~~change “rent” on popup to “price” when buying~~
- ~~add error handling for “no properties found”~~
- ~~request small versions of images from Domain server~~ 
- ~~add some kind of loading screen when changing maps~~
- ~~handle sentences like “one to three bedrooms”~~
- ~~incorrect carspace search with sentences like “houses in chatswood with one to three bathrooms and one to three carspaces”~~
  - ~~bug where carspaces go back to floats~~
- ~~Display warning message when no location detected~~
- Display warning message when location not found
- center map on all properties  
- Get microphone up 
- ~~add all suburbs and areas of Sydney~~
- Add instructions, some example sentences so user is guided
- ~~minCarspaces undefined bug~~ 
- redesign UI to look better 
  - redesign popup 
  - header image to jpg, diff sizes?
  - new layout 
  - webfonts
  - responsive
- deploy online



## Scope

Can specify 

- Dwelling type: house, apartment, duplex, townhouse or some combination of those (including all of them)
- min/max bedrooms, bathrooms and carparks

- Apartments or houses
- Suburb
- Rent or buy 





### Out of scope



* areas 
  * Implement area logic
    - current bug with “list index out of range” for “everything on the North Shore”

* multiple listings at one address. Currently just picks the first one in the ‘listings’ API object. Could do some nice scroll bar thing. Pair with [markerClusters](https://medium.com/@bobhaffner/folium-markerclusters-and-fastmarkerclusters-1e03b01cb7b1)
* 

