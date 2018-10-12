from bs4 import BeautifulSoup
import requests
import os
import re
import json
import pprint
import StringIO
from PIL import Image
import time
import traceback
import sys
from hotel_review_image_crawler import img_extractor_tripadvisor
import datetime
from browserBuilder.browserBuilder import get_new_webdriver

# https://www.tripadvisor.com/Hotel_Review-g32060-d226020-Reviews-HYATT_house_Belmont_Redwood_Shores-Belmont_California.html
# https://www.tripadvisor.com/Hotel_Review-g32060-d80974-Reviews-Holiday_Inn_Express_Suites_Belmont-Belmont_California.html
# https://www.tripadvisor.com/Hotel_Review-g32655-d1783764-Reviews-Regency_Inn_Los_Angeles-Los_Angeles_California.html
def url_generator(count,url):
    # 'https://www.tripadvisor.com/Hotel_Review-g32060-d226020-Reviews-HYATT_house_Belmont_Redwood_Shores-Belmont_California.html'
    # 'https://www.tripadvisor.com/Hotel_Review-g32112-d217296-Reviews-DoubleTree_by_Hilton_Hotel_San_Francisco_Airport_North-Brisbane_California.html'
    # print url
    return url.split('Reviews')[0]+'Reviews-or'+str(count*5)+url.split('Reviews')[1]

def text_clean_up(text):
    while len(text)>0 and (text[0]==' ' or text[0]=='\t' or text[0]=='\n'):
        text=text[1:]
    while len(text)>0 and (text[0]==' ' or text[0]=='\t' or text[0]=='\n'):
        text=text[:len(text)-1]
    # print 'cleaning: '+text
    return text

def convert_time_format(date):
    datetime.datetime.now().strftime('%m/%d/%Y');
    return datetime.datetime.strptime(date, "%a %b %d %H:%M:%S %Y")

def convert_str_to_rate(string):
    try:
        if(string.startswith("bubble_")):
            return int(string.split('_')[1])//10
    except:
        pass
    return -1

def hotel_reviews_crawler(hotel_link, xls_hotel_id, reviews_lines, driver):
    reviews_imgs=dict()
    reviews_count=0
    imgs_count=0
    reviews_id_set=set()

    # automatically detect end page
    flag=True
    page=0
    prefix='https://www.tripadvisor.com'
    r = requests.get(hotel_link)
    html = r.content

    # driver.get(hotel_link)
    # html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    page_numbers=int(soup.find('div','pageNumbers').find_all('a')[-1].text)
    print "Page count:", page_numbers

    while flag and page <= page_numbers:
        print 'Page: ', page, hotel_link
        url=url_generator(page, hotel_link)
        # print url
        page+=1
        try:
            r = requests.get(url)
            regex1 = re.compile(r'lazyImgs')
            regex2 = re.compile(r'{"data":"https:\/\/media-cdn.tripadvisor.com\/media(.*)}')
            html = r.content
            # print html
            with open('test.html','w') as fp:
                fp.write(html)
                fp.close()
            soup = BeautifulSoup(html,'html.parser')

            reviews=soup.find_all('div','reviewSelector')

            print "Num of revuews: ", len(reviews)
            for rv in reviews[:]:
                if rv['data-reviewid'] in reviews_id_set:
                    flag=False
                    print '***Find duplicates***'
                    break
                # print rv['data-reviewid']
                review_id=rv['data-reviewid']
                # print rv.find('div','quote').find('a')
                try:
                    review_link = prefix + rv.find('div','quote').find('a')['href']
                    print review_link
                except:
                    onclick = rv.find('div','quote').find('a')['onclick']
                    html_start_index = onclick.index('/ShowUserReviews')
                    html_end_index = onclick.index('.html') + 5
                    review_link = prefix + rv.find('div','quote').find('a')['onclick'][html_start_index:html_end_index]
                    print "Get review link from onclick: ", review_link

                reviews_id_set.add(review_id)
                reviews_count+=1

                date_of_scraping=datetime.datetime.now().strftime('%m/%d/%Y');
                # print date_of_scraping
                try:
                    img_extractor_tripadvisor(review_link,'./img/')
                    # print 'Find image'
                    has_picture=1
                except:
                    # print 'No image'
                    has_picture=0
                    pass

                regex_review_id=re.compile(r'-r([\d]+)-')
                review_id=regex_review_id.search(review_link).group(1)

                regex_hotel_id=re.compile(r'-d([\d]+)-')
                hotel_id=regex_hotel_id.search(review_link).group(1)

                regex_area_id=re.compile(r'-g([\d]+)-')
                area_id=regex_area_id.search(review_link).group(1)

                # print review_id,hotel_id,area_id

                review_date=''
                review_title=''
                review_content=''
                trip_month=''
                trip_purpose=''
                ratings={}
                ratings['Value']=''
                ratings['Rooms']=''
                ratings['Location']=''
                ratings['Cleanliness']=''
                ratings['SleepQuality']=''
                ratings['Service']=''
                review_rate=''
                response_header=''
                response_date=''
                response_text=''

                try:
                    r2 = requests.get(review_link).content
                    soup2 = BeautifulSoup(r2,'html.parser')
                    current_review=soup2.find('div','reviewSelector')
                    # print current_review
                    try:
                        review_date=rv.find('span',{'class':'ratingDate'})['title']
                        # print review_date
                    except:
                        review_date=current_review.find('span',{'class':'ratingDate'})['content']
                        # print review_date

                    try:
                        review_date_temp=current_review.find('span',{'class':'ratingDate'})['content']
                        if review_date=='':
                            review_date=review_date_temp
                    except:
                        print 'open chrome'
                        #driver = webdriver.Chrome('./chrome/chromedriver')
                        # go to the google home page
                        try:
                            driver.get(review_link)
                        except Exception as e:
                            print e
                            driver = get_new_webdriver(driver)
                            driver.get(review_link)

                        r2=driver.page_source
                        #driver.close()
                        soup2 = BeautifulSoup(r2,'html.parser')
                        current_review=soup2.find('div','reviewSelector')
                        # print current_review
                        if review_date=='':
                            try:
                                review_date=current_review.find('span',{'class':'ratingDate'}).text
                                # print review_date
                            except:
                                print 'can not find review_date'
                        # with open('./exception/'+review_id+'.html','w') as fp:
                        #     fp.write(r2)
                        #     fp.close()
                        # driver.close()
                    try:
                        try:
                            date_obj=datetime.datetime.strptime(review_date,'%B %d, %Y')
                        except:
                            date_obj=datetime.datetime.strptime(review_date,'%Y-%d-%m')
                        review_date=date_obj.strftime('%m/%d/%Y')
                        # print review_date
                    except:
                        pass
                    try:
                        review_title=current_review.find('div',{'class':'quote'}).text
                        # print review_title
                    except:
                        # print current_review
                        print 'do not find review_title'
                    try:
                        review_content=current_review.find('div',{'class':'entry'}).text
                    except:
                        print 'do not find review content'
                    # print review_content

                    # print current_review
                    try:
                        trip_stay_info=current_review.find('div',{'class':'recommend-titleInline'}).text
                        if trip_stay_info.startswith("Stayed:"):
                            trip_stay_info=trip_stay_info[8:]
                            trip_purpose=trip_stay_info.split(',')[1]
                            trip_month=trip_stay_info.split(',')[0]
                            # print trip_purpose,trip_month
                    except:
                        pass
                        # print trip_purpose
                    # review_rate=current_review.find('img',{'class':'sprite-rating_s_fill'})['alt'].split(' of ')[0]
                    # print review_rate
                    try:
                        try:
                            review_rate=current_review.find('div',{'class':'rating'}).find('span',{'class':'ui_bubble_rating'})['alt'].split(' of ')[0]
                        except:
                            review_rate =current_review.find('img', {'class': 'sprite-rating_s_fill'})['alt'].split(' of ')[0]
                    except:
                        try:
                            review_rate = convert_str_to_rate(current_review.find('span', {'class': 'ui_bubble_rating'})['class'][1])
                            # print review_rate,"*"*10
                        except:
                            print 'can not get review_rate'
                        # exit(0)
                    # print 'review_rate',review_rate
                    review_ratings=current_review.find_all('li',{'class':'recommend-answer'})
                    # print len(review_ratings)
                    for review_rating in review_ratings:
                        rating_name=review_rating.find('div',{'class':'recommend-description'}).text
                        # print rating_name
                        rating_score=review_rating.find('div',{'class':'ui_bubble_rating'})['class'][1]
                        # print rating_score
                        ratings[rating_name]=convert_str_to_rate(rating_score)
                    # print ratings
                    try:
                        response_date=current_review.find('span',{'class':'responseDate'}).text

                        # print 'd: '+response_date
                        date_obj=datetime.datetime.strptime(response_date,'%B %d, %Y')
                        response_date=date_obj.strftime('%m/%d/%Y')

                        print "response_date:",response_date
                    except:
                        pass

                    try:
                        response_text=current_review.find('p',{'class':'partial_entry'}).text
                    except:
                        pass

                    try:
                        driver.find_element_by_css_selector("span.moreBtn").click()
                    except:
                        pass

                    try:
                        response=current_review.find('div','mgrRspnInline')
                        try:
                            response_header=response.find('div','header').text
                            # response_date=response.find('span','res_date')['title']
                            # response_date=response.find('span','res_date')['title']
                        except:
                            # response_date=response.find('span','res_date').text
                            response_header=response.find('div','header').text.replace(response_date,'')

                        # January 19, 2017
                        # try:
                            # date_obj=datetime.datetime.strptime(response_date,'%B %d, %Y')
                            # response_date=date_obj.strftime('%m/%d/%Y')
                            # print "response_date:",response_date
                        # except:
                        #     pass
                        # response_text=response.find('div','displayText').text
                    except Exception:
                        # with open('./exception/'+review_id+'_response.html','w') as fp:
                        #     fp.write(r2)
                        #     fp.close()
                        exc_type, exc_value, exc_traceback = sys.exc_info()

                        # print "*** print_exception:"
                        #
                        # traceback.print_exception(exc_type, exc_value, exc_traceback,
                        #
                        #                           limit=2, file=sys.stdout)
                        #
                        # print "***"
                        # print 'No response'
                        # print 'h: '+response_header
                        # print 'd: '+response_date
                        # print 't: '+response_text


                except Exception:

                    exc_type, exc_value, exc_traceback = sys.exc_info()

                    print "*** print_exception:"

                    traceback.print_exception(exc_type, exc_value, exc_traceback,

                                              limit=2, file=sys.stdout)

                    print "***"


                # while not len(reviews_lines)<reviews_count:
                #     reviews_lines.append(list())
                review_temp=['' for i in xrange(25)]
                # while len(reviews_lines[review_content])<23:
                #     reviews_lines[reviews_count].append('')
                # print review_link
                review_temp[0]=xls_hotel_id
                review_temp[3]=reviews_count
                review_temp[4]=date_of_scraping
                review_temp[5]=review_link
                # review_id,hotel_id,area_id
                review_temp[6]=area_id
                review_temp[7]=hotel_id
                review_temp[8]=review_id
                review_temp[9]=review_date
                review_temp[10]=review_title
                review_temp[11]=text_clean_up(review_content)
                review_temp[12]=review_rate
                review_temp[13]=trip_month
                review_temp[14]=trip_purpose

                review_temp[15]=ratings['Value']
                review_temp[16]=ratings['Rooms']
                review_temp[17]=ratings['Location']
                review_temp[18]=ratings['Cleanliness']
                review_temp[19]=ratings['SleepQuality']
                review_temp[20]=ratings['Service']

                review_temp[21]=has_picture
                review_temp[22]=text_clean_up(response_header)
                review_temp[23]=response_date
                review_temp[24]=text_clean_up(response_text)
                # print review_temp[10]
                # print review_temp
                reviews_lines.append(review_temp)

        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print "*** print_exception:"
            traceback.print_exception(exc_type, exc_value, exc_traceback,
                                  limit=2, file=sys.stdout)
            print "***"

        # break

    print 'reviews\' images dictionary:'
    pp = pprint.PrettyPrinter()
    pp.pprint(reviews_imgs)

    print 'reviews count:'
    print reviews_count
    print 'images count'
    print imgs_count

    return reviews_lines


def redo_hotel_reviews_crawler(review_index,reviews_lines,driver):
    try:
        reviews_imgs=dict()
        reviews_count=0
        imgs_count=0

        date_of_scraping=datetime.datetime.now().strftime('%m/%d/%Y');


        review_link=reviews_lines[review_index][5]
        print "*"*50,review_link
        # print date_of_scraping
        try:
            img_extractor_tripadvisor(review_link,'./img/')
            # print 'Find image'
            has_picture=1
        except:
            # print 'No image'
            has_picture=0
            pass


        # print review_id,hotel_id,area_id

        review_date=''
        review_title=''
        review_content=''
        trip_purpose=''
        ratings={}
        ratings['Value']=''
        ratings['Rooms']=''
        ratings['Location']=''
        ratings['Cleanliness']=''
        ratings['SleepQuality']=''
        ratings['Service']=''
        review_rate=''
        response_header=''
        response_date=''
        response_text=''

        try:
            r2 = requests.get(review_link).content
            soup2 = BeautifulSoup(r2,'html.parser')
            current_review=soup2.find('div','reviewSelector')


            try:
                review_date_temp=current_review.find('span',{'class':'ratingDate'})['content']
                if review_date=='':
                    review_date=review_date_temp
            except:
                # print 'open chrome'
                #driver = webdriver.Chrome('./chrome/chromedriver')
                # go to the google home page
                driver.get(review_link)
                r2=driver.page_source
                #driver.close()
                soup2 = BeautifulSoup(r2,'html.parser')
                current_review=soup2.find('div','reviewSelector')
                # print current_review
                if review_date=='':
                    try:
                        review_date=current_review.find('span',{'class':'ratingDate'}).text
                        # print review_date
                    except:
                        print 'can not find review_date'
                # with open('./exception/'+review_id+'.html','w') as fp:
                #     fp.write(r2)
                #     fp.close()
                # driver.close()
            try:
                try:
                    date_obj=datetime.datetime.strptime(review_date,'%B %d, %Y')
                except:
                    date_obj=datetime.datetime.strptime(review_date,'%Y-%d-%m')
                review_date=date_obj.strftime('%m/%d/%Y')
                # print review_date
            except:
                pass
            try:
                review_title=current_review.find('div',{'class':'quote'}).text
                # print review_title
            except:
                print current_review
                print 'do not find review_title'
            try:
                review_content=current_review.find('div',{'class':'entry'}).text
            except:
                print 'do not find review content'
            # print review_content

            # print current_review
            try:

                trip_purpose=current_review.find('div',{'class':'recommend-titleInline'}).text
                print "trip_purpose",trip_purpose
            except:
                print trip_purpose
            # review_rate=current_review.find('img',{'class':'sprite-rating_s_fill'})['alt'].split(' of ')[0]
            # print review_rate
            try:
                try:
                    review_rate=current_review.find('div',{'class':'rating'}).find('span',{'class':'ui_bubble_rating'})['alt'].split(' of ')[0]
                except:
                    review_rate =current_review.find('img', {'class': 'sprite-rating_s_fill'})['alt'].split(' of ')[0]
            except:
                try:
                    review_rate =  current_review.find('span', {'class': 'ui_bubble_rating'})['class'][1].split('_')[1]
                    print review_rate,"*"*10
                except:
                    print 'can not get review_rate'
                # exit(0)
            print 'review_rate',review_rate
            review_ratings=current_review.find_all('li',{'class':'recommend-answer'})
            # print len(review_ratings)
            for review_rating in review_ratings:
                rating_name=review_rating.text.replace('\n','').replace(' ','')
                # print rating_name
                rating_score=review_rating.find('span',{'class':'ui_bubble_rating'})['alt'].split(' of ')[0]
                # print rating_score
                ratings[rating_name]=rating_score
            # print ratings


            # try:
            #     response=current_review.find('div','mgrRspnInline')
            #     try:
            #         response_header=response.find('div','header').text
            #         response_date=response.find('span','res_date')['title']
            #         response_date=response.find('span','res_date')['title']
            #     except:
            #         response_date=response.find('span','res_date').text
            #         response_header=response.find('div','header').text.replace(response_date,'')
            #
            #     # January 19, 2017
            #     try:
            #         date_obj=datetime.datetime.strptime(response_date,'%B %d, %Y')
            #         response_date=date_obj.strftime('%m/%d/%Y')
            #         # print "response_date:",response_date
            #     except:
            #         pass
            #     response_text=response.find('div','displayText').text
            # except:
            #     # with open('./exception/'+review_id+'_response.html','w') as fp:
            #     #     fp.write(r2)
            #     #     fp.close()
            #     print 'No response'
            #     # print 'h: '+response_header
            #     # print 'd: '+response_date
            #     # print 't: '+response_text


        except Exception:

            exc_type, exc_value, exc_traceback = sys.exc_info()

            print "*** print_exception:"

            traceback.print_exception(exc_type, exc_value, exc_traceback,

                                      limit=2, file=sys.stdout)

            print "***"


        # while not len(reviews_lines)<reviews_count:
        #     reviews_lines.append(list())
        # review_temp=['' for i in xrange(24)]
        review_temp=reviews_lines[review_index][:]
        while len(review_temp)<24:
            review_temp.append('')
        # while len(reviews_lines[review_content])<23:
        #     reviews_lines[reviews_count].append('')
        # print review_link
        # review_temp[0]=xls_hotel_id
        # review_temp[3]=reviews_count
        review_temp[4]=date_of_scraping
        # review_temp[5]=review_link
        # review_id,hotel_id,area_id
        # review_temp[6]=area_id
        # review_temp[7]=hotel_id
        # review_temp[8]=review_id
        review_temp[9]=review_date
        review_temp[10]=review_title
        review_temp[11]=text_clean_up(review_content)
        review_temp[12]=review_rate
        review_temp[13]=trip_purpose

        review_temp[14]=ratings['Value']
        review_temp[15]=ratings['Rooms']
        review_temp[16]=ratings['Location']
        review_temp[17]=ratings['Cleanliness']
        review_temp[18]=ratings['SleepQuality']
        review_temp[19]=ratings['Service']

        review_temp[20]=has_picture
        review_temp[21]=text_clean_up(response_header)
        review_temp[22]=response_date
        review_temp[23]=text_clean_up(response_text)
        # print review_temp[10]
        reviews_lines[review_index]=review_temp
        print reviews_lines[review_index]
    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print "*** print_exception:"
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                              limit=2, file=sys.stdout)
        print "***"



    print 'reviews\' images dictionary:'
    pp = pprint.PrettyPrinter()
    pp.pprint(reviews_imgs)

    print 'reviews count:'
    print reviews_count
    print 'images count'
    print imgs_count

    return reviews_lines


# download imgs to local
#
# foldername='./img/'
# dir = os.path.dirname(foldername)
# try:
#     os.stat(dir)
# except:
#     os.mkdir(dir)
#
# with open(foldername+'img_urls.json', 'w') as outfile:
#     json.dump(reviews_imgs, outfile,indent=4)
#
# for key,imgs in reviews_imgs.iteritems():
#     count=1
#     foldername='./img/'+key+'/'
#     dir = os.path.dirname(foldername)
#     try:
#         os.stat(dir)
#     except:
#         os.mkdir(dir)
#
#     for img_t in imgs:
#
#         file = StringIO.StringIO(requests.get(img_t).content)
#         img = Image.open(file)
#         img.save(foldername+str(count)+'_t.jpg')
#
#         img_s=str(img_t).replace('/photo-t/','/photo-s/')
#         file = StringIO.StringIO(requests.get(img_s).content)
#         img = Image.open(file)
#         img.save(foldername+str(count)+'_s.jpg')
#
#         count+=1


