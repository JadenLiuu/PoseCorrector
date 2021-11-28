from fastapi import status, FastAPI
from fastapi.responses import JSONResponse
from typing import List, Optional
from response_models import *

app = FastAPI()

@app.post('/ai/Start/', response_model=StartInfo, status_code=status.HTTP_201_CREATED)
async def Start(startInfo: StartInfo):
    print(startInfo.StartData)
    return startInfo.dict()


@app.post('/ai/Setting/', response_model=List[SettingInfo], status_code=status.HTTP_201_CREATED)
async def Setting(settings: List[SettingInfo]):
    if len(settings) <= 0:
        err = {'Error' : 'length of the inputs is zero'}
        return JSONResponse(content = err, status_code=400)
    try:
        return JSONResponse(content="succ", status_code=200)
    except Exception as e:
        err = {'Error': f"setting api failed, error: {e}"}
        return JSONResponse(content=err, status_code=400)


@app.post('/ai/END/', response_model=List[EndInfo], status_code=status.HTTP_201_CREATED)
async def End(endInfos: List[EndInfo]):
    if len(endInfos) <= 0:
        err = {'Error' : 'length of the inputs is zero'}
        return JSONResponse(content = err, status_code=400)
    try:
        return JSONResponse(content="succ", status_code=200)
    except Exception as e:
        err = {'Error': f"setting api failed, error: {e}"}
        return JSONResponse(content=err, status_code=400)