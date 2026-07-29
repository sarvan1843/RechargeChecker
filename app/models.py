from pydantic import BaseModel
from typing import Optional

class RechargeRequest(BaseModel):
    mobile: str
    operatorName: str
    circle: str

class UserRegister(BaseModel):
    mobile: str
    pin: str
    email: Optional[str] = None
    fullName: Optional[str] = None

class UserLogin(BaseModel):
    mobile: str
    pin: str

class OTPRequest(BaseModel):
    email: str

class OTPVerify(BaseModel):
    email: str
    otp: str