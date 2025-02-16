import streamlit as st
import yfinance as yf
import datetime
from models import greeks, option_pricing, volatility
from utils import login

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

st.set_page_config(layout="wide")

login.login_ui()  # Displays the login pop-up

st.title("📈 Option Pricing Calculator")

if not st.session_state["logged_in"]:
    st.warning("⚠️ You are not logged in. Some features may be limited.")

if "option_history" not in st.session_state:
    st.session_state.option_history = []  

col1, col2 = st.columns([3, 1])

with col1:
    tab_yfinance, tab_manual = st.tabs(["📡 Fetch from Yahoo Finance", "✍️ Enter Manually"])

    with tab_yfinance:
        st.subheader("Fetch Option Data from Yahoo Finance")
        ticker = st.text_input("Enter Stock Ticker:", "AAPL")
        
        if st.button("Fetch Data"):
            data = get_data(ticker)
            if data:
                st.session_state.data = data  
                st.session_state.data_source = f"Yahoo Finance ({ticker})"
                st.success("Data retrieved successfully!")

        if "data" in st.session_state and st.session_state.data:
            st.subheader("📊 Fetched Data")
            data = st.session_state.data
            st.table({
                "Metric": ["Stock Price (S)", "Closest Strike Price (K)", "Time to Maturity (T)", "Volatility (σ)", "Risk-Free Rate (r)"],
                "Value": [f"${data['S']:.2f}", f"${data['K']:.2f}", f"{data['T']:.4f} years", f"{data['sigma']:.4f}", f"{data['r']:.2f}"]
            })

    with tab_manual:
        st.subheader("Manually Enter Option Parameters")
        S_manual = st.number_input("Stock Price (S)", value=100.0) 
        K_manual = st.number_input("Strike Price (K)", value=100.0)  
        T_manual = st.number_input("Time to Maturity (T, in years)", value=1.0, format="%.4f")  
        r_manual = st.number_input("Risk-Free Rate (r)", value=0.05, format="%.2f") 
        sigma_manual = st.number_input("Volatility (σ)", value=0.2, format="%.4f")  

st.subheader("📊 Calculate Option Price")
model = st.selectbox("Choose Pricing Model", ["Black-Scholes", "Binomial Tree", "Monte Carlo"])
option_type = st.radio("Option Type", ["Call", "Put"])

if st.button("Calculate Price"):
    if "data" in st.session_state and st.session_state.data and "data_source" in st.session_state:
        data = st.session_state.data  
        S, K, T, r, sigma = data["S"], data["K"], data["T"], data["r"], data["sigma"]
        source = st.session_state.data_source
    else:
        S, K, T, r, sigma = S_manual, K_manual, T_manual, r_manual, sigma_manual
        source = "Entered Manually"

    if model == "Black-Scholes":
        price = option_pricing.black_scholes(S, K, T, r, sigma, option_type.lower())
    elif model == "Binomial Tree":
        price = option_pricing.binomial_tree(S, K, T, r, sigma, N=100, option_type=option_type.lower())
    elif model == "Monte Carlo":
        price = option_pricing.monte_carlo(S, K, T, r, sigma, simulations=10000, option_type=option_type.lower())

    st.session_state.option_history.append({
        "Model": model,
        "Option Type": option_type,
        "Price": f"${price:.2f}",
        "Source": source
    })

    if "data" in st.session_state:
        del st.session_state.data
    if "data_source" in st.session_state:   
        del st.session_state.data_source


with col2:
    st.subheader("📜 Calculation History")
    if st.session_state.option_history:
        st.table(st.session_state.option_history)
    else:
        st.info("No calculations yet. Perform an option pricing calculation to see history here.")
