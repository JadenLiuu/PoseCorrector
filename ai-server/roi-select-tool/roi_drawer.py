import tkinter as tk
import cv2
import os
import numpy as np
import json
import copy

COLOR_OF_BOX = (0,244, 10)
COLOR_OF_UNUSED_BOX = (77, 33, 33)
ACCELERATE_TIME = 90
RESIZE_RATIO = 0.5

"""
# print "Events in CV: ", [event for event in dir(cv2) if 'EVENT' in event]
Events in CV:  ['EVENT_FLAG_ALTKEY', 'EVENT_FLAG_CTRLKEY', 'EVENT_FLAG_LBUTTON', 
'EVENT_FLAG_MBUTTON', 'EVENT_FLAG_RBUTTON', 'EVENT_FLAG_SHIFTKEY', 
'EVENT_LBUTTONDBLCLK', 'EVENT_LBUTTONDOWN', 'EVENT_LBUTTONUP', 
'EVENT_MBUTTONDBLCLK', 'EVENT_MBUTTONDOWN', 'EVENT_MBUTTONUP', 
'EVENT_MOUSEHWHEEL', 'EVENT_MOUSEMOVE', 'EVENT_MOUSEWHEEL', 
'EVENT_RBUTTONDBLCLK', 'EVENT_RBUTTONDOWN', 'EVENT_RBUTTONUP']
"""

def get_color_score(frame):
    low_green = np.array([0, 100, 100])
    high_green = np.array([255, 255, 255])
    imgHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(imgHSV, low_green, high_green)
    res = cv2.bitwise_and(frame, frame, mask=mask)
    contrastRes = cv2.addWeighted(res, 1.5, res, 0, 0)
    s1 = contrastRes[:,:,2].mean(1).mean(0)
    yCbCr = cv2.cvtColor(contrastRes, cv2.COLOR_BGR2YCrCb)
    s2 = yCbCr[:,:,1].mean(1).mean(0)
    return s1, s2


class Labeler(object):
    """docstring for Labeler"""
    def __init__(self, videoName):
        super(Labeler, self).__init__()
        self.videoName = videoName


class IrregularLabeler(Labeler):
    """docstring for IrregularLabeler"""
    def __init__(self, videoName, jsonNameRoi):
        super(IrregularLabeler, self).__init__(videoName)
        self.leaveTheLoop = False
        self.refPt = list()
        self.savedROI = list()
        self.roiDict = {
            "rois": list(),
            "roiRatio": list(),
            "color": list(),
        }
        self.jsonNameRoi = jsonNameRoi
        self.originalImgShape = tuple()
        self.reset()

    def reset(self):
        self.refPt[:] = []

    def callback(self, event, x, y, flags, param):
        # if the left mouse button was clicked, record the starting (x, y) coordinates and indicate	 
        # check to see if the left mouse button was released.
        if len(self.refPt) == 0 and event == cv2.EVENT_LBUTTONDOWN:
            self.refPt.append((x, y))

        if event == cv2.EVENT_LBUTTONUP:
            self.refPt.append((x, y))

        # Leave the labeling process if right mouse button was clicked.
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.leaveTheLoop = True

    def draw_regular(self, mat, ptList, recurssive=False, color=COLOR_OF_BOX):
        _round = len(ptList)-1 if not recurssive else len(ptList)
        for ptInd in range(_round):
            cv2.rectangle(mat, ptList[ptInd], ptList[(ptInd+1)%2], color, 2)

        cv2.imshow("labeling", mat)
        k = cv2.waitKey(1) & 0xFF

    def draw_saved_rois(self, mat):
        for idx, tmpROI in enumerate(self.savedROI):
            color = COLOR_OF_BOX
            if len(self.savedROI) > 1 and idx < len(self.savedROI)-1:
                color = COLOR_OF_UNUSED_BOX
            self.draw_regular(mat, tmpROI, recurssive=True, color=color)

    def get_roi_ratio(self, shapeResizedMat):
        roiRatio = list()
        for pt in self.refPt:
            roiRatio.append((pt[0]/float(shapeResizedMat[1]), pt[1]/float(shapeResizedMat[0])))
        return roiRatio

    def get_original_roi(self, roiRatio):
        originalROI = list()
        for ratioPt in roiRatio:
            originalROI.append((int(ratioPt[0]*self.originalImgShape[1]), int(ratioPt[1]*self.originalImgShape[0])))
        return originalROI
        
    def save_roiInfos(self, originalROI, roiRatio):
        self.roiDict["rois"].append(originalROI)
        self.roiDict["roiRatio"].append(roiRatio)

    def save_rois_to_json(self):
        roi_dict = {
            "rois": self.roiDict["rois"][-1],
            "roiRatio": self.roiDict["roiRatio"][-1],
        }
        
        with open(self.jsonNameRoi, "w") as roiJson:
            roiJson.write(json.dumps(roi_dict))

    def start_play(self):
        cv2.namedWindow("labeling")
        cv2.setMouseCallback("labeling", self.callback)
            
        try:
            vc, fn = cv2.VideoCapture(self.videoName), 0
            retSucc, mat = vc.read()
            self.originalImgShape = mat.shape

            while retSucc and not self.leaveTheLoop:
                mat = cv2.resize(mat, (int(mat.shape[1]*RESIZE_RATIO), int(mat.shape[0]*RESIZE_RATIO)))
                tmpMat = copy.deepcopy(mat)
                self.draw_saved_rois(mat)
                cv2.imshow("labeling", mat)

                while len(self.refPt) < 2:
                    k = cv2.waitKey(5) & 0xFF
                    if k == ord("n") or self.leaveTheLoop or k == ord("q"):
                        break
                    self.draw_regular(mat, self.refPt, recurssive=False)

                if len(self.refPt)==2:
                    self.draw_regular(mat, self.refPt, recurssive=True)
                    self.savedROI.append(copy.deepcopy(self.refPt))
                    roiRatio = self.get_roi_ratio(mat.shape)
                    originalROI = self.get_original_roi(roiRatio)
                    self.save_roiInfos(originalROI, roiRatio)

                self.reset()
                retSucc, mat = vc.read()

        except Exception as e:
            print(f'[Exception] start_play @ IrregularLabeler:{e}')
        finally:
            vc.release()

        self.save_rois_to_json()
        cv2.destroyAllWindows()

def start_labeling():
    videoName = video_entry.get()
    jsonNameRoi = roi_entry.get()
    labelAgent = IrregularLabeler(videoName, jsonNameRoi)
    if os.path.exists(videoName):
        labelAgent.start_play()
    else:
        raise Exception(f"unknown video {videoName}")
        
def quit():
    window.destroy()

if __name__ == '__main__':
    window = tk.Tk()
    window.title('ROI Selector')
    window.geometry('640x400')
    window.configure(background='white')

    header_label = tk.Label(window, text='[Demo] Shoulder ROI Selector', width="40", height="5", bg='green', fg='white')
    header_label.pack(pady=50,ipady=10)

    video_frame = tk.Frame(window)
    video_frame.pack(side=tk.TOP)
    video_label = tk.Label(video_frame, text='rtsp or mp4', bg='white', fg='black').pack(side=tk.LEFT)
    video_entry = tk.Entry(video_frame)
    video_entry.pack(side=tk.LEFT)
    video_frame.pack()

    roi_frame = tk.Frame(window)
    roi_frame.pack(side=tk.TOP)
    roi_jsonName = tk.Label(roi_frame, text='roi results (JSON)', height="2", bg='white', fg='black').pack(side=tk.LEFT)
    roi_entry = tk.Entry(roi_frame)
    roi_entry.insert(tk.END, 'demo.json')
    roi_entry.pack(side=tk.LEFT)
    roi_frame.pack()

    tk.Button(window, text='Start Selection!', command=start_labeling).pack()
    tk.Button(window, text="Quit", command=quit).pack(side=tk.BOTTOM, pady=20, ipady=10)

    window.mainloop()