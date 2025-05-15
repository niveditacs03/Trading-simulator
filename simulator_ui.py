import tkinter as tk
from orderbook_ws import OrderbookProcessor

class TradeSimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GoQuant Trade Simulator")

        frame_left = tk.Frame(root)
        frame_left.pack(side=tk.LEFT, padx=10, pady=10)

        tk.Label(frame_left, text="Symbol:").pack()
        self.symbol_entry = tk.Entry(frame_left)
        self.symbol_entry.insert(0, "BTC-USDT-SWAP")
        self.symbol_entry.pack()

        tk.Label(frame_left, text="Order Qty ($):").pack()
        self.qty_entry = tk.Entry(frame_left)
        self.qty_entry.insert(0, "30")
        self.qty_entry.pack()

        self.predict_button = tk.Button(frame_left, text="Predict Maker/Taker", command=self.update_metrics)
        self.predict_button.pack(pady=5)

        self.proportion_label = tk.Label(frame_left, text="Maker: 0%, Taker: 0%")
        self.proportion_label.pack()

        frame_right = tk.Frame(root)
        frame_right.pack(side=tk.LEFT, padx=10, pady=10)

        self.text = tk.Text(frame_right, width=40, height=15)
        self.text.pack()

        self.obp = OrderbookProcessor(symbol=self.symbol_entry.get())
        self.obp.start()
        self.update_loop()

    def update_metrics(self):
        metrics = self.obp.get_metrics()
        self.text.delete("1.0", tk.END)
        for k, v in metrics.items():
            self.text.insert(tk.END, f"{k}: {v}\n")

        maker, taker = self.obp.predict_maker_taker()
        self.proportion_label.config(text=f"Maker: {maker}%, Taker: {taker}%")

    def update_loop(self):
        self.update_metrics()
        self.root.after(1000, self.update_loop)  

if __name__ == "__main__":
    root = tk.Tk()
    app = TradeSimulatorApp(root)
    root.mainloop()
