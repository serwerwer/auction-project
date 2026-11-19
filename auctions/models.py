from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


class Auction(models.Model):
    title = models.CharField(max_length=250)
    starting_price = models.DecimalField(
        max_digits=9,
        decimal_places=2,
        validators=[
            MinValueValidator(
                Decimal("1.00"), message="Auction price must be at least 1 PLN"
            )
        ],
    )
    ends_at = models.DateTimeField()
    closed = models.BooleanField(default=False)
    minimum_increment = models.DecimalField(
        max_digits=9,
        decimal_places=0,
        validators=[
            MinValueValidator(
                Decimal("1.00"), message="Minimum increment must be at least 1 PLN"
            )
        ],
    )

    # retrive main photo
    @property
    def main_photo(self):
        return self.auctionphoto_set.filter(is_main=True).first()


class Bid(models.Model):
    auction = models.ForeignKey(
        Auction, on_delete=models.PROTECT
    )  # deleting auctions restricted
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(
        max_digits=9,
        decimal_places=2,
    )


class AuctionPhoto(models.Model):
    auction = models.ForeignKey(
        Auction,
        on_delete=models.CASCADE,  # delete photos when associated auction is deleted
    )

    image = models.ImageField(upload_to="auction_photos/")

    is_main = models.BooleanField(default=False)

    class Meta:
        constraints = [  # noqa: RUF012
            models.UniqueConstraint(
                fields=["auction"],  # the condition is checked for a given auction
                condition=Q(is_main=True),
                name="unique_main_photo_per_auction",
            )
        ]
