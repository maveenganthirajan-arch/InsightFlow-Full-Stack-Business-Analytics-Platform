import csv
import random
from datetime import datetime, timedelta
import os

def generate_sample_sales_csv(filepath, num_records=2500):
    """Generates a realistic business dataset across 2024 and 2025."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    products = [
        {'name': 'Cloud Subscriptions Enterprise', 'category': 'Subscriptions', 'channel_weights': [0.45, 0.25, 0.20, 0.10], 'price_range': (120, 450), 'margin': 0.72},
        {'name': 'Professional Consulting Service', 'category': 'Services', 'channel_weights': [0.35, 0.35, 0.20, 0.10], 'price_range': (250, 900), 'margin': 0.55},
        {'name': 'API Data Exports & Downloads', 'category': 'Downloads', 'channel_weights': [0.40, 0.25, 0.15, 0.20], 'price_range': (40, 150), 'margin': 0.85},
        {'name': 'Developer SDK Pro', 'category': 'Subscriptions', 'channel_weights': [0.42, 0.28, 0.18, 0.12], 'price_range': (80, 220), 'margin': 0.78},
        {'name': 'Implementation & Onboarding', 'category': 'Services', 'channel_weights': [0.30, 0.40, 0.20, 0.10], 'price_range': (300, 750), 'margin': 0.50}
    ]

    channels = ['Direct', 'Search', 'Referrals', 'Social']
    regions = ['North America', 'Europe', 'Asia Pacific', 'Latin America']
    statuses = ['Completed', 'Completed', 'Completed', 'Completed', 'Processing', 'Refunded']

    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 12, 31)
    total_days = (end_date - start_date).days

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'order_id', 'order_date', 'customer_id', 'region', 
            'category', 'product', 'channel', 'quantity', 
            'sales', 'cost', 'status'
        ])

        for i in range(1, num_records + 1):
            random_day = random.randint(0, total_days)
            order_date = start_date + timedelta(days=random_day)
            year = order_date.year

            product_info = random.choice(products)
            channel = random.choices(channels, weights=product_info['channel_weights'])[0]
            region = random.choice(regions)
            quantity = random.randint(1, 4)
            unit_price = random.uniform(*product_info['price_range'])
            
            # Boost 2025 sales slightly to represent growth
            growth_factor = 1.168 if year == 2025 else 1.0
            sales = round(quantity * unit_price * growth_factor, 2)
            cost = round(sales * (1 - product_info['margin']), 2)
            
            customer_id = f"CUST-{random.randint(1000, 4200):04d}"
            order_id = f"ORD-{year}-{i:05d}"
            status = random.choice(statuses)

            writer.writerow([
                order_id,
                order_date.strftime('%Y-%m-%d'),
                customer_id,
                region,
                product_info['category'],
                product_info['name'],
                channel,
                quantity,
                sales,
                cost,
                status
            ])

    print(f"Generated {num_records} sample records in: {filepath}")

if __name__ == '__main__':
    target = os.path.join(os.path.dirname(__file__), '..', 'sample_data', 'sales_sample.csv')
    generate_sample_sales_csv(target, 2500)
