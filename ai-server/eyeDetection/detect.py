from eyeDetection import *
import numpy as np
import cv2
import time
import os
from eyeDetection.face_utils import resizeImg
from eyeDetection.face_detect import FaceDetector
from eyeDetection.validate.validate import Validation 
# from eyeDetection.eye_detect_dlib_68 import EyeDetector
from eyeDetection.eye_detector_haar_cascades import EyeDetectorHaarCascades
X1Ratio="X1Ratio"
X2Ratio="X2Ratio"
Y1Ratio="Y1Ratio"
Y2Ratio="Y2Ratio"

OPENEYE_CLASS_LABLES = [(0,0, 255),(0, 244, 0)]

eyeClosedModelPath = os.path.join(os.getcwd(), "eyeDetection/validate/modelEye.t7")

class Detector(object):
    FACE_DETECTOR = FaceDetector()
    # EYE_DETECTOR = EyeDetector()
    EYE_DETECTOR = EyeDetectorHaarCascades()
    Ratios = {}
    EYECLOSED_VALIDATOR = Validation(eyeClosedModelPath)
    eyeKeeper = StableKeeper()
    ii = 0
    
    @classmethod
    def setConfig(cls, x1Ratio=0.24, x2Ratio=0.2, y1Ratio=0.2, y2Ratio=0.2):
        print(f"CONFIG SET FOR x1, x2, y1, y2 Ratios:{x1Ratio, x2Ratio, y1Ratio, y2Ratio}")
        Detector.Ratios.setdefault(X1Ratio, x1Ratio)
        Detector.Ratios.setdefault(X2Ratio, x2Ratio)
        Detector.Ratios.setdefault(Y1Ratio, y1Ratio)
        Detector.Ratios.setdefault(Y2Ratio, y2Ratio)

    @classmethod
    def approximateEyeLocation(cls, tl, br) -> DetectBox:
        cx = (tl[0]+br[0])/2.0
        cy = (tl[1]+br[1])/2.0
        w, h = br[0]-tl[0], br[1]-tl[1]
        x1 = int(cx - w * Detector.Ratios[X1Ratio])
        x2 = int(cx + w * Detector.Ratios[X2Ratio])
        y1 = int(cy - h * Detector.Ratios[Y1Ratio])
        y2 = int(cy + h * Detector.Ratios[Y2Ratio])
        return DetectBox(x1, y1, x2, y2)

    @classmethod
    def detect(cls, frame):
        ## face detection
        main_detected_box = cls.FACE_DETECTOR.detect(frame)
        tl, br = main_detected_box.getBox()

        ## eyes detection
        eye = cls.EYE_DETECTOR.detect(frame, tl, br)
        dir = "haar"
        if eye.isEmpty():
            dir = "app"
            eye = cls.approximateEyeLocation(tl, br)
        etl, ebr = eye.getBox()

        ## open / closed eyes classification
        eyeOpenPred = cls.openEyesValidate(frame, etl, ebr)

        ## debug / demo
        detected_img = cv2.rectangle(frame, tl, br, (0,222,0), 2)
        if eyeOpenPred != -1:
            detected_img = cv2.rectangle(detected_img, etl, ebr, OPENEYE_CLASS_LABLES[eyeOpenPred], 2)
        cv2.imwrite(f'tmp/{dir}/Eye#{Detector.ii}.jpg', resizeImg(detected_img, 50))
        Detector.ii+=1
    
    @classmethod
    def openEyesValidate(cls, frame, etl, ebr) -> int:
        try:
            img = frame[etl[1]:ebr[1], etl[0]:ebr[0], :]
            prediction = cls.EYECLOSED_VALIDATOR.predict_one(img)
            # cv2.imwrite(f'tmp/12#{cls.ii}.jpg', img)
            # cls.ii +=1
            return prediction
        except Exception as e:
            print(e)
            return -1

    @classmethod
    def start(cls, path):
        cap = cv2.VideoCapture(path)
        if (cap.isOpened()== False): 
            print(f'Unfound video: {path}')

        while(cap.isOpened()):
            ret, frame = cap.read()
            if ret != True:
                break
            else:
                start = time.time()
                cls.detect(frame)
                end = time.time()
                print(f'FPS: {1/(end-start)}')
                ## cv2.imshow('Frame',detected_img)
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    # Press Q on keyboard to  exit
                    break
        cap.release()
        cv2.destroyAllWindows()