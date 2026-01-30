from django.test import TestCase
from django.urls import reverse
from home.models import User

class LoginViewTest(TestCase):
    def setUp(self):
        self.client.post(reverse('register'), data={
            'username': 'ajl',
            'email': 'ajl@gmail.com',
            'password': 'ajl'
        })

    def test_success(self):
        response = self.client.post(reverse('login'), data={
            'username': 'ajl',
            'password': 'ajl'
        })
        self.assertEqual(response.status_code, 200)

    # how do i handle already being logged in?
    def test_user_doesnt_exist(self):
        response = self.client.post(reverse('login'), data={
            'username': 'ajl1',
            'password': 'ajl1'
        })
        self.assertEqual(response.status_code, 400)
    