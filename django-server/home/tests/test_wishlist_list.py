from django.test import TestCase
from django.urls import reverse
from home.models import User
import uuid

class WishlistViewTest(TestCase):
    def setUp(self):
        User.objects.create_user(
            username='ajl',
            email='ajl@test.com',
            password='ajl',
            is_staff=True,
        )

        payload = {
           'product_name': 'ps5',
            'image_url': 'https://example.com/ps5.jpg',
            'listings': [
                {
                    'domain': 'jbhifi.com.au',
                    'link': 'https://jbhifi.com.au/ps5',
                    'name': 'PlayStation 5',
                    'price': '$799'
                },
                {
                    'domain': 'test.com.au',
                    'link': 'https://test.com.au/ps5',
                    'name': 'PlayStation 5',
                    'price': '$699'
                }
            ] 
        }

        payload1 = {
           'product_name': 'xbox',
            'image_url': 'https://example.com/xbox.jpg',
            'listings': [
                {
                    'domain': 'microsoft.com.au',
                    'link': 'https://microsoft.com.au/xbox',
                    'name': 'Xbox',
                    'price': '$899'
                }
            ] 
        }

        response = self.client.post(reverse('login'), data={
            'username': 'ajl',
            'password': 'ajl'
        })
        
        self.username = response.data['username']
        self.access_token = response.data['tokens']['access']

        self.prod = self.client.post(
            reverse('product'),
            data=payload,
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        ).data

        self.prod1 = self.client.post(
            reverse('product'),
            data=payload1,
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        ).data

        self.client.post(
            reverse('wishlist-post'),
            data = {
                'title': 'wishlist 1',
                'product_ids': [self.prod['id'], self.prod1['id']]
            },
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )

        self.client.post(
            reverse('wishlist-post'),
            data = {
                'title': 'wishlist 2',
                'product_ids': [self.prod['id']]
            },
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )

    def test_successful_read(self):
        url = reverse('wishlist-user', kwargs={'username': self.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        titles = [wishlist['title'] for wishlist in response.data]
        self.assertEqual(titles, ['wishlist 1', 'wishlist 2'])

    def test_user_not_found(self):
        url = reverse('wishlist-user', kwargs={'username':'hello'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


   
        
