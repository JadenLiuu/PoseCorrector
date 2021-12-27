import multiprocessing as mp
import time
import os
from job.exceptions import *
import utils.util as utils


SetLock = mp.Lock()

class CameraSet(mp.Process):
    ValidCam = set()

    def __init__(self, camId, startUnixMicroTs):
        mp.Process.__init__(self, daemon=True)
        self.exit = mp.Event()

        if camId in CameraSet.ValidCam:
            raise CAMERA_PROCESSING
        
        CameraSet.ValidCam.add(camId)
        self.camId = camId
        self.startUnixMicroTs = startUnixMicroTs
        print(f'{camId} is set up...')

    def set(self, fileDir):
        print(CameraSet.ValidCam)
        utils.dir_init(fileDir)
        fileName=f'{self.camId}-{self.startUnixMicroTs}.mp4'
        self.filePath = os.path.join(fileDir, fileName)
        
    def run(self):
        print('run...')
        while not self.exit.is_set():
            time.sleep(1)
            pass
            # start recording mp4....
        # record done. store to `filePath`
        # done
        
        os.system(f"touch {self.filePath}")
        
    def shutdown(self):
        print("Shutdown initiated")
        self.exit.set()
        return self.filePath

    def release(self):
        if self.isRunning:
            with SetLock:
                print(CameraSet.ValidCam)
                CameraSet.ValidCam.remove(self.camId)

    def isRunning(self, camId: str) -> bool:
        running = False
        with SetLock:
            running = camId in CameraSet.ValidCam
        return running
