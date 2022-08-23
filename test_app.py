from app import app
from unittest import TestCase

class CurrencyConverterTestCase(TestCase):
    """Integration tests for the Flask app."""

    def test_root_redirect(self):
        with app.test_client() as client:
            response = client.get('/')

            self.assertEqual(response.status_code, 302)

    def test_users_index(self):
        with app.test_client() as client:
            response = client.get('/users')
            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('<h1>Users</h1>', html)
            self.assertIn('<ul>', html)

    def test_convert_submit(self):
        with app.test_client() as client:
            response = client.post('/convert', follow_redirects=True, data={'convert-from': 'USD', 'amount': '1.0', 'convert-to': 'USD'})
            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('$ 1.00 (USD) converts to $ 1.00 (USD).', html)