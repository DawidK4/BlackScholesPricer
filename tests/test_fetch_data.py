import unittest
import pandas as pd 
from utils.fetch_data import get_last_year_income_statement, get_last_year_balance_sheet, get_last_year_cash_flow, get_last_year_assets

class TestFetchDataFunctions(unittest.TestCase):
    
    def test_get_last_year_income_statement(self):
        result = get_last_year_income_statement("AAPL")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertNotEmpty(result)
    
    def test_get_last_year_balance_sheet(self):
        result = get_last_year_balance_sheet("AAPL")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertNotEmpty(result)
    
    def test_get_last_year_cash_flow(self):
        result = get_last_year_cash_flow("AAPL")
        self.assertIsInstance(result, pd.DataFrame)
        self.assertNotEmpty(result)

if __name__ == "__main__":
    unittest.main()
