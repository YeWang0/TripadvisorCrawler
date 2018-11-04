from datetime import datetime
from collections import OrderedDict
from pyexcel_xls import get_data
from pyexcel_xls import save_data
from bson import json_util
import json


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial


def read_xls(file_path, sheet_name_list=None):
    xls = get_data(file_path)
    data=json.dumps(xls, default=json_serial)
    file_content = {}
    data_dict = json.loads(data, object_hook=json_util.object_hook)
    sheets = [k for k in data_dict]
    # print sheets
    for sheet in sheets:
        if not sheet_name_list or sheet in sheet_name_list:
            file_content[sheet] = data_dict[sheet]
    return file_content


def write_xls(file_path, content):
    result = OrderedDict()
    for sheet_name in content:
        result.update({sheet_name:content[sheet_name]})
    save_data(file_path,result)