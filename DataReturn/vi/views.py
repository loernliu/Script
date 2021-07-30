from django.shortcuts import HttpResponse
from django.http import JsonResponse
import json
from datetime import datetime
import base64
import uuid
from enum import Enum

import numpy

# from .dict_data import DictData, DICTDATA_CLASSES, HPEnum, ENUM_CLASSES



# Create your views here.

data_str = {'error': '', 'vi_result': '{"__type__": "DictData", "cls_name": "VIResult", "value": {"error": "", "defects": [{"class": "baidian", "prob": 0.8296175599098206, "loc": [3, 9], "coord": [2558, 1838, 2839, 1854]}], "is_ng": false, "ext_info": {}}}'}

def return_data(request):
    # data_str = {'error': 'algorithm failure', 'vi_result': 'null'}
    print(data_str)
    return JsonResponse(data_str, safe=False)

def save_vi_result(request):
    return JsonResponse(data_str, safe=False)

