import streamlit as st 

S = st.number_input("Stock Price (S)", min_value=1.0, value=100.0)
K = st.number_input("Strike Price (K)", min_value=1.0, value=100.0)
T = st.number_input("Time to Expiry (T in years)", min_value=0.01, value=1.0)
r = st.number_input("Risk-Free Rate (r in %)", min_value=0.0, value=5.0) / 100
sigma = st.number_input("Volatility (σ in %)", min_value=0.1, value=20.0) / 100

import numpy as np
from scipy.stats import norm

def black_scholes_call(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

if st.button("Calculate Call Option Price"):
    call_price = black_scholes_call(S, K, T, r, sigma)
    st.success(f"Call Option Price: ${call_price:.2f}")

import matplotlib.pyplot as plt

x = np.linspace(80, 120, 100)
y = [black_scholes_call(price, K, T, r, sigma) for price in x]

fig, ax = plt.subplots()
ax.plot(x, y, label="Call Option Price")
ax.set_xlabel("Stock Price")
ax.set_ylabel("Option Price")
ax.legend()

st.pyplot(fig)
