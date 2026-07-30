import httpx
import asyncio

async def test():
    print("Testing Non-Jio Number: 8103557998")
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            res1 = await client.post("http://localhost:8000/check-recharge", json={
                "mobile": "8103557998",
                "operatorName": "Jio",
                "circle": "Madhya Pradesh"
            })
            print("Result 1:", res1.json())
    except Exception as e:
        print("Error 1:", e)

    print("\nTesting Jio Number: 7869632727")
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            res2 = await client.post("http://localhost:8000/check-recharge", json={
                "mobile": "7869632727",
                "operatorName": "Jio",
                "circle": "Madhya Pradesh"
            })
            print("Result 2:", res2.json())
    except Exception as e:
        print("Error 2:", e)

if __name__ == "__main__":
    asyncio.run(test())
