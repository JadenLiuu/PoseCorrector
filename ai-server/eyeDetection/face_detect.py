from eyeDetection import *
import numpy as np
import cv2
import os

# cwd = os.getcwd()
cwd = "/home/dev/Documents/PoseCorrector/ai-server"

class FaceDetector(object):
    MODEL_FILE = os.path.join(cwd, 'eyeDetection', 'detection-model', 'opencv_face_detector_uint8.pb')
    NET_FILE = os.path.join(cwd, 'eyeDetection', 'detection-model', 'opencv_face_detection.pbtxt')
    NET = cv2.dnn.readNetFromTensorflow(MODEL_FILE, NET_FILE)
    
    def __init__(self) -> None:
        super().__init__()
        self.sizeKeeper = StableKeeper()
        
    def __face_pick(self, detections) -> int:
        pick = -1
        conf_ls = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            conf_ls.append(confidence)
        pick = np.argsort(np.array(conf_ls))[-1]
        return pick

    def detect(self, img) -> DetectBox:
        h, w = img.shape[:2]
        
        blob = cv2.dnn.blobFromImage(img, 1.0, (300, 300), [104, 117, 123], False, False)
        FaceDetector.NET.setInput(blob)
        detections = FaceDetector.NET.forward()
        
        pick = self.__face_pick(detections)
        x1 = int(detections[0, 0, pick, 3] * w)
        y1 = int(detections[0, 0, pick, 4] * h)
        x2 = int(detections[0, 0, pick, 5] * w)
        y2 = int(detections[0, 0, pick, 6] * h)
        box = DetectBox(x1, y1, x2, y2)
        box = self.sizeKeeper.keep(box)
        return box

