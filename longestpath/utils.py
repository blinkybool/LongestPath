import multiprocessing
import time

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

def timeout(seconds, action=None):
    """
    Calls any function with timeout after 'seconds'.
    If a timeout occurs, 'action' will be returned or called if it is a function-like object.
    """
    def handler(queue, func, args, kwargs):
        queue.put(func(args, *kwargs))

    def decorator(func):

        def wraps(*args, **kwargs):
            q = multiprocessing.Queue()
            p = multiprocessing.Process(target=handler, args=(q, func, args, kwargs))
            p.start()
            p.join(timeout=seconds)
            if p.is_alive():
                p.terminate()
                p.join()
                if hasattr(action, '__call__'):
                    return action()
                else:
                    return action
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