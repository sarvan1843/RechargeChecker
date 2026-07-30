"""
Test the confirmed plans endpoint: POST /static/data/plans
Required fields: operator_id, circle_id, orderDirection
"""
import asyncio
import httpx
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

MOBILE = "7869632727"
BASE = "https://v1.pro.rechargemojo.com"

HEADERS_BASE = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-IN,en;q=0.9",
    "Origin": "https://rechargemojo.com",
    "Referer": "https://rechargemojo.com/",
    "Content-Type": "application/json",
}

# Known operator IDs for Indian telecom (common mapping)
# Jio=1, Airtel=2, Vi=3, BSNL=4 OR different values - we'll test all
OPERATOR_IDS = [1, 2, 3, 4, 5, 6, 7, 8]
CIRCLE_IDS   = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
ORDER_DIRS   = ["asc", "desc", "ASC", "DESC", "price_asc", "price_desc", "low", "high"]

async def run():
    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:

        # Step 1: Get guest token
        print("Step 1: Getting guest token...")
        r = await client.post(f"{BASE}/auth/create-guest-token", headers=HEADERS_BASE)
        token = r.json().get("token")
        print(f"  Token: {token}")

        auth_headers = {**HEADERS_BASE, "Authorization": f"Bearer {token}"}

        # Step 2: Detect operator/circle for test number
        print(f"\nStep 2: Detecting operator/circle for {MOBILE}...")
        r = await client.post(
            f"{BASE}/static/data/mnp_detect_number",
            headers=auth_headers,
            json={"number": MOBILE}
        )
        data = r.json()
        print(f"  Response: {data}")
        detected_op = data.get("data", {}).get("operator_id")
        detected_circle = data.get("data", {}).get("circle_id")
        print(f"  Detected -> operator_id={detected_op}, circle_id={detected_circle}")

        # Step 3: Try POST /static/data/plans with various operator/circle/orderDirection combos
        print(f"\nStep 3: Testing POST /static/data/plans with correct params...")
        url = f"{BASE}/static/data/plans"

        # Try orderDirection values first with Jio (operator_id=1) + any circle
        for order_dir in ORDER_DIRS:
            payload = {
                "operator_id": 1,
                "circle_id": 1,
                "type": "prepaid",
                "orderDirection": order_dir
            }
            r = await client.post(url, headers=auth_headers, json=payload)
            body = r.text[:300]
            if "E_VALIDATION" not in body and "E_ROUTE" not in body:
                print(f"\n  [SUCCESS] orderDirection='{order_dir}'")
                print(f"  Body: {body}")
                break
            else:
                print(f"  [{order_dir}] -> {body[:100]}")

        # Step 4: Now try all operator_ids with valid orderDirection
        print(f"\nStep 4: Finding correct operator_id for Jio...")
        valid_order = "asc"  # will try this
        for op_id in OPERATOR_IDS:
            payload = {
                "operator_id": op_id,
                "circle_id": 1,
                "type": "prepaid",
                "orderDirection": valid_order
            }
            r = await client.post(url, headers=auth_headers, json=payload)
            body = r.text
            if r.status_code == 200 and "E_VALIDATION" not in body and "E_ROUTE" not in body:
                print(f"\n  [HIT] operator_id={op_id}")
                print(f"  Body snippet: {body[:500]}")
                # Check if Top Up is present
                if "Top Up" in body or "topup" in body.lower() or "top_up" in body.lower():
                    print("  [TOP UP FOUND] Active number!")
                else:
                    print("  [NO TOP UP] Expired/no topup")

        print("\nDone.")

if __name__ == "__main__":
    asyncio.run(run())
