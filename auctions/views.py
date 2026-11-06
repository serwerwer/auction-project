# Create your views here.
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404, redirect, render
from django.core.exceptions import ValidationError

from .models import Auction, Bid
from .services import place_bid
from .forms import BidForm

@require_http_methods(["GET", "POST"])
def auction_detail_and_bid(request, auction_id):

    auction = get_object_or_404(Auction, pk=auction_id)

    # handle POST request 
    if request.method == "POST":
        form = BidForm(request.POST)
        if form.is_valid():
            try:
                place_bid(
                    auction_id = auction_id, 
                    user = request.user, 
                    amount = form.cleaned_data["amount"])

            except ValidationError as error:
                form.add_error(None, ";".join(error.messages))
            else:
                return redirect("auctions:detail", auction_id = auction.id)    

    # Handle GET requests         
    else:
        form = BidForm()

    # Retrive bidding history 
    bids = (Bid.objects.filter(auction=auction).select_related("user").order_by("-amount","-created_at"))
    highest_bid = bids.first()

    current_price = (highest_bid.amount if highest_bid is not None else auction.starting_price)    

    # render the HTML response     
    return render(request, "auctions/auction_detail.html", {"auction": auction, "form": form, "bids": bids, "current_price": current_price,})    
