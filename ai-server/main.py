from eyeDetection.detect import Detector
import argparse


args = argparse.ArgumentParser()
args.add_argument('-p', '--path', type=str, default='/home/dev/fake_video.mp4')
args.add_argument('--eye', type=float, nargs='+', default=[0.18, 0.16, 0.1, 0.1]) # x1, x2, y1, y2
args.add_argument('-f', '--frames', type=int, nargs='+',default=[1,2,3,4,5,6], help='list of frames')
args.add_argument('-d', '--output_dir', type=str, required=True, help='directory to save output images')
opt = args.parse_args()

if __name__ == '__main__':
    if len(opt.eye) > 4:
        print("opt.eye must be len <= 4")
    else:
        Detector.setConfig(opt.output_dir, opt.frames, *opt.eye)
        Detector.start(opt.path)
