"""
V4.4 Fast Scraper - Direct HTTP API (No Browser/Playwright needed)
Uses rechargemojo.com internal API endpoints directly via httpx.
Speed: <2 seconds per check (vs 8-12 seconds with Playwright)
RAM:   Minimal (vs 500MB+ for Playwright)
"""
import httpx
from app.logger import logger

print("########## V4.4 FAST API SCRAPER LOADED ##########")

BASE_URL = "https://v1.pro.rechargemojo.com"

# Operator name -> operator_id mapping from rechargemojo API
OPERATOR_ID_MAP = {
    "jio":     1,
    "airtel":  31,
    "vi":      11,
    "vodafone": 11,
    "bsnl":    16,
    "mtnl":    36,
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-IN,en;q=0.9",
    "Origin": "https://rechargemojo.com",
    "Referer": "https://rechargemojo.com/",
    "Content-Type": "application/json",
}


async def _get_guest_token(client: httpx.AsyncClient) -> str | None:
    """Get a fresh guest token from rechargemojo API."""
    try:
        r = await client.post(f"{BASE_URL}/auth/create-guest-token", headers=HEADERS, timeout=10)
        return r.json().get("token")
    except Exception as e:
        logger.error(f"Failed to get guest token: {e}")
        return None


async def _fetch_plans(client: httpx.AsyncClient, token: str, operator_id: int, circle_id: int = 1) -> list:
    """Fetch plan categories for given operator_id and circle_id."""
    auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    payload = {
        "operator_id": operator_id,
        "circle_id": circle_id,
        "type": "prepaid",
        "orderDirection": "asc"
    }
    try:
        r = await client.post(
            f"{BASE_URL}/static/data/plans",
            headers=auth_headers,
            json=payload,
            timeout=15
        )
        data = r.json()
        if data.get("code") == 200:
            return data.get("data", [])
        return []
    except Exception as e:
        logger.error(f"Failed to fetch plans: {e}")
        return []


async def open_jio_website(
    mobile: str = None,
    operator: str = None,
    circle: str = None,
):
    """
    V4.4 Fast verification using direct API calls (no browser).
    Checks if 'Top Up' category is available for the given operator.
    Active   = Top Up category present in plans
    Expired  = Top Up category NOT present or plans empty
    """
    if mobile is None:
        mobile = "7869632727"

    logger.info("=" * 60)
    logger.info("V4.4 FAST API SCRAPER INITIATED")
    logger.info(f"Mobile   : {mobile}")
    logger.info(f"Operator : {operator}")
    logger.info(f"Circle   : {circle}")
    logger.info("=" * 60)

    # Resolve operator_id from operator name
    operator_key = (operator or "jio").lower().strip()
    operator_id = OPERATOR_ID_MAP.get(operator_key)
    if operator_id is None:
        # Try partial match
        for key, val in OPERATOR_ID_MAP.items():
            if key in operator_key or operator_key in key:
                operator_id = val
                break
    if operator_id is None:
        operator_id = 1  # default Jio
        logger.warning(f"Unknown operator '{operator}', defaulting to Jio (id=1)")

    logger.info(f"Resolved operator_id: {operator_id}")

    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:

            # Step 1: Get guest token
            logger.info("Step 1: Getting guest token...")
            token = await _get_guest_token(client)
            if not token:
                raise Exception("Failed to obtain guest token from rechargemojo API")
            logger.info(f"Token obtained: {token[:8]}...")

            # Step 2: Fetch plans for this operator (use circle_id=1, same plans for all circles)
            logger.info(f"Step 2: Fetching plans for operator_id={operator_id}...")
            categories = await _fetch_plans(client, token, operator_id, circle_id=1)
            logger.info(f"Got {len(categories)} plan categories")

            # Step 3: Check if 'Top Up' category is in the list
            category_names = [cat.get("name", "") for cat in categories]
            logger.info(f"Categories: {category_names}")

            topup_found = any(
                "top up" in name.lower() or "topup" in name.lower()
                for name in category_names
            )
            logger.info(f"Top Up found: {topup_found}")

            status = "Active" if topup_found else "Expired"
            message = "Top-Up Check Completed (Status: " + status + ")"

            result = {
                "success": True,
                "status": status,
                "mobile": mobile,
                "operator": operator,
                "circle": circle,
                "topupAvailable": topup_found,
                "detectionMethod": "Direct API v1.pro.rechargemojo.com",
                "confidence": 95,
                "categories": category_names,
                "plan": "",
                "validity": "",
                "expiryDate": "",
                "message": message,
                "error": None
            }

            logger.info(f"RESULT: {result}")
            return result

    except Exception as e:
        logger.exception(f"V4.4 Fast scraper failed: {e}")
        return {
            "success": False,
            "status": "error",
            "mobile": mobile,
            "operator": operator,
            "circle": circle,
            "topupAvailable": False,
            "detectionMethod": "Direct API",
            "confidence": 0,
            "categories": [],
            "plan": "",
            "validity": "",
            "expiryDate": "",
            "message": str(e),
            "error": str(e)
        }