import cv2
import numpy as np
import argparse
import json
import os

low_green = np.array([0, 100, 100])
high_green = np.array([255, 255, 255])

COLOR_RED = (0, 0, 244)
COLOR_GREEN = (12, 200, 0)

def detect_color(image):
    imgHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(imgHSV, low_green, high_green)
    res = cv2.bitwise_and(frame, frame, mask=mask)
    contrastRes = cv2.addWeighted(res, 1.5, res, 0, 0)
    redScore = contrastRes[:,:,2].mean(1).mean(0)
    return redScore

def detect_motion(image, min_diff_pixel=20, reset=False):
    if not hasattr(detect_motion, "prev_image"):
        setattr(detect_motion, "prev_image", image)
        setattr(detect_motion, "threshold", 0.21)
        setattr(detect_motion, "totalPixels", image.shape[0] * image.shape[1])
        return 0, False, None
    if reset:
        setattr(detect_motion, "prev_image", image)
    if hasattr(detect_motion, "FROZE") and detect_motion.FROZE > 0:
        detect_motion.FROZE-=1
        return 0, True, None
    
    diff = cv2.absdiff(detect_motion.prev_image, image)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    _, mask_diff = cv2.threshold(gray, min_diff_pixel, 255, cv2.THRESH_BINARY)
    # cv2.imshow('shoulder',  mask_diff)
    nonzeroPixelsDiff = cv2.countNonZero(mask_diff)
    movingPixelRatio = nonzeroPixelsDiff / detect_motion.totalPixels
    isMoving = movingPixelRatio > detect_motion.threshold
    
    # print(movingPixelRatio)

    # the action is moving too severly, reset the previous image
    if movingPixelRatio > 0.28:
        setattr(detect_motion, "prev_image", image)
        setattr(detect_motion, "FROZE", 0)
    elif isMoving:
        setattr(detect_motion, "FROZE", 5)
    return movingPixelRatio ,isMoving, mask_diff


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument("-p", "--video_path", type=str, help='mp4 path', required=True)
    args.add_argument("-r", "--roi_path", type=str, help='path of roi results', required=True)
    args.add_argument('-o', '--output_path', type=str, default='./output.mp4')
    args.add_argument('-f', '--frames', type=int, nargs='+',default=[1,2,3,4,5,6], help='list of frames')
    args.add_argument('-d', '--output_dir', type=str, required=True, help='directory to save output images')

    opt = args.parse_args()
    if not os.path.exists(opt.output_dir):
        os.makedirs(opt.output_dir)


    roi_tl, roi_br = None, None
    with open(opt.roi_path) as f:
        data = json.load(f)
        rois = data.get("rois")
        roi_tl, roi_br = rois[0], rois[1]

    x1, y1 = roi_tl
    x2, y2 = roi_br
    print(f"[Shrug] reading video : {opt.video_path}")
    print(f"[Shrug] frame numbers : {opt.frames}")
    cap = cv2.VideoCapture(opt.video_path)
    if not cap.isOpened():
        print("Error opening video file")

    fps = cap.get(cv2.CAP_PROP_FPS)

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    # out = cv2.VideoWriter(opt.output_path, fourcc, fps, (frame_width, frame_height))

    prev_mask_diff = None
    frame_counter = 0  
    while cap.isOpened():
        ret, frame = cap.read()
        frame_counter += 1  

        if ret:
            
            # core things we care start
            shoulderFrame = frame[y1:y2, x1:x2]
            mo, is_moving, mask_diff = detect_motion(shoulderFrame)
            # core things we care end
            
            if is_moving:
                cv2.rectangle(frame, tuple(roi_tl), tuple(roi_br), COLOR_RED, 2)
                cv2.putText(frame, 'Failed! The shoulder was moving!', (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, COLOR_RED, 2)
            else:
                cv2.rectangle(frame, tuple(roi_tl), tuple(roi_br), COLOR_GREEN, 2)
                cv2.putText(frame, 'Pass! The shooter did it well!', (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, COLOR_GREEN, 2)

            # cv2.putText(frame, 'mo: {:02f}'.format(mo), (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, COLOR_GREEN, 2)
            # cv2.imshow('frame', frame)

            s_height, s_width, _ = shoulderFrame.shape
            dst_x2, dst_y2 = frame.shape[1]-10, frame.shape[0]-10
            dst_x1, dst_y1 = frame.shape[1]-10-s_width, frame.shape[0]-10-s_height
            
            if mask_diff is not None:
                prev_mask_diff = cv2.cvtColor(mask_diff, cv2.COLOR_GRAY2BGR)
                
            if prev_mask_diff is not None:    
                frame[dst_y1:dst_y2, dst_x1:dst_x2, :] = prev_mask_diff
            if frame_counter in opt.frames:
                output_filename = f"shooter_shrug_{opt.frames.index(frame_counter)+1}.jpg"
                print(f"save img : {output_filename}, {mo = }")
                cv2.imwrite(os.path.join(opt.output_dir, output_filename), frame)
                # out.write(frame)

            # if cv2.waitKey(25) & 0xFF == ord('q'):
            #     break
        else:
            break

    cap.release()
    # out.release()
    # cv2.destroyAllWindows()
    