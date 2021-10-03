from eyeDetection.detect import Detector
import argparse


args = argparse.ArgumentParser()
args.add_argument('-p', '--path', type=str, default='./tests/videos/test4.mp4')
opt = args.parse_args()

if __name__ == '__main__':
    Detector.start(opt.path)