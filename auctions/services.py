from .models import Auction, Bid
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError


@transaction.atomic
def place_bid(auction_id, user, amount):

    # don't accept bids from unlogged users
    if user is None or not user.is_authenticated:
        raise ValidationError("Only logged users can plase bids")

    # this opration locks the database row corresponding to the given auction
    auction = Auction.objects.select_for_update().get(pk=auction_id)

    # don't accept bids after auction deadline
    if timezone.now() >= auction.ends_at:
        raise ValidationError("Auction has ended")

    # don't accept bids after auction is closed
    if auction.closed:
        raise ValidationError("This auction is already closed")

    new_bid = Bid(
        auction=auction,
        user=user,
        amount=amount,
    )

    # validate all model fields - prevents accepting invalid prices e.g. strings, NaN, infinity
    new_bid.full_clean()

    highest_bid = Bid.objects.filter(auction=auction).order_by("-amount").first()

    # Calculate the minimum acceptable bid
    if highest_bid is None:
        minimum_acceptable_bid = auction.starting_price
    else:
        minimum_acceptable_bid = highest_bid.amount + auction.minimum_increment

    # Reject bids below the minimum
    if new_bid.amount < minimum_acceptable_bid:
        raise ValidationError(f"Bid must be at least {minimum_acceptable_bid} PLN.")

    # save new bid to the database
    new_bid.save()

    return new_bid
