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

# Example usage
S = 100   # Stock price
K = 100   # Strike price
T = 1     # Time to maturity (in years)
r = 0.05  # Risk-free rate
sigma = 0.2  # Volatility

print("Black-Scholes Call Price:", black_scholes(S, K, T, r, sigma, "call"))
print("Binomial Call Price:", binomial_tree(S, K, T, r, sigma))
print("Monte Carlo Call Price:", monte_carlo(S, K, T, r, sigma))