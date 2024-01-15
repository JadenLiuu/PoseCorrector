import multiprocessing as mp
import time
import os
from job.exceptions import *
import utils.util as utils
from threading import Thread
import cv2
import numpy as np
from utils.fake_video_reader import FakeVideoReader
import shutil
SetLock = mp.Lock()



class CameraSet(Thread):
    ValidCam = set()

    def __init__(self, camId, startUnixMicroTs, ai=False):
        Thread.__init__(self, daemon=True)
        self.exit = mp.Event()

        if camId in CameraSet.ValidCam:
            raise CAMERA_PROCESSING
        # self.vc = cv2.VideoCapture()
        CameraSet.ValidCam.add(camId)
        self.ai = ai
        self.camId = camId
        self.startUnixMicroTs = startUnixMicroTs
        print(f'{camId} is set up...')
        self.rtsp = None
        self.fileDir = None
        self.video_path = None
        self.fake_video_reader = None
        self.fake_video_reader = FakeVideoReader("/home/dev/fake_video.mp4")
        self.skip_frame_num = 6

    def output_motion_frame(self, target_dir, target_rtsp):
        out = None
        cap = cv2.VideoCapture(target_rtsp)
        if not cap.isOpened():
            print("[output_motion_frame] can't open")
            exit()
        saved_frames = []
        frame_count = 0
        recent_frames = []
        motion_levels = []
        while not self.exit.is_set():
            ret, frame = cap.read()
            if not ret:
                break
            if out == None:
                print(f"create video {self.video_path}")
                fps = cap.get(cv2.CAP_PROP_FPS)
                image_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out = cv2.VideoWriter(self.video_path, fourcc, fps, image_size)
            else : 
                out.write(frame)
            frame_count += 1

            # 每六幀處理一次，以模擬 5 FPS
            if frame_count % 6 == 0:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # 維護最近五幀
                if len(recent_frames) >= 5:
                    recent_frames.pop(0)
                recent_frames.append(gray)

                # 計算最近五幀的均值
                mean_frame = np.mean(recent_frames, axis=0).astype(np.uint8)
                mean_blurred = cv2.GaussianBlur(mean_frame, (15, 15), 0)

                # 計算當前幀與均值的差異
                frame_delta = cv2.absdiff(mean_blurred, gray)
                thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
                motion_level = np.sum(thresh)

                if len(saved_frames) < 6:
                    saved_frames.append((motion_level, frame))
                else:
                    # 找到最小動態的幀
                    min_motion_frame = min(saved_frames, key=lambda x: x[0])
                    if motion_level > min_motion_frame[0]:
                        # 移除最小動態的幀並添加新幀
                        saved_frames.remove(min_motion_frame)
                        saved_frames.append((motion_level, frame))
        if not out is None:
            out.release()
        cap.release()
        cv2.destroyAllWindows()


        # 保存圖片
        print("===============================")
        for i, frame in enumerate(saved_frames):
            
            save_jpg_path = os.path.join(target_dir, f'shooter_{i}.jpg')
            print(f"{save_jpg_path = }")
            cv2.imwrite(save_jpg_path, frame[1])


    def output_last_frame(self, target_dir, target_rtsp):
        cap = cv2.VideoCapture(target_rtsp)
        if not cap.isOpened():
            print(f"{self.rtsp} can't open")
            exit()

        frame_count = 0
        while not self.exit.is_set():
            ret, frame = cap.read()
            retry = 0
            if not ret:
                print(f"rtsp : {self.rtsp} is broken at frame {frame_count}.......", flush=True)
                while(retry < 10):
                    print(f"rtsp : {self.rtsp} reopened {retry} times .......", flush=True)
                    retry += 1
                    if cap.isOpened():
                        break
                if not cap.isOpened():
                    break
                continue
            time.sleep(1)
            frame_count += 1


        cap.release()
        cv2.destroyAllWindows()
        # 保存圖片
        print("===========[output_last_frame end]==============")
        save_jpg_path = os.path.join(target_dir, f'shooting_paper.jpg')
        print(f"{save_jpg_path = }")
        cv2.imwrite(save_jpg_path, frame)

    def record(self):
        cap = cv2.VideoCapture(self.rtsp)
        if not cap.isOpened():
            print(f"rtsp : {self.rtsp} can't open", flush=True)
            exit()
        timestamp = f"{self.startUnixMicroTs}"
        timestamp = timestamp.split(".")[0]
        fileName=f'{self.camId}-{self.startUnixMicroTs}.mp4'
        self.video_path = os.path.join(self.fileDir, fileName)
        # self.video_path = os.path.join("/home/dev/Documents/PoseCorrector/server", fileName)
        print(f"create video {self.video_path}", flush=True)
        if not self.fake_video_reader is None:
            pass
            fps = self.fake_video_reader.fps
            image_size = self.fake_video_reader.size
        else:
            fps = cap.get(cv2.CAP_PROP_FPS)
            image_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(self.video_path, fourcc, fps, image_size)
        frame_cnt = 0
        while not self.exit.is_set():
            retry = 0
            ret, frame = cap.read()
            frame_cnt += 1
            if not ret:
                print(f"rtsp : {self.rtsp} is broken at frame {frame_cnt}.......", flush=True)
                while(retry < 10):
                    print(f"rtsp : {self.rtsp} reopened {retry} times .......", flush=True)
                    retry += 1
                    if cap.isOpened():
                        break
                if not cap.isOpened():
                    break
                continue
            if not self.fake_video_reader is None:
                frame = self.fake_video_reader.get_frame()
            if not frame_cnt % self.skip_frame_num == 0:
                continue
            out.write(frame)
            # print(frame.mean(), flush=True)
        out.release()
        cap.release()
        # shutil.move(self.video_path, self.fileDir)
        if not self.fake_video_reader is None:
            self.fake_video_reader.close_video()
            


    def set(self, fileDir, rtsp):
        print(CameraSet.ValidCam)
        # fileDir = "."
        fileDir = fileDir.replace("\\", "/").replace("/192.168.101.112/", "").replace("esms", "/mnt/nas")
        self.rtsp = rtsp
        self.fileDir = fileDir
        utils.dir_init(fileDir)
        print(f"{self.rtsp = }")
        
    def run(self):
        print('run...')
        recording = False
        while(self.fileDir is None):
            time.sleep(0.001)
        if self.ai:
            self.record()
        else:
            self.output_last_frame(self.fileDir, self.rtsp)
        # os.system(f"touch {self.video_path}")
        
    def shutdown(self):
        print("Shutdown initiated")
        self.exit.set()

        return self.video_path

    def release(self):
        if self.isRunning:
            with SetLock:
                print(CameraSet.ValidCam)
                CameraSet.ValidCam.remove(self.camId)

    def isRunning(self, camId: str) -> bool:
        running = False
        with SetLock:
            running = camId in CameraSet.ValidCam
        return running
