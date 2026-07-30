import httpx
import os
import json
from app.logger import logger

# These will be loaded from Render environment variables once you buy the API
API_BASE_URL = os.getenv("B2B_API_URL", "https://api.dummy-b2b-provider.com")
API_TOKEN = os.getenv("B2B_API_TOKEN", "dummy_token")

async def check_recharge_b2b(mobile: str, operator: str, circle: str) -> dict:
    """
    Calls the external B2B Recharge API to get real-time plan details.
    """
    try:
        # We will update this URL format tomorrow based on the exact API you purchase.
        # Example: ZuelPay, Lapu, Cybrilla, etc.
        url = f"{API_BASE_URL}/get-plan?mobile={mobile}&operator={operator}&circle={circle}&token={API_TOKEN}"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            
            # If the API requires authentication headers instead of URL parameters, we'll do this:
            # response = await client.get(url, headers={"Authorization": f"Bearer {API_TOKEN}"})

            if response.status_code == 200:
                data = response.json()
                
                # --- TEMPORARY MOCK RESPONSE (Until tomorrow) ---
                # This mimics exactly what the Flutter app expects
                return {
                    "success": True,
                    "status": "Active",
                    "operator": operator,
                    "circle": circle,
                    "plan": "Rs. 299",
                    "validity": "28 Days",
                    "expiryDate": "2026-08-30",
                    "message": "Plan fetched from B2B API successfully"
                }
                
                # Tomorrow we will parse the actual 'data' from the API here:
                # return {
                #     "success": True,
                #     "status": "Active",
                #     "operator": data.get("operator_name"),
                #     "circle": data.get("circle_name"),
                #     "plan": data.get("current_plan"),
                #     ...
                # }
            else:
                return {
                    "success": False,
                    "status": "Failed",
                    "operator": operator,
                    "circle": circle,
                    "message": f"API Provider Error: {response.status_code}",
                    "error": response.text
                }

    except Exception as e:
        logger.exception(f"B2B API Error for {mobile}")
        return {
            "success": False,
            "status": "Error",
            "operator": operator,
            "circle": circle,
            "message": "Connection to Provider failed",
            "error": str(e)
        }
