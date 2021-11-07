from eyeDetection import *
import numpy as np
import dlib
import cv2
import time
import os
from eyeDetection.face_detect import FaceDetector
from eyeDetection.eye_detect_dlib_68 import EyeDetector
# from eyeDetection.eye_detector_haar_cascades import EyeDetectorHaarCascades

class Detector(object):
    FACE_DETECTOR = FaceDetector()
    EYE_DETECTOR = EyeDetector()
    # EYE_DETECTOR = EyeDetectorHaarCascades()
    def __init__(self, path) -> None:
        super().__init__()
        
    @classmethod
    def start(cls, path):
        cap = cv2.VideoCapture(path)
        if (cap.isOpened()== False): 
            print(f'Unfound video: {path}')

        ii=0
        while(cap.isOpened()):
            ret, frame = cap.read()
            if ret == True:
                start = time.time()
                main_detected_box = cls.FACE_DETECTOR.detect(frame)
                tl, br = main_detected_box.getBox()

                eye = cls.EYE_DETECTOR.detect(frame, tl, br)
                etl, ebr = eye.getBox()
                end = time.time()

                detected_img = cv2.rectangle(frame, tl, br, (0,222,0), 2)
                print(f'FPS: {1/(end-start)}')
                detected_img = cv2.rectangle(detected_img, etl, ebr, (225,100,10), 2)
                
                ## cv2.imshow('Frame',detected_img)
                cv2.imwrite(f'tmp/{ii}.jpg', detected_img)
                ii = ii + 1
                if cv2.waitKey(25) & 0xFF == ord('q'): # Press Q on keyboard to  exit
                    break
            else: 
                break

        cap.release()
        cv2.destroyAllWindows()