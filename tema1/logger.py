enabled = True


def enable_logging():
    global enabled
    enabled = True


def disable_logging():
    global enabled
    enabled = False


def log(*args, **kwargs):
    if enabled:
        print(*args, **kwargs)