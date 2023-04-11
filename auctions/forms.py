from django import forms

from .models import Listing, Bid

# Source: https://ordinarycoders.com/blog/article/django-modelforms

# Create your forms here.
class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ("title", "description", "image_url", "starting_price")


class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ("value",)
        widgets = {
            "value": forms.NumberInput(attrs={"placeholder": "Bid"}),
        }
        labels = {
            "value": "",
        }
