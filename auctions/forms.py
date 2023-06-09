from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from crispy_forms.bootstrap import Div, FormActions

from .models import Listing, Bid, Comment

# Source: https://ordinarycoders.com/blog/article/django-modelforms

# Create your forms here.
class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ("title", "description", "starting_price", "image_url", "brand", "type", "condition")


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

    # https://stackoverflow.com/questions/17830470/get-request-in-form-field-validation
    def __init__(self, *args, **kwargs):
        self.listing_id = kwargs.pop('listing_id', None)
        super(BidForm, self).__init__(*args, **kwargs)

    def clean(self):

        # https://www.geeksforgeeks.org/python-form-validation-using-django/
        super(BidForm, self).clean()

        value = self.cleaned_data.get("value")

        listing = Listing.objects.get(pk=self.listing_id)

        try:
            # Ensure bid placed is higher than highest bid
            highest_bid = listing.bids.order_by('-value')[0].value
            if not value > highest_bid:
                self._errors['value'] = self.error_class([
                f'Bid should be more than ${highest_bid}']) 
        except IndexError:
            # Ensure bid placed at least equal to starting price
            if not value >= listing.starting_price:
                self._errors['value'] = self.error_class([
                f'Bid should be at least ${listing.starting_price}'])             

        return self.cleaned_data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("message",)
        widgets = {
            "message": forms.Textarea(attrs={
                "placeholder": "Add a comment...",
                "rows": "2",
            }),
        }
        labels = {
            "message": "",
        }


class CategoriesForm(forms.ModelForm):

    # https://stackoverflow.com/questions/46892518/inline-form-with-django-crispy-form
    def __init__(self, *args, **kwargs):
        super(CategoriesForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
        Div(
            Div("brand", css_class="col"),
            Div("type", css_class="col"),
            Div("condition", css_class="col"),
            Div(
                FormActions(Submit('submit', 'Filter')),
                css_class="col-auto categories-button"
            ),
            css_class='row container-fluid mx-auto',
        ))


    class Meta:
        model = Listing
        fields = ("brand", "type", "condition")
