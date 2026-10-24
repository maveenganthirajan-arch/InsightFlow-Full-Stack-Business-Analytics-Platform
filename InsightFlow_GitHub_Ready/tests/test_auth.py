import unittest
from app import create_app
from app.extensions import db
from app.models import User

class TestAuthSystem(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='analyst', email='analyst@insightflow.io')
        u.set_password('Secret123!')
        self.assertTrue(u.check_password('Secret123!'))
        self.assertFalse(u.check_password('WrongPassword'))

    def test_signup_and_login_flow(self):
        # Signup
        response = self.client.post('/auth/signup', data={
            'username': 'testuser',
            'email': 'test@insightflow.io',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Verify DB
        user = User.query.filter_by(username='testuser').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'test@insightflow.io')

        # Logout
        logout_resp = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(logout_resp.status_code, 200)

if __name__ == '__main__':
    unittest.main()
