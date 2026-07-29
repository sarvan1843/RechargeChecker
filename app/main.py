from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models import RechargeRequest
from app.logger import logger
from app.scraper import open_jio_website

app = FastAPI(
    title="Recharge Checker API",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def home():
    return {
        "success": True,
        "message": "Recharge Checker Backend Running"
    }


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