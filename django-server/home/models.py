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
    store_img_url = models.URLField(blank=True)
    url = models.URLField(unique=True)
    title = models.CharField(max_length=256)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.title} at {self.store} costs {self.price}"

class Wishlist(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wishlists'
    )
    title = models.CharField(max_length=256)

    def __str__(self):
        return f"{self.user.username} has a wishlist called {self.title}"


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(
        Wishlist,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='on_wishlist'
    )

    class Meta:
        unique_together = ('wishlist', 'product')

    def __str__(self):
        return f"{self.product.normalised_name} is on {self.wishlist.title}"
    
 