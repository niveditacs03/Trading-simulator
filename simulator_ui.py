import tkinter as tk
from tkinter import ttk
from orderbook_ws import OrderbookProcessor
import asyncio
import threading
from okx_wcs import connect

class UI:
    def __init__(self, root):
        self.root = root
        self.root.title("Orderbook Simulator with Regression")
        self.root.geometry("700x700")

        self.obp = OrderbookProcessor()
        self.left_frame = ttk.Frame(root, padding=10)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.right_frame = ttk.Frame(root, padding=10)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
     
        # left panel
        ttk.Label(self.left_frame, text="Parameters", font=("Arial", 14, "bold")).pack(pady=(0,10))
       
       #exchange
        ttk.Label(self.left_frame, text="Exchange:").pack(anchor="w")
        self.exchange_var = tk.StringVar(value="OKX")
        self.exchange_combo = ttk.Combobox(self.left_frame, textvariable=self.exchange_var, state="readonly")
        self.exchange_combo['values'] = ["OKX"]  
        self.exchange_combo.pack(fill=tk.X, pady=5)

        #spot assest
        ttk.Label(self.left_frame, text="Spot Asset:").pack(anchor="w")
        self.asset_var = tk.StringVar(value="BTC-USDT-SWAP")
        self.asset_combo = ttk.Combobox(self.left_frame, textvariable=self.asset_var, state="readonly")
        self.asset_combo['values'] = ["BTC-USDT-SWAP", "ETH-USDT-SWAP", "SOL-USDT-SWAP"]  
        self.asset_combo.pack(fill=tk.X, pady=5)

        #order type    
        ttk.Label(self.left_frame, text="Order Type:").pack(anchor="w")
        self.order_type_var = tk.StringVar(value="market")
        self.order_type_combo = ttk.Combobox(self.left_frame, textvariable=self.order_type_var, state="readonly")
        self.order_type_combo['values'] = ["market"]  
        self.order_type_combo.pack(fill=tk.X, pady=5)
        
        #order qnty
        ttk.Label(self.left_frame, text="Order Quantity:").pack(anchor="w")
        self.qty_entry = ttk.Entry(self.left_frame)
        self.qty_entry.insert(0, "100")
        self.qty_entry.pack(fill=tk.X, pady=5)

        #volaitily
        ttk.Label(self.left_frame, text="Volatility:").pack(anchor="w")
        self.volatility_entry = ttk.Entry(self.left_frame)
        self.volatility_entry.insert(0, "0.02")
        self.volatility_entry.pack(fill=tk.X, pady=5)
       # maker fee
        ttk.Label(self.left_frame, text="Maker fee (decimal):").pack(anchor="w")
        self.maker_fee_entry = ttk.Entry(self.left_frame)
        self.maker_fee_entry.insert(0, "0.001")
        self.maker_fee_entry.pack(fill=tk.X, pady=5)

        # taker fee
        ttk.Label(self.left_frame, text="Taker fee (decimal):").pack(anchor="w")
        self.taker_fee_entry = ttk.Entry(self.left_frame)
        self.taker_fee_entry.insert(0, "0.001")
        self.taker_fee_entry.pack(fill=tk.X, pady=5)

        self.update_button = ttk.Button(self.left_frame, text="Refresh", command=self.update_metrics)
        self.update_button.pack(pady=20)

        # right panel
        ttk.Label(self.right_frame, text="Live Orderbook Metrics", font=("Arial", 14, "bold")).pack(pady=(0,10))

        self.metrics_text = tk.Text(self.right_frame, width=40, height=18, state=tk.DISABLED, font=("Courier", 11))
        self.metrics_text.pack(fill=tk.BOTH, expand=True)

        self.proportion_label = ttk.Label(self.right_frame, text="Maker: 0%, Taker: 0%", font=("Arial", 12, "italic"))
        self.proportion_label.pack(pady=10)

        # separate thread to not block Tkinter mainloop
        threading.Thread(target=lambda: asyncio.run(connect(self.obp)), daemon=True).start()
        
        #update ui
        self.root.after(1, self.refresh_ui)

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
        self.obp.update_params(order_qty=order_qty, volatility=volatility, maker_fee=maker_fee,taker_fee=taker_fee)
        self.refresh_ui()

#function to refresh ui after every second with the updated values
    def refresh_ui(self):
        metrics = self.obp.get_metrics()
        self.metrics_text.config(state=tk.NORMAL)
        self.metrics_text.delete("1.0", tk.END)

        for key, value in metrics.items():
            self.metrics_text.insert(tk.END, f"{key:15}: {value}\n")

        self.metrics_text.config(state=tk.DISABLED)

        self.proportion_label.config(text=f"Maker: {metrics.get('Maker %', 0)}%, Taker: {metrics.get('Taker %', 0)}%")
        self.root.after(1, self.refresh_ui)

if __name__ == "__main__":
    root = tk.Tk()
    app = UI(root)
    root.mainloop()

