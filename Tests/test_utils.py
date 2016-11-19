import logging
import datetime

def log_name(func):

    def wrapper(*args, **kwargs):
        logging.info("START {}: {:%Y-%m-%d %H:%M:%S}".format(func.__name__, datetime.datetime.now()))
        func(*args, **kwargs)

    return wrapper

