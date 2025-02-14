import streamlit as st 
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt  
import yfinance as yf
import datetime

def get_data(ticker, period):
    stock = yf.Ticker(ticker)  # Assign the Ticker object here
    S = stock.history(period=period)["Close"].iloc[-1]  # Current stock price (last closing price)
    expirations = stock.options  # List of expiration dates
    selected_expiry = expirations[0]  # Take the first expiration date
    option_chain = stock.option_chain(selected_expiry)  # Get the option chain for the selected expiry
    strike_prices = option_chain.calls["strike"].values  # Call option strike prices
    
    # Find the closest strike price to a reference value (e.g., 5)
    K = min(strike_prices, key=lambda x: abs(x - 5))
    
    # Here, we need to define how you will get volatility (historical, implied, etc.)
    # For simplicity, let's assume we use the historical volatility of the stock
    historical_data = stock.history(period="1y")  # Fetch 1 year of historical data
    log_returns = np.log(historical_data["Close"] / historical_data["Close"].shift(1)).dropna()
    sigma = log_returns.std() * np.sqrt(252)  # Annualized standard deviation (volatility)
    
    expiry_date = datetime.datetime.strptime(selected_expiry, "%Y-%m-%d")
    today = datetime.datetime.today()
    T = (expiry_date - today).days / 365  # Time to maturity in years
    r = 0.05  # Risk-free rate (assumed constant)
    
    print(f"Stock Price (S): {S:.2f}")
    print(f"Strike Price (K): {K}")
    print(f"Time to Maturity (T): {T:.4f} years")
    print(f"Volatility (σ): {sigma:.4f}")
    print(f"Risk-Free Rate (r): {r:.2f}")

# Example usage
get_data("AAPL", "1mo")

