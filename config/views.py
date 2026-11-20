from django.db.models import Max
from django.shortcuts import render
from django.utils import timezone

from auctions.models import Auction


def home(request):
    # Fetch auctions with their highest bids
    auctions = Auction.objects.annotate(highest_bid=Max("bid__amount")).order_by(
        "ends_at"
    )

    now = timezone.now()
    auction_items = []

    for auction in auctions:
        # Use the highest bid or the starting price
        current_price = (
            auction.highest_bid
            if auction.highest_bid is not None
            else auction.starting_price
        )

        # Check whether the auction is still active
        is_active = not auction.closed and auction.ends_at > now

        auction_items.append(
            {
                "id": auction.pk,
                "title": auction.title,
                "current_price": current_price,
                "ends_at": auction.ends_at,
                "is_active": is_active,
            }
        )

    return render(
        request,
        "home.html",
        {
            "auctions": auction_items,
        },
    )
