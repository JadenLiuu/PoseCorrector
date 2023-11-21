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
import datetime
SetLock = mp.Lock()

class Recorder(mp.Process):
    def __init__(self, start_time, rtsp, fileDir, startUnixMicroTs, skip_frame_num, fake_video_reader=None):
        super().__init__()
        self.start_time = start_time
        self.rtsp = rtsp
        self.fileDir = fileDir
        self.startUnixMicroTs = startUnixMicroTs
        self.skip_frame_num = skip_frame_num
        self.fake_video_reader = fake_video_reader
        self.exit = mp.Event()

    def run(self):
        cap = cv2.VideoCapture(self.rtsp)
        retry = 0
        while(retry < 3):
            if not cap.isOpened():
                cap.release()
                cap = cv2.VideoCapture(self.rtsp)
                retry += 1
                continue
            break
        
        if retry >= 3:
            print(f"rtsp : {self.rtsp} can't open", flush=True)
            return
        
        # self.start_time = int(self.startUnixMicroTs)
        start_time = time.time()
        fileName = f'{self.start_time}.mp4'
        vid_log_name = f'{self.start_time}.log'
        video_path = os.path.join(self.fileDir, fileName)
        vid_log_path = os.path.join(self.fileDir, vid_log_name)
        fps = cap.get(cv2.CAP_PROP_FPS) if not self.fake_video_reader else self.fake_video_reader.fps
        image_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))) if not self.fake_video_reader else self.fake_video_reader.size
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(video_path, fourcc, fps, image_size)
        print(f"created video {video_path}", flush=True)

        frame_cnt = 0
        frame_time_list = []
        start_record_time = time.time()
        while not self.exit.is_set():
            if time.time() - start_record_time >= 180:
                self.shutdown()
                continue
            ret, frame = cap.read()
            retry = 0
            if not ret:
                print(f"rtsp : {self.rtsp} is broken at frame {frame_cnt}.......", flush=True)
                while(retry < 10):
                    cap.release()
                    cap = cv2.VideoCapture(self.rtsp)

                    print(f"rtsp : {self.rtsp} reopened {retry} times .......", flush=True)
                    retry += 1
                    if cap.isOpened():
                        break
                
            if retry >= 10:
                print(f"rtsp : {self.rtsp} is broken and retry more than {retry} times", flush=True)
                break
            
            if self.fake_video_reader:
                frame = self.fake_video_reader.get_frame()
            
            if frame_cnt % self.skip_frame_num == 0 and (not frame is None):
                frame_time = int(time.time() * 1e6)
                frame = self.write_time_stamp(frame)
                out.write(frame)
                frame_time_list.append(frame_time)

            frame_cnt += 1

        out.release()
        cap.release()
        if self.fake_video_reader:
            self.fake_video_reader.close_video()

        with open(vid_log_path, "w+") as f:
            f.write("\n".join(str(i) for i in frame_time_list))
        print(f"Recording stopped and video saved to {video_path}")

    def shutdown(self):
        self.exit.set()

    def write_time_stamp(self, frame):
        now = datetime.datetime.now()
        time_str = now.strftime("%Y%m%d %H:%M:%S.%f")[:-3]
        height, width = frame.shape[:2]
        position = (10, height - 10)
        cv2.putText(frame, time_str, position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        return frame

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
        self.start_time = None
        self.fileDir = None
        self.video_path = None
        self.vid_log_path = None
        self.fake_video_reader = None
        # self.fake_video_reader = FakeVideoReader("/home/dev/fake_video.mp4")
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
            print(f"ERROR {self.rtsp} can't open")
            return

        frame_count = 0
        retry = 0
        while not self.exit.is_set():
            ret, frame = cap.read()
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
            # time.sleep(1)
            frame_count += 1

        ret, frame = cap.read()
        cap.release()
        cv2.destroyAllWindows()
        # 保存圖片
        print("===========[output_last_frame end]==============")
        save_jpg_path = os.path.join(target_dir, f'shooting_paper.jpg')
        print(f"{save_jpg_path = }")
        cv2.imwrite(save_jpg_path, frame)


    def set(self, fileDir, rtsp):
        print(CameraSet.ValidCam)
        # fileDir = "."
        fileDir = fileDir.replace("\\", "/").replace("/192.168.101.112/", "").replace("esms", "/mnt/nas")
        self.rtsp = rtsp
        self.fileDir = fileDir
        utils.dir_init(fileDir)
        print(f"init dir : {fileDir}")
        print(f"{self.rtsp = }")
        
    def run(self):
        print('run...')
        recording = False
        while self.fileDir is None:
            time.sleep(0.001)
        if self.ai:
            self.start_time = int(self.startUnixMicroTs)
            fileName = f'{self.start_time}.mp4'
            self.video_path = os.path.join(self.fileDir, fileName)
            self.recorder = Recorder(self.start_time, self.rtsp, self.fileDir, self.startUnixMicroTs, self.skip_frame_num, self.fake_video_reader)
            self.recorder.start()


            
    def shutdown(self):
        print("Shutdown initiated")
        if hasattr(self, 'recorder') and self.recorder.is_alive():
            self.recorder.shutdown()
            self.recorder.join()
        self.exit.set()
        if not self.ai:
            self.output_last_frame(self.fileDir, self.rtsp)
        return self.video_path, self.start_time

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
