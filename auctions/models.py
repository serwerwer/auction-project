from django.db import models
from django.conf import settings

class Auction(models.Model):
    title = models.CharField(max_length=250)
    starting_price = models.DecimalField(max_digits = 9, decimal_places=2, default=100.00)
    ends_at = models.DateTimeField()

class User(models.Model):
    # to substitute with weras code
    pass

class Bid(models.Model):
    auction = models.ForeignKey(Auction,on_delete=models.PROTECT) # deleting auctions restricted
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT) 
    created_at = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits = 9, decimal_places=2)
