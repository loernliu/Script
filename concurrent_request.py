"""asynchronous http requests
~~~~~~~~~~~~~~~~~~~~~

Requests is an HTTP library, written in Python, for human beings.
Basic GET usage:
    from common import concurrent_request as concurrent

    urls = [
        'https://www.baidu.com',
        'http://www.bilibili.com',
        'http://www.gitee.com'
    ]
    Create a set of unsent Requests:

    >>> rs = (concurrent.get(u) for u in urls)
    Send them all at the same time:

    >>> concurrent.map(rs)
    [<Response [200]>, <Response [200]>, <Response [200]>, <Response [200]>, None, <Response [200]>]
    >>> for resp in concurrent.map(rs):
    >>>     print(resp.json())
    >>>     print(resp.status)
    json:{'error': '', 'vi_result': '{"__type__": "DictData", "cls_name": "VIResult", "value": {"error": "", "defects": [{"class": "xuhan", "prob": 0.999, "loc": [2, 1], "coord": [400, 200, 500, 300]}], "is_ng": false, "ext_info": {}}}'}
    status:200
"""
from cmath import pi
import sys
import asyncio
import logging
from functools import partial

from aiohttp import ClientSession, ClientTimeout


__all__ = ("map", "get", "options", "head", "post", "put", "patch", "delete")


class AsyncRequest(object):
    """Asynchronous request."""

    def __init__(self, method, url, **kwargs):
        self.method = method
        self.url = url

        self.kwargs = kwargs
        self.response = None

    async def send(self, **kwargs):
        """
        Prepares request based on parameter passed to constructor and optional ``kwargs```.
        Then sends request and saves response to :attr:`response`

        :returns: ``Response``
        """
        merged_kwargs = {}
        merged_kwargs.update(self.kwargs)
        timeout = self.kwargs.get("timeout", None)
        if timeout:
            merged_kwargs.update({"timeout": ClientTimeout(total=timeout)})
        merged_kwargs.update(kwargs)
        try:
            self.session = ClientSession()
            async with self.session:
                self._response = await self.session.request(
                    self.method, self.url, **merged_kwargs
                )
                # the `start` `read` `text` `json` method of the response is async, convert to sync
                # temp = await self._response.json()
                # print('--------------------->')
                # print(temp)
                self.response = MapResponse(response=self._response)
                self.response = await self.response.process()
        except Exception as e:
            self.exception = e
        return self


class MapResponse:
    """convert `ClientResponse` async mothod to sync"""

    def __init__(self, response):
        self.response = response

    def __getattr__(self, name):
        logging.debug("name:%s,type:%s" % (name, type(name)))

        val = getattr(self.response, name)
        logging.debug("val:%s,val:%s" % (val, type(val)))

        return val

    async def process(self):
        self._json = await self.response.json()
        self._read = await self.response.read()
        self._text = await self.response.text()
        return self

    def json(self):
        return self._json

    def text(self):
        return self._text

    def read(self):
        return self._read


async def send(request_list):
    """Sends the request object"""
    tasks = []
    for request in request_list:
        tasks.append(request.send())
    await asyncio.gather(*tasks)


def map(requests, exception_handler=None):
    """Concurrently converts a list of Requests to Responses."""
    requests = list(requests)
    try:
        if sys.platform == "win32":
            # windows use ProactorEventLoop
            loop = asyncio.ProactorEventLoop()
            asyncio.set_event_loop(loop)
        else:
            loop = asyncio.get_event_loop()
    except RuntimeError:
        # If the current thread doesn’t already have an event loop associated with it
        # the RuntimeError will be raised
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    finally:
        # future = asyncio.ensure_future(send(requests))
        loop.run_until_complete(send(requests))

        loop.close()

    ret = []

    for request in requests:
        if request.response is not None:
            ret.append(request.response)
        elif exception_handler and hasattr(request, "exception"):
            ret.append(exception_handler(request, request.exception))
        elif exception_handler and not hasattr(request, "exception"):
            ret.append(exception_handler(request, None))
        else:
            ret.append(None)

    return ret


get = partial(AsyncRequest, "GET")
options = partial(AsyncRequest, "OPTIONS")
head = partial(AsyncRequest, "HEAD")
post = partial(AsyncRequest, "POST")
put = partial(AsyncRequest, "PUT")
patch = partial(AsyncRequest, "PATCH")
delete = partial(AsyncRequest, "DELETE")


if __name__ == "__main__":
    import json
    import time

    start_time = time.time()
    headers = {"content-type": "application/json"}
    with open(r"C:\Users\LiuWanpin\Downloads\test.json", "r", encoding="utf8") as f:
        post_data = f.read()
    post_data = post_data
    # req_list = [post("http://192.168.3.216:12140/ws_vi_detect", headers=headers, data=post_data, timeout=1000) for url in range(2)]
    req_list = [
        post(
            "http://127.0.0.1:8000/vi_detect1",
            headers=headers,
            data=post_data,
            timeout=10,
        )
        for url in range(1)
    ]
    print(req_list)

    def except_callback(request, exception):
        print("================start================")
        print(request)
        print(type(exception))
        print(exception)
        print("================end==================")

    res_list = map(req_list, except_callback)
    print(res_list)
    for resp in res_list:
        print(str(res_list.index(resp)) * 40)
        print("status:%s" % resp.status)
        # print("url:%s" % resp.url)
        # print("text:%s" % resp.text())
        # print("read:%s" % resp.read())
        # print("json:%s" % resp.json())
        # res_data = resp.json()
        # print("vi_result:%s" % res_data['vi_result'])

    end_time = time.time()
    time_used = end_time - start_time
    print("用时: %.3f秒" % time_used)
