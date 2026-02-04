import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        blank=False,
        null=False
    )

class Product(models.Model):
    normalised_name = models.CharField(max_length=256)
    image_url = models.URLField(blank=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return self.normalised_name

class Listing(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='listings'
    )
    domain = models.CharField(max_length=256)
    link = models.URLField(unique=True)
    name = models.CharField(max_length=256)
    price = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return f"{self.name} at {self.domain} costs {self.price}"

class Wishlist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wishlists'
    )
    products = models.ManyToManyField(Product)
    title = models.CharField(max_length=256)
    
    def __str__(self):
        return f"{self.user.username} has a wishlist called {self.title} and the items are {self.products}"
 