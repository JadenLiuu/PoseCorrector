from fastapi import status, FastAPI
from fastapi.responses import JSONResponse
from typing import List, Optional
from response_models import *
from job.get import Job
from res_model import *

app = FastAPI()

SUCCESS_RESPONSE=JSONResponse(content="succ", status_code=200)

numCameras = 1

camShotJobs = { # lineID -> camera to shooter
    "01": Job(jobType=Job.TypeShooter)
}
camTargetJobs = { # lineID -> camera to target
    "01": Job(jobType=Job.TypeTarget)
}
# camShotJobs = { # lineID -> camera to shooter
#     "01": Job(jobType=Job.TypeShooter),
#     "02": Job(jobType=Job.TypeShooter),
#     "03": Job(jobType=Job.TypeShooter),
#     "04": Job(jobType=Job.TypeShooter),
#     "05": Job(jobType=Job.TypeShooter),
#     "06": Job(jobType=Job.TypeShooter)
# }

# camTargetJobs = { # lineID -> camera to target
#     "01": Job(jobType=Job.TypeTarget),
#     "02": Job(jobType=Job.TypeTarget),
#     "03": Job(jobType=Job.TypeTarget),
#     "04": Job(jobType=Job.TypeTarget),
#     "05": Job(jobType=Job.TypeTarget),
#     "06": Job(jobType=Job.TypeTarget)
# }

@app.post('/ai/', response_model=LineResponse, status_code=status.HTTP_201_CREATED)
async def Ai(startInfo: LineResponse):
    return SUCCESS_RESPONSE

@app.post('/ai/Start/', response_model=StartInfo, status_code=status.HTTP_201_CREATED)
async def Start(startInfo: StartInfo):
    try:
        print(startInfo.StartData)
        for camId in range(1, numCameras+1):
            key = '{:02d}'.format(camId)
            print(f'key:{key}')
            camShotJobs[key].start_record(key, startInfo.StartData)
            camTargetJobs[key].start_record(key, startInfo.StartData)
        return SUCCESS_RESPONSE
    except Exception as e:
        err = {'Error': f"setting api failed, error: {e}"}
        return JSONResponse(content=err, status_code=400)

@app.post('/ai/Setting/', response_model=SettingInfo, status_code=status.HTTP_201_CREATED)
async def Setting(settingInfo: SettingRequest):
    if len(settingInfo.Data) <= 0:
        err = {'Error' : 'length of the inputs is zero'}
        print(f"[Setting] Error : length of the inputs is zero", flush=True)
        return JSONResponse(content = err, status_code=400)
    try:
        print(f"[main][Setting] setting {len(settingInfo.Data)} lines")
        for setInfo in settingInfo.Data:
            if setInfo.LineName not in camTargetJobs.keys():
                print(f"[main][Setting] Error : {setInfo.LineName} is not valid in jobs")
                raise Exception(f'{setInfo.LineName} is not valid in jobs')
            if len(setInfo.Address) != 2:
                # TODO: lack of one of the cam, handling the faults!
                print(f"[main][Setting] Error : Setting Failed {setInfo.LineName}, inadequate IP Address ")
                continue
            print(f"[main][Setting] Setting {setInfo.LineName}")
            camShotJobs[setInfo.LineName].set(setInfo.Address[0], setInfo.Info_Id, setInfo.FilePath)
            camTargetJobs[setInfo.LineName].set(setInfo.Address[1], setInfo.Info_Id, setInfo.FilePath)

        return SUCCESS_RESPONSE
    except Exception as e:
        err = {'Error': f"setting api failed, error: {e}"}
        print(f"[Setting] Error : setting api failed, error : {e}")
        return JSONResponse(content=err, status_code=400)


@app.post('/ai/END/', response_model=EndRequest, status_code=status.HTTP_201_CREATED)
async def End(endInfos: EndRequest):
    end_camera_num = len(endInfos.Data)
    if len(endInfos.Data) <= 0:
        err = {'Error' : 'length of the inputs is zero'}
        return JSONResponse(content = err, status_code=400)
    try:
        for i, camId in enumerate(range(1, end_camera_num+1)):
            key = '{:02d}'.format(camId)
            camShotJobs[key].end_record(runAI=True, end_data=endInfos.Data[i])
            camTargetJobs[key].end_record(runAI=False)
        return SUCCESS_RESPONSE
    except Exception as e:
        err = {'Error': f"setting api failed, error: {e}"}
        print(f"[End] Error : setting api failed, error : {e}")
        return JSONResponse(content=err, status_code=40)