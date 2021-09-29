import asyncio
from functools import partial

from aiohttp import ClientSession, ClientTimeout


__all__ = (
    'map',
    'get', 'options', 'head', 'post', 'put', 'patch', 'delete'
)


class AsyncRequest(object):
    """ Asynchronous request."""
    def __init__(self, method, url, **kwargs):
        self.method = method
        self.url = url

        self.kwargs = kwargs
        self.response = None

    async def send(self, semaphore, **kwargs):
        """"""
        merged_kwargs = {}
        merged_kwargs.update(self.kwargs)
        timeout = self.kwargs.get('timeout', None)
        if timeout:
            merged_kwargs.update({'timeout': ClientTimeout(total=timeout)})
        merged_kwargs.update(kwargs)
        try:
            with await semaphore:
                self.session = ClientSession()
                async with self.session:
                    self.response = await self.session.request(self.method, self.url, **merged_kwargs)
        except Exception as e:
            self.exception = e
        return self


async def send(request_list):
    """Sends the request object"""
    tasks = []
    semaphore = asyncio.Semaphore(500)
    for request in request_list:
        tasks.append(request.send(semaphore))
    await asyncio.gather(*tasks)


def map(requests, exception_handler=None):
    """Concurrently converts a list of Requests to Responses."""

    requests = list(requests)
    loop = asyncio.get_event_loop()

    # future = asyncio.ensure_future(send(requests))
    loop.run_until_complete(send(requests))

    ret = []

    for request in requests:
        if request.response is not None:
            ret.append(request.response)
        elif exception_handler and hasattr(request, 'exception'):
            ret.append(exception_handler(request, request.exception))
        elif exception_handler and not hasattr(request, 'exception'):
            ret.append(exception_handler(request, None))
        else:
            ret.append(None)

    return ret


get = partial(AsyncRequest, 'GET')
options = partial(AsyncRequest, 'OPTIONS')
head = partial(AsyncRequest, 'HEAD')
post = partial(AsyncRequest, 'POST')
put = partial(AsyncRequest, 'PUT')
patch = partial(AsyncRequest, 'PATCH')
delete = partial(AsyncRequest, 'DELETE')


if __name__ == "__main__":
    import json, random, time
    start_time = time.time()
    headers = {'content-type': "application/json"}
    post_data = json.dumps({'el_data': "img_path", 'vi_data': 'vi_data'})
    req_list = [get("http://192.168.3.215:8001/double/123", headers=headers, timeout=10) for url in range(500)]
    # print(req_list)
    def except_callback(request, exception):
        print(request)
        print(exception)
    res_list = map(req_list, except_callback)
    print(res_list)
    end_time = time.time()
    time_used = (end_time - start_time)
    print("用时: %.3f秒" % time_used)
    # for res in res_list:
    #     print(res.status)
    #     print(res.json)

