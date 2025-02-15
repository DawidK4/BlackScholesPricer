import streamlit as st 
import numpy as np
import yfinance as yf
import datetime
import models  

def get_data(ticker, period="1mo"):
    stock = yf.Ticker(ticker)

    # Fetch latest closing price
    history = stock.history(period=period)
    if history.empty:
        st.error(f"No stock price data found for {ticker}.")
        return None

    S = history["Close"].iloc[-1]  # Last closing price

    # Fetch option expiration dates
    expirations = stock.options
    if not expirations:
        st.error(f"No options data found for {ticker}.")
        return None
    
    selected_expiry = expirations[0]  # Take the nearest expiry date
    option_chain = stock.option_chain(selected_expiry)

    # Get call option strike prices
    strike_prices = option_chain.calls["strike"].values
    
    # Find the closest strike price to current stock price
    K = min(strike_prices, key=lambda x: abs(x - S))

    # Estimate volatility using historical log returns
    historical_data = stock.history(period="1y")
    if historical_data.empty:
        st.error(f"Not enough historical data for volatility calculation.")
        return None
    
    log_returns = np.log(historical_data["Close"] / historical_data["Close"].shift(1)).dropna()
    sigma = log_returns.std() * np.sqrt(252)  # Annualized standard deviation
    
    # Calculate time to maturity
    expiry_date = datetime.datetime.strptime(selected_expiry, "%Y-%m-%d")
    today = datetime.datetime.today()
    T = max((expiry_date - today).days / 365, 0)  # Prevent negative values
    
    # Risk-free rate (assumed constant)
    r = 0.05  

    return {"S": S, "K": K, "T": T, "sigma": sigma, "r": r}

st.title("📈 Option Pricing Calculator")

data_source = st.radio("Select Data Source", ["Fetch from Yahoo Finance", "Enter Manually"])

if data_source == "Fetch from Yahoo Finance":
    ticker = st.text_input("Enter Stock Ticker:", "AAPL")
    if st.button("Fetch Data"):
        data = get_data(ticker)
        if data:
            st.success("Data retrieved successfully!")
            st.write(f"**Stock Price (S):** ${data['S']:.2f}")
            st.write(f"**Closest Strike Price (K):** ${data['K']:.2f}")
            st.write(f"**Time to Maturity (T):** {data['T']:.4f} years")
            st.write(f"**Volatility (σ):** {data['sigma']:.4f}")
            st.write(f"**Risk-Free Rate (r):** {data['r']:.2f}")
else:
    st.subheader("Enter Your Own Data")
    S = st.number_input("Stock Price (S)", value=100.0)
    K = st.number_input("Strike Price (K)", value=100.0)
    T = st.number_input("Time to Maturity (T, in years)", value=1.0, format="%.4f")
    r = st.number_input("Risk-Free Rate (r)", value=0.05, format="%.2f")
    sigma = st.number_input("Volatility (σ)", value=0.2, format="%.4f")

model = st.selectbox("Choose Pricing Model", ["Black-Scholes", "Binomial Tree", "Monte Carlo"])

option_type = st.radio("Option Type", ["Call", "Put"])

# Compute price based on model
if st.button("Calculate Price"):
    # Use fetched data if available
    if data_source == "Fetch from Yahoo Finance" and 'data' in locals() and data:
        S, K, T, r, sigma = data["S"], data["K"], data["T"], data["r"], data["sigma"]

    if model == "Black-Scholes":
        price = models.black_scholes(S, K, T, r, sigma, option_type.lower())
    elif model == "Binomial Tree":
        price = models.binomial_tree(S, K, T, r, sigma, N=100, option_type=option_type.lower())
    elif model == "Monte Carlo":
        price = models.monte_carlo(S, K, T, r, sigma, simulations=10000, option_type=option_type.lower())

    st.success(f"💰 **{model} Option Price:** ${price:.2f}")
