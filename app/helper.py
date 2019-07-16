import folium

####### TEXT TO POST FIELDS FUNCTIONS ########################

def check_word(doc, word):   return True if word in [o.lemma_.strip() for o in doc] else False

def get_noun_chunks(doc):    return [o for o in doc.noun_chunks]

def get_noun_classes(doc, words):
    """words: python list of words to check for"""
    ents = [(e.text, e.label_) for e in doc.ents]
    return [o[0] for o in ents if o[1] in words]

def find_pos_in_noun_chunks(doc, pos):
    l = []
    for chunk in doc.noun_chunks:
        flag = True if pos in [word.pos_ for word in chunk] else False
        if flag: l.append(chunk.string.strip())
    return l

def find_cardinals_for_keyword(doc, keyword_list):
    """Extracts the number of the keyword_list to search for.
    keyword_list is a python list with lemma bases and synonyms.
    e.g. noun = 'bedroom', extract how many bedrooms to look for """
    l = []
    for chunk in get_noun_chunks(doc):
        for keyword in keyword_list:
            if check_word(chunk, keyword):
                l += chunk.ents
    return [o.string.strip() for o in l]

def check_too_many_cardinals(cardinals_keyword):
    if len(cardinals_keyword) > 1:
        print("More than one cardinal for ", keyword, "found")
        return False
    return True

def check_keyword_not_missed(doc, cardinals_keyword, keyword):
    if len(cardinals_keyword) == 0 and check_word(doc, keyword):
        print("No noun phrase including", keyword, "picked up, but",
             keyword, "present in doc")
        return False
    return True

def get_cardinals(doc, lemma_dict):
    """Returns how many bedrooms, bathrooms and carspaces to look for. """
    # First pass: noun chunks parsing
    cardinals_bedrooms  = find_cardinals_for_keyword(doc, lemma_dict['bedroom'])
    cardinals_bathrooms = find_cardinals_for_keyword(doc, lemma_dict['bathroom'])
    cardinals_carspaces = find_cardinals_for_keyword(doc, lemma_dict['carspace'])

    # check that you only get one cardinal at most for each keyword
    # also check that you've picked up each one
    check_too_many_cardinals(cardinals_bedrooms)
    check_too_many_cardinals(cardinals_bathrooms)
    check_too_many_cardinals(cardinals_carspaces)
    bedroom_ok_flag  = check_keyword_not_missed(doc, cardinals_bedrooms, 'bedroom')
    bathroom_ok_flag = check_keyword_not_missed(doc, cardinals_bathrooms, 'bathroom')
    carspace_ok_flag = check_keyword_not_missed(doc, cardinals_carspaces, 'carspace')
    if not bedroom_ok_flag or not bathroom_ok_flag or not carspace_ok_flag:
        keywords = get_keyword_ordering(doc, lemma_dict)
        cardinals = get_noun_classes(doc, 'CARDINAL')
        if not bedroom_ok_flag:
            cardinals_bedrooms = get_keyword_cardinals('bedroom', keywords, cardinals)
        if not bathroom_ok_flag:
            cardinals_bathrooms = get_keyword_cardinals('bathroom', keywords, cardinals)
        if not carspace_ok_flag:
            cardinals_carspaces = get_keyword_cardinals('carspace', keywords, cardinals)
    return (cardinals_bedrooms, cardinals_bathrooms, cardinals_carspaces)

# These functions are for the case where noun chunk approach failed
def get_keyword_ordering(doc, lemma_dict):
    """Returns an ordered list of keywords. The list is ordered in the same
        order as the keywords appear in the doc.
    doc: nlp(sentence) from Spacy
    lemma_dict: dictionary of synonyms for the keywords we use
    (e.g. bathroom, bedroom) """
    ## Get positions of each keyword
    position_dict = {}
    for key in lemma_dict:
        position_dict[key] = []
        for i,token in enumerate(doc):
            if token.lemma_.strip() in lemma_dict[key]:
                position_dict[key] += [i]
    positions = [o for l in position_dict.values() for o in l]  # flatten list of lists
    # Find the keyword associated with each position
    keywords = []
    for pos in positions:
        for key in position_dict:
            if pos in position_dict[key]: keywords += [key]
    return keywords

def get_keyword_cardinals(word, keywords, cardinals):
    """
    Find the cardinal associated with each keyword.
    word: what keyword to look for
    keywords: ordered list of keywords appearing in sentence
    cardinals: list of cardinals extracted from the sentence
    e.g. word = bedroom """
    word_positions = [i for i,o in  enumerate(keywords) if o == word]
    return ([cardinals[i] for i in word_positions])

def get_nummod(doc, word, n, after=True):
    """
    word: word to search for (e.g. "within")
    n: return this many words before/after the word you find.
    after=True: select the n words after the word, else select n words before"""
    l=[]
    if word in str(doc):
        words = str(doc).split(' ')
        pos = [i for i,o in enumerate(words) if o == word][0]
        for i in range(1, n+1):
            if after: l += [words[pos + i]]
            else:     l += [words[pos - i]]
    return l

def get_station_dist(station_modifier):
    if station_modifier[1] in ['metres', 'm']:
        station_dist = [float(o) for o in station_modifier if o.isnumeric()][0]
    elif station_modifier[1] in ['kilometre', 'kilometres', 'km']:
        station_dist = [float(o) * 1000 for o in station_modifier if o.isnumeric()][0]
    return station_dist

def get_num_and_op(c, phrases_dict):
    """converts a cardinal phrase c into the number and the action"""
    from text2digits import text2digits
    t2d = text2digits.Text2Digits()
    c = t2d.convert(c)
    # identify number
    num = [float(o) for o in c.split(' ') if o.isnumeric()][0]
    # identify operation
    op = 'eq'  # default if nothing else said
    for k in phrases_dict:
        for o in phrases_dict[k]:
            if o in c: op = k
    return (num, op)

def process_place(place, suburbs, areas):
    """ Tag each place as a suburb or an area. Also split them if you get
    something like "Chatswood Atarmon"
    place: entry in places list
    suburbs: list of suburbs to recognise
    areas: list of areas to recognise"""
    place = ' ' + place + ' '
    if ' the ' in place: place = place.replace(' the ', '  ')
    place = place.strip()
    area_flag = True if place in areas else False
    if area_flag: l = areas
    else:         l = suburbs
    cnt = 0
    for o in l:
        if o in place: cnt += 1
    if cnt == 0: raise ValueError("place is not in either suburbs or areas")
    if cnt == len(place.split(' ')) and cnt != 1:  place_l = place.split(' ')
    else:                                          place_l = [place]
    return dict(zip(place_l, ['area' if area_flag else 'suburb' for i in range(len(place_l))]))

def update_post_field_with_rooms(post_fields, actions, field):
    """post_fields: the thing you send to Domain
    actions: tuple with (number, modifier)
    field: one of 'bedrooms', 'bathrooms', 'carspaces'
    """
    if not len(actions): return post_fields
    # bit of a hack. truth is I don't know how to handle multiple modifiers for a room yet
    actions = actions[0]
    field_values = ['bedrooms', 'bathrooms', 'carspaces']
    if field not in field_values: raise ValueError("not a valid field")
    field = field.title()
    if   actions[1] == 'eq':   post_fields["min" + field] = actions[0];  post_fields["max" + field] = actions[0]
    elif actions[1] == "geq":  post_fields["min" + field] = actions[0];
    elif actions[1] == "gt":   post_fields["min" + field] = actions[0] + 1;
    elif actions[1] == "leq":  post_fields["max" + field] = actions[0];
    elif actions[1] == "lt":   post_fields["max" + field] = actions[0] + 1;
    return post_fields


########## Folium and Domain API functions ################

def get_attribute(o,field_name, dict_name='propertyDetails' ):
    if field_name not in o['listing'][dict_name].keys():   return "Not Found"
    else: return str(o['listing'][dict_name][field_name])

def add_marker(m, lat, lon, popup):  folium.Marker(location=[lat, lon], popup=popup).add_to(m)
