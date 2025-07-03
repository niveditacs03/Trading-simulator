## Trade Simulator - Orderbook Analysis Tool


## Overview
This project provides a real-time orderbook analysis tool that calculates trading costs (slippage, fees, market impact) for large orders. It connects to OKX's WebSocket API to receive live orderbook data and uses machine learning models to predict execution quality metrics.

## Features
Real-time Orderbook Visualization: Displays top bid/ask prices and quantities

## Cost Prediction Models:

- Regression model for slippage estimation
- Logistic regression for maker/taker probability
- Almgren-Chriss model for market impact

## Customizable Parameters:
- Order quantity
- Asset selection (BTC, ETH, SOL futures)
- Volatility assumption
- Maker/taker fee structure
- Latency monitoring
- Spread tracking
- Net cost breakdown

## Installation
Clone the repository:
```
git clone https://github.com/yourusername/trade-simulator.git
cd trade-simulator
```
## Usage
Run the application:


```
python simulator_ui.py
```
## The UI provides:
- Left panel: Parameter configuration
- Right panel: Real-time metrics display
- Automatic updates every second

## Technical Components
- Core Modules
- WebSocket Client (okx_wcs.py)
- Maintains connection to OKX's orderbook WebSocket (not currently)
- Processes incoming messages with minimal latency

- Orderbook Processor (orderbook_ws.py)

- Calculates key metrics (spread, top of book)

- Integrates machine learning models

- Maintains trading cost calculations

-  Machine Learning Models

- RegressionModel: Predicts slippage and execution probabilities

- AlmgredChriss: Estimates market impact for large orders

- UI Application (simulator_ui.py)

- Tkinter-based interface

- Real-time metrics display

## Parameter configuration

- Configuration
Edit config.json to customize:

- WebSocket endpoint

- Default parameters

## Model settings

Requirements
- Python 3.8+
Packages:

- websockets
- numpy
- pandas
- scikit-learn
- tkinter

