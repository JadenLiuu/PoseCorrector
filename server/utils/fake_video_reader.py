import cv2

class FakeVideoReader:
    def __init__(self, video_path):
        self.video_path = video_path
        self.cap = None
        self.open_video()
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.size = (int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        print(self.size, self.fps)

    def open_video(self):
        self.cap = cv2.VideoCapture(self.video_path)
    def close_video(self):
        if self.cap is not None:
            self.cap.release()

    def get_frame(self):
        if self.cap is None:
            self.open_video()

        while(True):
            ret, frame = self.cap.read()
            if not ret:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            break
        return frame

if __name__ == "__main__":
    f = FakeVideoReader("/home/dev/fake_video.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter("test3.mp4", fourcc, f.fps, f.size)
    for i in range(1000):
        frame = f.get_frame()
        # frame = cv2.imread(f'img.jpg') 
        out.write(frame)
        # print(frame.shape)
    f.close_video()
    out.release()