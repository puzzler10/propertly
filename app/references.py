import pandas as pd
path_data = './data/'
path_audio = './audio/flac/'

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


SUBURBS = open(path_data + "australia_suburbs.csv").read().split("\n")[1:]
SUBURBS = list(set(SUBURBS))

# Postcode to suburb mapping
POSTCODES = pd.read_csv(path_data + "australian_postcodes.csv")
# Filter out postal boxes (ref: http://post-code.net.au/postcode/)
ranges = [{'min': 800, 'max': 899},
          {'min': 2000, 'max': 2599},
          {'min': 2619, 'max': 2898},
          {'min': 2921, 'max': 2999},
          {'min': 2600, 'max': 2618},
          {'min': 2900, 'max': 2920},
          {'min': 3000, 'max': 3999},
          {'min': 4000, 'max': 4999},
          {'min': 5000, 'max': 5799},
          {'min': 6000, 'max': 6797},
          {'min': 7000, 'max': 7799}]
s = ''
for o in ranges:
    s += '(postcode >= '+ str(o['min']) + ' and postcode <= ' + str(o['max']) + ') or '
s = s[:-4] # remove last 'or'
POSTCODES = POSTCODES.query(s)
# Some suburbs have more than one postcode. For these we choose the lowest
POSTCODES = POSTCODES.groupby(['suburb', 'state']).agg('min')


# From here: https://www.domain.com.au/Public/SiteMap.aspx
# Defined now in a callback function
#AREAS = open(path_data + "areas.csv").read().split('\n')[1:]

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

