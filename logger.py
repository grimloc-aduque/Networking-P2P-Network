import time
import datetime
import os


class Logger:
    _path = None

    def __init__(self, path):
        self._path = path

    def add(self, ip, port, sentido, mensaje):
        time_stamp = time.time()
        str_time_stamp = datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S')
        line = f'{str_time_stamp},{ip},{port},{sentido},{mensaje}'
        os.system(f'echo "{line}" >> {self._path}')
