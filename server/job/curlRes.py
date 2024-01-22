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

def __shrug_task(res):
    # todo: send curl with the post response: res
    cmd = f"sh job/doShrug.sh \'{res[0]}\' {res[1]} {res[2]} \"{res[3]}\" \'{res[4]}\'"
    print(f"[__shrug_task] {cmd = }", flush=True)
    os.system(cmd)
    return
def __eye_task(res):
    # todo: send curl with the post response: res
    cmd = f"sh job/doEye.sh \'{res[0]}\' \"{res[1]}\" \'{res[2]}\'"
    print(f"[__eye_task] {cmd = }", flush=True)
    os.system(cmd)
    return

def sendInfo2(video_path, frame_numbers):
    demo_json_path = "demo.json"
    output_video = "output.mp4"
    output_dir = os.path.dirname(video_path)
    p = mp.Process(target=__shrug_task, args=([video_path, demo_json_path, output_video, frame_numbers, output_dir],))

    p2 = mp.Process(target=__eye_task, args=([video_path, frame_numbers, output_dir],))
    p.daemon = True
    p2.daemon = True
    p2.start()
    p.start()
    p.join()
    p2.join()
    print("sent!!!")    


if __name__ == "__main__":
    res = ["~/fake_video.mp4",  "demo.json" ,"output.mp4",  "50 56 57 58 59 110", "/mnt/nas/test"]
    sendInfo2("/mnt/nas/test/test/IMG_5540.mp4", "50 56 57 58 59 110")
    # test = Test("123")
    # test.hello()
    # print("hello")