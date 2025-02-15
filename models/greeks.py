import numpy as np
import scipy.stats as si

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