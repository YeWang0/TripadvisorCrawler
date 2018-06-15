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
# from pyvirtualdisplay import Display
from timeout import timeout
import sys
from hotel_reviewer_scores import get_reviewer_scores
import os
import datetime

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial

def integeration(root_path, path):

        result = OrderedDict()
        xls1 = get_data(root_path)
        data1 = json.dumps(xls1, default=json_serial)

        root_hotel_list = json.loads(data1, object_hook=json_util.object_hook)['hotel_info']
        root_reviews = json.loads(data1, object_hook=json_util.object_hook)['review_info']
        root_reviewers = json.loads(data1, object_hook=json_util.object_hook)['reviewer_info']
        reviewers_id_lst = [line[1] for line in root_reviewers[1:]]
        # print 'reviewers_id_lst:',reviewers_id_lst

        xls2 = get_data(path)
        data2 = json.dumps(xls2, default=json_serial)

        new_hotel_list = json.loads(data2, object_hook=json_util.object_hook)['hotel_info']
        new_reviews = json.loads(data2, object_hook=json_util.object_hook)['review_info']
        new_reviewers = json.loads(data2, object_hook=json_util.object_hook)['reviewer_info']
        # new_reviewers_id_set = [line[1] for line in new_reviewers[1:]]
        # print len(root_reviewers)
        updated_reviewer_id={}
        for index,new_reviewer in enumerate(new_reviewers):
                if index==0:
                        continue
                new_reviewer_name=new_reviewer[1]
                new_reviewer_row=new_reviewer[:]
                if 'A TripAdvisor' in new_reviewer_name or len(new_reviewer)<3 or new_reviewer[2]=='':
                        updated_reviewer_id[index]=0
                else:
                        if new_reviewer_name not in reviewers_id_lst:
                                reviewers_id_lst.append(new_reviewer_name)
                        updated_reviewer_id[index]=reviewers_id_lst.index(new_reviewer_name)
                        new_reviewer_row[0]=updated_reviewer_id[index]
                        # update reviewers csv
                        
                        for i in xrange(4,8):
                                try:
                                        new_reviewer_row[i]=int(new_reviewer_row[i])
                                except:
                                        pass

                        root_reviewers.append(new_reviewer_row)
                # update reviews csv
        # print len(root_reviewers)
        # print '*'*10
        # print len(root_reviews)
        # print len(new_reviews)
        
        
        for index,new_review in enumerate(new_reviews):
                if index==0:
                        continue
                try:
                        new_review[1]=updated_reviewer_id[new_review[1]]
                except:
                        new_review[1]=0
                new_review[2]=reviewers_id_lst[new_review[1]]
                # if new_review[10]=='"' and new_review[-1]=='"':
                try:
                        new_review[10]=new_review[10][1:-1]
                        new_review[12]=int(new_review[12][0])
                        for i in xrange(14,20):
                                try:
                                        new_review[i]=int(new_review[i])
                                except:
                                        pass
                except:
                        pass
                # print new_review[10]     
                root_reviews.append(new_review)
        # print '*'*10
        # print len(root_reviews)
        # print len(new_reviews)
        
        result.update({"hotel_info":root_hotel_list})
        result.update({"review_info":root_reviews})
        result.update({"reviewer_info":root_reviewers})

        

        

        save_data(root_path,result)


        
root_path='./data/Tripadvisor_SF_final.xlsx'
# for index in xrange(12,19):
#         for sub_index in xrange(1,50):
#                 # if index==1 and sub_index==1:
#                 #         continue
#                 path = 'data/sub/Tripadvisor_SF_sub_' + str(index) +'_' + str(sub_index) + '.xlsx'
                
#                 if os.path.exists(path):
#                         print path
#                         integeration(root_path, path)
#                 else:
#                         break

def integeration2(root_path):
    
        result = OrderedDict()
        xls1 = get_data(root_path)
        data1 = json.dumps(xls1, default=json_serial)

        root_hotel_list = json.loads(data1, object_hook=json_util.object_hook)['hotel_info']
        root_reviews = json.loads(data1, object_hook=json_util.object_hook)['review_info']
        root_reviewers = json.loads(data1, object_hook=json_util.object_hook)['reviewer_info']
        # reviewers_id_lst = [line[1] for line in root_reviewers[1:]]
        
        
        count=0
        for review in root_reviews:
                if count==0:
                        review.insert(13,'trip_month')
                        count+=1
                else:
                        if 'Reviewed' in str(review[9]):
                                # print type(review[9])
                                try:
                                        d=review[9]
                                        d=d.replace('Reviewed','')  
                                        while d[-1]==' ' or d[-1]=='\n':
                                                d=d[:len(d)-1]
                                        while d[0]==' ' or d[0]=='\n':
                                                d=d[1:]
                                        print 'Yes',d    
                                        date_obj=datetime.datetime.strptime(d,'%B %d, %Y')
                                        review_date=date_obj.strftime('%m/%d/%Y')
                                        print 'Yes',review_date
                                        review[9]=review_date
                                        # break
                                except:
                                        print review[9]
                                        print d
                                        pass
                        review.insert(14,'')
                        data=review[13]
                        if data and data.count(','):
                                review[13]=data.split(',')[0]
                                review[14]=data.split(',')[1]
                                while review[14][0]==' ':
                                        review[14]=review[14][1:]
                                # print review
                                # break
                
        result.update({"hotel_info":root_hotel_list})
        result.update({"review_info":root_reviews})
        result.update({"reviewer_info":root_reviewers})

        save_data(root_path,result)

integeration2(root_path)