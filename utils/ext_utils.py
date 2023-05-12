from django.utils.http import urlquote
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse, HttpResponse
from xlrd import xldate_as_tuple
from django.db import connection

import os
import re
import pandas as pd
import numpy as np
import datetime
import time


def VIEW_SUCCESS(msg=None, data={}):
    res_dict = {'code': 1, 'msg': 'success', 'data': data}
    if msg:
        res_dict['msg'] = msg
    return JsonResponse(res_dict)


def VIEW_FAIL(msg=None, data={}):
    res_dict = {'code': 0, 'msg': 'fail', 'data': data}
    if msg:
        res_dict['msg'] = msg
    return JsonResponse(res_dict)


def REST_SUCCESS(data={}):
    return Response(data)


def REST_FAIL(data={}):
    return Response(data, status=status.HTTP_400_BAD_REQUEST)


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def trans_type(x):
    if x:
        try:
            x = str(int(x))
        except:
            x = x
        return x


def trans_float_ts(ts, infmt, outfmt):
    """
    转换日期格式
    """
    try:
        if not ts:
            return ''
        if isinstance(ts, pd._libs.tslibs.timestamps.Timestamp):
            ts = ts.to_pydatetime()
        if isinstance(ts, str):
            if re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d+|\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}|\d{4}-\d{2}-\d{2}', ts):
                return ts
            try:
                dt = datetime.datetime.strptime(ts, infmt)
            except:
                dt = datetime.datetime(*xldate_as_tuple(ts, 0))
        elif isinstance(ts, datetime.datetime):
            dt = ts
        return dt.strftime(outfmt)
    except:
        return ts


def execute_batch_sql(sql, datas):
    if not datas:
        return None
    with connection.cursor() as cursor:
        res = cursor.executemany(sql, datas)
    return res


def create_suffix():
    ts = time.time()
    suffix = str(int(round(ts, 5) * 10**5))[:15]
    return suffix


def create_excel_resp(file_path, filename):
    with open(file_path, 'rb') as f:
        result = f.read()
    response = HttpResponse(result)
    response['Content-Type'] = 'application/vnd.ms-excel;charset=UTF-8'
    response['Content-Disposition'] = 'attachment;filename="' + urlquote(filename) + '.xlsx"'
    return response


def get_file_path(prefix, dir_name='report_files'):
    current_path = os.path.dirname(__file__)
    file_dir = os.path.join(current_path, dir_name)
    if not os.path.exists(file_dir):
        os.mkdir(file_dir)

    file_name = '{}-{}'.format(prefix, create_suffix())
    file_path = os.path.join(file_dir, file_name)
    return file_path
