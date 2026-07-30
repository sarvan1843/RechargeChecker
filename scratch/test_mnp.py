import httpx
import asyncio

async def test_paytm(mobile):
    url = "https://paytm.com/papi/v1/expresscart/verify/mobile/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(url + mobile, headers=headers)
            print("Paytm:", r.text[:200])
        except Exception as e:
            print("Paytm error:", e)

async def test_mobikwik(mobile):
    url = f"https://www.mobikwik.com/check-recharge/api/v1/app/getoperatorinfo?number={mobile}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(url, headers=headers)
            print("Mobikwik:", r.text[:200])
        except Exception as e:
            print("Mobikwik error:", e)

async def main():
    mobile = "6266258150"
    await test_paytm(mobile)
    await test_mobikwik(mobile)

if __name__ == "__main__":
    asyncio.run(main())
