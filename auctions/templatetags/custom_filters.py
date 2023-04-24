from django import template
from django.utils import timezone

from auctions.models import Bid

import re

# https://www.geeksforgeeks.org/custom-template-filters-in-django/

register = template.Library()

@register.filter()
def time_ago(date_created):
    """Returns X days/minutes etc. ago"""

    diff = timezone.now() - date_created

    # https://stackoverflow.com/questions/2119472/convert-a-timedelta-to-days-hours-and-minutes
    if diff.days:
        if diff.days >= 30:
            diff_str = f"{diff.days // 30} months ago"
        elif diff.days >= 14:
            diff_str = f"{diff.days // 7} weeks ago"
        else:
            diff_str = f"{diff.days} days ago"
    else:
        if diff.seconds >= 3600:
            diff_str = f"{diff.seconds // 3600} hours ago"
        elif diff.seconds >= 60:
            diff_str = f"{diff.seconds // 60} minutes ago"
        else:
            diff_str = f"{diff.seconds} seconds ago"
        
    return re.sub(r"^1 (\w+)s ago$", r"1 \1 ago", diff_str)


@register.filter()
def number_commas(num):
    """ Returns a number separated by commas """
    return f"{num:,}"


@register.filter()
def cutoff(s):
    """ Cuts off a long string into a shorter one """
    
    if len(s) > 220:
        count = 220
        while True:
            if s[count] in [",", ".", "!", "?", " "]:
                return s[:count] + " ..."
            else:
                count += 1 
    else:
        return s
            

@register.simple_tag
def is_watching(user, listing):
    """ Returns True/False if user is watching a listing """
    return user in listing.watchers.all()


@register.simple_tag
def get_comments(listing):
    """ Returns a list of comments for given listing """
    return listing.comments.all().order_by("-date")


@register.simple_tag
def comment_count(listing):
    """ Returns the number of comments """

    count = listing.comments.count()

    if count == 1:
        return f"<h4 class='mt-4'>{count} Comment</h4>"
    else:
        return f"<h4 class='mt-4'>{count} Comments</h4>"


@register.simple_tag
def bid_status_message(user, listing):
    """ Returns a message indicating the total bid count and user's bid status """

    # Get total number of bids
    bid_count = listing.bids.count()

    if listing.active:
        if user.is_authenticated:
            if user != listing.seller:
                if bid_count:
                    # https://stackoverflow.com/questions/844591/how-to-do-select-max-in-django
                    highest_bid = listing.bids.order_by('-value')[0].value

                    # Check if user has placed a bid
                    user_bid = listing.bids.filter(bidder=user)
                    if user_bid:
                        if user_bid.order_by('-value')[0].value == highest_bid:
                            bid_msg = "<strong class='text-success'>Your bid is the current bid.</strong>"
                        else:
                            bid_msg = "<strong class='text-danger'>Your bid is not the current bid. Place a new bid to buy the listing.</strong>"
                    else:
                        bid_msg = "<strong>You have not placed a bid.</strong>"
                else:
                    bid_msg = "<strong class='text-success'>Be the first to place a bid.</strong>"
            else:
                if bid_count:
                    bid_msg = f"<strong class='text-success'>The price has increased by ${ listing.current_price - listing.starting_price } compared to your starting price.</strong>"
                else:
                    bid_msg = f"<strong class='text-danger'>Keep waiting for potential buyers.</strong>"
        else:
            bid_msg = "<strong class='text-danger'>Login in to place a bid.</strong>"
    else:
        bid_msg = "<strong class='text-danger'>The listing has been closed.</strong>"

    if bid_count == 1:
        return f"<p class='small mb-1'>{bid_count} bid so far. {bid_msg}</p>"
    else:
        return f"<p class='small mb-1'>{bid_count} bids so far. {bid_msg}</p>"


@register.simple_tag
def bid_result(user, listing):
    """ Returns the bid result for a closed listing """

    if user != listing.seller:
        user_bid = listing.bids.filter(bidder=user)

        if user_bid:
            if user_bid.order_by('-value')[0].value == listing.bids.order_by('-value')[0].value:
                return f"<div class='alert alert-success' role='alert'>Congrats! You won the listing! Contact <strong>@{listing.seller}</strong> for your item.</div>"
            else:
                return "<div class='alert alert-danger' role='alert'>You lost the bid. Better luck next time!</div>"
        else:
            return "<div class='alert alert-warning' role='alert'>You did not placed a bid.</div>"
    
    else:
        try:
            winner = Bid.objects.filter(listing=listing).order_by('-value')[0].bidder
        except:
            return f"<div class='alert alert-danger' role='alert'>No one had placed a bid on your listing.</div>"

        return f"<div class='alert alert-primary' role='alert'><strong>@{winner}</strong> has won your listing. The price has increased by <strong>${ listing.current_price - listing.starting_price }</strong> compared to your starting price.</div>"


# https://stackoverflow.com/questions/420703/how-do-i-add-multiple-arguments-to-my-custom-template-filter-in-a-django-templat
@register.simple_tag
def bid_status_badge(user, listing):
    """ Returns a bootstrap badge indicating the user's bid status """

    try: 
        highest_bid = listing.bids.order_by('-value')[0].value
    except IndexError:
        return "<span class='badge text-bg-secondary'>No Bids</span>"
    
    user_bid = listing.bids.filter(bidder=user)

    if listing.active:    
        if user_bid:
            if user_bid.order_by('-value')[0].value == highest_bid:
                return "<span class='badge text-bg-success'>You have the leading bid</span>"
            else:
                return "<span class='badge text-bg-danger'>Place a new bid to be in the lead</span>"
        else:
            return "<span class='badge text-bg-secondary'>You have not placed a bid</span>"
    else:
        if user_bid:
            if user_bid.order_by('-value')[0].value == highest_bid:
                return "<span class='badge text-bg-success'>You won</span>"
            else:
                return "<span class='badge text-bg-danger'>You lost</span>"
        else:
            return "<span class='badge text-bg-secondary'>You did not placed a bid</span>"


@register.simple_tag
def categories_badge(listing):
    """ Returns a bootstrap badge indicating the categories for a given listing """

    BADGE_COLORS = {
        "AP": "text-bg-dark",
        "SM": "text-bg-primary",
        "NK": "text-bg-info",
        "LUX": "text-bg-warning",
        "LTS": "text-bg-primary",
        "OLD": "text-bg-success",
        "LEG": "text-bg-dark",
        "N": "text-bg-success",
        "U": "text-bg-secondary",
        "B": "text-bg-danger",
    }

    badges = ""

    if listing.brand:
        badges += f"<span class='badge {BADGE_COLORS[listing.brand]}'>{listing.get_brand_display()}</span> "
    if listing.type:
        badges += f"<span class='badge {BADGE_COLORS[listing.type]}'>{listing.get_type_display()}</span> "
    if listing.condition:
        badges += f"<span class='badge {BADGE_COLORS[listing.condition]}'>{listing.get_condition_display()}</span> "

    return badges
