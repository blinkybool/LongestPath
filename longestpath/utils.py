"""
Various wrappers for decorating functions
"""
import multiprocessing
import os
import random
import signal
import time

import numpy as np
import psutil

from longestpath import brute
from longestpath.gen import gen_num_edges
from longestpath.kalp import solve_KaLP


def handler(queue, process_queue, func, args, kwargs):
    '''
    Handle exceptions here - it's difficult to handled them elsewhere
    '''
    try:
        assert "process_queue" not in kwargs
        kwargs["process_queue"] = process_queue
        result = func(*args, **kwargs)
    except Exception as e:
        result = {
            "failure" : repr(e)
        }
    queue.put(result)

def with_timeout(seconds, default=None):
    """
    Calls any function with timeout after 'seconds'.
    If a timeout occurs, 'action' will be returned or called if it is a function-like object.
    Handles exceptions by returning dictionary {"failure" : repr(e)}
    """

    def decorator(func):
        def wraps(*args, **kwargs):
            q = multiprocessing.Queue()
            process_queue = multiprocessing.Queue()
            p = multiprocessing.Process(target=handler, args=(q, process_queue, func, args, kwargs))
            p.start()
            p.join(timeout=seconds)

            while not process_queue.empty():
                pid = process_queue.get_nowait()
                if psutil.pid_exists(pid):
                    os.kill(pid, signal.SIGTERM)

            if p.is_alive():
                p.terminate()
                p.join()
                if hasattr(default, '__call__'):
                    return default()
                else:
                    return default
            else:
                return q.get()

        return wraps

    return decorator

def with_timed_result(func):
    '''
    Wraps func such that execution time is recorded and saved to dictionary returned by func
    at key "run_time"
    Usage: result_dict = with_timed_result(func)(x,y)
    '''
    def wrapped(*args, **kwargs):
        tick = time.perf_counter()
        result = func(*args, **kwargs)
        tock = time.perf_counter()
        assert type(result) == dict
        if not "run_time" in result:
            result["run_time"] = tock - tick

        return result
    return wrapped

def with_time(func):
    '''
    Usage: result, run_time = with_time(func)(x,y)
    '''
    def wrapped(*args, **kwargs):
        tick = time.perf_counter()
        result = func(*args, **kwargs)
        tock = time.perf_counter()
        return result, tock-tick

    return wrapped

if __name__ == "__main__":
    random.seed(0)
    np.random.seed(0)
    G = gen_num_edges(10, 40)
