# rext 2 post fields Logic:
# * if neither rent or buy are specified, use rent
# * if neither house or apartment are specified, use both

import spacy, sys, pprint, pickle, re
from IPython.core.debugger import set_trace
from references import SUBURBS, PHRASES, LEMMAS, MISSPELLINGS, POSTCODES, path_data
sys.path.append("./app/")  # path contains python_file.py
from helper import *
import numpy as np

nlp = spacy.load("en_core_web_sm")
AREAS = pd.read_csv(path_data + 'areas_tmp.csv')
state = open(path_data + 'state.txt').read()
rent_or_buy = open(path_data + 'rent_default.txt').read()
rent_phrases = ['rent', 'renting', 'rental', 'rented', 'lease', 'leased', 'leasing']
buy_phrases = ['for sale',  'buying', 'buy', 'bought', 'sold', 'purchase', 'purchasing',
               'acquisition' ,'investment', 'obtain', 'obtaining', 'getting' ,'get', 'procur']
### Load saved sentence from previous
pickle_in = open("sen.pickle","rb")
sen = pickle.load(pickle_in)
print('orig sen', sen)

#### Clean up result
# Run some quick rules over the input to fix some common errors
sen = sen + ' ' # so you match words at end of sentence too
for k,v in zip(MISSPELLINGS.keys(), MISSPELLINGS.values()):  # keys are misspels, values are wanted spellings
    # add spaces around misspellings so you don't take part of a word by accident
    k1,v1 = (' ' + k + ' '),(' ' + v + ' ')
    sen = sen.replace(k,v)

### REGEX
## TESTING
#l= ["one and two bedroom and one bathroom apartments",
#"one and two bathroom apartments",
#"with one or two carspaces apartments",
#"one and two carparks apartments",
#"one bedroom and two bedroom",
#"one two and three bedroom",
#"one two and three bathroom",
#"one two three and four bathrooms",
#"one two three and four bathrooms and one two or three bedrooms apartments",
#"two and three bedroom",
#"two and three carpark",
#"two carpark and three carpark",
#"two bathroom and three bathroom",
#"one bedroom and four bedroom",
#"apartments with one or two bedrooms and one or two bathrooms"]

# Change "one and two bedroom" to "one bedroom and two bedroom" etc
# change "one two and three bedroom" to "one bedroom and two bedroom and three bedroom
# and so on and so forth

nums= "(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)"
for max_groups in range(6,0, -1):  # match the esoteric cases first
    re_string = (nums + " ") * max_groups + "(and|or) " + nums + " ([a-zA-z]*)"  # the string to look for
    g_word = '\g<' + str(max_groups+3) + '>'  # one of "bedrooms or bathrooms or carspaces"
    s = ''  # build up the replace string by substituting in the appropiate groups
    for i in range(1, max_groups+1):
        s += '\g<' +str(i)+ '> ' + g_word + ' and '
    s += '\g<'+str(i+2)+'> ' + g_word
    sen = re.sub(pattern=re_string,repl=s,string=sen)


# Replace things like "one to three bedrooms" with "one bedroom and three bedroom"
re_string = nums + " to " + nums + " ([a-zA-z]*)"
s= '\g<1> \g<3> to \g<2> \g<3>'
sen = re.sub(pattern=re_string, repl=s, string=sen)


### Replace lowercase suburbs with proper nouns
for o in SUBURBS:
    if check_phrase(sen, o.lower()):   sen = sen.replace(o.lower(), o)

# this suburb messes things up
if 'Sale' in sen:
    if state != 'VIC' or check_phrase(sen.lower(), 'for sale'): sen = sen.replace('Sale', 'sale')
sen = sen.strip()

# weird bug with "one carspaces" not being picked up by doc.noun_chunks
sen = ' '  + sen + ' '
sen = sen.replace(' one carspaces ',' one carspace ')
sen = sen.replace(' one bathrooms ',' one bathroom ')
sen = sen.replace(' one bedrooms ',' one bedroom ')
sen = sen.strip()


print(sen)
doc = nlp(sen)

####### Parse the sentence
noun_chunks = get_noun_chunks(doc)
places = find_places(doc, SUBURBS)
cardinals = get_noun_classes(doc, 'CARDINAL')
cardinals_bedrooms,cardinals_bathrooms,cardinals_carspaces = get_cardinals(doc, LEMMAS)

#### Flags
rent_flag = np.any([check_phrase(sen, o) for o in rent_phrases])
buy_flag = np.any([check_phrase(sen, o) for o in buy_phrases])
apartment_flag,house_flag = check_word(doc, 'apartment'),check_word(doc, 'house')
surrounding_suburbs_flag = 'surrounding suburb' in str(doc)

#### Logic
if not rent_flag and not buy_flag:
    if   rent_or_buy == 'rent':    rent_flag = True
    elif rent_or_buy == 'buy':     buy_flag = True
    else: raise Exception('something ain\'t right here')
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

### Deal with surrounding suburbs
if len(places_dict):
    for place,place_type in zip(places_dict.keys(), places_dict.values()):
        if place == "North Shore" or place == "lower North Shore": place = "North Shore - Lower"
        if place == "upper North Shore": place = "North Shore - Upper"
        loc_dict = {"state":state, place_type: place}
        if surrounding_suburbs_flag:
            loc_dict["includeSurroundingSuburbs"] = "true"
            postcode = str(int(POSTCODES.query('state == "' + state + '"and suburb=="' + place.upper() + '"')['postcode']))
            loc_dict['postcode'] = postcode
        post_fields["locations"] += [loc_dict]
pprint.pprint(post_fields)

#### Save result to file
pickle_out = open("post_fields.pickle","wb")
pickle.dump(post_fields, pickle_out)
pickle_out.close()
