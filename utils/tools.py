import logging
import os
import sys


def Singleton(cls):
    _instance = {}

    def _singleton(*args, **kargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kargs)
        return _instance[cls]

    return _singleton


# 日志类
@Singleton
class Logger(logging.Logger):
    def __init__(self, application: str = '', path: str = None):
        super().__init__(application, logging.INFO)
        fmt = '%(asctime)s-%(name)s-%(levelname)s: %(message)s'
        hdlr = logging.StreamHandler(sys.stdout)
        hdlr.formatter = logging.Formatter(fmt)
        self.addHandler(hdlr)


# 获取路径
def get_root_path():
    return os.path.split(os.path.realpath(__file__))[0]
