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
 
class LineInfo(BaseModel):
    LineName: str
    One: str
    Two: str
    Three: str
    Four: str
    Five: str
    Six: str

class EndInfo(BaseModel):
    EndData: str
    Data: List[LineInfo]