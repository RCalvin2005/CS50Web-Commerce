def get_bid_status(request, listing):
    """ Returns the bid status message """

    # Get total number of bids
    bid_count = listing.bids.count()

    if request.user.is_authenticated:
        if bid_count:
            # https://stackoverflow.com/questions/844591/how-to-do-select-max-in-django
            highest_bid = listing.bids.order_by('-value')[0].value

            # Check if user has placed a bid
            user_bid = listing.bids.filter(bidder=request.user)
            if user_bid:
                if user_bid.order_by('-value')[0].value == highest_bid:
                    bid_msg = "<strong class='text-success'>Your bid is the current bid.</strong>"
                else:
                    bid_msg = "<strong class='text-danger'>Your bid is not the current bid. Place a new bid to buy the listing.</strong>"
            else:
                bid_msg = "You have not placed a bid."
        else:
            bid_msg = "Be the first to place a bid."
    else:
        bid_msg = "<strong class='text-danger'>Login in to place a bid.</strong>"

    return f"{bid_count} bid(s) so far. {bid_msg}"
