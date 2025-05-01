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
    
def get_income_statement(ticker, period="1y"):
    stock = yf.Ticker(ticker)
    income_stmt = stock.financials

    if income_stmt is not None and not income_stmt.empty:
        num_years = int(period.strip("y"))
        columns = income_stmt.columns[:num_years]
        df = income_stmt[columns].copy()
        df.columns = [col.strftime('%Y') for col in df.columns]
        df.reset_index(inplace=True)
        df = df.melt(id_vars="index", var_name="Year", value_name="Value")
        df.rename(columns={"index": "Item"}, inplace=True)
        df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
        df["Item"] = df["Item"].astype(str)
        return df
    else:
        return pd.DataFrame(columns=['Item', 'Year', 'Value'])
    
def get_balance_sheet(ticker, period="1y"):
    stock = yf.Ticker(ticker)
    balance_sheet = stock.balance_sheet

    if balance_sheet is not None and not balance_sheet.empty:
        num_years = int(period.strip("y"))
        columns = balance_sheet.columns[:num_years]
        df = balance_sheet[columns].copy()
        df.columns = [col.strftime('%Y') for col in df.columns]
        df.reset_index(inplace=True)
        df = df.melt(id_vars="index", var_name="Year", value_name="Value")
        df.rename(columns={"index": "Item"}, inplace=True)
        df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
        df["Item"] = df["Item"].astype(str)
        return df
    else:
        return pd.DataFrame(columns=['Item', 'Year', 'Value'])

def get_cash_flow(ticker, period="1y"):
    stock = yf.Ticker(ticker)
    cash_flow = stock.cashflow

    if cash_flow is not None and not cash_flow.empty:
        num_years = int(period.strip("y"))
        columns = cash_flow.columns[:num_years]
        df = cash_flow[columns].copy()
        df.columns = [col.strftime('%Y') for col in df.columns]
        df.reset_index(inplace=True)
        df = df.melt(id_vars="index", var_name="Year", value_name="Value")
        df.rename(columns={"index": "Item"}, inplace=True)
        df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
        df["Item"] = df["Item"].astype(str)
        return df
    else:
        return pd.DataFrame(columns=['Item', 'Year', 'Value'])

def get_dividents(ticker, period="5y"):
    stock = yf.Ticker(ticker)
    dividends = stock.dividends
    if dividends.empty:
        return pd.DataFrame(columns=["Date", "Dividend"])
    
    unit = period[-1]
    amount = int(period[:-1])
    if unit == "y":
        offset = pd.DateOffset(years=amount)
    elif unit == "m":
        offset = pd.DateOffset(months=amount)
    else:
        raise ValueError("Unsupported period unit. Use 'y' or 'm'.")

    now = pd.Timestamp.now(tz=dividends.index.tz)

    dividends = dividends[dividends.index >= now - offset]
    return dividends.reset_index().rename(columns={"Dividends": "Dividend"})
    
    dividends = dividends[dividends.index >= pd.Timestamp.today() - offset]
    return dividends.reset_index().rename(columns={"Dividends": "Dividend"})

def get_splits(ticker, period="5y"):
    stock = yf.Ticker(ticker)
    splits = stock.splits
    if splits.empty:
        return pd.DataFrame(columns=["Date", "Split Ratio"])
    
    unit = period[-1]
    amount = int(period[:-1])
    if unit == "y":
        offset = pd.DateOffset(years=amount)
    elif unit == "m":
        offset = pd.DateOffset(months=amount)
    else:
        raise ValueError("Unsupported period unit. Use 'y' or 'm'.")

    now = pd.Timestamp.now(tz=splits.index.tz)
    splits = splits[splits.index >= now - offset]
    return splits.reset_index().rename(columns={"Stock Splits": "Split Ratio"})