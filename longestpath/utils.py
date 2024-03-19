import multiprocessing

def call(fun, args, kwargs):
    return fun(*args, **kwargs)


def run_with_timeout(fun, args=[], kwargs={}, timeout: float | None = None):
    if timeout == None:
        return fun()

    else:
        result = None

        with multiprocessing.Pool(processes=1) as pool:
            result = pool.apply_async(fun, args, kwargs).get(timeout=timeout)

        return result
