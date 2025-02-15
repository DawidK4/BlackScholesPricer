from yahoo_fin import options
import pandas as pd 

stock = 'AAPL'

pd.set_option('display.max_columns', None)
chain = options.get_options_chain(stock)

print(type(chain))

# for key in chain:
#     print(key)

print(chain)