from functools import wraps
import datetime
from filemanager import *


class Decorator(object):
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def log_it(func):
        @wraps(func)
        def logger():
            start_time = datetime.datetime.now()
            result = func()
            execution_time_in_microseconds = (datetime.datetime.now() - start_time).microseconds
            log_str = str(start_time.date()) + ' in ' + str(start_time.time()) + ' function: "' + func.__name__ + '()" was performed for ' + str(execution_time_in_microseconds) + ' microseconds'
            FileManager.update_log(log_str)
            return result
        return logger


    def cach_it(func):
        def cacher(*args):
            key_for_cach = func.__name__ + '('
            for arg in args:
              key_for_cach += str(arg) + ','
            if len(args) > 0:
                key_for_cach = key_for_cach[0:-1]
            key_for_cach  += ')'
            cached_value = FileManager.find_cached_value(key_for_cach)
            if cached_value is not None:
                return cached_value
            else:
                result = func(*args)
                FileManager.upload_value_to_cach(key_for_cach, result)
                return result
        return cacher
