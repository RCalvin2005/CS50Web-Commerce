from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Bid, Comment
from .forms import ListingForm, BidForm, CommentForm
from .util import get_bid_status


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

    msg = request.session.get("msg")
    request.session["msg"] = None

    return render(request, "auctions/listing_page.html", {
        "listing": listing,
        "watchers": listing.watchers.all(),
        "comments": listing.comments.all().order_by("-date"),
        "comment_count": listing.comments.count(),
        "bid_status": get_bid_status(request, listing),
        "bid_form": BidForm(),
        "comment_form": CommentForm(),
        "msg": msg,
    })


@login_required
def place_bid(request, listing_id):
    """ Allows user to place bid on listing """
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        form = BidForm(request.POST, listing_id=listing_id)

        if form.is_valid():
            # Save bid data
            bid = form.save(commit=False)
            bid.listing = listing
            bid.bidder = request.user
            bid.save()

            # Update current price
            listing.current_price = bid.value
            listing.save()
            
            # Add listing to watchlist
            if listing not in request.user.watchlist.all():
                listing.watchers.add(request.user) 
                request.session["msg"] = {"msg": "Bid placed successfully. Listing added to watchlist.", "class": "alert-success"}
            else:
                request.session["msg"] = {"msg": "Bid placed successfully.", "class": "alert-success"}

            return HttpResponseRedirect(reverse("listing_page", args=[listing_id]))
        else:
            return render(request, "auctions/listing_page.html", {
                "listing": listing,
                "watchers": listing.watchers.all(),
                "comments": listing.comments.all().order_by("-date"),
                "comment_count": listing.comments.count(),
                "bid_status": get_bid_status(request, listing),
                "bid_form": form,
                "comment_form": CommentForm(),
                "msg": {"msg": "Failed to place bid.", "class": "alert-danger"}
            })
    else:
        return HttpResponseRedirect(reverse("listing_page", args=[listing_id]))


@login_required
def post_comment(request, listing_id):
    """ Allows user to post comment on listing """

    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        form = CommentForm(request.POST)

        if form.is_valid():
            # Save comment data
            comment = form.save(commit=False)
            comment.listing = listing
            comment.author = request.user
            comment.save()
            
            request.session["msg"] = {"msg": "Comment posted!", "class": "alert-success"}

            return HttpResponseRedirect(reverse("listing_page", args=[listing_id]))
        else:
            return render(request, "auctions/listing_page.html", {
                "listing": listing,
                "comments": listing.comments.all().order_by("-date"),
                "comment_count": listing.comments.count(),
                "bid_status": get_bid_status(request, listing),
                "bid_form": BidForm(),
                "comment_form": form,
                "msg": {"msg": "Failed to post comment.", "class": "alert-danger"}
            })
    else:
        return HttpResponseRedirect(reverse("listing_page", args=[listing_id]))


@login_required
def close_listing(request, listing_id):
    """ Allows seller to close their listing """

    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        if request.user == listing.seller:
            listing.active = False
            listing.save()
            request.session["msg"] = {"msg": "Listing has been closed!", "class": "alert-success"}

    return HttpResponseRedirect(reverse("listing_page", args=[listing_id]))


def user_listings(request, username):
    """ Displays all listings created by a specified user """

    seller = User.objects.get(username=username)

    return render(request, "auctions/user_listings.html", {
        "seller": seller,
        "listings": seller.listings.all(),
    })


@login_required
def watchlist(request, username):
    """ Displays all listings in user's own watchlist """

    # Redirect to own watchlist if trying to view someone else's
    if request.user.username != username:
        return HttpResponseRedirect(reverse("watchlist", args=[request.user.username]))

    return render(request, "auctions/watchlist.html", {
        "watchlist": request.user.watchlist.all(),
    })


@login_required
def watchlist_add(request, listing_id):
    """ Allows a user to add a listing to their watchlist """

    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        listing.watchers.add(request.user)
        listing.save()
        request.session["msg"] = {"msg": "Listing has been added to watchlist!", "class": "alert-success"}

    return HttpResponseRedirect(reverse("listing_page", args=[listing_id]))


@login_required
def watchlist_remove(request, listing_id):
    """ Allows a user to remove a listing from their watchlist """

    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        listing.watchers.remove(request.user)
        listing.save()
        request.session["msg"] = {"msg": "Listing has been removed from watchlist!", "class": "alert-success"}

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
