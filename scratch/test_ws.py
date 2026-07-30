import asyncio
import websockets
import json

async def test_ws():
    uri = "ws://localhost:8000/ws/check-recharge"
    async with websockets.connect(uri) as ws:
        req = {
            "row_id": "test_123",
            "mobile": "7746815442",
            "operator": "Jio",
            "circle": "Madhya Pradesh"
        }
        await ws.send(json.dumps(req))
        
        while True:
            response = await ws.recv()
            data = json.loads(response)
            print("Received:", data)
            if data.get("status") == "complete":
                break

if __name__ == "__main__":
    asyncio.run(test_ws())
