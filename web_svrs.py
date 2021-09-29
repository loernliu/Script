import requests
import time
import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed


class WebSvr:

    def request_thread_product(self, url):
        """
        向svr发送请求
        :param random_svr:
        :return:
        """
        # print(threading.current_thread().name + "生产者准备向svr发送请求！")
        post_data = {
            "el_data": 'self.el_data',
            "vi_data": 'self.vi_data'
        }
        headers = {'content-type': "application/json"}
        response = requests.get(url, headers=headers, timeout=10)
        return response

    def send_svr_request(self, random_svr_list):
        """
        将返回的缺陷信息合并返回
        :param sorted_groups_dict:
        :return:
        """
        res_data_all = []
        with ThreadPoolExecutor(max_workers=100) as t:
            obj_list = []
            for random_svr in range(1000):
                obj = t.submit(self.request_thread_product, "http://192.168.3.215:8001/double/123")
                obj_list.append(obj)
            for future in as_completed(obj_list):
                res_data = future.result()
                # print("res_data:%s", res_data)
                res_data_all.append(res_data)
        print("res_data_all:%s", res_data_all)
        return res_data_all


if __name__ == "__main__":
    start_time = time.time()
    thread_req = WebSvr()
    random_svr_list = [
        "http://127.0.0.1:8000/vi_detect1",
        "http://127.0.0.1:8000/vi_detect2",
        "http://127.0.0.1:8000/vi_detect3",
        "http://127.0.0.1:8000/vi_detect4",
        "http://127.0.0.1:8000/vi_detect5"
    ]
    res_data_all = thread_req.send_svr_request("http://127.0.0.1:8000/vi_detect1")
    print(res_data_all)
    end_time = time.time()
    time_used = (end_time - start_time)
    print("用时: %.3f秒" % time_used)
    pass
