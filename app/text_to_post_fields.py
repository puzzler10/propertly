# rext 2 post fields Logic:
# * if neither rent or buy are specified, use rent
# * if neither house or apartment are specified, use both
# * the word 'station' refers to a train station

import spacy, sys, pprint, pickle
from IPython.core.debugger import set_trace
from references import SUBURBS, AREAS, PHRASES, LEMMAS
sys.path.append("./app/")  # path contains python_file.py
from helper import *
nlp = spacy.load("en_core_web_sm")

### Load saved sentence from previous
pickle_in = open("sen.pickle","rb")
sen = pickle.load(pickle_in)
doc = nlp(sen)

####### Parse the sentence
noun_chunks = get_noun_chunks(doc)
places = find_pos_in_noun_chunks(doc, 'PROPN')
cardinals = get_noun_classes(doc, 'CARDINAL')
cardinals_bedrooms,cardinals_bathrooms,cardinals_carspaces = get_cardinals(doc, LEMMAS)

#### Flags
rent_flag,buy_flag = check_word(doc, 'rent'),check_word(doc, 'buy')
apartment_flag,house_flag = check_word(doc, 'apartment'),check_word(doc, 'house')
surrounding_suburbs_flag = 'surrounding suburb' in str(doc)

### Train station stuff
station_flag,train_station_flag = 'station' in str(doc),'train station' in str(doc)
if station_flag or train_station_flag:
    within_flag,between_flag = 'within' in str(doc), 'between' in str(doc)
    upto_flag,under_flag = ' up to ' in str(doc), 'under' in str(doc)
    morethan_flag,over_flag = ' more than ' in str(doc), 'over' in str(doc)
    if within_flag:  station_modifier = get_nummod(doc, 'within', 2)
    if under_flag:   station_modifier = get_nummod(doc, 'under', 2)
    if over_flag:    station_modifier = get_nummod(doc, 'over', 2)

    if upto_flag:
        # dodgy, bigram approach better, or smth that can handle spaces
        station_modifier = get_nummod(doc, 'up', 3)[1:3]
    if morethan_flag:
        # same here
        station_modifier = get_nummod(doc, 'more', 3)[1:3]
    station_dist = get_station_dist(station_modifier)
    if between_flag:
        print('do something here ')
#### Logic
if not rent_flag and not buy_flag: rent_flag = True
if not apartment_flag and not house_flag: apartment_flag = True; house_flag = True;


#### Checking
#print(doc)
#if rent_flag:      print("Looking to rent")
#if buy_flag:       print("Looking to buy")
#if apartment_flag: print("Looking for apartments")
#if house_flag:     print("Looking for houses")
#print ("This many bedrooms: ", cardinals_bedrooms)
#print ("This many bathrooms: ", cardinals_bathrooms)
#print ("This many carspaces: ", cardinals_carspaces)
#print("In these suburbs:", ", ".join(places))
#if surrounding_suburbs_flag: print("Also include surrounding suburbs")
#if station_flag or train_station_flag:
#    if within_flag or under_flag or upto_flag:
#        print("Less than", station_dist, "metres from a train station")
#    if morethan_flag or over_flag:
#        print("More than", station_dist, "metres from a train station")


#### Words to numbers
actions_bedrooms =  [get_num_and_op(o, PHRASES) for o in cardinals_bedrooms]
actions_bathrooms = [get_num_and_op(o, PHRASES) for o in cardinals_bathrooms]
actions_carspaces = [get_num_and_op(o, PHRASES) for o in cardinals_carspaces]

### Actions to Domain API
# Tag places as suburb/area, also split them if needed
d_list = list()
places_dict = dict()
for place in places:
    d_list.append(process_place(place, SUBURBS, AREAS))
for d in d_list:
    places_dict = {**places_dict, **d}

### Set up default post fields
# These are the same with every request
post_fields = {
   "page": 1,
  "pageSize": 200,
    "propertyTypes":[],
    "locations":[]
}
### Add on bits to the post fields
if apartment_flag: post_fields["propertyTypes"] += ["NewApartments", "ApartmentUnitFlat", "Studio"]
if house_flag:     post_fields["propertyTypes"] += ["House", "Duplex", "Townhouse", "Terrace"]
if rent_flag and buy_flag: raise ValueError("Can't look for both renting and buying in one search.")
if rent_flag and not buy_flag:      post_fields["listingType"] = "Rent"
if buy_flag and not rent_flag:      post_fields["listingType"] = "Sale"
post_fields = update_post_field_with_rooms(post_fields, actions_bedrooms, 'bedrooms')
post_fields = update_post_field_with_rooms(post_fields, actions_bathrooms, 'bathrooms')
post_fields = update_post_field_with_rooms(post_fields, actions_carspaces, 'carspaces')

### Deal with surrounding suburbs, place
if len(places_dict):
    for place,place_type in zip(places_dict.keys(), places_dict.values()):
        if place == "North Shore" or place == "lower North Shore": place = "North Shore - Lower"
        if place == "upper North Shore": place = "North Shore - Upper"
        loc_dict = {"state":"NSW", place_type: place}
        if surrounding_suburbs_flag: loc_dict["includeSurroundingSuburbs"] = "true"
        post_fields["locations"] += [loc_dict]
pprint.pprint(post_fields)

#### Save result to file
pickle_out = open("post_fields.pickle","wb")
pickle.dump(post_fields, pickle_out)
pickle_out.close()
