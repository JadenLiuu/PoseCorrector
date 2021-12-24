from fastapi import status, FastAPI
from fastapi.responses import JSONResponse
from typing import List, Optional
from response_models import *
from job.get import Job
from res_model import *

app = FastAPI()

SUCCESS_RESPONSE=JSONResponse(content="succ", status_code=200)

numCameras = 6

camShotJobs = { # lineID -> camera to shooter
    "01": Job(jobType=Job.TypeShooter),
    "02": Job(jobType=Job.TypeShooter),
    "03": Job(jobType=Job.TypeShooter),
    "04": Job(jobType=Job.TypeShooter),
    "05": Job(jobType=Job.TypeShooter),
    "06": Job(jobType=Job.TypeShooter),
}

camTargetJobs = { # lineID -> camera to target
    "01": Job(jobType=Job.TypeTarget),
    "02": Job(jobType=Job.TypeTarget),
    "03": Job(jobType=Job.TypeTarget),
    "04": Job(jobType=Job.TypeTarget),
    "05": Job(jobType=Job.TypeTarget),
    "06": Job(jobType=Job.TypeTarget),
}

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
            camShotJobs[key].start_record(key)
            camTargetJobs[key].start_record(key)
        return startInfo.dict()
    except Exception as e:
        err = {'Error': f"setting api failed, error: {e}"}
        return JSONResponse(content=err, status_code=400)

@app.post('/ai/Setting/', response_model=List[SettingInfo], status_code=status.HTTP_201_CREATED)
async def Setting(settings: List[SettingInfo]):
    if len(settings) <= 0:
        err = {'Error' : 'length of the inputs is zero'}
        return JSONResponse(content = err, status_code=400)
    try:
        for setInfo in settings:
            if setInfo.LineName not in camTargetJobs.keys():
                raise Exception(f'{setInfo.LineName} is not valid in jobs')
            if len(setInfo.Address) != 2:
                # TODO: lack of one of the cam, handling the faults!
                continue
            camShotJobs[setInfo.LineName].set(setInfo.Address[0], setInfo.Info_Id, setInfo.FilePath)
            camTargetJobs[setInfo.LineName].set(setInfo.Address[1], setInfo.Info_Id, setInfo.FilePath)

        return SUCCESS_RESPONSE
    except Exception as e:
        err = {'Error': f"setting api failed, error: {e}"}
        return JSONResponse(content=err, status_code=400)


@app.post('/ai/END/', response_model=List[EndInfo], status_code=status.HTTP_201_CREATED)
async def End(endInfos: List[EndInfo]):
    if len(endInfos) <= 0:
        err = {'Error' : 'length of the inputs is zero'}
        return JSONResponse(content = err, status_code=400)
    try:
        for camId in range(1, numCameras+1):
            key = '{:02d}'.format(camId)
            camShotJobs[key].end_record(runAI=True)
            camTargetJobs[key].end_record(runAI=False)
        return SUCCESS_RESPONSE
    except Exception as e:
        err = {'Error': f"setting api failed, error: {e}"}
        return JSONResponse(content=err, status_code=400)