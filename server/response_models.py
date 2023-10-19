from pydantic import BaseModel
from typing import List, Optional


class StartInfo(BaseModel):
    StartData: str

class AddressInfo(BaseModel):
    ID:str
    IP:str
 
class SettingInfo(BaseModel):
    LineName: str
    Address: List[AddressInfo] 
    Info_Id: str
    FilePath: str

class SettingRequest(BaseModel):
    Data: List[SettingInfo]

class LineInfo(BaseModel):
    LineName: str
    One: str
    Two: str
    Three: str
    Four: str
    Five: str
    Six: str

class EndRequest(BaseModel):
    EndDate: str
    Data: List[LineInfo]