from bs4 import BeautifulSoup
import requests
import os
import re
import json
import pprint
import StringIO
from PIL import Image

def img_extractor_tripadvisor(url,folder_path):
    # url='https://www.tripadvisor.com/ShowUserReviews-g32060-d226020-r78195328-HYATT_house_Belmont_Redwood_Shores-Belmont_California.html'
    regex_review_id=re.compile(r'-r([\d]+)-')
    review_id=regex_review_id.search(url).group(1)

    regex_hotel_id=re.compile(r'-d([\d]+)-')
    hotel_id=regex_hotel_id.search(url).group(1)

    regex_area_id=re.compile(r'-g([\d]+)-')
    area_id=regex_area_id.search(url).group(1)



    r = requests.get(url)
    regex1 = re.compile(r'lazyImgs')
    regex2=re.compile(r'{"data":"https:\/\/media-cdn.tripadvisor.com\/media(.*)}')
    html = r.content
    # print html

    with open('test.html','w') as fp:
        fp.write(html)

    soup = BeautifulSoup(html,'lxml')

    imgs_text=[]
    for s in soup.find_all('script'):
        if regex1.search(s.text) is not None:
            # print s.text
            for data in regex2.finditer(s.text):
                imgs_text.append(str(data.group(0)))
    imgs_obj=[]
    for i in imgs_text:
        imgs_obj.append(json.loads(i))
    # print imgs_obj[0]['data']
    # print imgs_obj[0]['id']
    imgs_url_dict=dict()
    for i in imgs_obj:
         imgs_url_dict[i['id']]=i['data']

    # print imgs_url_dict
    # print imgs_obj
    regex3=re.compile(r'lazyload_(.*?)"')
    review=soup.find('div','reviewSelector')
    # print review


    imgs=review.find_all('li','ThumbNailContainer')
    if imgs:
        imgs_list=[]
        for img in imgs:
            # print img.find('img')['id']
            try:
                imgs_list.append(imgs_url_dict[img.find('img')['id']])
            except:
                pass
        # print imgs_list

    # foldername='./temp/'
    dir = os.path.dirname(folder_path)
    try:
        os.stat(dir)
    except:
        os.mkdir(dir)

    with open(folder_path+'img_urls.json', 'a') as outfile:
        json.dump({review_id:imgs_list}, outfile,indent=4)
        outfile.writelines(',')

    foldername=folder_path+area_id+'/'
    dir = os.path.dirname(foldername)
    try:
        os.stat(dir)
    except:
        os.mkdir(dir)

    foldername=folder_path+area_id+'/'+hotel_id+'/'
    dir = os.path.dirname(foldername)
    try:
        os.stat(dir)
    except:
        os.mkdir(dir)

    foldername=folder_path+area_id+'/'+hotel_id+'/'+review_id+'/'
    dir = os.path.dirname(foldername)
    try:
        os.stat(dir)
    except:
        os.mkdir(dir)

    file_names_set=set()
    for img_t in imgs_list:
        file_name=img_t.split('/')[-1]

        # file = StringIO.StringIO(requests.get(img_t).content)
        # img = Image.open(file)
        # suf_no=1
        # suffix=''
        # while os.path.isfile(foldername+file_name.split('.')[0]+suffix+'_t.'+file_name.split('.')[-1]):
        #     suf_no+=1
        #     suffix=str(suf_no)
        # if suf_no==1:
        #     suffix=''
        # img.save(foldername+file_name.split('.')[0]+suffix+'_t.'+file_name.split('.')[-1])

        img_s=str(img_t).replace('/photo-t/','/photo-s/')
        file = StringIO.StringIO(requests.get(img_s).content)
        img = Image.open(file)


        file_path_name=foldername+file_name.split('.')[0]+'_s.'+file_name.split('.')[-1]
        suf_no=1
        suffix=''
        while file_path_name in file_names_set:
            suf_no+=1
            suffix=str(suf_no)
            file_path_name=foldername+file_name.split('.')[0]+suffix+'_s.'+file_name.split('.')[-1]

        # print file_path_name
        file_names_set.add(file_path_name)
        img.save(file_path_name)
    # print file_names_set
        # img_f = str(img_t).replace('/photo-t/', '/photo-f/')
        # file = StringIO.StringIO(requests.get(img_f).content)
        # img = Image.open(file)
        # # suffix=1
        # # while os.path.isfile(foldername+file_name.split['.'][0]+str(suffix)+'_t.'+file_name.split['.'][1]):
        # #     suffix+=1
        # # if suffix==1:
        # #     suffix=''
        # img.save(foldername+file_name.split('.')[0]+suffix+'_f.'+file_name.split('.')[-1])
        #
        #
    return review_id

