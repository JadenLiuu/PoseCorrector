import os
import time
from datetime import datetime

def now_unix_micro():
    # function available after python 3.7
    return time.time_ns()/1000.0

def dir_init(pathDir):
    if not os.path.exists(pathDir):
        os.makedirs(pathDir)

def date_to_timestamp(time_str):
    datetime_obj = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S.%f")
    timestamp = datetime_obj.timestamp()
    timestamp_ms = timestamp * 1000000 + int(datetime_obj.microsecond)
    # print(f"{timestamp_ms = }")
    return int(timestamp_ms)

if __name__ == "__main__":
    date_str = "2024-01-15 10:17:00.000000"
    print(date_to_timestamp(date_str))
   