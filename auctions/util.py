def get_bid_status(request, listing):
    """ Returns the bid status message """

    # Get total number of bids
    bid_count = listing.bids.count()

    if bid_count:
        # https://stackoverflow.com/questions/844591/how-to-do-select-max-in-django
        highest_bid = listing.bids.order_by('-value')[0].value

        # Check if user has placed a bid
        user_bid = listing.bids.filter(bidder=request.user)
        if user_bid:
            if user_bid.order_by('-value')[0].value == highest_bid:
                bid_msg = "Your bid is the current bid."
            else:
                bid_msg = "Your bid is not the current bid. Place a new bid to buy the listing."
        else:
            bid_msg = "You have not placed a bid."
    else:
        bid_msg = "Be the first to place a bid."

    return f"{bid_count} bid(s) so far. {bid_msg}"
