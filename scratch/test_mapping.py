"""
Final confirmation test:
1. Find correct mobile number format for mnp_detect_number
2. Map operator names to operator_ids
3. Find circle_id mapping
4. Full end-to-end test: mobile -> detect operator/circle -> fetch plans -> check Top Up
"""
import asyncio
import httpx
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = "https://v1.pro.rechargemojo.com"
HEADERS_BASE = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-IN,en;q=0.9",
    "Origin": "https://rechargemojo.com",
    "Referer": "https://rechargemojo.com/",
    "Content-Type": "application/json",
}

# Test with known Jio number
TEST_MOBILE = "7869632727"

async def run():
    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:

        # Get token
        r = await client.post(f"{BASE}/auth/create-guest-token", headers=HEADERS_BASE)
        token = r.json().get("token")
        auth_headers = {**HEADERS_BASE, "Authorization": f"Bearer {token}"}
        print(f"Token: {token}")

        # Test mnp_detect_number with different payloads
        print("\n--- Testing mnp_detect_number field names ---")
        payloads = [
            {"mobile": TEST_MOBILE},
            {"mobile_number": TEST_MOBILE},
            {"number": TEST_MOBILE},
            {"phone": TEST_MOBILE},
            {"msisdn": TEST_MOBILE},
            {"mobile": TEST_MOBILE, "type": "prepaid"},
        ]
        for payload in payloads:
            r = await client.post(f"{BASE}/static/data/mnp_detect_number", headers=auth_headers, json=payload)
            body = r.text[:200]
            if "E_VALIDATION" not in body:
                print(f"  [SUCCESS] payload={payload}")
                print(f"  Body: {body}")
                break
            else:
                print(f"  payload={list(payload.keys())} -> {body[:80]}")

        # Get operator list
        print("\n--- Getting operator list ---")
        op_endpoints = ["/static/data/operators", "/operators", "/static/operators", "/recharge/operators"]
        for ep in op_endpoints:
            r = await client.get(f"{BASE}{ep}", headers=auth_headers)
            if r.status_code == 200 and "E_ROUTE" not in r.text:
                print(f"  [HIT] GET {ep}")
                print(f"  Body: {r.text[:500]}")
                break

        # Get circle list
        print("\n--- Getting circle list ---")
        circle_endpoints = ["/static/data/circles", "/circles", "/static/circles", "/recharge/circles"]
        for ep in circle_endpoints:
            r = await client.get(f"{BASE}{ep}", headers=auth_headers)
            if r.status_code == 200 and "E_ROUTE" not in r.text:
                print(f"  [HIT] GET {ep}")
                print(f"  Body: {r.text[:600]}")
                break

        # Full Top Up check for Jio number (operator_id=1)
        print(f"\n--- Full Top Up check for {TEST_MOBILE} (Jio) ---")
        # Try all circle_ids 1-30 to find non-empty results
        for circle_id in range(1, 31):
            payload = {"operator_id": 1, "circle_id": circle_id, "type": "prepaid", "orderDirection": "asc"}
            r = await client.post(f"{BASE}/static/data/plans", headers=auth_headers, json=payload)
            data = r.json()
            categories = data.get("data", [])
            if categories:
                cat_names = [c.get("name", "") for c in categories]
                topup = any("Top Up" in n or "topup" in n.lower() for n in cat_names)
                print(f"  circle_id={circle_id}: categories={cat_names} | Top Up={topup}")
                if circle_id >= 5:
                    break  # found enough

        print("\nDone.")

if __name__ == "__main__":
    asyncio.run(run())
