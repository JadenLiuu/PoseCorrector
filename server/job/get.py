import time
from job.cam import CameraSet, CAMERA_PROCESSING
from res_model import *
from response_models import *
from job.curlRes import sendInfo
from job.exceptions import *


def now_unix_micro():
    # function available after python 3.7
    return time.time_ns()/1000.0

class Job(object):
    TypeShooter="shooter"
    TypeTarget="target"
    __validTypes = [TypeShooter, TypeTarget]

    def __init__(self, jobType :str):
        super(Job, self).__init__()
        if jobType not in Job.__validTypes:
            raise Exception(f"{jobType} is not a valid job type!")
        self.startUnixMicroTs = None
        self.endUnixMicroTs = None
        self.jobType = jobType

    def start_record(self, camId):
        camId = f'{self.jobType}-{camId}'
        self.startUnixMicroTs = now_unix_micro()
        self.cameraRecorder = CameraSet(camId)
        self.camId=camId
        print('go')
        self.cameraRecorder.start()
        print('go done')

    def set(self, address: AddressInfo, infoId: str, filePath: str):
        print(f'set....{address}, {infoId}, {filePath}')
        self.address = address
        self.infoId = infoId
        self.cameraRecorder.set(filePath)

    def end_record(self, runAI=False):
        res = None
        if not self.cameraRecorder.isRunning(self.camId):
            raise NOTRUNNING
    
        filePath = self.cameraRecorder.shutdown()
        self.cameraRecorder.join()
        self.cameraRecorder.release()

        if runAI:
            # todo: use the filePath to get the ai result of the input mp4
            sendInfo(LineResponse(
                LineName=self.camId, 
                Info_Id= self.infoId,
                TargetMp4Path=Camera(IP=self.address.IP,ID=self.address.ID, Path=filePath),
                Ai=[AnalysisResult(
                    Shot="1",EyeClosed=True,EyeClosedScore="0.99",IsShrug=False,IsShrugScore="0.12"
                )]
            ))

        elapsed = now_unix_micro()-self.startUnixMicroTs
        print(f'elapsed: {elapsed}')
        return res
