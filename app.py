import streamlit as st
import yfinance as yf
import datetime
import models.option_pricing as option_pricing
import models.greeks as greeks
import models.volatility as volatility

def get_data(ticker, option_type="call", period="1mo"):
    """
    Fetches financial data for a given stock ticker using Yahoo Finance (via yfinance).
    Retrieves the latest closing price, expiration dates for options, strike prices, volatility, and time to maturity.

    Parameters:
    ticker: The stock ticker symbol (e.g., "AAPL", "GOOG").
    option_type: The type of option to fetch ("call" or "put").
    period: The period of historical data (default: "1mo").

    Returns:
    A dictionary with:
      - "S": Latest closing price
      - "K": Closest strike price
      - "T": Time to maturity (years)
      - "sigma": Estimated volatility
      - "r": Fixed risk-free rate (0.05)
    """
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

    if option_type == "call":
        strike_prices = option_chain.calls["strike"].values
    else:
        strike_prices = option_chain.puts["strike"].values

    K = min(strike_prices, key=lambda x: abs(x - S))

    sigma = volatility.calculate_historical_volatility(ticker, period="1y")
    
    expiry_date = datetime.datetime.strptime(selected_expiry, "%Y-%m-%d")
    today = datetime.datetime.today()
    T = max((expiry_date - today).days / 365, 0)  
    r = 0.05  

    return {"S": S, "K": K, "T": T, "sigma": sigma, "r": r}

st.title("📈 Option Pricing Calculator")

data_source = st.radio("Select Data Source", ["Fetch from Yahoo Finance", "Enter Manually"])

if "data" not in st.session_state:
    st.session_state.data = None

if data_source == "Fetch from Yahoo Finance":
    ticker = st.text_input("Enter Stock Ticker:", "AAPL")
    option_type = st.radio("Select Option Type", ["Call", "Put"])

    if st.button("Fetch Data"):
        data = get_data(ticker, option_type.lower())  # Pass option type
        if data:
            st.session_state.data = data  
            st.success(f"Data retrieved successfully for {option_type} option!")

            st.subheader(f"📊 Fetched Data for {option_type} Option")
            st.table({
                "Metric": ["Stock Price (S)", "Closest Strike Price (K)", "Time to Maturity (T)", "Volatility (σ)", "Risk-Free Rate (r)"],
                "Value": [f"${data['S']:.2f}", f"${data['K']:.2f}", f"{data['T']:.4f} years", f"{data['sigma']:.4f}", f"{data['r']:.2f}"]
            })

            # Calculate Greeks for selected option type
            st.session_state.greeks = greeks.calculate_greeks(
                data['S'], data['K'], data['T'], data['r'], data['sigma'], option_type.lower()
            )

            st.subheader(f"📉 Greeks for {option_type} Option")
            st.table({
                "Greek": ["Delta", "Gamma", "Theta", "Vega", "Rho"],
                "Value": [f"{st.session_state.greeks['delta']:.4f}", f"{st.session_state.greeks['gamma']:.4f}", 
                          f"{st.session_state.greeks['theta']:.4f}", f"{st.session_state.greeks['vega']:.4f}", 
                          f"{st.session_state.greeks['rho']:.4f}"]
            })
        else:
            st.error("Failed to retrieve data from Yahoo Finance.")

else:
    st.subheader("🔢 Enter Option Parameters Manually")
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

    # Calculate option price
    if model == "Black-Scholes":
        price = option_pricing.black_scholes(S, K, T, r, sigma, option_type.lower())
    elif model == "Binomial Tree":
        price = option_pricing.binomial_tree(S, K, T, r, sigma, N=100, option_type=option_type.lower())
    elif model == "Monte Carlo":
        price = option_pricing.monte_carlo(S, K, T, r, sigma, simulations=10000, option_type=option_type.lower())

    # Display price result in a table
    st.subheader("💰 Option Price Result")
    st.table({
        "Model": [model],
        "Option Type": [option_type],
        "Price": [f"${price:.2f}"]
    })
