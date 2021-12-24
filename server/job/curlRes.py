from res_model import *

import multiprocessing as mp

def __task(res: LineResponse):
    # todo: send curl with the post response: res
    print(res.LineName)
    return

def sendInfo(res: LineResponse):
    p = mp.Process(target=__task, args=(res,))
    p.daemon = True
    p.start()
    print("sent!!!")    
