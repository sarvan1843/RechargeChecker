import asyncio
import json
import websockets

async def test():
    uri = "ws://localhost:8000/ws/check-recharge"
    print(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected! Sending check request for mobile 7869632727...")
            payload = {
                "row_id": "test_row_123",
                "mobile": "7869632727",
                "operator": "Jio",
                "circle": "Madhya Pradesh"
            }
            await websocket.send(json.dumps(payload))
            
            print("Listening for streamed progress updates...")
            async for message in websocket:
                data = json.loads(message)
                print(f"WS EVENT: {data}")
                if data.get("status") == "complete":
                    print("\nVerification process finished successfully!")
                    break
    except Exception as e:
        print(f"WebSocket test execution error: {e}")

if __name__ == "__main__":
    asyncio.run(test())
