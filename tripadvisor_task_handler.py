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
from hotel_reviewer_profile_crawler import hotel_reviewer_profile_crawler, get_reviewer_profile_link, hotel_reviewer_name_crawler
from hotel_reviewer_scores import get_reviewer_scores
from browserBuilder.browserBuilder import *
from os.path import getsize

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
    # lines3=json.loads(data, object_hook=json_util.object_hook)['reviewer_info']
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
    # result.update({"reviewer_info":lines3})
    save_data(path,result)

def get_hotel_tripadvisor_summary(path):
    result = OrderedDict()
    xls = get_data(path)
    data=json.dumps(xls, default=json_serial)
    lines=json.loads(data, object_hook=json_util.object_hook)['hotel_info']
    lines2=json.loads(data, object_hook=json_util.object_hook)['review_info']
    # lines3=json.loads(data, object_hook=json_util.object_hook)['reviewer_info']
    # lines[0].append('Link')
    for line in lines[1:]:
        try:
            while len(line)<9:
                line.append('')
            # if not line[8]=='':
            #     continue
            url = line[5]
            print url
            r = requests.get(url)
            html = r.content
            # print html
            soup = BeautifulSoup(html,'html.parser')
            rank_num=soup.find('b',{'class':'rank'})
            # print rank_num.text[1:]
            #
            try:
                line[7]=rank_num.text[1:]
            except:
                print rank_num
            # try:
            #     line[5]=soup.find('h1',{'id':'HEADING'}).text
            # except:
            #     print soup.find('h1',{'id':'HEADING'})
            english_reviews=soup.find('div',{'data-value':'en'}).text
            line[6]=re.search(r'(([\d]+))',english_reviews.replace(',','')).group(1)
            print line[6]
            # rating=soup.find('div',{'class':'rating'})
            # print rating

            # reviews_count=reviews_count.find('span',{'property':'v:count'})
            # print reviews_count
            reviews_count\
                =soup.find('span',{'class':'reviewCount'})
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
        except Exception as e:
            print e
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
    # result.update({"reviewer_info":lines3})
    save_data(path,result)

def get_hotel_tripadvisor_reviews(path, output_path=None):
    if not output_path:
        output_path = path
    result = OrderedDict()
    xls = get_data(path)
    data=json.dumps(xls, default=json_serial)
    lines=json.loads(data, object_hook=json_util.object_hook)['hotel_info']
    reviews=json.loads(data, object_hook=json_util.object_hook)['review_info'][:1]
    # lines3=json.loads(data, object_hook=json_util.object_hook)['reviewer_info']

    print lines

    try:
        # lines[0].append('Link')
        for line in lines[1:]:
            driver = get_webdriver()
            hotel_id=line[0]
            hotel_link=line[5]
            print hotel_id, hotel_link
            try:

                reviews=hotel_reviews_crawler(hotel_link,hotel_id,reviews, driver)
                driver.close()
                driver.quit()
            except Exception as e:
                print line
                print e
            # break
    except Exception as e:
        print e
    result.update({"hotel_info":lines})
    result.update({"review_info":reviews})
    # result.update({"reviewer_info":lines3})
    save_data(output_path,result)

def crawl_hotel_reviewer_name(path, reviewer_path):
    print path
    result = OrderedDict()
    xls = get_data(path)
    data=json.dumps(xls, default=json_serial)
    # print data
    lines=json.loads(data, object_hook=json_util.object_hook)['hotel_info']
    reviews=json.loads(data, object_hook=json_util.object_hook)['review_info']

    # reviewer_result = OrderedDict()
    # reviewer_xls = get_data(reviewer_path)
    # reviewer_data = json.dumps(reviewer_xls, default=json_serial)
    # reviewers=json.loads(reviewer_data, object_hook=json_util.object_hook)['reviewer_info']

    # reviewers_id_set=[reviewer[1] for reviewer in reviewers[1:] if len(reviewer) > 1]
    reviewers_id_set=[]
    # print reviewers_id_set
    # exit(0)

    driver = get_webdriver()

    for index,review in enumerate(reviews[1:]):
        print index
        #  review[5],review[8]
        try:
            url = review[5]
            reviewer_data = hotel_reviewer_name_crawler(driver, url, reviewers_id_set)
            reviewer_id = reviewer_data[0]
            reviewer_name = reviewer_data[1]
            reviewer_exist = reviewer_data[2]
            print "Get reviewer: ", reviewer_name
            # if not reviewer_id or not reviewer_name:
            #     print 'Passed'
            #     continue

            reviews[index+1][1]=reviewer_id
            reviews[index+1][2]=reviewer_name

            if not reviewer_exist:
                print "Add new reviewer: ", reviewer_id,reviewer_name
                temp=[]
                temp.append(reviewer_id)
                temp.append(reviewer_name)
                temp.append(url)

                # print len(reviewers)
                # reviewers.append(temp)
                # print len(reviewers)

        except Exception as e:
            print e
            driver = get_new_webdriver(driver)

    closeDriver(driver)

    result.update({"hotel_info":lines})
    result.update({"review_info":reviews})
    save_data(path,result)

    # reviewer_result.update({"reviewer_info":reviewers})
    # save_data(reviewer_path, reviewer_result)


def update_hotel_reviewer(path, reviewer_path):
    print path
    result = OrderedDict()
    xls = get_data(path)
    data=json.dumps(xls, default=json_serial)
    # print data
    lines=json.loads(data, object_hook=json_util.object_hook)['hotel_info']
    reviews=json.loads(data, object_hook=json_util.object_hook)['review_info']

    reviewer_result = OrderedDict()
    reviewer_xls = get_data(reviewer_path)
    reviewer_data = json.dumps(reviewer_xls, default=json_serial)
    reviewers=json.loads(reviewer_data, object_hook=json_util.object_hook)['reviewer_info']

    reviewers_id_set=[reviewer[1] for reviewer in reviewers[1:] if len(reviewer) > 1]
    # print reviewers_id_set
    # exit(0)
    previous_reviewers_info = [reviewer for reviewer in reviewers[1:]]
    new_reviewers_info=[]

    driver = get_webdriver()

    for index,review in enumerate(reviews[1:]):
        print index
        #  review[5],review[8]
        try:
            reviewer_id, reviewer_name = hotel_reviewer_profile_crawler(driver,review[5],review[8],reviewers_id_set,new_reviewers_info, previous_reviewers_info)

            print reviewer_id,reviewer_name
            reviews[index+1][1]=reviewer_id
            reviews[index+1][2]=reviewer_name
        except Exception as e:
            print e
            driver = get_new_webdriver(driver)
        # break
    try:
        driver.close()
    except:
        pass
    for info in new_reviewers_info:
        # previous_reviewers_id=[reviewer[1] for reviewer in reviewers[1:] if len]
        added = False
        try:
            print info
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
            temp.append(info.get('review_url',''))
            for i in xrange(len(reviewers)):
                reviewer = reviewers[i]
                if reviewer[1] == temp[1]:
                    if reviewer[0] != temp[0]:
                        temp[0] =reviewer[0]
                    reviewers[i] = temp
                    added = True
                    break
            if not added:
                reviewers.append(temp)
        except:
            pass
    result.update({"hotel_info":lines})
    result.update({"review_info":reviews})
    save_data(path,result)

    reviewer_result.update({"reviewer_info":reviewers})
    save_data(reviewer_path, reviewer_result)

def update_hotel_missed_reviewer(reviewer_path):
    reviewer_result = OrderedDict()
    reviewer_xls = get_data(reviewer_path)
    reviewer_data=json.dumps(reviewer_xls, default=json_serial)
    reviewers=json.loads(reviewer_data, object_hook=json_util.object_hook)['reviewer_info']
    # print reviewers[0]
    # driver = get_webdriver()
    for i,reviewer in enumerate(reviewers):
        try:
            print i
            reviewer_id = reviewer[0]
            if len(reviewer) > 2 and (not reviewer[2] or len(reviewer[2]) == 0):
                review_url = reviewer[-1]
                info = get_reviewer_profile_link(review_url, get_webdriver(), reviewer[1])
                temp=[]
                temp.append(reviewer_id)
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
                temp.append(info.get('review_url',''))
                # print temp
                reviewers[i] = temp[:]
        except Exception as e:
            print e
    # driver.close()
    reviewer_result.update({"reviewer_info":reviewers})
    save_data(reviewer_path,reviewer_result)


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
        while len(reviewer)<3:
            reviewer.append('')
        reviewer_map[int(reviewer[0])]=reviewer[1]
    for index,review in enumerate(reviews[1:]):
        review[2]=reviewer_map[int(review[1])]
    result.update({"hotel_info":lines})
    result.update({"reviewer_info":reviewers})
    result.update({"review_info":reviews})
    save_data(path,result)
