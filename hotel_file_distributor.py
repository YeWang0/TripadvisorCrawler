from pyexcel_xls import get_data
from pyexcel_xls import save_data
from collections import OrderedDict
import json
from bson import json_util
from datetime import datetime

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    # raise TypeError ("Type not serializable")

def split_hotel_file(path,file_number):

    xls = get_data(path)
    data = json.dumps(xls, default=json_serial)
    lines = json.loads(data, object_hook=json_util.object_hook)['hotel_info']
    lines2 = json.loads(data, object_hook=json_util.object_hook)['review_info']
    lines3 = json.loads(data, object_hook=json_util.object_hook)['reviewer_info']
    # lines[0].append('Link')
    head=lines[0]
    head2 = lines2[0]
    head3 = lines3[0]
    interval=1000
    start=1
    count=1
    for i in xrange(start,len(lines2),interval):
        result = OrderedDict()
        print i,min(i+interval,len(lines2))
        data=lines2[i:min(i+interval,len(lines2))]
        data.insert(0,head2)
        result.update({"hotel_info": lines})
        result.update({"review_info": data})
        result.update({"reviewer_info": [head3]})
        save_data('data/sub/Tripadvisor_SF_sub_'+str(file_number)+'_'+str(count)+'.xlsx', result)
        count+=1
    # for i in xrange(1, len(lines)):
    #     while len(lines[i]) < 9:
    #         lines[i].append('')
    #     q = [str(x) for x in lines[i]]
    #     # print q
    #     # try:
    #     link = url_crawler(q[0], ' '.join(q[2:5]) + " tripadvisor").start_crawl()
    #     print link
    #     try:
    #         lines[i][7] = link
    #     except:
    #         lines[i].append(link)
    #         # time.sleep(1)
    #         # except:
    #         #     # link=''
    #         #     # print 'fail'
    #         #     break
    #
    # # # print lines[:10]

    # result.update({"hotel_info": lines})
    # result.update({"review_info": []})
    # result.update({"reviewer_info": []})
    # save_data(path, result)


def split_hotel_file(path):
    xls = get_data(path)
    data = json.dumps(xls, default=json_serial)
    lines = json.loads(data, object_hook=json_util.object_hook)['hotel_info']
    lines2 = json.loads(data, object_hook=json_util.object_hook)['review_info']
    lines3 = json.loads(data, object_hook=json_util.object_hook)['reviewer_info']

    head=lines[0]
    head2 = lines2[0]
    head3 = lines3[0]

    interval=1
    start=1
    count=1
    # print head
    for i in xrange(start,len(lines),interval):
        result = OrderedDict()
        print i, min(i+interval,len(lines))
        data=lines[i:min(i+interval,len(lines))]
        data.insert(0,head)
        result.update({"hotel_info": data})
        result.update({"review_info": [head2]})
        result.update({"reviewer_info": [head3]})
        save_data(path.replace('.xlsx', '_shard_{}.xlsx'.format(i)), result)
        count+=1

if __name__ == '__main__':
    # for i in xrange(3,19):
    #     print i
    path='data/split/Tripadvisor_new_orleans.xlsx'
    split_hotel_file(path)