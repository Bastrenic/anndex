from django.test import TestCase
from django.urls import reverse
from home.models import User

class ProductViewTest(TestCase):
    def test_success(self):
        response = self.client.get(reverse('product'), data={
            'q': 'ps5'
        })
        print(response.json())
        #self.assertEqual(response.status_code, 200)
    