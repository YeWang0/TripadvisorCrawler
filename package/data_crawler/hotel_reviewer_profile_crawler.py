
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ActionChains
import time
import re

def hotel_reviewer_name_crawler(driver, url, reviewers_id_set):
    print url#, len(reviewers_id_set)
    driver.get(url)
    # time.sleep(1)
    r2=driver.page_source

    soup2 = BeautifulSoup(r2,'html.parser')
    try:
        current_review=soup2.find('div','reviewSelector')
    except:
        return
    try:
        reviewer_info=current_review.find('div','member_info')
    except:
        return
    # print "data:",current_review,reviewer_info
    try:
        screen_name=reviewer_info.find('div','info_text').find('div').text
        # print screen_name, screen_name in reviewers_id_set
        screen_name=screen_name.replace('\n','')
        return (-1, screen_name, True)

    except:
        return

    if screen_name not in reviewers_id_set:
        reviewers_id_set.append(screen_name)
        return (len(reviewers_id_set), screen_name, True)
    else:
        return (reviewers_id_set.index(screen_name), screen_name, False)

def hotel_reviewer_profile_crawler(driver,url,review_id,reviewers_id_set,reviewers_info, previous_reviewers_info):
    # go to the google home page
    # print driver
    print url
    driver.get(url)
    time.sleep(1)
    r2=driver.page_source

    soup2 = BeautifulSoup(r2,'html.parser')
    try:
        current_review=soup2.find('div','reviewSelector')
    except:
        return
    try:
        reviewer_info=current_review.find('div','member_info')
    except:
        return
    # print "data:",current_review,reviewer_info
    try:
        screen_name=reviewer_info.find('div','info_text').find('div').text
        print screen_name, screen_name in reviewers_id_set
        screen_name=screen_name.replace('\n','')
        # return
    except:
        return

    if screen_name not in reviewers_id_set:
        reviewers_id_set.append(screen_name)
        reviewer_info_link=''

        reviewer_data = get_reviewer_link(url, driver, review_id, screen_name, reviewers_id_set)

        print reviewer_data
        if reviewer_data:
            reviewers_info.append(reviewer_data)
        return len(reviewers_id_set), screen_name
    else:
        for index,reviewer_name in enumerate(reviewers_id_set):
            if reviewer_name==screen_name:
                # if not previous_reviewers_info[0] or len(previous_reviewers_info[0]) == 0:
                #     # need to re-crawl:
                #     reviewer_data = get_reviewer_link(url, driver, review_id, screen_name, reviewers_id_set)
                #     reviewer_data['Reviewer_ID'] = index + 1
                #     reviewers_info.append(reviewer_data)
                return index+1, reviewer_name

def get_reviewer_link(url, driver, review_id, screen_name, reviewers_id_set):
    reviewer_data = {}
    try:
        for i in xrange(1):
            try:
                reviewer_info_link = ''
                member_info=driver.find_element_by_class_name('member_info')
                # print member_info.text
                # time.sleep(30)

                for i in xrange(1):
                    ActionChains(driver).click().move_to_element(member_info).click().perform()
                    time.sleep(1)
                    reviewer_info = driver.find_element_by_class_name('memberOverlayRedesign')
                    if reviewer_info:
                        if reviewer_info.find_element_by_css_selector('a') and reviewer_info.find_element_by_css_selector('a').text == screen_name:
                            reviewer_info_link = reviewer_info.find_element_by_css_selector('a').get_attribute('href')
                            break
                    else:
                        print "."
                # if not reviewer_info_link:
                #     driver.get("about:blank")
                #     time.sleep(10)
                #     driver.get(url)
                #     time.sleep(1)

                reviewer_data = get_reviewer_info(reviewer_info_link,driver)
                # print 1
            except Exception as e:
                print '#Exception 1', e
                continue
    except Exception as e:
        print '#Exception 2.1', e
        pass
    if reviewer_data and not reviewer_data.get('reviewer_name', None):
        reviewer_data['reviewer_name'] = screen_name
    reviewer_data['Reviewer_ID'] = len(reviewers_id_set)
    reviewer_data['review_url'] = url
    reviewer_data['reviewer_link']=reviewer_info_link
    return reviewer_data

def get_reviewer_profile_link(url, driver, screen_name):

    try:
        driver.get(url)
        reviewer_data = {}
        for i in xrange(1):
            try:
                reviewer_info_link = ''
                member_info=driver.find_element_by_class_name('member_info')

                for i in xrange(1):
                    ActionChains(driver).click().move_to_element(member_info).click().perform()
                    time.sleep(1)
                    reviewer_info = driver.find_element_by_class_name('memberOverlayRedesign')
                    if reviewer_info:
                        if reviewer_info.find_element_by_css_selector('a') and reviewer_info.find_element_by_css_selector('a').text == screen_name:
                            reviewer_info_link = reviewer_info.find_element_by_css_selector('a').get_attribute('href')
                            print reviewer_info_link
                            break
                    else:
                        print "."

                reviewer_data = get_reviewer_info(reviewer_info_link,driver)
                # print 1
            except Exception as e:
                print '#Exception 1', e
                continue
    except Exception as e:
        print '#Exception 2.2', e
        driver.close()
        pass
    finally:
        driver.quit()

    if not reviewer_data.get('reviewer_name', None):
        reviewer_data['reviewer_name'] = screen_name
    reviewer_data['review_url'] = url
    reviewer_data['reviewer_link'] = reviewer_info_link

    return reviewer_data


def get_reviewer_info(link,driver):
    reviewer_data={}
    # driver = webdriver.Chrome()
    # go to the google home page
    print 'reviewer link: ',link
    driver.get(link)
    # time.sleep(3)
    try:
        name=driver.find_element_by_class_name('nameText ').text
        # print name
        reviewer_data['reviewer_name']=name
    except:
        pass

    try:
        hometown=driver.find_element_by_class_name('hometown').text
        # print hometown
        reviewer_data['reviewer_location']=hometown
    except:
        pass

    try:
        ageSince=driver.find_element_by_class_name('ageSince').text
        if ageSince.count('\n'):
            since=ageSince.split('\n')[0].split('Since ')[1]
            # print since
            person=ageSince.split('\n')[1]
            if person.count(' year old '):
                age=person.split(' year old ')[0]
                gender=person.split(' year old ')[1]
                # print age
                # print gender
                reviewer_data['reviewer_age']=age
                reviewer_data['reviewer_gender']=gender

        else:
            since=ageSince.split('Since ')[1]
        reviewer_data['reviewer_firstmonth']=since
    except:
        pass

    try:
        level=re.search(r'([\d]+)',driver.find_element_by_class_name('level').text).group(0)
        # print level
        reviewer_data['reviewer_level']=level
    except:
        pass

    try:
        points=int(re.search(r'([\d,]+)',driver.find_element_by_class_name('points').text).group(0).replace(',',''))
        # print points
        reviewer_data['reviewer_readership']=points
    except:
        pass
    try:
        Reviews_num= re.search(r'([\d]+)',driver.find_element_by_partial_link_text('Reviews').text).group(0)
        # print Reviews_num
        reviewer_data['reviewer_num_reviews']=Reviews_num
    except:
        pass

    try:
        Votes_num= re.search(r'([\d]+)',driver.find_element_by_partial_link_text('Helpful votes').text).group(0)
        # print Votes_num
        reviewer_data['reviewer_num_helpful_votes']=Votes_num
    # try:
    # print driver.find_element_by_partial_link_text('Reviews (').text
    except:
        pass

    try:
        Hotel_reviews_num=re.search(r'Hotels \(([\d]+)\)',driver.find_element_by_class_name('cs-filter-bar').text).group(1)
        # print Hotel_reviews_num
        reviewer_data['reviewer_num_hotel_reviews']=Hotel_reviews_num
    except:
        pass

    try:
        aboutMeDesc=driver.find_element_by_class_name('aboutMeDesc').text
        # print aboutMeDesc
        reviewer_data['reviewer_description']=aboutMeDesc
    except:
        pass
    # driver.close()
    # time.sleep(1)
    # print '---reviewer_name: ',reviewer_data['reviewer_name']
    # print ''
    return reviewer_data
    # Hotel_reviews_num= re.search(r'([\d]+)',driver.find_element_by_partial_link_text('Hotels').text).group(0)
    # print Hotel_reviews_num
# get_reviewer_info('https://www.tripadvisor.com/members/freykr')