from django.urls import path
from . import views 

# path is a function that connects URL pattern to Python view 

app_name = "auctions"

urlpatterns = [
    path("<int:auction_id>/", views.auction_detail_and_bid, name="detail")
    ]