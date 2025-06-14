import json
import time
import random

from Almgred import AlmgredChriss
from regression import RegressionModel

class OrderbookProcessor:
    def __init__(self):
        self.latest_tick = None
        self.last_latency = None

        self.ac_model = AlmgredChriss()
        self.reg_model = RegressionModel()

        self.order_qty = random.uniform(10, 2000)
        self.volatility = 0.02
        self.maker_fee = 0.001
        self.taker_fee = 0.001

        self.slippage = 0.0
        self.fees = 0.0
        self.market_impact = 0.0
        self.maker = 0.0
        self.taker = 0.0
        self.net_cost = 0.0

    def on_message(self, message):
        start_time = time.time()
        data = json.loads(message)
        self.latest_tick = data

        spread = float(data["asks"][0][0]) - float(data["bids"][0][0])
        top_bid_qty = float(data["bids"][0][1])
        top_ask_qty = float(data["asks"][0][1])
        size = self.order_qty
        volatility = self.volatility
        # regression model predictions
        slippage, maker_pct, taker_pct = self.reg_model.predict(
            spread, top_bid_qty=top_bid_qty,top_ask_qty=top_ask_qty
        )
        # market impact via Almgren-Chriss
        mid_price = (float(data["asks"][0][0]) + float(data["bids"][0][0])) / 2
        impact = self.ac_model.estimate_impact(
            order_qty=self.order_qty,
            mid_price=mid_price,
            volatility=self.volatility
        )
        impact = round(impact, 4)

        # fee calculation
        maker_fee_cost = self.maker_fee * maker_pct * size
        taker_fee_cost = self.taker_fee * taker_pct * size
        total_fees = round(maker_fee_cost + taker_fee_cost, 4)

        self.slippage = round(slippage, 4)
        self.fees = total_fees
        self.market_impact = impact
        self.maker = round(maker_pct * 100, 2)
        self.taker = round(taker_pct * 100, 2)
        self.net_cost = round(slippage + total_fees, 4)

        self.last_latency = round((time.time() - start_time) * 1000, 8)

    def get_metrics(self):
        if not self.latest_tick:
            return {}

        return {
            "Last Latency (ms)": self.last_latency,
            "Top Bid": self.latest_tick["bids"][0],
            "Top Ask": self.latest_tick["asks"][0],
            "Spread": round(float(self.latest_tick["asks"][0][0]) - float(self.latest_tick["bids"][0][0]), 4),
            "Volatility": self.volatility,
            "Maker Fee": self.maker_fee,
            "Taker Fee": self.taker_fee,
            "Slippage": self.slippage,
            "Fees": self.fees,
            "Market Impact": self.market_impact,
            "Maker %": self.maker,
            "Taker %": self.taker,
            "Net Cost": self.net_cost,
        }

    def update_params(self, order_qty=None, volatility=None, maker_fee=None, taker_fee=None, **kwargs):
        if order_qty is not None:
            self.order_qty = order_qty
        if volatility is not None:
            self.volatility = volatility
        if maker_fee is not None:
            self.maker_fee = maker_fee
        if taker_fee is not None:
            self.taker_fee = taker_fee

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
            maker_fee = float(self.maker_fee_entry.get())
        except:
            maker_fee = 0.001
        try:
            taker_fee = float(self.taker_fee_entry.get())
        except:
            taker_fee = 0.001

        exchange = self.exchange_var.get()
        asset = self.asset_var.get()
        order_type = self.order_type_var.get()

        self.update_params(order_qty=order_qty, volatility=volatility, maker_fee=maker_fee, taker_fee=taker_fee)
        self.refresh_ui()
