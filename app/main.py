from fastapi import FastAPI, Header, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import time
import json
import asyncio

from app.models import RechargeRequest, UserRegister, UserLogin, OTPRequest, OTPVerify
from app.logger import logger
from app.scraper import open_jio_website
from app.database import init_db, create_user, get_user_by_mobile, get_user_by_email, store_otp, get_otp, delete_otp, update_last_login
from app.auth import hash_password, verify_password, generate_token, verify_token
from app.pool import session_pool

app = FastAPI(
    title="Recharge Checker API",
    version="3.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    init_db()
    # Initialize session pool in the background (prevents blocking startup)
    asyncio.create_task(session_pool.start())

@app.on_event("shutdown")
async def on_shutdown():
    print("Shutting down app, closing session pool...")
    await session_pool.close_all()

@app.get("/")
async def home():
    return {
        "success": True,
        "message": "Recharge Checker Backend Running"
    }

# ----------------------------------------------------
# AUTHENTICATION ROUTERS
# ----------------------------------------------------

@app.post("/auth/register")
async def register(data: UserRegister):
    try:
        # Validate inputs
        if len(data.mobile) != 10 or not data.mobile.isdigit():
            return {"success": False, "message": "Mobile number must be exactly 10 digits"}
        if len(data.pin) != 4 or not data.pin.isdigit():
            return {"success": False, "message": "PIN must be exactly 4 digits"}

        # Check if mobile or email already exists
        if get_user_by_mobile(data.mobile):
            return {"success": False, "message": "Mobile number already registered"}
        if data.email and get_user_by_email(data.email):
            return {"success": False, "message": "Email already exists"}
        
        hashed = hash_password(data.pin)
        create_user(data.mobile, hashed, data.email, data.fullName)
        return {"success": True, "message": "Registration successful"}
    except Exception as e:
        logger.exception("REGISTRATION FAILED")
        return {"success": False, "message": str(e)}

@app.post("/auth/login")
async def login(data: UserLogin):
    try:
        if len(data.mobile) != 10 or not data.mobile.isdigit():
            return {"success": False, "message": "Invalid 10-digit mobile number"}
        if len(data.pin) != 4 or not data.pin.isdigit():
            return {"success": False, "message": "Invalid 4-digit PIN"}

        user = get_user_by_mobile(data.mobile)
        if not user:
            return {"success": False, "message": "Mobile number is not registered"}
        
        if not verify_password(data.pin, user["pin_hash"]):
            return {"success": False, "message": "Incorrect 4-digit PIN"}
        
        # Update last login timestamp in Excel database
        try:
            update_last_login(data.mobile)
        except Exception as update_err:
            logger.warning(f"Failed to update last login timestamp: {update_err}")

        token = generate_token(data.mobile)
        return {
            "success": True,
            "token": token,
            "mobile": user["mobile"],
            "email": user["email"] or "",
            "fullName": user["full_name"] or "",
            "message": "Login successful"
        }
    except Exception as e:
        logger.exception("LOGIN FAILED")
        return {"success": False, "message": str(e)}

@app.post("/auth/send-otp")
async def send_otp(data: OTPRequest):
    try:
        otp_code = "123456" # Mock OTP code for simplicity and testing
        expiry = int(time.time()) + 300 # 5 minutes
        store_otp(data.email, otp_code, expiry)
        return {
            "success": True,
            "message": f"OTP sent to {data.email}. (Test Code: {otp_code})"
        }
    except Exception as e:
        logger.exception("SEND OTP FAILED")
        return {"success": False, "message": str(e)}

@app.post("/auth/verify-otp")
async def verify_otp(data: OTPVerify):
    try:
        otp_record = get_otp(data.email)
        if not otp_record:
            return {"success": False, "message": "OTP not requested or expired"}
        
        if int(time.time()) > otp_record["expires_at"]:
            delete_otp(data.email)
            return {"success": False, "message": "OTP expired"}
        
        if otp_record["otp"] != data.otp:
            return {"success": False, "message": "Invalid OTP code"}
        
        delete_otp(data.email)
        return {"success": True, "message": "OTP verified successfully"}
    except Exception as e:
        logger.exception("VERIFY OTP FAILED")
        return {"success": False, "message": str(e)}

@app.get("/auth/profile")
async def profile(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.split(" ")[1]
    mobile = verify_token(token)
    if not mobile:
        raise HTTPException(status_code=401, detail="Token expired or invalid")
        
    user = get_user_by_mobile(mobile)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return {
        "success": True,
        "mobile": user["mobile"],
        "email": user["email"] or "",
        "fullName": user["full_name"] or "",
        "createdAt": user["created_at"]
    }

# ----------------------------------------------------
# RECHARGE CHECK ROUTER
# ----------------------------------------------------

@app.post("/check-recharge")
async def check_recharge(data: RechargeRequest):
    logger.info("=" * 60)
    logger.info("NEW REQUEST RECEIVED")
    logger.info(f"Mobile   : {data.mobile}")
    logger.info(f"Operator : {data.operatorName}")
    logger.info(f"Circle   : {data.circle}")

    print("=" * 60)
    print("NEW REQUEST RECEIVED")
    print(f"Mobile   : {data.mobile}")
    print(f"Operator : {data.operatorName}")
    print(f"Circle   : {data.circle}")
    print("=" * 60)

    try:
        result = await open_jio_website(
            mobile=data.mobile,
            operator=data.operatorName,
            circle=data.circle,
        )

        logger.info(f"API RESPONSE : {result}")
        print("\nAPI RESPONSE:")
        print(result)

        return result

    except Exception as e:
        logger.exception("CHECK RECHARGE FAILED")
        print("\nCHECK RECHARGE FAILED")
        print(str(e))

        return {
            "success": False,
            "status": "Failed",
            "operator": data.operatorName,
            "circle": data.circle,
            "plan": "",
            "validity": "",
            "expiryDate": "",
            "message": str(e),
            "error": str(e),
        }

@app.websocket("/ws/check-recharge")
async def websocket_check_recharge(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket client connected.")
    try:
        while True:
            data_str = await websocket.receive_text()
            data = json.loads(data_str)
            
            row_id = data.get("row_id")
            mobile = data.get("mobile")
            operator = data.get("operator")
            circle = data.get("circle")
            
            async def send_progress(stage: str):
                try:
                    await websocket.send_json({
                        "row_id": row_id,
                        "status": "progress",
                        "stage": stage
                    })
                except Exception:
                    pass
                
            try:
                await send_progress("Initializing API")
                await send_progress("Fetching Token")
                
                # Fast API Scraper (V4.4) call
                result = await open_jio_website(
                    mobile=mobile,
                    operator=operator,
                    circle=circle
                )
                
                await send_progress("Verification Complete")
                
                await websocket.send_json({
                    "row_id": row_id,
                    "status": "complete",
                    "result": result
                })
                    
            except Exception as outer_err:
                await websocket.send_json({
                    "row_id": row_id,
                    "status": "complete",
                    "result": {
                        "success": False,
                        "status": "error",
                        "mobile": mobile,
                        "operator": operator,
                        "circle": circle,
                        "topupAvailable": False,
                        "message": str(outer_err),
                        "error": str(outer_err)
                    }
                })
    except WebSocketDisconnect:
        print("WebSocket client disconnected.")
    except Exception as ws_err:
        print(f"WebSocket execution error: {ws_err}")