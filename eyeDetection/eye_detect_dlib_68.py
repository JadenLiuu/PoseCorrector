import numpy as np
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
NOSE_KEY = "nose"

class EyeDetector(object):
    ii = 0
    PREDICTOR = None
    MODEL_FILE ='shape_predictor_68_face_landmarks_GTX.dat'
    EYE_LANDMARK_KEYS = {
        # LEFT_KEY: [36, 37, 38, 39, 40, 41],
        LEFT_KEY: [38,39,41],
        RIGHT_KEY: range(43, 48),
        NOSE_KEY: range(30, 34),
        # NOSE_KEY: range(28, 36),
    }
    
    def __init__(self) -> None:
        super().__init__()
        if EyeDetector.PREDICTOR is None:
            EyeDetector.load_model()

    @classmethod
    def load_model(cls):
        PREDICTOR_FILE = os.path.join(cwd, 'eyeDetection', 'detection-model', cls.MODEL_FILE)
        cls.PREDICTOR = dlib.shape_predictor(PREDICTOR_FILE)

    def getEyeBox(self, landmark, tl, br) -> DetectBox:
        ptx, pty = [], []
        for key in [LEFT_KEY, NOSE_KEY]:
            for kp in EyeDetector.EYE_LANDMARK_KEYS[key]:
                pt = landmark.part(kp)
                ptx.append(pt.x)
                pty.append(pt.y)
        d = DetectBox(np.min(ptx), np.min(pty), np.max(ptx), np.max(pty))
        d.zoomIn(1.5, 1.8)
        return d

    def getEyeBoxByEyes(self, landmark, key) -> DetectBox:
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

    def drawLandMarks(self, landmarks, frame):
        for i in range(18, 48):
            center = landmarks.part(i)
            frame = cv2.circle(frame, (center.x, center.y), 2, (0, 255, 255), -1)
        cv2.imwrite(f'tmp/{EyeDetector.ii}.jpg', frame)
        EyeDetector.ii+=1

    def detect(self, img, tl, br) -> DetectBox:
        faceDlibRect = dlib.rectangle(tl[0], tl[1], br[0], br[1])
        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        landmarks = EyeDetector.PREDICTOR(imgGray, faceDlibRect)
        eyeBox = self.getEyeBox(landmarks, tl, br)
        # self.drawLandMarks(landmarks, img)
        return eyeBox
        
# if __name__ == '__main__':
#     detector = dlib.get_frontal_face_detector()
#     img = cv2.imread('eyeDetection/testImg/test1.png')
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     facesLs = detector(gray, 1)
#     faces = facesLs[0]
#     print(dir(faces))
#     print(type(faces))
 