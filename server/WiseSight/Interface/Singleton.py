import time
from threading import Lock

class SingletonMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


# class SingletonMeta(type):
#     __instance = None
#     __lock = Lock()
#     def __new__(cls, *args, **kwargs):
#         with cls.__lock:
#             if cls.__instance is None:
#                 # 1. 代码量多了，遇到阻塞了
#                 # 2. 计算机资源有限
#                 time.sleep(0.1)
#                 cls.__instance = super().__new__(cls)
#             return cls.__instance