from pyexcel_xls import get_data
from pyexcel_xls import save_data
from collections import OrderedDict
import json
import re
from hotel_link_crawler import url_crawler
import time

xls = get_data("1SanFranciscoSanMateoCA_CensusList_with_link.xls")
data=json.dumps(xls)
lines=json.loads(data)['Participation']
def check_link():
    regex=re.compile(r'h[\d]*([-p]*[\d]*.Hotel-Reviews)')
    # time.sleep(3600)
    for i in xrange(1,len(lines)):
        l=lines[i]
        if len(l)>4:
            link=l[4]
        else:
            link=" "
        if not re.search(r'Hotel-Information',link) and not re.search(r'Hotel-Reviews',link):
            print ' '.join(l[1:4])+" expedia.com"
            print i,link
            print ''
        #     link=url_crawler(l[0],' '.join(l[1:4])+" expedia.com").start_crawl()
        #     print "Final:"+link
        #     lines[i][4]=link
        #     print ""

        if not re.search(r'Hotel-Information',link) and re.search(r'Hotel-Reviews',link):
            print ' '.join(l[1:4])+" expedia.com"
            print i,link
            # link=link.replace(regex.search(link).group(1),'.Hotel-Information')
            # print link
            # lines[i][4]=link
            # print ""

def check_duplicates():
    links=dict()
    for i in xrange(1,len(lines)):
        l=lines[i]
        if l[4] in links.keys():
            print l[4]
            print ' '.join(l[1:4])
            print links[l[4]]
            print i

        else:
            links[l[4]]=str(i)+' '.join(l[1:4])
    print len(lines),len(links)
# check_duplicates()
# check_link()
# #
# result = OrderedDict()
# result.update({"Participation":lines})
# save_data("SanFranciscoSanMateoCA_CensusList_with_link.xls",result)


