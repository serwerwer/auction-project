from django.contrib import admin
from .models import Auction

# Register auction model
# This means that the model can be managed from the admin site
admin.site.register(Auction)
