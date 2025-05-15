import asyncio
import websockets
import json
import time

url = "wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/BTC-USDT-SWAP"

async def connect():
    async with websockets.connect(url) as ws:
        print("connected")
        while True:
            try:
                raw_data = await ws.recv()
                timestamp = time.time()
                data = json.loads(raw_data)
                print(f"[{timestamp}] Top Bid: {data['bids'][0]} | Top Ask: {data['asks'][0]}")
            except Exception as e:
                print("Error:", e)

if __name__ == "__main__":
    asyncio.run(connect())
