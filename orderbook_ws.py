import asyncio
import websockets
import json
import time
import random

from Almgred import AlmgredChriss
from regression import RegressionModel

class OrderbookProcessor:
    def __init__(self):
        self.url = f"wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/BTC-USDT-SWAP"
        self.ws = None
        self.running = False
        self.latest_tick = None
        self.last_latency = None
        self.ac_model=AlmgredChriss()
     
        self.order_qty = random.uniform(10,2000)
        self.volatility = 0.02
        self.fee_tier = 0.001 
        
        self.reg_model = RegressionModel()

        self.slippage = 0.0
        self.fees = 0.0
        self.market_impact = 0.0
        self.maker = 0.0
        self.taker = 0.0
        self.net_cost = 0.0

    async def connect(self):
        async with websockets.connect(self.url) as ws:
            self.ws = ws
            print(f"Connected to L2 Orderbook WebSocket")
            self.running = True
            while self.running:
                try:
                    raw_data = await ws.recv()
                    self.on_message(raw_data)
                except Exception as e:
                    print("WebSocket error:", e)
                    self.running = False


    def on_message(self, message):
        start_time = time.time()
        data = json.loads(message)
        self.latest_tick = data

        #features for regression
        spread = float(data["asks"][0][0]) - float(data["bids"][0][0])
        size = self.order_qty
        volatility = self.volatility
        fee_tier = self.fee_tier

        slippage, fees, _, maker, taker = self.reg_model.predict(spread, size, volatility, fee_tier)
       
        mid_price = (float(data["asks"][0][0]) + float(data["bids"][0][0])) / 2
        impact = self.ac_model.estimate_impact( order_qty=self.order_qty,mid_price=mid_price,volatility=self.volatility)
        impact=round(impact,4)
        
        self.slippage = slippage
        self.fees = fees
        self.market_impact = impact
        self.maker = maker
        self.taker = taker
        self.net_cost = round(slippage + fees, 4)

        self.last_latency = round((time.time() - start_time) * 1000, 8) #latency

    def get_metrics(self):
        if not self.latest_tick:
            return {}

        return {
            "Last Latency (ms)": self.last_latency,
            "Top Bid": self.latest_tick["bids"][0],
            "Top Ask": self.latest_tick["asks"][0],
            "Spread": round(float(self.latest_tick["asks"][0][0]) - float(self.latest_tick["bids"][0][0]), 4),
            "Volatility": self.volatility,
            "Fee Tier": self.fee_tier,
            "Slippage": self.slippage,
            "Fees": self.fees,
            "Market Impact": self.market_impact,
            "Maker %": self.maker,
            "Taker %": self.taker,
            "Net Cost": self.net_cost,
        }
        
    
    def update_params(self, order_qty=None, volatility=None, fee_tier=None, exchange=None, asset=None, order_type=None):
        if order_qty is not None:
            self.order_qty = order_qty
        if volatility is not None:
            self.volatility = volatility
        if fee_tier is not None:
            self.fee_tier = fee_tier
        if exchange is not None:
            self.exchange = exchange
        if asset is not None:
            self.asset = asset
        if order_type is not None:
            self.order_type = order_type

    def update_metrics(self):
        try:
            order_qty = float(self.qty_entry.get())
        except:
            order_qty = 100
        try:
            volatility = float(self.volatility_entry.get())
        except:
            volatility = 0.02

        try:
            fee_tier = float(self.fee_tier_entry.get())
        except:
            fee_tier = 0.001

        exchange = self.exchange_var.get()
        asset = self.asset_var.get()
        order_type = self.order_type_var.get()

        # refresh
        self.obp.update_params(order_qty=order_qty, volatility=volatility, fee_tier=fee_tier,
                            exchange=exchange, asset=asset, order_type=order_type)
        self.refresh_ui()


if __name__ == "__main__":
    obp = OrderbookProcessor()
    asyncio.run(obp.connect())
