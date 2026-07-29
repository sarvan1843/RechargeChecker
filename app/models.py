from pydantic import BaseModel
from typing import Optional


class RechargeRequest(BaseModel):
    mobile: str
    operatorName: str
    circle: str


class RechargeResponse(BaseModel):
    success: bool
    status: Optional[str] = None
    mobile: Optional[str] = None
    operator: Optional[str] = None
    circle: Optional[str] = None
    plan: Optional[str] = None
    validity: Optional[str] = None
    expiryDate: Optional[str] = None
    message: str
    error: Optional[str] = None