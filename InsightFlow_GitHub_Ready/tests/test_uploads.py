import unittest
import io
import os
from app import create_app
from app.extensions import db
from app.models import User, Dataset

class TestUploadsSystem(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        # Create user
        self.user = User(username='uploader', email='uploader@test.com')
        self.user.set_password('pass123')
        db.session.add(self.user)
        db.session.commit()

        # Log in
        self.client.post('/auth/login', data={'identifier': 'uploader', 'password': 'pass123'})

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_upload_csv(self):
        csv_content = b"order_id,date,sales,channel\nORD-1,2025-01-01,150,Direct\nORD-2,2025-01-02,300,Search\n"
        data = {
            'file': (io.BytesIO(csv_content), 'test_orders.csv')
        }
        resp = self.client.post('/datasets/upload', data=data, content_type='multipart/form-data', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

        # Check in DB
        dataset = Dataset.query.filter_by(original_filename='test_orders.csv').first()
        self.assertIsNotNone(dataset)
        self.assertEqual(dataset.row_count, 2)
        self.assertEqual(dataset.column_count, 4)

if __name__ == '__main__':
    unittest.main()
