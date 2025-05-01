import streamlit as st
from utils.fetch_data import get_last_year_cash_flow, get_last_year_balance_sheet, get_last_year_income_statement, get_stock_info, get_stock_calendar, get_stock_price_targets

st.title("Stock Information Dashboard")

ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, MSFT, TSLA)")

# Check if ticker is provided
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
        
        st.subheader(f"{ticker} - Last Year's Income Statement")
        income_statement = get_last_year_income_statement(ticker)
        st.dataframe(income_statement)
        
        st.subheader(f"{ticker} - Last Year's Balance Sheet")
        balance_sheet = get_last_year_balance_sheet(ticker)
        st.dataframe(balance_sheet)
        
        st.subheader(f"{ticker} - Last Year's Cash Flow")
        cash_flow = get_last_year_cash_flow(ticker)
        st.dataframe(cash_flow)
    
    except ValueError as e:
        st.error(f"Error: {str(e)}. Please check the ticker symbol.")
else:
    st.warning("Please enter a valid stock ticker.")
