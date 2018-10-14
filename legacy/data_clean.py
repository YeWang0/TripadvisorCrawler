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


path = 'data/reviewer_data/Tripadvisor_reviewer_path_ONLY.xlsx'
xls = get_data(path)
data = json.dumps(xls, default=json_serial)
lines = json.loads(data, object_hook=json_util.object_hook)['reviewer_info']

# names = set([l[1] for l in lines[1:]])

# new_lines = [lines[0]]
# for line in lines[1:]:
#     if line[1] in names:
#         new_lines.append(line)
#         names.remove(line[1])
#
# result = OrderedDict()
# result.update({"reviewer_info": new_lines})
# save_data(path, result)


reviewer_map = {}
for line in lines[1:]:
    reviewer_map[line[1]] = line[0]
output = {}
for i in xrange(1, 790):
    path = 'data/hotels_by_city/Dallas/Dallas_shard_{}.xlsx'.format(i)
    xls = get_data(path)
    data = json.dumps(xls, default=json_serial)
    hotel_info = json.loads(data, object_hook=json_util.object_hook)['hotel_info']
    review_info = json.loads(data, object_hook=json_util.object_hook)['review_info']
    count = 0
    new_review_info = [review_info[0]]
    for line in review_info[1:]:
        if line[2] in reviewer_map:
            line[1] = reviewer_map[line[2]]
            new_review_info.append(line)
        else:
            print line[1:3]
            count+=1
    output[i]=count

print "Missing: ", output
print "All: ", sum(output.values())

    # result = OrderedDict()
    # result.update({"review_info": new_review_info})
    # result.update({"hotel_info": hotel_info})
    # save_data(path.replace('1','1_x'), result)