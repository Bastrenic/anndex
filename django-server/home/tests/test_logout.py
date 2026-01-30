from django.test import TestCase
from django.urls import reverse
from home.models import User

class LoginViewTest(TestCase):
    def setUp(self):
        response = self.client.post(reverse('register'), data={
            'username': 'ajl',
            'email': 'ajl@gmail.com',
            'password': 'ajl'
        })
        self.refresh_token = response.data['tokens']['refresh']

    def test_success(self):
        response = self.client.post(reverse('logout'), data={
            'refresh': self.refresh_token
        })
        self.assertEqual(response.status_code, 205)

    
    def test_invalid_token(self):
        response = self.client.post(reverse('logout'), data={
            'refresh': 'invalid'
        })
        self.assertEqual(response.status_code, 400)


        
