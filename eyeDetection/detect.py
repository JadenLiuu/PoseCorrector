from numpy.lib.function_base import average
from . import face_utils as utils
# from imutils import face_utils
import numpy as np
import dlib
import cv2
import os
from collections import namedtuple

cwd = os.getcwd()

_BoxLoc = namedtuple("BoxLoc", ['x1', 'y1', 'x2', 'y2'])

class DetectBox(object):
    def __init__(self, x1, y1, x2, y2) -> None:
        super().__init__()
        self._box_locations = _BoxLoc(x1, y1, x2, y2)

    def area(self) -> int:
        ydiff = self._box_locations.y2 - self._box_locations.y1
        xdiff = self._box_locations.x2 - self._box_locations.x1
        return xdiff * ydiff
    
    def getBox(self):
        x1, y1 = self._box_locations.x1, self._box_locations.y1
        x2, y2 = self._box_locations.x2, self._box_locations.y2
        return (x1, y1), (x2, y2)
    
    
class StableKeeper(object):
    """
        To maintain the size of detected faces, keep it from large variation
    """
    THRESH = 0.8
    N_KEEP = 3
    def __init__(self) -> None:
        super().__init__()
        self.ls = []
        
    def keep(self, detect_box: DetectBox) -> DetectBox:
        if len(self.ls) < StableKeeper.N_KEEP:
            self.ls.append(detect_box)
        else:
            avg = average([i.area() for i in self.ls])
            area = detect_box.area()
            variation = abs(area - avg) / max(area, avg)
            if variation > StableKeeper.THRESH: ## unstable
                return self.ls[-1]
            else:
                self.ls.pop(0)
                self.ls.append(detect_box)
        return detect_box         


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
    PREDICTOR_FILE = os.path.join(cwd, 'eyeDetection', 'detection-model', 'shape_predictor_68_face_landmarks_GTX.dat')
    PREDICTOR = dlib.shape_predictor(PREDICTOR_FILE)
    
    def __init__(self) -> None:
        super().__init__()
        

class Detector(object):
    FACE_DETECTOR = FaceDetector()
    def __init__(self, path) -> None:
        super().__init__()
    
    @classmethod
    def start(cls, path):
        cap = cv2.VideoCapture(path)
        if (cap.isOpened()== False): 
            print(f'Unfound video: {path}')

        while(cap.isOpened()):
            ret, frame = cap.read()
            if ret == True:
                main_detected_box = cls.FACE_DETECTOR.detect(frame)
                tl, br = main_detected_box.getBox()
                detected_img = cv2.rectangle(frame, tl, br, (0,222,0), 2)
                
                cv2.imshow('Frame',detected_img)
                if cv2.waitKey(25) & 0xFF == ord('q'): # Press Q on keyboard to  exit
                    break
            else: 
                break

        cap.release()
        cv2.destroyAllWindows()