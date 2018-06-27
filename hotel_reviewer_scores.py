from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ActionChains
import time
import re

def get_reviewer_scores(driver,url):
    print 'get_reviewer_scores', url
    driver.get(url)
    scores=[0 for i in xrange(5)]
    try:
        get_reviewer_socres_helper(driver,scores)
    except:
        pass
    return scores

def get_reviewer_socres_helper(driver,scores):
    r2=driver.page_source

    soup2 = BeautifulSoup(r2,'html.parser')
    # reviews_summary_pre=soup2.find('div','modules-membercenter-content-stream')
    reviews_summary=soup2.find('div','cs-content-container')
    # print reviews_summary
    reviews_count=reviews_summary.find_all('li','cs-review')
    print len(reviews_count)
    # screen_name=screen_name.replace('\n','')
    for review_detail in reviews_count:
        # print review_detail
        score=review_detail.find('span','ui_bubble_rating')['class'][1].split('_')[1]
        print score
        # exit(0)
        scores[int(score)-1]+=1
    # print scores
    next_button=soup2.find('div','cs-pagination-bar').find('button',id='cs-paginate-next')
    # print next_button
    has_next=next_button['class'][0]
    print has_next,has_next=='disabled'
    if has_next!='disabled':
        driver.find_element_by_class_name('cs-pagination-bar').find_element_by_id('cs-paginate-next').click()
        # time.sleep(1)
        get_reviewer_socres_helper(driver,scores)

