from django import template
from django.utils import timezone

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
