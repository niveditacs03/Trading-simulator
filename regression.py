import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.utils import resample
import os

class RegressionModel:
    def __init__(self, csv_file="orderbook_data.csv"):
        self.csv_file = csv_file
        self.scaler = StandardScaler()
        self.maker_taker_model = LogisticRegression(class_weight='balanced', random_state=42)
        self.load_and_train()

    def load_and_train(self):
        df = pd.read_csv(self.csv_file)
        if not os.path.exists(self.csv_file):
             print("⚠️ File not found. Generating dummy training data.")
             df = pd.DataFrame({
                'spread': np.random.uniform(0, 0.1, 1000),
                'top_bid_qty': np.random.uniform(1, 100, 1000),
                'top_ask_qty': np.random.uniform(1, 100, 1000),
                'maker_label': np.random.choice([0, 1], 1000)
        })
        else:
            df = pd.read_csv(self.csv_file)
            print("CSV Columns:", df.columns.tolist())
            
        df["maker_label"] = np.random.choice([0, 1], size=len(df))
        features = ['spread', 'top_bid_qty', 'top_ask_qty']
        target = 'maker_label'

        # Select relevant features and target
        features = ['spread', 'top_bid_qty', 'top_ask_qty']
        target = 'maker_label'

        # Handle imbalance by upsampling the minority class
        df_maker = df[df[target] == 1]
        df_taker = df[df[target] == 0]

        if len(df_maker) < len(df_taker):
            df_maker = resample(df_maker, replace=True, n_samples=len(df_taker), random_state=42)
        else:
            df_taker = resample(df_taker, replace=True, n_samples=len(df_maker), random_state=42)

        df_balanced = pd.concat([df_maker, df_taker])

        X = df_balanced[features].values
        y = df_balanced[target].values

        # Standardize features
        X_scaled = self.scaler.fit_transform(X)

        # Train the model
        self.maker_taker_model.fit(X_scaled, y)

    def predict(self, spread, top_bid_qty, top_ask_qty):
        features = np.array([[spread, top_bid_qty, top_ask_qty]])
        features_scaled = self.scaler.transform(features)

        maker_prob = self.maker_taker_model.predict_proba(features_scaled)[0][1]
        taker_prob = 1 - maker_prob

        slippage = spread / (top_bid_qty + 1e-9)  # crude placeholder slippage estimate

        return round(slippage, 4), round(maker_prob, 2), round(taker_prob, 2)
