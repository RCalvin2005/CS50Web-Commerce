from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    pass


class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    image_url = models.CharField(max_length=160, blank=True)

    # Categories
    BRAND_CHOICES = [
        ("AP", "Apple"),
        ("SM", "Samsung"),
        ("NK", "Nokia"),
    ]
    TYPE_CHOICES = [
        ("LUX", "Luxury"),
        ("LTS", "Latest Model"),
        ("STD", "Standard Model"),
        ("LEG", "Legacy"),
    ]
    CONDITION_CHOICES = [
        ("N", "New"),
        ("U", "Used"),
        ("B", "Broken"),
    ]
    brand = models.CharField(
        max_length=2,
        choices=BRAND_CHOICES,
        blank=True,
    )
    type = models.CharField(
        max_length=3,
        choices=TYPE_CHOICES,
        blank=True,
    )
    condition = models.CharField(
        max_length=1,
        choices=CONDITION_CHOICES,
        blank=True,
    )

    # https://stackoverflow.com/questions/849142/how-to-limit-the-maximum-value-of-a-numeric-field-in-a-django-model
    starting_price = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(999999999)])
    current_price = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(999999999)])

    date = models.DateTimeField(auto_now_add=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    active = models.BooleanField(default=True)
    watchers = models.ManyToManyField(User, blank=True, related_name="watchlist")
    
    def __str__(self):
        return f"{self.title}"
    

class Bid(models.Model):
    value = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(999999999)])
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")

    def __str__(self):
        return f"{self.bidder} has placed a bid of ${self.value} for {self.listing}"


class Comment(models.Model):
    message = models.TextField()
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author} commented \"{self.message}\" at {self.listing}"
