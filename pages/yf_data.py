import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from utils import fetch_data
from models import option_pricing, volatility, greeks

st.set_page_config(page_title="Stock Data & Option Pricing", layout="wide")
st.title("Stock Data and Option Pricing")

st.markdown("""
This app allows users to fetch stock market data and perform option pricing calculations. 
Simply enter a valid stock ticker symbol and click the **Fetch Data** button.
""")

if 'option_type' not in st.session_state:
    st.session_state.option_type = 'Call'
if 'pricing_model' not in st.session_state:
    st.session_state.pricing_model = 'Black-Scholes'
if 'data' not in st.session_state:
    st.session_state.data = None

with st.sidebar:
    ticker = st.text_input("Enter Ticker Symbol:", "AAPL", help="Enter the stock ticker symbol (e.g., AAPL for Apple Inc.).")
    pricing_model = st.selectbox("Select Pricing Model:", ["Black-Scholes", "Binomial Tree", "Monte Carlo"])
    st.session_state.pricing_model = pricing_model
    option_type = st.selectbox("Select Option Type:", ["Call", "Put"], index=0 if st.session_state.option_type == "Call" else 1)
    st.session_state.option_type = option_type
    fetch_button = st.button("Fetch Data")

if fetch_button:
    st.session_state.data = fetch_data.get_data(ticker)
    
    if st.session_state.data:
        st.success(f"Successfully fetched data for **{ticker}**.")
        
        renamed_data = {
            "S": "Stock Price",
            "K": "Strike Price",
            "T": "Time to Maturity",
            "r": "Risk-Free Rate",
            "sigma": "Volatility"
        }
        
        df = pd.DataFrame(st.session_state.data.items(), columns=["Parameters", "Values"])
        df["Parameters"] = df["Parameters"].replace(renamed_data)
        df = df.set_index("Parameters")
        
        st.dataframe(df, use_container_width=True)

        if pricing_model == "Black-Scholes":
            price = option_pricing.black_scholes(
                st.session_state.data["S"], st.session_state.data["K"], st.session_state.data["T"], 
                st.session_state.data["r"], st.session_state.data["sigma"], option_type.lower()
            )
        elif pricing_model == "Binomial Tree":
            price = option_pricing.binomial_tree(
                st.session_state.data["S"], st.session_state.data["K"], st.session_state.data["T"], 
                st.session_state.data["r"], st.session_state.data["sigma"], option_type.lower()
            )
        else:
            price = option_pricing.monte_carlo(
                st.session_state.data["S"], st.session_state.data["K"], st.session_state.data["T"], 
                st.session_state.data["r"], st.session_state.data["sigma"], option_type.lower()
            )
        
        st.success(f"The estimated {option_type.lower()} option price is: **${price:.2f}**")
        
        greeks_dict = greeks.calculate_greeks(
            st.session_state.data["S"], st.session_state.data["K"], st.session_state.data["T"], 
            st.session_state.data["r"], st.session_state.data["sigma"], option_type.lower()
        )
        
        if greeks_dict:
            greeks_values = {
                "Delta": greeks_dict.get("delta", "N/A"),
                "Gamma": greeks_dict.get("gamma", "N/A"),
                "Theta": greeks_dict.get("theta", "N/A"),
                "Vega": greeks_dict.get("vega", "N/A"),
                "Rho": greeks_dict.get("rho", "N/A")
            }

            greeks_df = pd.DataFrame(greeks_values.items(), columns=["Greek", "Value"])
            greeks_df.set_index("Greek", inplace=True)

            st.dataframe(greeks_df, use_container_width=True)
        else:
            st.error("Failed to calculate Greeks.")

        hist_vol = volatility.calculate_historical_volatility(ticker)

        if hist_vol is not None:
            st.metric(label="Historical Volatility", value=f"{hist_vol:.2%}")
        else:
            st.error("Failed to calculate historical volatility.")

        stock_price = st.session_state.data["S"]
        strike_price = st.session_state.data["K"]

        stock_prices_range = [stock_price * (1 + i * 0.01) for i in range(-10, 21)] 

        profits = []
        for price in stock_prices_range:
            if option_type == "Call":
                profits.append(max(0, price - strike_price))  
            else: 
                profits.append(max(0, strike_price - price))  

        at_the_money_price = strike_price

        st.metric("At the Money Price", f"${at_the_money_price:.2f}")

        plt.figure(figsize=(10, 6))
        plt.plot(stock_prices_range, profits, label=f"{option_type} Option Profit", color='b')
        plt.axvline(x=stock_price, color='r', linestyle='--', label="Current Stock Price")
        plt.axvline(x=strike_price, color='g', linestyle='--', label="Strike Price")
        plt.fill_between(stock_prices_range, profits, color='b', alpha=0.1)
        plt.title(f"Profit from Exercising {option_type} Option")
        plt.xlabel("Stock Price")
        plt.ylabel("Profit ($)")
        plt.legend()
        plt.grid(True)

        st.pyplot(plt)

    else:
        st.error("Failed to fetch data. Please check the ticker symbol and try again.")
