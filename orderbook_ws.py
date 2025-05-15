import websocket
import threading
import json
import time
import numpy as np
import random

class OrderbookProcessor:
    def __init__(self, symbol="BTC-USDT-SWAP"):
        self.url = f"wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/{symbol}"
        self.ws = None
        self.running = False
        self.latest_tick = None
        self.last_latency = None

    def on_message(self, ws, message):
        start_time = time.time()

        data = json.loads(message)
        self.latest_tick = data

        total_qty = random.uniform(10, 250)  # USD
        ask_levels = [(float(p), float(q)) for p, q in data["asks"]]

        # Market Impact via Almgren-Chriss
        X = total_qty
        T = 1
        gamma = 0.0005
        eta = 0.002
        impact = gamma * X + eta * (X / T)
        self.market_impact = round(impact, 4)

        filled_value = 0  # total usd spent
        filled_qty = 0    # total quantity bought

        for price, qty in ask_levels:
            level_value = price * qty
            if filled_value + level_value >= total_qty:
                needed_qty = (total_qty - filled_value) / price
                filled_qty += needed_qty
                filled_value += needed_qty * price
                break
            else:
                filled_qty += qty
                filled_value += level_value

        avg_price = filled_value / filled_qty if filled_qty > 0 else 0
        best_ask = float(data["asks"][0][0])
        slippage = avg_price - best_ask

        taker_fee_rate = 0.001  # 0.1%
        fees = total_qty * taker_fee_rate

        self.last_latency = round((time.time() - start_time) * 1000, 2)

        self.slippage = round(slippage, 4)
        self.fees = round(fees, 2)
        self.net_cost = round(slippage + fees, 4)
        self.market_impact = round(slippage * 0.7, 4)  # you can adjust this formula later


    def on_open(self, ws):
        print("[WS] Connected.")

    def on_error(self, ws, error):
        print(f"[WS] Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("[WS] Closed.")

    def run(self):
        self.ws = websocket.WebSocketApp(
            self.url,
            on_message=self.on_message,
            on_open=self.on_open,
            on_close=self.on_close,
            on_error=self.on_error
        )
        self.running = True
        self.ws.run_forever()

    def start(self):
        threading.Thread(target=self.run, daemon=True).start()

    def get_metrics(self):
        if self.latest_tick is None:
            return {"Status": "Waiting for data..."}

        maker, taker = self.predict_maker_taker()
        return {
            "Expected Slippage": f"{self.slippage} USD",
            "Expected Fees": f"{self.fees} USD",
            "Net Cost": f"{self.net_cost} USD",
            "Expected Market Impact": f"{self.market_impact} USD",
            "Internal Latency": f"{self.last_latency} ms",
            "Maker/Taker Proportion": f"{maker}% / {taker}%"
        }
    
    def predict_maker_taker(self):
        if self.latest_tick is None:
            return 0.0, 0.0 
        
        spread = float(self.latest_tick["asks"][0][0]) - float(self.latest_tick["bids"][0][0])
        size = random.uniform(10,200)  
        volatility = 0.02  # hardcoded for now

        # logistic
        weights = np.array([0.5, -0.1, 0.3])  # dummy weights
        features = np.array([spread, size, volatility])
        bias = -2

        z = np.dot(weights, features) + bias
        prob_taker = 1 / (1 + np.exp(-z))
        prob_maker = 1 - prob_taker

        return round(prob_maker * 100, 2), round(prob_taker * 100, 2)

if __name__ == "__main__":
    obp = OrderbookProcessor()
    obp.start()

    # Display metrics every 2 seconds
    try:
        while True:
            time.sleep(2)
            metrics = obp.get_metrics()
            print("\n=== Live Metrics ===")
            for k, v in metrics.items():
                print(f"{k}: {v}")
    except KeyboardInterrupt:
        print("Stopped.")
