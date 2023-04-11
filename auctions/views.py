from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Bid, Comment
from .forms import ListingForm, BidForm


def index(request):
    """ Shows currently active listings """

    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(active=True),
    })


@login_required
def add_listing(request):
    """ Allows a user to create a listing """

    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            # https://docs.djangoproject.com/en/4.2/topics/forms/modelforms/#the-save-method
            listing = form.save(commit=False)
            listing.seller = request.user
            listing.current_price = listing.starting_price
            listing.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/add_listing.html", {
                "form": form,
                "message": "Failed to add listing.",
            })
    else:
        return render(request, "auctions/add_listing.html", {
            "form": ListingForm()
        })


def listing_page(request, listing_id):
    """ Shows information for given listing """

    # Get listing info
    listing = Listing.objects.get(pk=listing_id)

    # Get total number of bids
    bid_count = listing.bids.count()

    if bid_count:
        # https://stackoverflow.com/questions/844591/how-to-do-select-max-in-django
        highest_bid = listing.bids.order_by('-value')[0].value

        # Check if user has placed a bid
        user_bid = listing.bids.filter(bidder=request.user)
        if user_bid:
            if user_bid[0].value == highest_bid:
                message = "Your bid is the current bid."
            else:
                message = "Your bid is not the current bid. Place a new bid to buy the listing."
        else:
            message = "You have not placed a bid."
    else:
        message = "Be the first to place a bid."

    return render(request, "auctions/listing_page.html", {
        "listing": listing,
        "bid_status": f"{bid_count} bid(s) so far. {message}",
        "form": BidForm(),
    })


def place_bid(request, listing_id):
    """ Allows user to place bid on listing """
    
    if request.method == "POST":
        form = BidForm(request.POST)
        if form.is_valid():
            pass
    else:
        return HttpResponseRedirect(reverse("listing_page", args=[listing_id]))


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
