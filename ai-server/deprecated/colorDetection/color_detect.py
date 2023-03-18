import cv2
import numpy as np
import argparse


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument("-p", "--path", type=str, help='image path', required=True)
    opt = args.parse_args()

    imgName = opt.path.split("test/roi/")[-1]

    frame = cv2.imread(opt.path)
    # frame = cv2.resize(frame, (224, 224)) # w, h, c = 224, 224, 3

    low_green = np.array([0, 100, 100])
    high_green = np.array([255, 255, 255])

    imgHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(imgHSV, low_green, high_green)
    res = cv2.bitwise_and(frame, frame, mask=mask)
    contrastRes = cv2.addWeighted(res, 1.5, res, 0, 0)
    
    redScore = contrastRes[:,:,2].mean(1).mean(0)
    print(f"green removal redScore: {redScore}")
    cv2.imwrite(f"./red{imgName}", contrastRes[:,:,2])

    yCbCr = cv2.cvtColor(contrastRes, cv2.COLOR_BGR2YCrCb)
    cv2.imwrite(f"./cr{imgName}", yCbCr[:,:,1])

    redScore = yCbCr[:,:,1].mean(1).mean(0)
    print(f"yCbCr redScore: {redScore}")