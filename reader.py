from bs4 import BeautifulSoup as bs
import requests

class Reader:
    def __init__(self, url):
        self.url = url
        self.urls = dict()
        self.set_up()

    def set_up(self):
        '''
        Set all region urls to grab urls for beverages
        '''        
        soup = self.get_dom(self.url)
        regions = soup.select("#navigation > ul:nth-of-type(2) li a")
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
        response = requests.get(self.url)
        if response.status_code == 200:
            soup = bs(response.text, 'html')
            return soup
        else:
            return None

    def getRegionUrls(self, region, page=1):
        url = self.urls[region]
        soup = self.get_dom(url)
        region_urls = dict()
        if not soup:
            return None
        
        css_selector = '#winesortlist > div.tblbdr > table > tbody > tr:nth-of-type(1)'
        headers = soup.select(css_selector)[0].split()
        css_selector = "#winesortlist > div.tblbdr > table > tbody > tr > td > a"
        cells = soup.select(css_selector)
        for i in range(len(cells)):
            region_urls[cells[i].text] = cells[i]['href']