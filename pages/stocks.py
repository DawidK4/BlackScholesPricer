import streamlit as st
import yfinance as yf
import pandas as pd 

from utils.fetch_data import (
    get_cash_flow,
    get_balance_sheet,
    get_income_statement,
    get_stock_info,
    get_stock_calendar,
    get_stock_price_targets,
    get_dividents,
    get_splits,
)

st.title("📊 Stock Information Dashboard")

ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, MSFT, TSLA)")
period = st.selectbox("Select Financial Period", ["1y", "2y", "3y", "5y"], index=0)

if ticker:
    try:
        st.subheader(f"{ticker} - Stock Info")
        stock_info = get_stock_info(ticker)
        st.dataframe(stock_info)

        st.subheader(f"{ticker} - Stock Calendar")
        stock_calendar = get_stock_calendar(ticker)
        st.dataframe(stock_calendar)

        st.subheader(f"{ticker} - Price Targets")
        price_targets = get_stock_price_targets(ticker)
        st.json(price_targets)

        st.subheader(f"{ticker} - Income Statement ({period})")
        income_statement = get_income_statement(ticker, period)
        st.dataframe(income_statement)

        st.subheader(f"{ticker} - Balance Sheet ({period})")
        balance_sheet = get_balance_sheet(ticker, period)
        st.dataframe(balance_sheet)

        st.subheader(f"{ticker} - Cash Flow Statement ({period})")
        cash_flow = get_cash_flow(ticker, period)
        st.dataframe(cash_flow)

        st.subheader(f"{ticker} - Dividends ({period})")
        dividends = get_dividents(ticker, period)
        st.dataframe(dividends)

        st.subheader(f"{ticker} - Stock Splits ({period})")
        splits = get_splits(ticker, period)
        st.dataframe(splits)

        stock = yf.Ticker(ticker)
        news = stock.news
            
    except Exception as e:
        st.error(f"Error: {str(e)}. Please check the ticker symbol and try again.")
else:
    st.warning("Please enter a valid stock ticker.")
