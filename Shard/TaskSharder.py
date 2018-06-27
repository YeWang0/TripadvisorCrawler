from pyexcel_xls import get_data
from pyexcel_xls import save_data
from collections import OrderedDict
import json
from bson import json_util
from datetime import datetime
import os.path

class TaskSharder(object):
    def __init__(self):
        pass

    def json_serial(self, obj):
        """JSON serializer for objects not serializable by default json code"""

        if isinstance(obj, datetime):
            serial = obj.isoformat()
            return serial

    def write_to_xlsx(self, output_file):
        return
    def read_from_xlsx(self, input_file):
        return

    def shard(self, path, output_template):
        xls = get_data(path)
        data = json.dumps(xls, default=self.json_serial)
        lines = json.loads(data, object_hook=json_util.object_hook)['hotel_info']
        lines2 = json.loads(data, object_hook=json_util.object_hook)['review_info']
        # lines3 = json.loads(data, object_hook=json_util.object_hook)['reviewer_info']

        head=lines[0]
        head2 = lines2[0]
        # head3 = lines3[0]

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
            # result.update({"reviewer_info": [head3]})
            save_data(output_template.format(i), result)
            count+=1

    def shard_reviewer(self, interval, path, output_format):
        xls = get_data(path)
        data = json.dumps(xls, default=self.json_serial)
        lines = json.loads(data, object_hook=json_util.object_hook)['reviewer_info']

        head=lines[0]
        start=1
        count=1
        # print head
        for i in xrange(start,len(lines),interval):
            output_file = output_format.format(count)
            result = OrderedDict()
            print i, min(i+interval,len(lines))
            if os.path.isfile(output_file):
                print True
                # if not os.path.isfile(output_format.format(count + 1)):
                #     data=lines[i:min(i+interval,len(lines))]
                #     data.insert(0,head)
                #     result.update({"reviewer_info": data})
                #     output_file = output_format.format(str(count)+"_x")
                #     save_data(output_file, result)
            else:
                data=lines[i:min(i+interval,len(lines))]
                data.insert(0,head)
                result.update({"reviewer_info": data})
                save_data(output_file, result)
            count+=1

ts = TaskSharder()
# ts.shard_reviewer(100, '../data/reviewer_data/Tripadvisor_reviewer_path_ONLY.xlsx', '../data/reviewer_data/reviewer_split/Tripadvisor_reviewer_path_shard_{}.xlsx')

ts.shard("../data/hotels_by_city/City/Los_Angeles_filled.xlsx", "../data/hotels_by_city/Los_Angeles/Los_Angeles_shard_{}.xlsx")
