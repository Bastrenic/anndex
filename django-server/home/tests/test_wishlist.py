from django.test import TestCase
from django.urls import reverse
from home.models import User

class WishlistViewTest(TestCase):
    def setUp(self):
        response = self.client.post(reverse('register'), data={
            'username': 'ajl',
            'email': 'ajl@gmail.com',
            'password': 'ajl'
        })
        self.refresh_token = response.data['tokens']['refresh']

   
        
