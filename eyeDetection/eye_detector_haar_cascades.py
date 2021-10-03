import cv2
import os
from eyeDetection import *

from . import face_utils as utils

cwd = os.getcwd()

class EyeDetectorHaarCascades(object):
    __path = os.path.join(cwd, 'eyeDetection', 'detection-model', 'eye_haarcascades.xml')
    DETECTOR = cv2.CascadeClassifier(__path)
    def __init__(self) -> None:
        super().__init__()
        
    def __eye_pick(self, eyeRects, face_roi_br) -> int:
        idx = 0
        if len(eyeRects) == 1:
            return idx
        face_center = (face_roi_br[0]/2.0, face_roi_br[1]/2.0)
        minDst = max(face_roi_br)
        for idx, (ex, ey, ew, eh) in enumerate(eyeRects):
            eye_center = (ex + ew/2.0, ey + eh/2.0)
            dist = utils.dists(eye_center, face_center)
            if dist < minDst:
                minDst = dist
                pick = idx
        return idx
        
    def detect(self, img, tl, br) -> DetectBox:
        tlx, tly = tl
        brx, bry = br
        faceROI = img[tly:bry, tlx:brx]
        
        eyeRects = EyeDetectorHaarCascades.DETECTOR.detectMultiScale(
			faceROI, scaleFactor=1.12, minNeighbors=12, minSize=(30, 20), flags=cv2.CASCADE_SCALE_IMAGE)
        
        if len(eyeRects) == 0:
            return DetectBox(0,0,0,0)
        pick = self.__eye_pick(eyeRects, faceROI.shape[:2][::-1])
        ex, ey, ew, eh = eyeRects[pick]
        return DetectBox(ex+tlx, ey+tly, ex+ew+tlx, ey+eh+tly)