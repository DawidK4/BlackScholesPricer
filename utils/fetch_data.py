import yfinance as yf
import streamlit as st
import datetime
import pandas as pd 
from models import volatility

def get_options_data(ticker, period="1mo"):
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

def get_stock_info(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    df = pd.DataFrame(info.items(), columns=['Attribute', 'Value'])
    return df

def get_stock_calendar(ticker):
    stock = yf.Ticker(ticker)
    calendar = stock.calendar
    return calendar

def get_stock_price_targets(ticker):
    stock = yf.Ticker(ticker)
    try:
        targets = stock.recommendations_summary.get('targetMeanPrice', None)
        return {
            "target_high": stock.info.get("targetHighPrice"),
            "target_low": stock.info.get("targetLowPrice"),
            "target_mean": stock.info.get("targetMeanPrice"),
            "target_median": stock.info.get("targetMedianPrice")
        }
    except Exception as e:
        return {"error": str(e)}
    
def get_last_year_income_statement(ticker):
    stock = yf.Ticker(ticker)
    income_stmt = stock.financials  
    
    if income_stmt is not None and not income_stmt.empty:
        latest_year = income_stmt.columns[0]
        df = income_stmt[[latest_year]].copy()
        df.columns = [latest_year.strftime('%Y')]  
        df.reset_index(inplace=True)
        df.columns = ['Item', 'Value']
        return df
    else:
        return pd.DataFrame(columns=['Item', 'Value'])
    
def get_last_year_balance_sheet(ticker):
    stock = yf.Ticker(ticker)
    balance_sheet = stock.balance_sheet 

    if balance_sheet is not None and not balance_sheet.empty:
        latest_year = balance_sheet.columns[0]
        df = balance_sheet[[latest_year]].copy()
        df.columns = [latest_year.strftime('%Y')]
        df.reset_index(inplace=True)
        df.columns = ['Item', 'Value']
        return df
    else:
        return pd.DataFrame(columns=['Item', 'Value'])
    
def get_last_year_cash_flow(ticker):
    stock = yf.Ticker(ticker)
    cash_flow = stock.cashflow  

    if cash_flow is not None and not cash_flow.empty:
        latest_year = cash_flow.columns[0]
        df = cash_flow[[latest_year]].copy()
        df.columns = [latest_year.strftime('%Y')]
        df.reset_index(inplace=True)
        df.columns = ['Item', 'Value']
        return df
    else:
        return pd.DataFrame(columns=['Item', 'Value'])