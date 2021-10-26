from eyeDetection import *
from eyeDetection.face_utils import midpoint
import dlib
import cv2
import os
from eyeDetection.eye_detector_haar_cascades import *

cwd = os.getcwd()
USE_CUDA = dlib.DLIB_USE_CUDA
LEFT_KEY = "left"
RIGHT_KEY = "right"

class EyeDetector(object):
    PREDICTOR = None
    MODEL_FILE ='shape_predictor_68_face_landmarks_GTX.dat'
    EYE_LANDMARK_KEYS = {
        LEFT_KEY: [36, 37, 38, 39, 40, 41],
        RIGHT_KEY: [42, 43, 44, 45, 46, 47],
    }
    
    def __init__(self) -> None:
        super().__init__()
        if EyeDetector.PREDICTOR is None:
            EyeDetector.load_model()

    @classmethod
    def load_model(cls):
        PREDICTOR_FILE = os.path.join(cwd, 'eyeDetection', 'detection-model', cls.MODEL_FILE)
        cls.PREDICTOR = dlib.shape_predictor(PREDICTOR_FILE)

    def getEyeBox(self, landmark, key) -> DetectBox:
        eyePts = EyeDetector.EYE_LANDMARK_KEYS[key]
        
        leftPt = landmark.part(eyePts[0])
        rightPt = landmark.part(eyePts[3])
        centerTop_x, centerTop_y = midpoint(landmark.part(eyePts[2]), landmark.part(eyePts[1]))
        centerBottom_x, centerBottom_y = midpoint(landmark.part(eyePts[4]), landmark.part(eyePts[5]))

        minX = min(min(leftPt.x, centerTop_x), centerBottom_x)
        maxX = max(max(rightPt.x, centerTop_x), centerBottom_x)
        minY = min(min(leftPt.y, rightPt.y), centerTop_y)
        maxY = max(max(leftPt.y, rightPt.y), centerBottom_y)
        return DetectBox(minX, minY, maxX, maxY)

    def detect(self, img, tl, br) -> DetectBox:
        faceDlibRect = dlib.rectangle(tl[0], tl[1], br[0], br[1])
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        landmarks = EyeDetector.PREDICTOR(img, faceDlibRect)
        bl = self.getEyeBox(landmarks, LEFT_KEY)
        br = self.getEyeBox(landmarks, RIGHT_KEY)
        return bl if bl.area() > br.area() else br
        
# if __name__ == '__main__':
#     detector = dlib.get_frontal_face_detector()
#     img = cv2.imread('eyeDetection/testImg/test1.png')
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     facesLs = detector(gray, 1)
#     faces = facesLs[0]
#     print(dir(faces))
#     print(type(faces))
 