import unittest
import pandas as pd
from app.analytics.metrics import compute_business_kpis, detect_column
from app.analytics.charts import get_dashboard_chart_configs

class TestAnalyticsEngine(unittest.TestCase):

    def setUp(self):
        self.sample_df = pd.DataFrame({
            'order_id': ['ORD-1', 'ORD-2', 'ORD-3', 'ORD-4'],
            'order_date': ['2025-01-10', '2025-02-15', '2025-03-20', '2024-01-15'],
            'customer_id': ['C-1', 'C-2', 'C-1', 'C-3'],
            'sales': [1000.0, 2500.0, 1500.0, 4000.0],
            'cost': [400.0, 1000.0, 600.0, 1600.0],
            'channel': ['Direct', 'Search', 'Direct', 'Social'],
            'product': ['Enterprise Cloud', 'Consulting', 'Enterprise Cloud', 'Downloads']
        })

    def test_detect_column(self):
        col = detect_column(self.sample_df, ['sales', 'revenue', 'amount'])
        self.assertEqual(col, 'sales')

        date_col = detect_column(self.sample_df, ['date', 'time'])
        self.assertEqual(date_col, 'order_date')

    def test_compute_business_kpis(self):
        kpis = compute_business_kpis(self.sample_df, year_filter='2025')
        self.assertIn('total_revenue', kpis)
        self.assertIn('paid_orders', kpis)
        self.assertIn('channels', kpis)
        self.assertIn('quarters', kpis)
        self.assertIn('targets', kpis)
        
        # 2025 orders = 3 orders (total sales 1000 + 2500 + 1500 = 5000.0)
        self.assertEqual(kpis['total_revenue'], 5000.0)
        self.assertEqual(kpis['paid_orders'], 3)

    def test_chart_configs_generation(self):
        kpis = compute_business_kpis(self.sample_df, year_filter='2025')
        configs = get_dashboard_chart_configs(kpis)
        self.assertIn('revenue_trend', configs)
        self.assertIn('revenue_channel', configs)
        self.assertIn('orders_quarter', configs)
        self.assertEqual(configs['revenue_trend']['type'], 'line')
        self.assertEqual(configs['revenue_channel']['type'], 'doughnut')
        self.assertEqual(configs['orders_quarter']['type'], 'bar')

    def test_empty_dataframe_fallback(self):
        empty_df = pd.DataFrame()
        kpis = compute_business_kpis(empty_df)
        self.assertGreater(kpis['total_revenue'], 0)
        self.assertGreater(kpis['paid_orders'], 0)

if __name__ == '__main__':
    unittest.main()
