
import json
import grequests
import time
start_time = time.time()
headers = {'content-type': "application/json"}
with open(r"D:\Gitee\el_app\test.json", "r", encoding='utf8') as f:
    post_data = f.read()
post_data = post_data
# req_list = [post("http://192.168.3.216:12140/ws_vi_detect", headers=headers, data=post_data, timeout=1000) for url in range(2)]
req_list = [grequests.post("http://127.0.0.1:8003/detect_data", headers=headers, data=post_data, timeout=10) for url in range(40)]


def except_callback(request, exception):
    print('==================================')
    print(request)
    print(type(exception))
    print(exception)


res_list = grequests.map(req_list, except_callback)
print(res_list)
# for resp in res_list:
#     print(str(res_list.index(resp)) * 40)
#     # print("status:%s" % resp.status)
#     # print("url:%s" % resp.url)
#     print("text:%s" % resp.text())
#     print("read:%s" % resp.read())
#     print("json:%s" % resp.json())
#     res_data = resp.json()
#     print("vi_result:%s" % res_data['vi_result'])

end_time = time.time()
time_used = (end_time - start_time)
print("用时: %.3f秒" % time_used)