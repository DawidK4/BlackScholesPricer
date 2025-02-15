import streamlit as st
import yfinance as yf
import datetime
import models.option_pricing as option_pricing
import models.greeks as greeks
import models.volatility as volatility

'''
This function fetches financial data for a given stock ticker using Yahoo Finance (via yfinance). 
It retrieves the latest closing price, expiration dates for options, strike prices, volatility, and time to maturity.

Parameters:
ticker: The stock ticker symbol (e.g., "AAPL", "GOOG") for which data is fetched.
period: The period of historical data (default is "1mo", but can be adjusted to other values like "1y", "6mo", etc.).

Returns:
A dictionary containing:
"S": The latest closing price of the stock.
"K": The closest strike price to the current stock price.
"T": The time to maturity of the nearest option in years.
"sigma": The estimated volatility of the stock using historical data.
"r": A fixed risk-free rate (defaulted to 0.05 or 5%).
'''
def get_data(ticker, period="1mo"):
    stock = yf.Ticker(ticker)

    history = stock.history(period=period)
    if history.empty:
        st.error(f"No stock price data found for {ticker}.")
        return None

    S = history["Close"].iloc[-1]  

    expirations = stock.options
    if not expirations:
        st.error(f"No options data found for {ticker}.")
        return None
    
    selected_expiry = expirations[0]  
    option_chain = stock.option_chain(selected_expiry)

    strike_prices = option_chain.calls["strike"].values
    
    K = min(strike_prices, key=lambda x: abs(x - S))

    sigma = volatility.calculate_historical_volatility(ticker, period="1y")
    
    expiry_date = datetime.datetime.strptime(selected_expiry, "%Y-%m-%d")
    today = datetime.datetime.today()
    T = max((expiry_date - today).days / 365, 0)  
    
    # Risk-free rate (assumed constant)
    r = 0.05  

    return {"S": S, "K": K, "T": T, "sigma": sigma, "r": r}

st.title("📈 Option Pricing Calculator")

data_source = st.radio("Select Data Source", ["Fetch from Yahoo Finance", "Enter Manually"])

if "data" not in st.session_state:
    st.session_state.data = None

if data_source == "Fetch from Yahoo Finance":
    ticker = st.text_input("Enter Stock Ticker:", "AAPL")
    if st.button("Fetch Data"):
        data = get_data(ticker)
        if data:
            st.session_state.data = data  
            st.success("Data retrieved successfully!")
            st.write(f"**Stock Price (S):** ${data['S']:.2f}")
            st.write(f"**Closest Strike Price (K):** ${data['K']:.2f}")
            st.write(f"**Time to Maturity (T):** {data['T']:.4f} years")
            st.write(f"**Volatility (σ):** {data['sigma']:.4f}")
            st.write(f"**Risk-Free Rate (r):** {data['r']:.2f}")

            # Store Greeks data
            if "greeks" not in st.session_state:
                greeks = greeks.calculate_greeks(data['S'], data['K'], data['T'], data['r'], data['sigma'], option_type="call")
                st.session_state.greeks = greeks

            st.write("**Greeks for Call Option:**")
            st.write(f"**Delta:** {st.session_state.greeks['delta']:.4f}")
            st.write(f"**Gamma:** {st.session_state.greeks['gamma']:.4f}")
            st.write(f"**Theta:** {st.session_state.greeks['theta']:.4f}")
            st.write(f"**Vega:** {st.session_state.greeks['vega']:.4f}")
            st.write(f"**Rho:** {st.session_state.greeks['rho']:.4f}")
        else:
            st.error("Failed to retrieve data from Yahoo Finance.")
else:
    S = st.number_input("Stock Price (S)", value=100.0, key="S_input") 
    K = st.number_input("Strike Price (K)", value=100.0, key="K_input")  
    T = st.number_input("Time to Maturity (T, in years)", value=1.0, format="%.4f", key="T_input")  
    r = st.number_input("Risk-Free Rate (r)", value=0.05, format="%.2f", key="r_input") 
    sigma = st.number_input("Volatility (σ)", value=0.2, format="%.4f", key="sigma_input")  

model = st.selectbox("Choose Pricing Model", ["Black-Scholes", "Binomial Tree", "Monte Carlo"])

option_type = st.radio("Option Type", ["Call", "Put"])

if st.button("Calculate Price"):
    if data_source == "Fetch from Yahoo Finance" and st.session_state.data:
        data = st.session_state.data  
        S, K, T, r, sigma = data["S"], data["K"], data["T"], data["r"], data["sigma"]
    else:
        S = st.session_state.get("S_input", 100.0)
        K = st.session_state.get("K_input", 100.0)
        T = st.session_state.get("T_input", 1.0)
        r = st.session_state.get("r_input", 0.05)
        sigma = st.session_state.get("sigma_input", 0.2)

    if model == "Black-Scholes":
        price = option_pricing.black_scholes(S, K, T, r, sigma, option_type.lower())
    elif model == "Binomial Tree":
        price = option_pricing.binomial_tree(S, K, T, r, sigma, N=100, option_type=option_type.lower())
    elif model == "Monte Carlo":
        price = option_pricing.monte_carlo(S, K, T, r, sigma, simulations=10000, option_type=option_type.lower())

    st.success(f"💰 **{model} Option Price:** ${price:.2f}")
