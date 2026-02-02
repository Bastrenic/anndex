from django.test import TestCase
from django.urls import reverse
from home.models import User, Product
from django.utils import timezone
from django.core.cache import cache



class ProductViewTest(TestCase):
    def test_success(self):
        response = self.client.get(reverse('product'), data={
            'q': 'ps5'
        })
        self.assertEqual(response.status_code, 200)
    
    def test_successful_save(self):
        response = self.client.get(reverse('product'), data={
            'q': 'ps5'
        })
        data = response.json()
        payload = {
            'product_name': data['product_name'],
            'image_url': data['image_url'],
            'listings': data['listings']
        }
        
        response = self.client.post(
            reverse('product'),
            data=payload,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)

    