"""
Direct HTTP API test for rechargemojo.com internal API.
No browser needed - pure httpx calls.
Steps:
1. Get guest token
2. Detect operator/circle from mobile number
3. Try to fetch plans using various endpoint patterns
4. Check if Top Up category is present
"""
import asyncio
import httpx
import json
import sys
import io
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

async def run():
    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        
        # STEP 1: Get guest token
        print("Step 1: Getting guest token...")
        r = await client.post(f"{BASE}/auth/create-guest-token", headers=HEADERS_BASE)
        print(f"  Status: {r.status_code}")
        print(f"  Body: {r.text[:300]}")
        
        token = None
        try:
            data = r.json()
            token = data.get("token")
            print(f"  [OK] Token: {token}")
        except Exception as e:
            print(f"  [FAIL] Failed to parse token: {e}")
            return

        auth_headers = {**HEADERS_BASE, "Authorization": f"Bearer {token}"}
        
        # STEP 2: Detect operator/circle
        print(f"\nStep 2: Detecting operator/circle for {MOBILE}...")
        r = await client.post(
            f"{BASE}/static/data/mnp_detect_number",
            headers=auth_headers,
            json={"number": MOBILE}
        )
        print(f"  Status: {r.status_code}")
        print(f"  Body: {r.text[:400]}")
        
        operator_id = None
        circle_id = None
        try:
            data = r.json()
            operator_id = data.get("data", {}).get("operator_id")
            circle_id = data.get("data", {}).get("circle_id")
            print(f"  Operator ID: {operator_id}, Circle ID: {circle_id}")
        except Exception as e:
            print(f"  Parse error: {e}")

        # STEP 3: Try various plans endpoints (GET)
        print(f"\nStep 3: Trying GET plans endpoints...")
        plan_endpoints = [
            "/plans", "/plan", "/recharge/plans", "/mobile/plans",
            "/plans/mobile", "/static/data/plans", "/plans/list",
            "/recharge-plans", "/operator/plans", "/browse/plans",
        ]
        params_list = [
            {"operator_id": 3, "circle_id": 1, "type": "prepaid"},
            {"operator_id": 3, "circle_id": 20, "type": "prepaid"},
            {"mobile": MOBILE, "type": "prepaid"},
            {"operator_id": operator_id, "circle_id": circle_id},
        ]
        for endpoint in plan_endpoints:
            for params in params_list:
                try:
                    url = f"{BASE}{endpoint}"
                    r = await client.get(url, headers=auth_headers, params=params)
                    if r.status_code == 200 and "json" in r.headers.get("content-type", ""):
                        print(f"\n  [HIT] GET {url} params={params}")
                        print(f"  Body: {r.text[:500]}")
                    elif r.status_code not in [404, 405, 422, 401]:
                        print(f"  [{r.status_code}] GET {url}")
                except Exception:
                    pass
        
        # STEP 4: Try POST plans endpoints
        print(f"\nStep 4: Trying POST plans endpoints...")
        for endpoint in plan_endpoints:
            for payload in params_list:
                try:
                    url = f"{BASE}{endpoint}"
                    r = await client.post(url, headers=auth_headers, json=payload)
                    if r.status_code == 200 and "json" in r.headers.get("content-type", ""):
                        print(f"\n  [POST HIT] {url}")
                        print(f"  Body: {r.text[:500]}")
                    elif r.status_code not in [404, 405, 422, 401]:
                        print(f"  [{r.status_code}] POST {url}")
                except Exception:
                    pass

        print("\nDone.")

if __name__ == "__main__":
    asyncio.run(run())
