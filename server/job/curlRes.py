import os
import sys
sys.path.append('../ai-server')
sys.path.append('..')
# from res_model import *
import multiprocessing as mp
# import test.Test
# from ai_server.eyeDetection.detect import Detector



# def __task(res: LineResponse):
#     # todo: send curl with the post response: res
#     print(res.LineName)
#     return

# def sendInfo(res: LineResponse):
#     p = mp.Process(target=__task, args=(res,))
#     p.daemon = True
#     p.start()
#     print("sent!!!")    

def __task2(res):
    # todo: send curl with the post response: res
    print(res)
    cmd = f"sh job/doShrug.sh {res[0]} {res[1]} {res[2]} \"{res[3]}\" {res[4]}"
    print(cmd)
    os.system(cmd)
    return

def sendInfo2(res):
    p = mp.Process(target=__task2, args=(res,))
    p.daemon = True
    p.start()
    p.join()
    print("sent!!!")    


if __name__ == "__main__":
    res = ["~/fake_video.mp4",  "demo.json" ,"output.mp4",  "50 56 57 58 59 110", "/mnt/nas/test"]
    sendInfo2(res)
    # test = Test("123")
    # test.hello()
    # print("hello")