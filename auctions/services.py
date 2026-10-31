from .models import Auction, Bid
from django.utils import timezone
from django.core.exceptions import ValidationError

def place_bid(auction_id, user, amount):
    auction = Auction.objects.get(pk=auction_id)

    # don't accept bids after auction deadline
    if timezone.now() >= auction.ends_at:
        raise ValidationError("Auction has ended")

    highest_bid = Bid.objects.filter(auction=auction).order_by("-amount").first()

    if highest_bid is None:
        current_price = auction.starting_price
    else:
        current_price = highest_bid.amount

    # Cannot accept lower bids 
    if amount <= current_price:
        raise ValidationError("Bid must exceed the current price.")

    new_bid = Bid.objects.create(auction = auction, amout = amount, user = user)

    return new_bid
            