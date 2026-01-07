import unittest
from unittest.mock import MagicMock
import pandas as pd
import numpy as np
import app

class TestPEGSkipLogic(unittest.TestCase):
    def test_get_valuation_data_skip_nan(self):
        # Mock stock and info
        mock_stock = MagicMock()
        mock_info = {
            'currentPrice': 100.0,
            'trailingPE': 20.0,
            'trailingEps': 5.0,
        }
        
        # Data: Y0=5, Y1=NaN, Y2=4, Y3=2
        # Loop 0: 5 vs NaN -> NaN/Error -> Skipped
        # Loop 1: NaN vs 4 -> NaN/Error -> Skipped
        # Loop 2: 4 vs 2 -> 100% Growth (1.0)
        # Avg Growth should be 1.0 (based on 1 valid point), NOT (0+0+1)/3 = 0.33
        dates = pd.to_datetime(['2025-01-01', '2024-01-01', '2023-01-01', '2022-01-01'])
        eps_data = [5.0, np.nan, 4.0, 2.0]
        
        df = pd.DataFrame(data=[eps_data], columns=dates, index=["Diluted EPS"])
        mock_stock.income_stmt = df
        
        result = app.get_valuation_data(mock_stock, mock_info)
        
        print("\nTest PEG Skip Logic:")
        print(f"Calculated PEG: {result.get('peg')}")
        print(f"Source: {result.get('peg_source')}")
        
        # PEG = 20 / (1.0 * 100) = 0.2
        # If it treated NaNs as 0: PEG = 20 / 33 = 0.6
        if result['peg']:
            self.assertAlmostEqual(result['peg'], 0.2, delta=0.05)
            self.assertTrue("Calculated (1yr Avg Growth)" in result['peg_source'] or "1yr Avg Growth" in result['peg_source'])
        else:
            self.fail("PEG should be calculated")

if __name__ == '__main__':
    unittest.main()
