'''
    This code has been created as part of assignment 03 for AS (Software Architecture) Lecture
    Department of Informatics Engineering, University of Coimbra
    2016-2017

    Authors:
    André Santos , ailhicas@student.dei.uc.pt
    Afonso Morais , fvmorais@student.dei.uc.pt
    Miguel Freitas , mfreitas@student.dei.uc.pt
'''

from __future__ import generators
from bs4 import BeautifulSoup as bs
import requests
import time
import json

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
        time.sleep(1)
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
        #print(self.urls)
        url = self.urls[region]
        soup = self.get_dom(url)
        region_urls = dict()
        if not soup:
            return None
        limit = 2+limit
        css_selector = '#winesortlist > div.tblbdr > table > tbody > tr:nth-of-type(1)'
        headers = soup.select(css_selector)[0].text.split()
        css_selector = "#winesortlist > div.tblbdr > table > tbody > tr > td"
        cells = soup.select(css_selector)
        for i in range(2,limit,5):
            _type = cells[i].find('span')['class'][-1]
            _name = cells[i].find('a').text
            _url = cells[i].find('a')['href']
            region_urls[_name] = {'url':_url, 'type':_type}
            
        return region_urls

class Item(object):
    '''
    Class responsible for the return of Items of different instance types according to item to "manufacture"
    '''
    def factory(type, material, name):
        if type == 'btlwht': return WhiteWine(material, name)
        if type == 'btlred': return RedWine(material, name)
        if type == 'beverage': return Beverage(material, name)
        assert 0, 'Not Implemented' + type
    factory = staticmethod(factory)


class WhiteWine(Item):
    def __init__(self, dom, name):
        self.dom = dom
        self.name = name
        self._type = "White Wine"

    def assemble(self):
        self.price = self.dom.select("#tab > div > div > div.col2resulttemp2.noprint > div > div:nth-of-type(2) > span.dtlbl.sidepanel-text")[0].find('b').text.strip()

    def get_json(self):
        json = {"type":self._type, "price":self.price, "name": self.name}
        return json

class RedWine(Item):
    def __init__(self, dom, name):
        self.dom = dom
        self.name = name
        self._type = "Red Wine"
        
    def assemble(self):
        self.alcohol = self.dom.select('#tab > div > div > div.col2resulttemp2.noprint > div > div:nth-of-type(10) > div')[0].find('b').text

    def get_json(self):
        json = {"type":self._type, "alcohol":self.alcohol, "name": self.name}
        return json

class Beverage(Item):
    '''This is mocked instance'''
    def __init__(self, dom, name):
        self.dom = dom
        self.name = "Mocked Instance of Beverage"
        self._type = "Beverage"

    def assemble(self):
        self.spirit = "Vodka"

    def get_json(self):
        json = {"type":self._type, "spirit":self.spirit, "name":self.name}
        return json

def item_input_generator(region):
    '''Generating doms as it gets them'''
    rdr = Worker('http://www.wine-searcher.com/regions.lml')
    urls = rdr.get_region_urls(region, limit=30)
    #print(urls)
    for item in urls.keys():
        yield rdr.get_dom(urls[item]['url']), item, urls[item]['type']

items = [Item.factory(info[2],info[0], info[1]) for info in item_input_generator('Portugal')]

for item in items:
    item.assemble()
    with open("wines.json","a") as f:
        (json.dump(item.get_json(), f, indent=4))


