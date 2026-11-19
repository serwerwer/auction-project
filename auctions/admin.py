from django.contrib import admin

from .models import Auction, AuctionPhoto

# Register auction model
# This means that the model can be managed from the admin site
# add photo uploads


class AuctionPhotoInline(admin.TabularInline):
    model = AuctionPhoto
    extra = 2


@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    inlines = [AuctionPhotoInline] # noqa: RUF012