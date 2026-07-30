"""
Get full operator list and circle list from rechargemojo API
to build the complete ID mapping.
"""
import asyncio
import httpx
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = "https://v1.pro.rechargemojo.com"
HEADERS_BASE = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://rechargemojo.com",
    "Referer": "https://rechargemojo.com/",
    "Content-Type": "application/json",
}

async def run():
    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        # Get token
        r = await client.post(f"{BASE}/auth/create-guest-token", headers=HEADERS_BASE)
        token = r.json().get("token")
        auth_headers = {**HEADERS_BASE, "Authorization": f"Bearer {token}"}

        # Operators - need category field
        print("--- Operator list (category=mobile) ---")
        for cat in ["mobile", "recharge", "prepaid", "all", "operator", "1", "mobile_recharge"]:
            r = await client.get(f"{BASE}/static/data/operators",
                                 headers=auth_headers, params={"category": cat})
            if r.status_code == 200 and "E_VALIDATION" not in r.text and "E_ROUTE" not in r.text:
                print(f"  [HIT] category={cat}")
                print(f"  Body: {r.text[:800]}")
                break
            else:
                print(f"  [{cat}] -> {r.text[:60]}")

        # Circles
        print("\n--- Circle list ---")
        for ep in ["/static/data/circles", "/static/data/states", "/circles", "/states"]:
            r = await client.get(f"{BASE}{ep}", headers=auth_headers)
            if r.status_code == 200 and "E_ROUTE" not in r.text and "E_VALIDATION" not in r.text:
                print(f"  [HIT] GET {ep}")
                print(f"  Body: {r.text[:800]}")
                break

        # Try POST for operators
        print("\n--- POST operators ---")
        for payload in [{"category": "mobile"}, {"type": "prepaid"}, {"category": "recharge"}]:
            r = await client.post(f"{BASE}/static/data/operators", headers=auth_headers, json=payload)
            if r.status_code == 200 and "E_VALIDATION" not in r.text:
                print(f"  [HIT] payload={payload}")
                print(f"  Body: {r.text[:800]}")
                break
            else:
                print(f"  {payload} -> {r.text[:80]}")

if __name__ == "__main__":
    asyncio.run(run())
