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
from selenium import webdriver
from hotel_reviews_crawler import hotel_reviews_crawler,redo_hotel_reviews_crawler
from hotel_reviewer_profile_crawler import hotel_reviewer_profile_crawler
from pyvirtualdisplay import Display
from timeout import timeout
import sys

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
        while len(line)<10:
            line.append('')
        if not line[9]=='':
            continue
        url = line[7]
        print url
        r = requests.get(url)
        html = r.content
        # print html
        soup = BeautifulSoup(html,'lxml')
        # rank_num=soup.find('b',{'class':'rank'})
        # print rank_num.text[1:]
        #
        # line[8]=rank_num.text[1:]

        reviews_count=soup.find('div',{'property':'aggregateRating'})

        # reviews_count=soup.find('div',{'class':'rating'})
        # print reviews_count
        # reviews_count=reviews_count.find('span',{'property':'v:count'})
        # print reviews_count
        try:
            reviews_num= re.search(r'([\d]+) reviews',reviews_count.text.replace(',','')).group(1)
            # reviews_num=reviews_count.text.replace(',','')
            print reviews_num
            # if(line[9]!=-1):
            line[9]=reviews_num
        except:
            # break
            pass
            # reviews_num=-1


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

def get_hotel_tripadvisor_reviews(path,start,end,driver):
    result = OrderedDict()
    xls = get_data(path)
    data=json.dumps(xls, default=json_serial)
    lines=json.loads(data, object_hook=json_util.object_hook)['hotel_info']
    reviews=json.loads(data, object_hook=json_util.object_hook)['review_info']
    lines3=json.loads(data, object_hook=json_util.object_hook)['reviewer_info']
    hotel_id_set=set([line[0] for line in reviews])
    
    # lines[0].append('Link')
    for line in lines[start:end]:
        try:
            hotel_id=line[0]
            if hotel_id in hotel_id_set:
                print hotel_id, "already crawled"
                continue
            hotel_link=line[7]
            print hotel_id
            hotel_reviews_crawler(hotel_link,hotel_id,reviews,driver)
        except:
            pass
        # break
    result.update({"hotel_info":lines})
    result.update({"review_info":reviews})
    result.update({"reviewer_info":lines3})
    save_data(path,result)


def redo_hotel_tripadvisor_reviews(path, driver):
    result = OrderedDict()
    xls = get_data(path)
    data = json.dumps(xls, default=json_serial)
    lines = json.loads(data, object_hook=json_util.object_hook)['hotel_info']
    reviews = json.loads(data, object_hook=json_util.object_hook)['review_info']
    lines3 = json.loads(data, object_hook=json_util.object_hook)['reviewer_info']
    hotel_id_set = set([line[0] for line in reviews])

    # lines[0].append('Link')
    for index,line in enumerate(reviews[1:]):
        try:
            if not line[11]:
                print line
                redo_hotel_reviews_crawler(index+1,reviews, driver)
                # exit(0)
        except:
            pass
            # break
    result.update({"hotel_info": lines})
    result.update({"review_info": reviews})
    result.update({"reviewer_info": lines3})
    save_data(path, result)

def update_hotel_reviewer(path,driver):
    # driver = webdriver.Chrome()
    print path
    result = OrderedDict()
    xls = get_data(path)
    data=json.dumps(xls, default=json_serial)

    lines=json.loads(data, object_hook=json_util.object_hook)['hotel_info']
    reviews=json.loads(data, object_hook=json_util.object_hook)['review_info']
    reviewers=json.loads(data, object_hook=json_util.object_hook)['reviewer_info']
    reviewers_id_set=[line[1] for line in reviewers[1:]]
    reviewers_info=[]


    # driver.get("https://www.tripadvisor.com/ShowUserReviews-g60713-d81241-r489215913-Hotel_Whitcomb-San_Francisco_California.html#CHECK_RATES_CONT")
    for index,review in enumerate(reviews[1:1100]):
        try:
            # print review[5],review[8]
            if not reviews[index+1][1]:
                reviewer_id=hotel_reviewer_profile_crawler(driver,review[5],review[8],reviewers_id_set,reviewers_info)

                print reviewer_id
                # print reviewer_id,screen_name
                reviews[index+1][1]=reviewer_id
        except:
            pass
        # break
    # try:
    #     driver.close()
    # except:
    #     pass
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

def combine_csv(path1,path2,path3,path4):
    result = OrderedDict()
    xls = get_data(path1)
    data=json.dumps(xls, default=json_serial)
    lines=json.loads(data, object_hook=json_util.object_hook)['hotel_info']
    reviews=json.loads(data, object_hook=json_util.object_hook)['review_info']
    lines3=json.loads(data, object_hook=json_util.object_hook)['reviewer_info']
    
    xls = get_data(path2)
    data=json.dumps(xls, default=json_serial)
    reviews2=json.loads(data, object_hook=json_util.object_hook)['review_info']
    for review in reviews2[1:]:
        reviews.append(review)
    xls = get_data(path3)
    data=json.dumps(xls, default=json_serial)
    reviews3=json.loads(data, object_hook=json_util.object_hook)['review_info']
    for review in reviews3[1:]:
        reviews.append(review)
    result.update({"hotel_info":lines})
    result.update({"review_info":reviews})
    result.update({"reviewer_info":lines3})
    save_data(path4,result)

def check(path):
    result = OrderedDict()
    xls = get_data(path)
    data=json.dumps(xls, default=json_serial)
    lines=json.loads(data, object_hook=json_util.object_hook)['hotel_info']
    reviews=json.loads(data, object_hook=json_util.object_hook)['review_info']
    lines3=json.loads(data, object_hook=json_util.object_hook)['reviewer_info']
    hotel_id_set=set([str(line[0]) for line in reviews])
    hotel_id_map={}
    for line in reviews[1:]:
        if line[0] not in hotel_id_map:
            hotel_id_map[line[0]]=1
        else:
            hotel_id_map[line[0]]+=1
    for line in lines[1:]:
        hotel_id_map[line[0]]-=int(line[9])
    print hotel_id_map
    # count=0
    # print hotel_id_set
    # for line in lines:
    #     print line[0]
    #     if str(line[0]) not in hotel_id_set:
    #         count+=1
    #         print 'does not find'
    #     else:
    #         print 'ok'
    # print count

def check_failed_reviews(path):
    result = OrderedDict()
    xls = get_data(path)
    data = json.dumps(xls, default=json_serial)
    lines = json.loads(data, object_hook=json_util.object_hook)['hotel_info']
    reviews = json.loads(data, object_hook=json_util.object_hook)['review_info']
    lines3 = json.loads(data, object_hook=json_util.object_hook)['reviewer_info']
    # hotel_id_set = set([line[0] for line in reviews])

    # count=0
    # for review in reviews:
    #     if review[11]=='':
    #         count+=1
    # print count
    # print (count+0.)/len(reviews)

    count=-1
    for reviewer in lines3:
        if len(reviewer)>11:
            # print reviewer[11]
            # print reviewer[11]==''
            try:
                int(reviewer[11])
            except:
                # print reviewer[11]
                count+=1
        else:
            print reviewer[1]
    print count
    # print (count+0.)/len(lines3)

    # if len(lines3)==1:
    #     print path

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'illegal input arguments...'
        exit(0)

    index = int(sys.argv[1])
    for sub_index in xrange(1,41):
        try:
            path = 'data/sub/Tripadvisor_SF_sub_' + str(index) +'_' + str(sub_index) + '.xlsx'

            check_failed_reviews(path)
            print path
        except:
            pass
    # exit(0)

    # display = Display(visible=1, size=(900, 900))
    # display.start()
    #
    # print path
    # check(path)
    # exit(0)
    # print '===get_hotel_tripadvisor_link'
    # get_hotel_tripadvisor_link(path)

    # print '===get_hotel_tripadvisor_summary'
    # get_hotel_tripadvisor_summary(path)

    # interval=1
    # startINdex=input("i")

    # for start in xrange(1,352,interval):
    # driver = webdriver.Chrome('./chrome/chromedriver')
        # end = min(352,start+interval)
        # print start,end
        # print '===get_hotel_tripadvisor_reviews'
    # crawling reviews
    # start=1
    # end=21
    # get_hotel_tripadvisor_reviews(path,start,end,driver)


    # redo reviews crawling
    # redo_hotel_tripadvisor_reviews(path, driver)


    # crawling reviewer
    # print '===update_hotel_reviewer:'+str(index)
    # update_hotel_reviewer(path,driver)

    # driver.close()
    # path2='data/Tripadvisor_SF_2.xlsx'
    # path3='data/Tripadvisor_SF2.xlsx'
    # path4='data/Tripadvisor_SF_x.xlsx'
    # combine_csv(path,path2,path3,path4)

    # begin=1
    # max=2000
    # reviewers_id_set=[]

    # for start in xrange(begin,max,interval):
    #     end = min(max,start+interval)
    #     print '===update_hotel_reviewer'
    #     update_hotel_reviewer(path,start,end,reviewers_id_set)

    # display.stop()

#
# Tripadvisor_Hotel_Name
# Reviews_num
# HotelURL


