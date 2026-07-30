import asyncio
import httpx

MOBILE_NUMBERS = ["7869632727", "6266258150", "9589847274"]
BASE = "https://v1.pro.rechargemojo.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
    "Content-Type": "application/json",
}

async def run():
    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        r = await client.post(f"{BASE}/auth/create-guest-token", headers=HEADERS)
        token = r.json().get("token")
        auth_headers = {**HEADERS, "Authorization": f"Bearer {token}"}
        
        for mobile in MOBILE_NUMBERS:
            r = await client.post(
                f"{BASE}/static/data/mnp_detect_number",
                headers=auth_headers,
                json={"mobile": mobile}
            )
            data = r.json()
            print(f"{mobile}: {data.get('data')}")

if __name__ == "__main__":
    asyncio.run(run())
