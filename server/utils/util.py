import os
import time

def now_unix_micro():
    # function available after python 3.7
    return time.time_ns()/1000.0

def dir_init(pathDir):
    if not os.path.exists(pathDir):
        os.makedirs(pathDir)