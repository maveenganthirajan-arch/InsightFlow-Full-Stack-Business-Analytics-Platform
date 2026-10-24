import os
import shutil
import json
from app import create_app
from app.extensions import db
from app.models import User, Dataset, Dashboard
from app.analytics.cleaning import inspect_dataset
import pandas as pd

app = create_app(os.environ.get('FLASK_CONFIG', 'default'))

def initialize_database():
    """Seeds default demo account and preloads sample dataset if empty."""
    with app.app_context():
        db.create_all()

        # Check if default admin user exists
        demo_user = User.query.filter_by(username='admin').first()
        if not demo_user:
            demo_user = User(
                username='admin',
                email='admin@insightflow.io'
            )
            demo_user.set_password('admin123')
            db.session.add(demo_user)
            db.session.commit()
            print("[InsightFlow] Created demo user: admin / admin123")

            # Create default dashboard
            default_dash = Dashboard(
                user_id=demo_user.id,
                name='Executive Business Overview',
                is_default=True
            )
            db.session.add(default_dash)
            db.session.commit()

        # Check if sample dataset is registered
        existing_dataset = Dataset.query.filter_by(user_id=demo_user.id).first()
        sample_source = os.path.join(app.root_path, '..', 'sample_data', 'sales_sample.csv')

        if not existing_dataset and os.path.exists(sample_source):
            user_upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(demo_user.id))
            os.makedirs(user_upload_dir, exist_ok=True)
            dest_path = os.path.join(user_upload_dir, 'sample_sales_benchmark.csv')
            shutil.copyfile(sample_source, dest_path)

            try:
                df = pd.read_csv(dest_path)
                summary = inspect_dataset(df)
                dataset = Dataset(
                    user_id=demo_user.id,
                    filename='sample_sales_benchmark.csv',
                    original_filename='Sales_Transactions_2024_2025.csv',
                    file_path=dest_path,
                    file_size_kb=os.path.getsize(dest_path) / 1024.0,
                    row_count=len(df),
                    column_count=len(df.columns),
                    columns_json=json.dumps([str(c) for c in df.columns]),
                    summary_json=json.dumps(summary),
                    is_cleaned=True
                )
                db.session.add(dataset)
                db.session.commit()
                print("[InsightFlow] Pre-loaded sample sales dataset.")
            except Exception as e:
                print(f"[InsightFlow] Warning: Could not preload sample dataset: {e}")

if __name__ == '__main__':
    initialize_database()
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() in ['true', '1']
    print(f"\n=======================================================")
    print(f">> InsightFlow Business Analytics Platform Running at:")
    print(f"   http://{host}:{port}/")
    print(f"   Demo Credentials: admin / admin123")
    print(f"=======================================================\n")
    app.run(host=host, port=port, debug=debug)
