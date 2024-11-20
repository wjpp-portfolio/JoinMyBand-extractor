from bs4 import BeautifulSoup
import requests, re

urls = ['https://www.joinmyband.co.uk/classifieds/london-f14.html',
        'https://www.joinmyband.co.uk/classifieds/london-f14-s25.html',
        'https://www.joinmyband.co.uk/classifieds/kent-f116.html',
        'https://www.joinmyband.co.uk/classifieds/kent-f116-s25.html',
        'https://www.joinmyband.co.uk/classifieds/essex-f110.html',
        'https://www.joinmyband.co.uk/classifieds/essex-f110-s25.html'
        ]

jmb_partial_url = 'https://www.joinmyband.co.uk/classifieds/'

title_avoid = ['singer', 'drummer', 'keys', 'keyboard', 'drums', 'vocalist', 'female', 'bassist looking', 'bass player looking', 'bassist seeking', 'bass guitarist looking','available', 'lead guitar']
title_keep = ['bass','bassist']
snippet_avoid = ['looking to', 'available', '''i'm a bass''', 'looking for female', 'bassist looking', 'bass player looking', 'guitarist wanted', 'drummer wanted', 'jam', 'bassist seeking']
snippet_keep = ['bass','bassist']

def build_listings(urls: list) -> dict:
    d = {}

    for url in urls:
        jmb_region =  re.search(r'(?<=ieds/)(.*)(?=-f)', url)[0]
        source = requests.get(url)
        soup = BeautifulSoup(source.content, "html.parser")

        listing_section = soup.find('div', {'id': 'listings'})
        listings = listing_section.find_all('div', {'class': 'topic-row'})

        for item in listings:
            z = {}
            featured = False
            
            try:
                z['date'] = item.find('p', {'class': 'small'}).contents[0].split(',')[0]
                z['listing_title'] = item.a.contents[0]
            except:
                continue
            
            z['listing_snippet'] = item.find('p', {'class': 'snippet'}).contents[0]
            z['location'] = re.search(r'(?<=\()(.*)(?=\))', str(item.find('p', {'class': 'title'}).span))[0]
            z['jmb_region'] = jmb_region
            
            z['url'] = jmb_partial_url+item.a['href']
            uid = int(re.search(r'(?<=-t)(\d.*)(?=.html)', item.a['href'])[0])
     
            if item.find('span', {'class': 'icon featured'}):
                featured = True
            z['featured'] = featured
            z['views'] = int(item.find('p', {'class': 'small'}).contents[0].split(' · ')[1].split(' ')[0])
            d[uid] = z
    return d

#def filter_listings(listings: dict, interesting_terms: list, avoid_terms: list, avoid_location: list, ignore_featured: bool = False) -> dict:
def filter_listings(listings: dict, title_avoid: list, title_keep: list, snippet_avoid: list, snippet_keep: list, ignore_featured: bool = False) -> dict:
    '''find interesting terms and then filter out avoid terms'''

    keep = []
    bin = []
    for id, listing in listings.items():
        if ignore_featured and listing['featured']:
            continue
        
        for term in title_keep:
            if id not in keep and term in listing['listing_title'].lower():
                keep.append(id)

        for term in snippet_avoid:
            if id in keep and id not in bin and term in listing['listing_snippet'].lower():
                bin.append(id)

        for term in title_avoid:
            if id not in bin and term in listing['listing_title'].lower():
                bin.append(id)

        for term in snippet_keep:
            if id not in keep and id not in bin and term in listing['listing_snippet'].lower():
                keep.append(id)

    for id in bin:
        if id in keep:
            keep.remove(id)

    z = {}
    for k in keep:
        z[k] = listings[k]
    return z

y = filter_listings(listings=build_listings(urls), title_avoid=title_avoid, title_keep=title_keep, snippet_avoid=snippet_avoid, snippet_keep=snippet_keep, ignore_featured=False)

for k, v in y.items():
    print(f'----- {k} -----')
    for i, j in v.items():
        print(f'{i}: {j}')
    print('')
    