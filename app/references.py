DOMAIN_CREDS = {'client_id':'client_c3bcd20a4906487ba71bc2394ad5d978',
         "client_secret":"secret_0b307b7200ab553e4b586d6bd156f77e",
         "grant_type":"client_credentials",
         "scope":"api_listings_read",
         "Content-Type":"text/json"}

SPEECH_CONTEXT_PHRASES = ['all one','all apartments','apartments', 'apartment', 'houses', 'house',
                    'carpark', 'carspace', 'the North Shore', 'the Inner West', 'North Sydney',
                    'Waverton', 'Woolstonecraft', 'Milsons Point', 'St Leonards',
                    'St Ives', 'Newtown', 'Pyrmont', 'train station', 'bedroom',
                    'bathroom', 'within', 'between', 'metres', 'kilometres', 'carparks',
                    'carspaces', 'Waitara', 'Hornsby', 'Wolli Creek', 'Turramurra', 'St Ives',
                    'Cronulla', 'rent', 'sale', 'surrounding suburbs','Town Hall', 'Wynyard',
                    'Chatswood', 'Artarmon', 'in Ku-ring-gai', 'Northern Beaches', 'East Sydney',
                    'Camperdown', 'Pymble', 'Gordon']


SUBURBS = ['Chatswood', 'St Ives', 'Artarmon', "St Leonards", "Mosman", "Pymble", "Gordon",
          "Newtown", "Hornsby", "Turramurra", "North Sydney", "Milsons Point", "Warrawee", "Wollstonecraft"]

AREAS = ["Inner West", "North Shore - Lower", "North Shore", "North Shore - Upper", "Eastern Suburbs"]


PHRASES = {
    'eq': ['equals', 'exactly'],
    'geq': ['at least', 'minimum', 'or more'],
    'gt': ['more than', 'greater than', 'over'],
    'leq':['no more than', 'maximum', 'at most', 'up to', 'within'],
    'lt': ['less than', 'under']
}


LEMMAS = {
    'bedroom': ['bedroom'],
    'bathroom': ['bathroom'],
    'carspace': ['carspace', 'carpark']
}

MISSPELLINGS = {
    'car park':'carpark', 'car space': 'carspace', 'car parks':'carparks', 'car spaces': 'carspaces',
    'Ku-ringgai':'Ku-ring-gai', 'days':'metres', 'north shore':'North Shore',
    'northern beaches':'Northern Beaches'
}

