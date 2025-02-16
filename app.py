import streamlit as st
import yfinance as yf
import datetime
import models.option_pricing as option_pricing
import models.greeks as greeks
import models.volatility as volatility

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
    r = 0.05  

    return {"S": S, "K": K, "T": T, "sigma": sigma, "r": r}

st.title("📈 Option Pricing Calculator")

# Initialize session state variables
if "data" not in st.session_state:
    st.session_state.data = None
if "greeks" not in st.session_state:
    st.session_state.greeks = None
if "option_price" not in st.session_state:
    st.session_state.option_price = None

# Create two tabs
tab_yfinance, tab_manual = st.tabs(["📡 Fetch from Yahoo Finance", "✍️ Enter Manually"])

with tab_yfinance:
    st.subheader("Fetch Option Data from Yahoo Finance")
    ticker = st.text_input("Enter Stock Ticker:", "AAPL")
    
    if st.button("Fetch Data"):
        data = get_data(ticker)
        if data:
            st.session_state.data = data  
            st.success("Data retrieved successfully!")

            # Calculate Greeks immediately so they persist visually
            st.session_state.greeks = greeks.calculate_greeks(
                data['S'], data['K'], data['T'], data['r'], data['sigma'], option_type="call"
            )

    # Display fetched data
    if st.session_state.data:
        st.subheader("📊 Fetched Data")
        data = st.session_state.data
        st.table({
            "Metric": ["Stock Price (S)", "Closest Strike Price (K)", "Time to Maturity (T)", "Volatility (σ)", "Risk-Free Rate (r)"],
            "Value": [f"${data['S']:.2f}", f"${data['K']:.2f}", f"{data['T']:.4f} years", f"{data['sigma']:.4f}", f"{data['r']:.2f}"]
        })

        st.subheader("📉 Greeks for Call Option")
        st.table({
            "Greek": ["Delta", "Gamma", "Theta", "Vega", "Rho"],
            "Value": [f"{st.session_state.greeks['delta']:.4f}", f"{st.session_state.greeks['gamma']:.4f}", 
                      f"{st.session_state.greeks['theta']:.4f}", f"{st.session_state.greeks['vega']:.4f}", 
                      f"{st.session_state.greeks['rho']:.4f}"]
        })

with tab_manual:
    st.subheader("Manually Enter Option Parameters")
    S = st.number_input("Stock Price (S)", value=100.0, key="S_input") 
    K = st.number_input("Strike Price (K)", value=100.0, key="K_input")  
    T = st.number_input("Time to Maturity (T, in years)", value=1.0, format="%.4f", key="T_input")  
    r = st.number_input("Risk-Free Rate (r)", value=0.05, format="%.2f", key="r_input") 
    sigma = st.number_input("Volatility (σ)", value=0.2, format="%.4f", key="sigma_input")  

# Common section for calculating option price
st.subheader("📊 Calculate Option Price")
model = st.selectbox("Choose Pricing Model", ["Black-Scholes", "Binomial Tree", "Monte Carlo"])
option_type = st.radio("Option Type", ["Call", "Put"])

if st.button("Calculate Price"):
    if st.session_state.data:
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

    st.session_state.option_price = {"Model": model, "Option Type": option_type, "Price": price}

# Always display option price if calculated
if st.session_state.option_price:
    st.subheader("💰 Option Price Result")
    result = st.session_state.option_price
    st.table({
        "Model": [result["Model"]],
        "Option Type": [result["Option Type"]],
        "Price": [f"${result['Price']:.2f}"]
    })
