from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import LinearRegression
import numpy as np

#we have logisctic regression only for maker taker model its better to use simple regression for the rest for simplicity and accuracy
class RegressionModel:
    def __init__(self):
        self.slippage_model = LinearRegression()
        self.fees_model = LinearRegression()
        self.impact_model = LinearRegression()
        self.maker_taker_model = LogisticRegression()
        self.synthetic_data()

#we use syntethic data to train the models, this is a custom function to generate synthetic data
    def synthetic_data(self):
        X = []
        y_slippage = []
        y_fees = []
        y_impact = []
        y_maker_taker = []

        for _ in range(100):
            spread = np.random.uniform(0.1, 1.0)
            size = np.random.uniform(10, 200)
            volatility = np.random.uniform(0.01, 0.05)
            fee_tier = np.random.uniform(0.0005, 0.002)

            X.append([spread, size, volatility, fee_tier])

            slippage =  np.random.normal(0, 0.01)
            fees = np.random.normal(0, 0.5)
            impact = np.random.normal(0, 0.01)
            maker_taker_label = np.random.choice([0, 1])  

            y_slippage.append(slippage)
            y_fees.append(fees)
            y_impact.append(impact)
            y_maker_taker.append(maker_taker_label)

        X = np.array(X)
        self.slippage_model.fit(X, y_slippage)
        self.fees_model.fit(X, y_fees)
        self.impact_model.fit(X, y_impact)
        self.maker_taker_model.fit(X, y_maker_taker)

#final prediction of the model - testing it
    def predict(self, spread, size, volatility, fee_tier):
        features = np.array([[spread, size, volatility, fee_tier]])

        slippage = self.slippage_model.predict(features)[0]
        fees = self.fees_model.predict(features)[0]
        impact = self.impact_model.predict(features)[0]
        
        maker_prob = self.maker_taker_model.predict_proba(features)[0][1]  # prob of class 1 (maker)
        taker_prob = 1 - maker_prob
        maker_pct = round(maker_prob, 2)
        taker_pct = round(taker_prob, 2)

        return round(slippage, 4), round(fees, 2), round(impact, 4), maker_pct, taker_pct

