from django.test import TestCase
from django.urls import reverse
from home.models import User, Product
from django.utils import timezone
from django.core.cache import cache



class ProductViewTest(TestCase):
    def setUp(self):
        User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='admin',
            is_staff=True,
        )

        User.objects.create_user(
            username='notadmin',
            email='notadmin@test.com',
            password='notadmin',
            is_staff=False,
        )


    def test_success(self):
        response = self.client.get(reverse('product'), data={
            'q': 'ps5'
        })
        self.assertEqual(response.status_code, 200)
    
    def test_successful_save(self):
        response = self.client.post(reverse('login'), data={
            'username': 'admin',
            'password': 'admin'
        })

        access_token = response.data['tokens']['access']

        payload = {
           'product_name': 'ps5',
            'image_url': 'https://example.com/ps5.jpg',
            'listings': [
                {
                    'domain': 'jbhifi.com.au',
                    'link': 'https://jbhifi.com.au/ps5',
                    'name': 'PlayStation 5',
                    'price': '$799'
                }
            ] 
        }

        response = self.client.post(
            reverse('product'),
            data=payload,
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        self.assertEqual(response.status_code, 201)

    def test_unauthenticated_save(self):
        response = self.client.post(reverse('login'), data={
            'username': 'notadmin',
            'password': 'notadmin'
        })

        access_token = response.data['tokens']['access']

        payload = {
           'product_name': 'ps5',
            'image_url': 'https://example.com/ps5.jpg',
            'listings': [
                {
                    'domain': 'jbhifi.com.au',
                    'link': 'https://jbhifi.com.au/ps5',
                    'name': 'PlayStation 5',
                    'price': '$799'
                }
            ] 
        }

        response = self.client.post(
            reverse('product'),
            data=payload,
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        self.assertEqual(response.status_code, 403)



    