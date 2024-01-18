from job.cam import CameraSet, CAMERA_PROCESSING
from res_model import *
from response_models import *
from job.curlRes import sendInfo2
from job.exceptions import *
import utils.util as utils

def get_time_points_from_end_data(end_data, fake=False, start_time=None):
    end_time_points = []    
    if fake:
        for i in range(6):
            end_time_points.append(start_time + i * 1e6)
        return end_time_points
    time_point = end_data.One
    if not len(str(time_point)) <= 20:
        end_time_points.append(utils.date_to_timestamp(time_point))
    time_point = end_data.Two
    if not len(str(time_point)) <= 20:
        end_time_points.append(utils.date_to_timestamp(time_point))
    time_point = end_data.Three
    if not len(str(time_point)) <= 20:
        end_time_points.append(utils.date_to_timestamp(time_point))
    time_point = end_data.Four
    if not len(str(time_point)) <= 20:
        end_time_points.append(utils.date_to_timestamp(time_point))
    time_point = end_data.Five
    if not len(str(time_point)) <= 20:
        end_time_points.append(utils.date_to_timestamp(time_point))
    time_point = end_data.Six
    if not len(str(time_point)) <= 20:
        end_time_points.append(utils.date_to_timestamp(time_point))

    return end_time_points

def timestamp_to_frameNums(start_time, time_points):
    interval = 2 * 100000
    output = []
    for time_point in time_points:
        frame_num = int((time_point - start_time)/interval)
        if frame_num >= 1:
            output.append()
    return output

class Job(object):
    TypeShooter="shooter"
    TypeTarget="target"
    __validTypes = [TypeShooter, TypeTarget]

    def __init__(self, jobType :str):
        super(Job, self).__init__()
        if jobType not in Job.__validTypes:
            raise Exception(f"{jobType} is not a valid job type!")
        self.jobType = jobType

    def start_record(self, camId: str, startDate: str):
        self.startUnixMicroTs = utils.now_unix_micro()
        self.camId = f'{self.jobType}-{camId}'
        if self.jobType == "shooter":
            ai = True
        else :
            ai = False
        self.cameraRecorder = CameraSet(self.camId, self.startUnixMicroTs, ai=ai)
        self.cameraRecorder.start()
        self.startDate=startDate

    def set(self, address: AddressInfo, infoId: str, filePath: str):
        if self.jobType == "shooter" : 
            address.IP = f"rtsp://admin:123456@{address.IP}:7070/track1"
            # address.IP = f"rtsp://admin:1qaz@WSX3edc@{address.IP}:554/media/video1"
        else:
            address.IP = f"rtsp://admin:1qaz@WSX3edc@{address.IP}:554/media/video1"

        print(f'set....{address}, {infoId}, {filePath}')
        self.address = address
        self.infoId = infoId
        self.cameraRecorder.set(filePath, address.IP)
    
    def end_record(self, runAI=False, end_data=None):
        res = None
        if not self.cameraRecorder.isRunning(self.camId):
            raise NOTRUNNING
    
        filePath, start_time = self.cameraRecorder.shutdown()
        self.cameraRecorder.join()
        self.cameraRecorder.release()
        if runAI:
            print(f"received end data : {end_data}", flush=True)
            end_time_points = get_time_points_from_end_data(end_data, fake=False, start_time=start_time)
            print(f"{end_time_points = }, {start_time = }", flush=True)
            frame_numbers = timestamp_to_frameNums(start_time, end_time_points)
            frame_numbers_str = " ".join(str(number) for number in frame_numbers)
            print(f"{frame_numbers_str = }")
            # todo: use the filePath to get the ai result of the input mp4
            sendInfo2(filePath, frame_numbers_str)
            # sendInfo(LineResponse(
            #     LineName=self.camId, 
            #     Info_Id= self.infoId,
            #     TargetMp4Path=Camera(IP=self.address.IP,ID=self.address.ID, Path=filePath),
            #     Ai=[AnalysisResult(
            #         Shot="1",EyeClosed=True,EyeClosedScore="0.99",IsShrug=False,IsShrugScore="0.12"
            #     )]
            # ))

        elapsed = utils.now_unix_micro()-self.startUnixMicroTs
        print(f'elapsed: {elapsed}')
        return res