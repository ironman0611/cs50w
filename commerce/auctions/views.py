from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from decimal import Decimal

from .models import User, Listing, Watchlist, Bid, Comment


def index(request):
    listings = Listing.objects.filter(is_active=True)
    return render(request, "auctions/index.html", {
        "listings": listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def create_listing(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        starting_bid = request.POST["starting_bid"]
        image_url = request.POST["image_url"]
        category = request.POST["category"]
        listing = Listing(
            title=title,
            description=description,
            starting_bid=starting_bid,
            image_url=image_url,
            category=category,
            owner=request.user
        )
        listing.save()
        return HttpResponseRedirect(reverse("index"))

    return render(request, "auctions/create.html")


def listing(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    message = None

    if request.method == "POST":
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("login"))

        if "watchlist" in request.POST:
            item = Watchlist.objects.filter(user=request.user, listing=listing)
            if item:
                item.delete()
            else:
                watch = Watchlist(user=request.user, listing=listing)
                watch.save()
            return HttpResponseRedirect(reverse("listing", args=(listing.id,)))

        elif "place_bid" in request.POST:
            if not listing.is_active:
                message = "This listing is closed."
            else:
                bid_amount = Decimal(request.POST["bid"])
                highest = listing.bids.order_by("-amount").first()
                if highest is None:
                    if bid_amount < listing.starting_bid:
                        message = "Bid must be at least as large as the starting bid."
                    else:
                        bid = Bid(amount=bid_amount, bidder=request.user, listing=listing)
                        bid.save()
                        return HttpResponseRedirect(reverse("listing", args=(listing.id,)))
                else:
                    if bid_amount <= highest.amount:
                        message = "Bid must be greater than the current bid."
                    else:
                        bid = Bid(amount=bid_amount, bidder=request.user, listing=listing)
                        bid.save()
                        return HttpResponseRedirect(reverse("listing", args=(listing.id,)))

        elif "close" in request.POST:
            if request.user == listing.owner and listing.is_active:
                listing.is_active = False
                listing.save()
            return HttpResponseRedirect(reverse("listing", args=(listing.id,)))

        elif "add_comment" in request.POST:
            content = request.POST["comment"]
            comment = Comment(content=content, author=request.user, listing=listing)
            comment.save()
            return HttpResponseRedirect(reverse("listing", args=(listing.id,)))

    on_watchlist = False
    if request.user.is_authenticated:
        on_watchlist = Watchlist.objects.filter(user=request.user, listing=listing)

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comments": listing.comments.all(),
        "on_watchlist": on_watchlist,
        "message": message,
        "winner": listing.winner()
    })


def watchlist(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    if request.method == "POST":
        listing_id = request.POST["listing_id"]
        listing = Listing.objects.get(id=listing_id)
        Watchlist.objects.filter(user=request.user, listing=listing).delete()
        return HttpResponseRedirect(reverse("watchlist"))

    listings = []
    for item in Watchlist.objects.filter(user=request.user):
        listings.append(item.listing)

    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })


def categories(request):
    listings = Listing.objects.all()
    categories = []
    for listing in listings:
        if listing.category and listing.category not in categories:
            categories.append(listing.category)

    return render(request, "auctions/categories.html", {
        "categories": categories
    })


def category(request, category):
    listings = Listing.objects.filter(category=category, is_active=True)
    return render(request, "auctions/category.html", {
        "listings": listings,
        "category": category
    })
