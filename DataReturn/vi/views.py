import random
import time
from django.http import JsonResponse

# Create your views here.

data_list = [{'error': '', 'vi_result': '{"__type__": "DictData", "cls_name": "VIResult", "value": {"error": "", "defects": [{"class": "yinlie", "prob": 0.999, "loc": [1, 1], "coord": [100, 120, 200, 220]}], "is_ng": false, "ext_info": {}}}'}]


def return_data(request):
    # data_str = {'error': 'algorithm failure', 'vi_result': 'null'}

    """
    @FLASK_APP.route('/vi_detect', methods=['POST'])
    img_cache_key = None
    try:
        data = request.get_data()
        json_data = json.loads(data.decode("utf-8"), cls=HPJsonDecoder)

        el_data = json_data['el_data']
        el_data.img_info.cache_image_bytes()
        img_cache_key = el_data.img_info._img_bytes
        vi_data = json_data['vi_data']

        logging.info('get a detect task from station: facility_id=%s, product_line=%s, equip_id=%s', el_data.mes_info.facility_id, el_data.mes_info.product_line, el_data.mes_info.equip_id)
        vi_result = do_vi_detect(el_data, vi_data)
        return jsonify({'error': '', 'vi_result': json.dumps(vi_result, cls=HPJsonEncoder)})
    except redis.exceptions.ConnectionError:
        logging.exception('redis 连接错误')
        REDIS_MGR.clear_redis_cache()
        return jsonify({'error': 'redis connection failure', 'vi_result': json.dumps(None, cls=HPJsonEncoder)})
    except Exception:
        logging.exception('algorithm failure')
        return jsonify({'error': 'algorithm failure', 'vi_result': json.dumps(None, cls=HPJsonEncoder)})
    finally:
        if isinstance(img_cache_key, uuid.UUID):
            delete_result = REDIS_MGR.redis_cache.delete(str(img_cache_key))
            logging.info('删除图像缓存%s is %s', el_data.img_info.img_name, delete_result)
    """
    data_list.append({'error': 'algorithm failure', 'vi_result': 'null'})
    data_list.append({'error': '', 'vi_result': '{"__type__": "DictData", "cls_name": "VIResult", "value": {"error": "", "defects": [{"class": "xuhan", "prob": 0.999, "loc": [1, 2], "coord": [600, 100, 700, 200]}], "is_ng": false, "ext_info": {}}}'})
    data_list.append({'error': '', 'vi_result': '{"__type__": "DictData", "cls_name": "VIResult", "value": {"error": "", "defects": [{"class": "xuhan", "prob": 0.999, "loc": [2, 1], "coord": [400, 200, 500, 300]}], "is_ng": false, "ext_info": {}}}'})
    data_list.append({'error': '', 'vi_result': '{"__type__": "DictData", "cls_name": "VIResult", "value": {"error": "", "defects": [], "is_ng": false, "ext_info": {}}}'})
    data_list.append({'error': '', 'vi_result': '{"__type__": "DictData", "cls_name": "VIResult", "value": {"error": "", "defects": [], "is_ng": false, "ext_info": {}}}'})
    data_list.append({'error': '', 'vi_result': '{"__type__": "DictData", "cls_name": "VIResult", "value": {"error": "", "defects": [], "is_ng": false, "ext_info": {}}}'})
    data_list.append({'error': '', 'vi_result': '{"__type__": "DictData", "cls_name": "VIResult", "value": {"error": "", "defects": [], "is_ng": false, "ext_info": {}}}'})
    data_list.append({'error': '', 'vi_result': '{"__type__": "DictData", "cls_name": "VIResult", "value": {"error": "", "defects": [], "is_ng": false, "ext_info": {}}}'})
    # data_list.append({'error': 'redis connection failure', 'vi_result': 'null'})
    res = random.choice(data_list)
    print(res)
    time.sleep(random.randint(0, 15))
    return JsonResponse(res, safe=False)


def data_return1(request):
    # res = {'error': '', 'vi_result': '{"__type__": "DictData", "cls_name": "VIResult", "value": {"error": "", "defects": [{"class": "heidian", "prob": 0.8296175599098206, "loc": [3, 9], "coord": [2558, 1838, 2839, 1854]}], "is_ng": false, "ext_info": {}}}'}
    res = {'111': 111}
    temp = random.randint(0, 13)
    print(temp)
    # time.sleep(temp)
    return JsonResponse(res, safe=False)


def data_return2(request):
    # res = {'error': '', 'vi_result': '{"__type__": "DictData", "cls_name": "VIResult", "value": {"error": "", "defects": [{"class": "yinlie", "prob": 0.99, "loc": (1, 1), "coord": [100, 120, 200, 220]}], "is_ng": false, "ext_info": {}}}'}
    res = {'222': 222}
    print(2)
    # time.sleep(11)
    return JsonResponse(res, safe=False)

def data_return3(request):
    print(3)
    res = {'333': 333}
    # res = {'error': '', 'vi_result': '{"__type__": "DictData", "cls_name": "VIResult", "value": {"error": "", "defects": [{"class": "xuhan", "prob": 0.99, "loc": (1, 2), "coord": [600, 100, 700, 200]}], "is_ng": false, "ext_info": {}}}'}
    return JsonResponse(res, safe=False)

def data_return4(request):
    res = {'444': 444}
    return JsonResponse(res, safe=False)

def data_return5(request):
    res = {'555': 555}
    return JsonResponse(res, safe=False)


def save_vi_result(request):
    return JsonResponse(data_list, safe=False)
