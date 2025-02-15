import numpy as np
import scipy.stats as si

'''
Computes the price of a European call or put option using the Black-Scholes formula.

Parameters:
S (float): Current stock price
K (float): Strike price of the option
T (float): Time to maturity (in years)
r (float): Risk-free interest rate (annualized)
sigma (float): Volatility of the underlying asset (annualized)
option_type (str, optional): Type of option ('call' or 'put')

Returns:
(float): Option price
'''
def black_scholes(S, K, T, r, sigma, option_type="call"):
    """Computes the Black-Scholes option price."""
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if option_type == "call":
        return S * si.norm.cdf(d1) - K * np.exp(-r * T) * si.norm.cdf(d2)
    elif option_type == "put":
        return K * np.exp(-r * T) * si.norm.cdf(-d2) - S * si.norm.cdf(-d1)
    else:
        raise ValueError("Invalid option type. Choose 'call' or 'put'.")
    
'''
Computes the price of an option using the Binomial Tree method.

Parameters:
S (float): Current stock price
K (float): Strike price of the option
T (float): Time to maturity (in years)
r (float): Risk-free interest rate (annualized)
sigma (float): Volatility of the underlying asset (annualized)
N (int, optional): Number of time steps in the binomial tree (default: 100)
option_type (str, optional): Type of option ('call' or 'put')

Returns:
(float): Option price
'''
def binomial_tree(S, K, T, r, sigma, N=100, option_type="call"):
    """Computes option price using Binomial Tree method."""
    dt = T / N
    u = np.exp(sigma * np.sqrt(dt))
    d = 1 / u
    p = (np.exp(r * dt) - d) / (u - d)
    
    stock_prices = np.zeros((N+1, N+1))
    option_values = np.zeros((N+1, N+1))
    
    for i in range(N+1):
        for j in range(i+1):
            stock_prices[j, i] = S * (u ** (i-j)) * (d ** j)
    
    if option_type == "call":
        option_values[:, N] = np.maximum(stock_prices[:, N] - K, 0)
    else:
        option_values[:, N] = np.maximum(K - stock_prices[:, N], 0)
    
    for i in range(N-1, -1, -1):
        for j in range(i+1):
            option_values[j, i] = np.exp(-r * dt) * (p * option_values[j, i+1] + (1-p) * option_values[j+1, i+1])
    
    return option_values[0, 0]

'''
Computes the price of an option using Monte Carlo simulation.

Parameters:
S (float): Current stock price
K (float): Strike price of the option
T (float): Time to maturity (in years)
r (float): Risk-free interest rate (annualized)
sigma (float): Volatility of the underlying asset (annualized)
simulations (int, optional): Number of Monte Carlo simulations (default: 10,000)
option_type (str, optional): Type of option ('call' or 'put')

Returns:
(float): Option price (Monte Carlo estimate)
'''
def monte_carlo(S, K, T, r, sigma, simulations=10000, option_type="call"):
    """Computes option price using Monte Carlo simulation."""
    np.random.seed(42)  # For reproducibility
    Z = np.random.standard_normal(simulations)
    ST = S * np.exp((r - 0.5 * sigma ** 2) * T + sigma * np.sqrt(T) * Z)
    
    if option_type == "call":
        payoff = np.maximum(ST - K, 0)
    else:
        payoff = np.maximum(K - ST, 0)
    
    return np.exp(-r * T) * np.mean(payoff)

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

'''
Calculates the option Greeks (Delta, Gamma, Theta, Vega, Rho) using the Black-Scholes model.

Parameters:
S (float): Current stock price.
K (float): Strike price of the option.
T (float): Time to maturity (in years).
r (float): Risk-free interest rate (annualized).
sigma (float): Volatility of the underlying asset (annualized).
option_type (str, optional): Type of option ('call' or 'put'). Default is "call".

Returns:
dict: A dictionary containing the calculated Greeks:
    delta: Sensitivity to changes in the stock price.
    gamma: Sensitivity to changes in delta.
    theta: Sensitivity to changes in time to maturity.
    vega: Sensitivity to changes in volatility.
    rho: Sensitivity to changes in the risk-free interest rate.
'''
def calculate_greeks(S, K, T, r, sigma, option_type="call"):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    delta = si.norm.cdf(d1) if option_type == "call" else si.norm.cdf(d1) - 1
    gamma = si.norm.pdf(d1) / (S * sigma * np.sqrt(T))
    theta = - (S * si.norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * si.norm.cdf(d2) if option_type == "call" else - (S * si.norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * si.norm.cdf(-d2)
    vega = S * np.sqrt(T) * si.norm.pdf(d1)
    rho = K * T * np.exp(-r * T) * si.norm.cdf(d2) if option_type == "call" else - K * T * np.exp(-r * T) * si.norm.cdf(-d2)
    
    return {"delta": delta, "gamma": gamma, "theta": theta, "vega": vega, "rho": rho}