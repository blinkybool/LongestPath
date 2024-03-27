import multiprocessing
import time
from.kalp import solve_KaLP
from .gen import gen_num_edges
# from benchmarking import Solver
import longestpath.brute as brute
import numpy as np
import random

def call(fun, args, kwargs):
    return fun(*args, **kwargs)


def run_with_timeout(fun, args=[], kwargs={}, timeout: float | None = None):
    if timeout == None:
        return fun(*args, **kwargs)

    else:
        result = None

        with multiprocessing.Pool(processes=1) as pool:
            result = pool.apply_async(fun, args, kwargs).get(timeout=timeout)

        return result

def handler(queue, func, args, kwargs):
    '''
    Handle exceptions here - it's difficult to handled them elsewhere
    '''
    # try:
    result = func(*args, **kwargs)
    # except Exception as e:
    #     result = {
    #         "failure" : repr(e)
    #     }
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
            p = multiprocessing.Process(target=handler, args=(q, func, args, kwargs))
            p.start()
            p.join(timeout=seconds)
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

# def with_try_result(func):
#     def wrapped(*args, **kwargs):
#         try:
#             result = func(*args, **kwargs)
#         except Exception as e:
#             result = {
#                 "failure" : repr(e)
#             }
#         return result

#     return wrapped

def test():
    while True:
        print("Z")
        time.sleep(0.1)

    return 1

if __name__ == "__main__":
    random.seed(0)
    np.random.seed(0)
    G = gen_num_edges(100, 400)
    # print(with_timeout(2)(brute.solve)(G, "FAST_BOUND"))
    # print(with_timeout(2)(solve_KaLP)(G))
    run_with_timeout(solve_KaLP, [G], timeout=2)