import sys,os
import re
from bs4 import BeautifulSoup
import requests


reload(sys)
sys.setdefaultencoding('utf-8')

class url_crawler():
    def __init__(self, query_id, query):
        self.query_id = query_id
        self.query = query
        self.url_base = ''
        self.parameters = {}
        self.url_list = []
        self.results = []

    def get_page(self,url,para=None):
        try:
            response = requests.get(url, params=para)
            response.encoding = 'utf-8'
            if response.status_code == 403:
                print '403: ' + url
                sys.exit()

            return response.url,response.text
        except:
            print 'Error: ' + url
            return 'ERROR','ERROR'

    def google_get_search_results(self, url, content):
        page = BeautifulSoup(content, 'lxml')
        # print page
        link=''
        if page.find('div', id='ires'):
            #results_cnt = int(page.find(id='sortBy').find('span', 'sortRight').span.string.split()[-2])
            results = page.find('div', id='ires').find_all('div', 'g')
            for row in results:
                if row.find('h3','r'):
                    link=row.find('a')['href']
                    if not re.search(r'Hotel_Review',link) or not re.search(r'tripadvisor',link):
                        print 'Unmatch: '+link
                        continue
                    else:
                        print 'Find: '+link
                        return link
        return ''

    def google_crawl(self):
        self.url_base = 'https://www.google.com/search?'
        self.parameters = {}
        self.parameters['q'] = self.query
        self.parameters['hl'] = 'en'

        self.results = []
        self.url_list = []

        final_url, content = self.get_page(self.url_base, self.parameters)
        # print final_url
        # with codecs.open('./google_test', 'wb', 'utf-8') as out:
        #     out.write(content)

        # print 'crawling Google data...'

        row_url=self.google_get_search_results(final_url, content)
        # print url
        # print row_url
        if row_url:
            hotel_url=re.search(r'https:\/\/[\d\w.\/-]+',row_url).group(0)
            # print hotel_url
            return hotel_url
        else:
            return ''

    def start_crawl(self):
        print 'Query:' + self.query
        return self.google_crawl()
