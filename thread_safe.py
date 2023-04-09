import _thread as thread
from functools import wraps
from queue import Queue


class CallSerializer:
    def __init__(self):
        self.queue = Queue()
        thread.start_new_thread(
            self.call_functions,
            (),
        )

    def call_functions(self):
        while 1:
            func, args, kwargs = self.queue.get(block=True)
            func(*args, **kwargs)

    def serialize_call(self, function):
        """
        a call to a function decorated will not have
        overlapping calls, i.e thread safe
        """

        @wraps(function)
        def decorator(*args, **kwargs):
            self.queue.put((function, args, kwargs))

        return decorator
