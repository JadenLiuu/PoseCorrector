from typing import Union
import cv2
import numpy as np
import os
import math
from eyeDetection import *

from . import face_utils as utils

cwd = os.getcwd()

class EyeDetectorHaarCascades(object):
    __path = os.path.join(cwd, 'eyeDetection', 'detection-model', 'eye_haarcascades.xml')
    DETECTOR = cv2.CascadeClassifier(__path)

    DIST_THRESHOLD = 0.1
    SHRINK_RATIO = 0.6
    ii=0
    def __init__(self) -> None:
        super().__init__()
        
    def __eye_pick(self, eyeRects, face_roi_br) -> Union[int, float, float]:
        idx = 0
        pick = 0
        face_center = (face_roi_br[0]/2.0, face_roi_br[1]/2.0)
        faceBoundaryDist = math.sqrt(face_roi_br[1]**2+face_roi_br[0]**2)
        minDst = max(face_roi_br)
        for idx, (ex, ey, ew, eh) in enumerate(eyeRects):
            eye_center = (ex + ew/2.0, ey + eh/2.0)
            dist = utils.dists(eye_center, face_center)
            if dist/faceBoundaryDist < EyeDetectorHaarCascades.DIST_THRESHOLD:
                return idx, dist, faceBoundaryDist
            if dist < minDst:
                minDst = dist
                pick = idx
        return pick, minDst, faceBoundaryDist

    def _draw(self, img, pick:int, box: np.ndarray):
        for id, box in enumerate(box):
            x,y, w,h=box
            tl, br=(x,y),(x+w,y+h)
            if id == pick:
                detected_img = cv2.rectangle(img, tl, br, (30,199,2), 2)
            else:
                detected_img = cv2.rectangle(img, tl, br, (0,30,212), 2)
        cv2.imwrite(f'tmp/eye#{EyeDetectorHaarCascades.ii}.jpg', utils.resizeImg(detected_img, 50))
        EyeDetectorHaarCascades.ii+=1


    def postProcessing(self, eyeRects, face_roi_br, tlx, tly) -> DetectBox:
        if len(eyeRects) == 0:
            return DetectBox(0,0,0,0)

        pick, minDist, faceBoundaryDist = self.__eye_pick(eyeRects, face_roi_br)
        if minDist/faceBoundaryDist > EyeDetectorHaarCascades.DIST_THRESHOLD:
            # print(minDist/faceBoundaryDist)
            # self._draw(faceROI, pick, eyeRects)
            return DetectBox(0,0,0,0)
        
        ex, ey, ew, eh = eyeRects[pick]
        d = DetectBox(ex,ey,ex+ew,ey+eh)
        d.shrinkBack(EyeDetectorHaarCascades.SHRINK_RATIO)
        eTl, eBr = d.getBox()
        return DetectBox(eTl[0]+tlx, eTl[1]+tly, eBr[0]+tlx, eBr[1]+tly)


    def detect(self, img, tl, br) -> DetectBox:
        tlx, tly = tl
        brx, bry = br
        faceROI = img[tly:bry, tlx:brx]

        try:
            faceROI = utils.resizeImg(faceROI, EyeDetectorHaarCascades.SHRINK_RATIO)
        except Exception as e:
            print(f"Exception: {e}, img shape: {faceROI.shape}")
            return DetectBox(0,0,0,0)

        try:
            eyeRects = EyeDetectorHaarCascades.DETECTOR.detectMultiScale(
                faceROI, scaleFactor=1.025, minNeighbors=5, minSize=(10, 10), flags=cv2.CASCADE_SCALE_IMAGE)
        except Exception as e:
            print(f"Exception: {e}, harr detect failed")
            return DetectBox(0,0,0,0)

        return self.postProcessing(eyeRects, faceROI.shape[:2], tlx, tly)
        