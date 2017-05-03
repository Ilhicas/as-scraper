from __future__ import generators
from bs4 import BeautifulSoup as bs
import requests
import time

class Worker:
    def __init__(self, url):
        self.url = url
        self.urls = dict()
        self.headers = {
            "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36"
        }
        self.set_up()

    def set_up(self):
        '''
        Set all region urls to grab urls for beverages
        '''        
        soup = self.get_dom(self.url)
        regions = soup.select("#navigation > ul:nth-of-type(1) li a")
        print (regions)
        for region in regions:
            self.urls[region.text] = region['href']
    
    def get_dom(self, url):
        '''
        Get DOM text in parsed html tree after BeautifulSoup Object conversion
        Params:
            String url       
        Returns:
            If successful Object BeautifulSoup else None
        '''
        #Do not abuse on requests
        #time.sleep(1)
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            soup = bs(response.text, "html.parser")
            return soup
        else:
            return None

    def get_region_urls(self, region, limit=1):
        '''
        Params:
            Name of the region to fetch urls i.e Portugal
        Returns:
            Dict ({'item_name':{'url':url, 'type':item_type}})
        '''
        
        url = self.urls[region]
        
        soup = self.get_dom(url)
        region_urls = dict()
        if not soup:
            return None
        
        css_selector = '#winesortlist > div.tblbdr > table > tbody > tr:nth-of-type(1)'
        print(soup)
        headers = soup.select(css_selector)[0].text.split()
        css_selector = "#winesortlist > div.tblbdr > table > tbody > tr > td > a"
        cells = soup.select(css_selector)
        for i in range(limit):
            region_urls[cells[i].text] = cells[i]['href']

        return region_urls

class Item(object):
    def factory(type, material):
        if type == 'white': return WhiteWine(material)
        if type == 'red': return RedWine(material)
        if type == 'beverage': return Beverage(material)
        assert 0, 'Not Implemented' + type
    factory = staticmethod(factory)


class WhiteWine(Item):
    def __init__(self, dom):
        self.dom = dom

    def get_json(self):
        return ''

class RedWine(Item):
    def __init__(self, dom):
        self.dom = dom
    
    def assemble(self):
        pass

    def get_json(self):
        return ''

class Beverage(Item):
    def __init__(self, dom):
        self.dom = dom
    
    def assemble(self):
        pass

    def get_json(self):
        return ''

def item_input_generator(region):
    '''Generating doms as it gets them'''
    rdr = Worker('http://www.wine-searcher.com/regions.lml')
    urls = rdr.get_region_urls(region)
    for item in region.keys():
        yield rdr.get_dom(region[item]['url']), item, region[item]['type']

items = [Item.factory(dom) for dom in item_input_generator('Portugal')]

for item in items:
    item.assemble()
    item.get_json()


