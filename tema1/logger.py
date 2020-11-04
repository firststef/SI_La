from threading import Lock

enabled = True
mutex = Lock()


def enable_logging():
    global enabled
    enabled = True


def disable_logging():
    global enabled
    enabled = False


def log(*args, **kwargs):
    if enabled:
        mutex.acquire()
        print(*args, **kwargs)
        mutex.release()