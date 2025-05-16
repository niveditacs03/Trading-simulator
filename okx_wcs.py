import asyncio
import websockets
import json
import csv
import time
from orderbook_ws import OrderbookProcessor

obp = OrderbookProcessor()
url = "wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/BTC-USDT-SWAP"

# Open CSV in append mode and write header if new
csv_file = open("orderbook_data2.csv", "a", newline="")
csv_writer = csv.writer(csv_file)

# Write header once if file is empty
if csv_file.tell() == 0:
    csv_writer.writerow([
        "timestamp", "top_bid_price", "top_bid_qty",
        "top_ask_price", "top_ask_qty", "spread"
    ])

async def connect(processor):
    async with websockets.connect(url) as ws:
        print("connected")
        while True:
            try:
                raw_data = await ws.recv()
                data = json.loads(raw_data)

                # Extract data for CSV
                top_bid = data["bids"][0]  # [price, qty]
                top_ask = data["asks"][0]  # [price, qty]
                top_bid_price = float(top_bid[0])
                top_bid_qty = float(top_bid[1])
                top_ask_price = float(top_ask[0])
                top_ask_qty = float(top_ask[1])
                spread = top_ask_price - top_bid_price

                # Write a new row with current timestamp and orderbook info
                csv_writer.writerow([
                    time.time(),
                    top_bid_price,
                    top_bid_qty,
                    top_ask_price,
                    top_ask_qty,
                    spread
                ])
                csv_file.flush()  # flush after each write to save instantly

                processor.on_message(raw_data)  # feed data to processor

            except Exception as e:
                print("Error:", e)

if __name__ == "__main__":
    asyncio.run(connect(obp))
