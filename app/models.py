from pydantic import BaseModel
from typing import Optional, List

class RechargeRequest(BaseModel):
    mobile: str
    operatorName: str
    circle: str

class UserRegister(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    fullName: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class OTPRequest(BaseModel):
    email: str

class OTPVerify(BaseModel):
    email: str
    otp: str