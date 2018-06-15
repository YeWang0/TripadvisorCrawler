from pyexcel_xls import get_data
from pyexcel_xls import save_data
from collections import OrderedDict
import json
from bson import json_util
from hotel_link_crawler import url_crawler
import time
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import re
from hotel_reviews_crawler import hotel_reviews_crawler
from hotel_reviewer_profile_crawler import hotel_reviewer_profile_crawler
from hotel_reviewer_scores import get_reviewer_scores
from browserBuilder import get_webdriver

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    # raise TypeError ("Type not serializable")


def get_hotel_tripadvisor_link(path):
    result = OrderedDict()
    xls = get_data(path)
    data=json.dumps(xls, default=json_serial)
    lines=json.loads(data, object_hook=json_util.object_hook)['hotel_info']
    lines2=json.loads(data, object_hook=json_util.object_hook)['review_info']
    lines3=json.loads(data, object_hook=json_util.object_hook)['reviewer_info']
    # lines[0].append('Link')
    for i in xrange(1,len(lines)):
        while len(lines[i])<9:
            lines[i].append('')
        q=[str(x) for x in lines[i]]
        # print q
        # try:
        link=url_crawler(q[0],' '.join(q[2:5])+" tripadvisor").start_crawl()
        print link
        try:
            lines[i][7]=link
        except:
            lines[i].append(link)
        # time.sleep(1)
        # except:
        #     # link=''
        #     # print 'fail'
        #     break

    # # print lines[:10]

    result.update({"hotel_info":lines})
    result.update({"review_info":lines2})
    result.update({"reviewer_info":lines3})
    save_data(path,result)

def get_hotel_tripadvisor_summary(path):
    result = OrderedDict()
    xls = get_data(path)
    data=json.dumps(xls, default=json_serial)
    lines=json.loads(data, object_hook=json_util.object_hook)['hotel_info']
    lines2=json.loads(data, object_hook=json_util.object_hook)['review_info']
    lines3=json.loads(data, object_hook=json_util.object_hook)['reviewer_info']
    # lines[0].append('Link')
    for line in lines[1:]:
        try:
            while len(line)<9:
                line.append('')
            # if not line[8]=='':
            #     continue
            url = line[4]
            print url
            r = requests.get(url)
            html = r.content
            # print html
            soup = BeautifulSoup(html,'lxml')
            rank_num=soup.find('b',{'class':'rank'})
            # print rank_num.text[1:]
            #
            try:
                line[7]=rank_num.text[1:]
            except:
                print rank_num
            try:
                line[5]=soup.find('h1',{'id':'HEADING'}).text
            except:
                print soup.find('h1',{'id':'HEADING'})
            english_reviews=soup.find('div',{'data-value':'en'}).text
            line[6]=re.search(r'(([\d]+))',english_reviews.replace(',','')).group(1)
            print line[6]
            # rating=soup.find('div',{'class':'rating'})
            # print rating

            # reviews_count=reviews_count.find('span',{'property':'v:count'})
            # print reviews_count
            reviews_count=soup.find('span',{'class':'reviewCount'})
            print reviews_count
            try:
                reviews_num= re.search(r'([\d]+) reviews',reviews_count.text.replace(',','')).group(1)
                # reviews_num=reviews_count.text.replace(',','')
                print reviews_num
                # if(line[9]!=-1):
                line[8]=reviews_num
            except:
                # break
                pass
                # reviews_num=-1
        except:
            print 'Failed to execute: ' + str(line)

        # hotel_name=soup.find('h1',{'id':'HEADING'}).text
        # print hotel_name
        # line[5]=hotel_name
        # try:
        #     text=soup.find('div','language').text.replace(',','').replace('\n','').replace('\t','')
        #     print text
        #     hotel_reviews_num=re.search('English\D?\((\d+)\)',text).group(1)
        #     print 'hotel_reviews_num',hotel_reviews_num
        #     line[6]=hotel_reviews_num
        # except:
        #     break
            # pass
        time.sleep(1)
        # break
    result.update({"hotel_info":lines})
    result.update({"review_info":lines2})
    result.update({"reviewer_info":lines3})
    save_data(path,result)

def get_hotel_tripadvisor_reviews(path):
    result = OrderedDict()
    xls = get_data(path)
    data=json.dumps(xls, default=json_serial)
    lines=json.loads(data, object_hook=json_util.object_hook)['hotel_info']
    reviews=json.loads(data, object_hook=json_util.object_hook)['review_info']
    lines3=json.loads(data, object_hook=json_util.object_hook)['reviewer_info']

    # lines[0].append('Link')
    for line in lines[1:]:
        driver = get_webdriver()
        hotel_id=line[0]
        hotel_link=line[4]
        try:
            reviews=hotel_reviews_crawler(hotel_link,hotel_id,reviews, driver)
            driver.close()
            driver.quit()
        except:
            print line
        # break
    result.update({"hotel_info":lines})
    result.update({"review_info":reviews})
    result.update({"reviewer_info":lines3})
    save_data(path,result)

def update_hotel_reviewer(path):
    result = OrderedDict()
    xls = get_data(path)
    data=json.dumps(xls, default=json_serial)

    lines=json.loads(data, object_hook=json_util.object_hook)['hotel_info']
    reviews=json.loads(data, object_hook=json_util.object_hook)['review_info']
    reviewers=json.loads(data, object_hook=json_util.object_hook)['reviewer_info']
    reviewers_id_set=[]
    reviewers_info=[]

    driver = get_webdriver()

    for index,review in enumerate(reviews[1:]):
        try:
            reviewer_id, reviewer_name = hotel_reviewer_profile_crawler(driver,review[5],review[8],reviewers_id_set,reviewers_info)

            # print reviewer_id
            print reviewer_id,reviewer_name
            reviews[index+1][1]=reviewer_id
            reviews[index+1][2]=reviewer_name
        except:
            pass
        # break
    try:
        driver.close()
    except:
        pass
    for info in reviewers_info:
        try:
            # print info
            temp=[]
            temp.append(info.get('Reviewer_ID',''))
            temp.append(info.get('reviewer_name',''))
            temp.append(info.get('reviewer_link',''))
            temp.append(info.get('reviewer_location',''))
            temp.append(info.get('reviewer_level',''))
            temp.append(info.get('reviewer_num_reviews',''))
            temp.append(info.get('reviewer_num_hotel_reviews',''))
            temp.append(info.get('reviewer_num_helpful_votes',''))
            temp.append(info.get('reviewer_firstmonth',''))
            temp.append(info.get('reviewer_gender',''))
            temp.append(info.get('reviewer_age',''))
            temp.append(info.get('reviewer_num_1',''))
            temp.append(info.get('reviewer_num_2',''))
            temp.append(info.get('reviewer_num_3',''))
            temp.append(info.get('reviewer_num_4',''))
            temp.append(info.get('reviewer_num_5',''))
            temp.append(info.get('reviewer_description',''))
            temp.append(info.get('reviewer_readership',''))

            reviewers.append(temp)
        except:
            pass
    result.update({"hotel_info":lines})
    result.update({"reviewer_info":reviewers})
    result.update({"review_info":reviews})
    save_data(path,result)

def update_hotel_reviewer_score(path):
    driver = get_webdriver()
    result = OrderedDict()
    xls = get_data(path)
    data=json.dumps(xls, default=json_serial)

    lines=json.loads(data, object_hook=json_util.object_hook)['hotel_info']
    reviews=json.loads(data, object_hook=json_util.object_hook)['review_info']
    reviewers=json.loads(data, object_hook=json_util.object_hook)['reviewer_info']
    for index,reviewer in enumerate(reviewers[1:]):
        print reviewer
        while len(reviewer)<18:
            reviewer.append('')
        if True:#reviewer[11]!='' and reviewer[12]!='':
            link=reviewer[2]
            # print reviewer
            print link
            try:
                scores=get_reviewer_scores(driver, link)
                print scores
                # break

                reviewer[11]=scores[0]
                reviewer[12]=scores[1]
                reviewer[13]=scores[2]
                reviewer[14]=scores[3]
                reviewer[15]=scores[4]
            except:
                pass
    result.update({"hotel_info":lines})
    result.update({"reviewer_info":reviewers})
    result.update({"review_info":reviews})
    save_data(path,result)

def update_hotel_reviewer_name(path):
    result = OrderedDict()
    xls = get_data(path)
    data=json.dumps(xls, default=json_serial)

    lines=json.loads(data, object_hook=json_util.object_hook)['hotel_info']
    reviews=json.loads(data, object_hook=json_util.object_hook)['review_info']
    reviewers=json.loads(data, object_hook=json_util.object_hook)['reviewer_info']

    reviewer_map={}
    for index,reviewer in enumerate(reviewers[1:]):
        while len(reviewer)<18:
            reviewer.append('')
        reviewer_map[int(reviewer[0])]=reviewer[1]
    for index,review in enumerate(reviews[1:]):
        review[2]=reviewer_map[int(review[1])]
    result.update({"hotel_info":lines})
    result.update({"reviewer_info":reviewers})
    result.update({"review_info":reviews})
    save_data(path,result)

if __name__ == '__main__':
    import timeit
    path_template = 'data/split/Tripadvisor_new_orleans_shard_{}.xlsx'
    for i in xrange(1, 217):

        start = timeit.default_timer()
        path = path_template.format(i)
        print "Start to crawl {} at {}...".format(path, start)

        # print '===get_hotel_tripadvisor_link'
        # get_hotel_tripadvisor_link(path)
        #
        # print '===get_hotel_tripadvisor_summary'
        # get_hotel_tripadvisor_summary(path)
        #
        print '===get_hotel_tripadvisor_reviews'
        get_hotel_tripadvisor_reviews(path)

    #     print '===update_hotel_reviewer'
    #     update_hotel_reviewer(path)
    #
    #     print '===update_hotel_reviewer_score'
    #     update_hotel_reviewer_score(path)
    #
    #     print '===update_hotel_review_name'
    #     update_hotel_reviewer_name(path)
    # #
        stop = timeit.default_timer()

        print stop - start
        break
# Tripadvisor_Hotel_Name
# Reviews_num
# HotelURL


