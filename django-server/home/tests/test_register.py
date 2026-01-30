from django.test import TestCase
from django.urls import reverse
from home.models import User


class RegisterViewTest(TestCase):
    def test_success(self):
        response = self.client.post(reverse('register'), data={
            'username': 'ajl1',
            'email': 'ajl1@gmail.com',
            'password': 'ajl1'
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 1)

    def test_duplicate_username(self):
        response = self.client.post(reverse('register'), data={
            'username': 'ajl1',
            'email': 'ajl1@gmail.com',
            'password': 'ajl1'
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 1)

        response = self.client.post(reverse('register'), data={
            'username': 'ajl1',
            'email': 'ajl2@gmail.com',
            'password': 'ajl2'
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.count(), 1)

    def test_duplicate_email(self):
        response = self.client.post(reverse('register'), data={
            'username': 'ajl1',
            'email': 'ajl1@gmail.com',
            'password': 'ajl1'
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 1)

        response = self.client.post(reverse('register'), data={
            'username': 'ajl2',
            'email': 'ajl1@gmail.com',
            'password': 'ajl2'
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.count(), 1)

    def test_invalid_email(self):
        response = self.client.post(reverse('register'), data={
            'username': 'ajl',
            'email': 'ajl',
            'password': 'ajl'
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.count(), 0)
