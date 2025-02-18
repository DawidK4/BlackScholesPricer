import streamlit as st
import pandas as pd
import matplotlib as plt 
import seaborn as sns

from utils import fetch_data
from models import option_pricing, volatility, greeks

st.set_page_config(page_title="Stock Data & Option Pricing", layout="wide")
st.title("Stock Data and Option Pricing")

st.markdown("""
This app allows users to fetch stock market data and perform option pricing calculations. 
Simply enter a valid stock ticker symbol and click the **Fetch Data** button.
""")

# Initialize session state
if 'option_type' not in st.session_state:
    st.session_state.option_type = 'Call'
if 'pricing_model' not in st.session_state:
    st.session_state.pricing_model = 'Black-Scholes'
if 'data' not in st.session_state:
    st.session_state.data = None

ticker = st.text_input("Enter Ticker Symbol:", "AAPL", help="Enter the stock ticker symbol (e.g., AAPL for Apple Inc.).")

pricing_model = st.selectbox("Select Pricing Model:", ["Black-Scholes", "Binomial Tree", "Monte Carlo"])
st.session_state.pricing_model = pricing_model

option_type = st.selectbox("Select Option Type:", ["Call", "Put"], index=0 if st.session_state.option_type == "Call" else 1)
st.session_state.option_type = option_type


if st.button("Fetch Data"):
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

        # Option pricing calculation
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
        
        # Greeks calculation
        greeks_dict = greeks.calculate_greeks(
            st.session_state.data["S"], st.session_state.data["K"], st.session_state.data["T"], 
            st.session_state.data["r"], st.session_state.data["sigma"], option_type.lower()
        )
        
        # Ensure the dictionary is correctly structured
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

        # Volatility calculation
                # Volatility calculation
        hist_vol = volatility.calculate_historical_volatility(ticker)

        if hist_vol is not None:
            st.metric(label="Historical Volatility", value=f"{hist_vol:.2%}")
        else:
            st.error("Failed to calculate historical volatility.")


        
    else:
        st.error("Failed to fetch data. Please check the ticker symbol and try again.")
