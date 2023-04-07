from django.forms import ModelForm

from .models import Listing

# Source: https://ordinarycoders.com/blog/article/django-modelforms

# Create your forms here.
class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ("title", "description", "image_url", "starting_price")

