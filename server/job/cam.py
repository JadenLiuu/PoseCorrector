import multiprocessing as mp
import time
import os
from job.exceptions import *
import utils.util as utils
from threading import Thread
import cv2
import numpy as np
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

    def output_motion_frame(self, target_dir, target_rtsp):
        cap = cv2.VideoCapture(target_rtsp)
        if not cap.isOpened():
            print("can't open")
            exit()

        saved_frames = []
        frame_count = 0
        recent_frames = []
        motion_levels = []
        while not self.exit.is_set():
            ret, frame = cap.read()
            if not ret:
                break

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
            print("can't open")
            exit()

        saved_frames = []
        frame_count = 0
        while not self.exit.is_set():
            ret, frame = cap.read()
            if not ret:
                break
            frame_count += 1

            # 每六幀處理一次，以模擬 5 FPS
            if frame_count % 6 == 0:
                saved_frames = [(0, frame)]

        cap.release()
        cv2.destroyAllWindows()
        # 保存圖片
        print("===============================")
        for i, frame in enumerate(saved_frames):
            
            save_jpg_path = os.path.join(target_dir, f'shooting_paper_{i}.jpg')
            print(f"{save_jpg_path = }")
            cv2.imwrite(save_jpg_path, frame[1])

    def set(self, fileDir, rtsp):
        print(CameraSet.ValidCam)
        utils.dir_init(fileDir)
        fileName=f'{self.camId}-{self.startUnixMicroTs}.mp4'
        # fileDir = "."
        self.filePath = os.path.join(fileDir, fileName)
        fileDir = fileDir.replace("\\", "/").replace("/192.168.101.112/", "").replace("esms", "/mnt/nas")
        self.fileDir = fileDir
        if not os.path.exists(fileDir):
            os.makedirs(fileDir)
        self.rtsp = rtsp
        
    def run(self):
        print('run...')
        recording = False
        while(self.fileDir is None):
            time.sleep(0.1)
        if self.ai:
            self.output_motion_frame(self.fileDir, self.rtsp)
        else:
            self.output_last_frame(self.fileDir, self.rtsp)
        # os.system(f"touch {self.filePath}")
        
    def shutdown(self):
        print("Shutdown initiated")
        self.exit.set()

        return self.filePath

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
