

class Test():
    def __init__(self, video_path):
        self.video_path = video_path
    def hello(self):
        print(f"[Test] {self.video_path} say hello", flush=True)