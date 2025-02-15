import numpy as np
import scipy.stats as si

'''
Calculates the historical volatility of a stock by analyzing its historical closing prices.

Parameters:
ticker (str): Stock ticker symbol (e.g., "AAPL").
period (str, optional): Time period for the historical data (default: "1y"). Other options include "1mo", "3mo", etc.

Returns:
float: The annualized volatility of the stock.
'''
def calculate_historical_volatility(ticker, period="1y"):
    import yfinance as yf
    stock = yf.Ticker(ticker)
    historical_data = stock.history(period=period)
    log_returns = np.log(historical_data["Close"] / historical_data["Close"].shift(1)).dropna()
    sigma = log_returns.std() * np.sqrt(252)  # Annualized standard deviation
    return sigma