import streamlit as st
import pandas as pd
from utils import fetch_data
from models import option_pricing

st.set_page_config(page_title="Stock Data & Option Pricing", layout="wide")

st.title("Stock Data and Option Pricing")

st.markdown(
    """
    This app allows users to fetch stock market data and perform option pricing calculations. 
    Simply enter a valid stock ticker symbol and click the **Fetch Data** button.
    """
)

ticker = st.text_input(
    "Enter Ticker Symbol:", 
    "AAPL", 
    help="Enter the stock ticker symbol (e.g., AAPL for Apple Inc.)."
)

if "last_ticker" not in st.session_state:
    st.session_state.last_ticker = ticker

if ticker != st.session_state.last_ticker:
    st.session_state.data = None
    st.session_state.last_ticker = ticker

if "data" not in st.session_state or st.session_state.data is None:
    data = None
    if st.button("Fetch Data"):
        data = fetch_data.get_data(ticker)
        
        if data:
            st.session_state.data = data
            st.success(f"Successfully fetched data for **{ticker}**.")
        else:
            st.error("Failed to fetch data. Please check the ticker symbol and try again.")
else:
    data = st.session_state.data

if data:
    renamed_data = {
        "S": "Stock Price",
        "K": "Strike Price",
        "T": "Time to Maturity",
        "r": "Risk-Free Rate",
        "sigma": "Volatility"
    }
    
    df = pd.DataFrame(data.items(), columns=["Parameters", "Values"])
    df["Parameters"] = df["Parameters"].replace(renamed_data)
    df = df.set_index("Parameters")
    
    st.dataframe(df, use_container_width=True)

    option_type = st.radio("Select Option Type:", ("Call", "Put"))
    model = st.selectbox("Select Pricing Model:", ("Black-Scholes", "Binomial Tree", "Monte Carlo"))
    
    if model == "Black-Scholes":
        price = option_pricing.black_scholes(
            data["S"], data["K"], data["T"], data["r"], data["sigma"], option_type.lower()
        )
    elif model == "Binomial Tree":
        price = option_pricing.binomial_tree(
            data["S"], data["K"], data["T"], data["r"], data["sigma"], option_type.lower()
        )
    else:
        price = option_pricing.monte_carlo(
            data["S"], data["K"], data["T"], data["r"], data["sigma"], option_type.lower()
        )
    
    st.success(f"The estimated {option_type.lower()} option price is: **${price:.2f}**")
