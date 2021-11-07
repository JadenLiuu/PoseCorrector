from eyeDetection.detect import Detector
import argparse


args = argparse.ArgumentParser()
args.add_argument('-p', '--path', type=str, default='./tests/videos/test4.mp4')
args.add_argument('--eye', type=float, nargs='+', default=[0.24, 0.2, 0.2, 0.2])
opt = args.parse_args()

if __name__ == '__main__':
    if len(opt.eye) > 4:
        print("opt.eye must be len <= 4")
    else:
        Detector.setConfig(*opt.eye)
        Detector.start(opt.path)