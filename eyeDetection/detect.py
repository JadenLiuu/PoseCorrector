from eyeDetection import *
import numpy as np
import dlib
import cv2
import time
import os
from eyeDetection.eye_detector_haar_cascades import *

cwd = os.getcwd()

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
    
class EyeDetector(object):
    # PREDICTOR_FILE = os.path.join(cwd, 'eyeDetection', 'detection-model', 'shape_predictor_68_face_landmarks_GTX.dat')
    # PREDICTOR = dlib.shape_predictor(PREDICTOR_FILE)
    def __init__(self) -> None:
        super().__init__()


class Detector(object):
    FACE_DETECTOR = FaceDetector()
    # EYE_DETECTOR = EyeDetector()
    def __init__(self, path) -> None:
        super().__init__()
        
    @classmethod
    def start(cls, path):
        # EYE_DETECTOR = EyeDetectorHaarCascades()
        cap = cv2.VideoCapture(path)
        if (cap.isOpened()== False): 
            print(f'Unfound video: {path}')

        # ii=0
        while(cap.isOpened()):
            ret, frame = cap.read()
            if ret == True:
                start = time.time()
                main_detected_box = cls.FACE_DETECTOR.detect(frame)
                tl, br = main_detected_box.getBox()
                end = time.time()
                # eye = EYE_DETECTOR.detect(frame, tl, br)
                # etl, ebr = eye.getBox()

                detected_img = cv2.rectangle(frame, tl, br, (0,222,0), 2)
                print(f'FPS: {1/(end-start)}')
                # detected_img = cv2.rectangle(detected_img, etl, ebr, (225,100,10), 2)
                
                ## cv2.imshow('Frame',detected_img)
                cv2.imwrite(f'res3/{ii}.jpg', detected_img)
                ii = ii + 1
                if cv2.waitKey(25) & 0xFF == ord('q'): # Press Q on keyboard to  exit
                    break
            else: 
                break

        cap.release()
        cv2.destroyAllWindows()