import unittest
import pandas as pd
import numpy as np
from app.analytics.cleaning import inspect_dataset, clean_dataset

class TestDataCleaningPipeline(unittest.TestCase):

    def setUp(self):
        self.dirty_df = pd.DataFrame({
            'Order ID': ['ORD-1', 'ORD-2', 'ORD-2', 'ORD-3'],
            'Customer Name': ['Alice', 'Bob', 'Bob', None],
            'Order Date': ['2025-01-01', '2025-02-01', '2025-02-01', 'invalid-date'],
            'Sales $': [100.0, 200.0, 200.0, np.nan]
        })

    def test_inspect_dataset(self):
        report = inspect_dataset(self.dirty_df)
        self.assertEqual(report['total_rows'], 4)
        self.assertEqual(report['duplicate_rows'], 1)
        self.assertIn('Sales $', report['missing_info'])
        self.assertEqual(report['missing_info']['Sales $']['count'], 1)

    def test_clean_remove_duplicates(self):
        cleaned, stats = clean_dataset(self.dirty_df, options={'remove_duplicates': True, 'standardize_column_names': False, 'missing_action': 'none'})
        self.assertEqual(len(cleaned), 3)
        self.assertEqual(stats['duplicates_removed'], 1)

    def test_clean_standardize_headers(self):
        cleaned, stats = clean_dataset(self.dirty_df, options={'remove_duplicates': False, 'standardize_column_names': True, 'missing_action': 'none'})
        self.assertIn('order_id', cleaned.columns)
        self.assertIn('customer_name', cleaned.columns)
        self.assertIn('sales', cleaned.columns)

    def test_impute_missing_values(self):
        cleaned, stats = clean_dataset(self.dirty_df, options={'remove_duplicates': False, 'standardize_column_names': True, 'missing_action': 'fill_mean_mode'})
        # Sales numeric missing should be imputed with median
        self.assertFalse(cleaned['sales'].isnull().any())

if __name__ == '__main__':
    unittest.main()
