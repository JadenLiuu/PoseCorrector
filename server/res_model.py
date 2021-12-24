from pydantic import BaseModel
from typing import List, Optional
from response_models import *

class AnalysisResult(BaseModel):
    Shot: str
    EyeClosed: bool
    EyeClosedScore: str # don't use float beacuse 64 bits is too long
    IsShrug: bool
    IsShrugScore: str

class Camera(BaseModel):
    IP: str
    ID: str
    Path: str

# each time it shot the gun, record each of the analysis results
# continuous record the video for all of the shots in one line, 
# here we use list for different cameras.
class LineResponse(BaseModel):
    LineName: str
    Info_Id: str
    TargetMp4Path: Camera
    Ai: Optional[List[AnalysisResult]]
