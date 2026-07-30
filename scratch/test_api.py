import asyncio
import httpx

async def main():
    async with httpx.AsyncClient(timeout=30) as client:
        req = {
            "mobile": "7746815442",
            "operatorName": "Jio",
            "circle": "Madhya Pradesh"
        }
        res = await client.post("http://localhost:8000/check-recharge", json=req)
        print("Result:", res.json())

if __name__ == "__main__":
    asyncio.run(main())
