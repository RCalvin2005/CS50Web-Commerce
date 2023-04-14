def get_bid_status(request, listing):
    """ Returns the bid status message """

    # Get total number of bids
    bid_count = listing.bids.count()

    if listing.active:
        if request.user.is_authenticated:
            if request.user != listing.seller:
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

    return f"{bid_count} bid(s) so far. {bid_msg}"
