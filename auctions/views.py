from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404, redirect
from django.urls import reverse

from .models import User, Listing, Category, Bid, Comment, Watchlist
from .forms import ListingForm

from django.contrib.auth.decorators import login_required

from django.contrib import messages


def index(request):
    active_listings = Listing.objects.filter(is_active=True)
    return render(request, "auctions/index.html", {'listings': active_listings})


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


@login_required
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


@login_required
def create_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)  # Guarda el formulario pero aún no lo comete en la base de datos
            listing.owner = request.user  # Asigna el usuario actual como propietario
            listing.save()  # Ahora sí, guarda el objeto en la base de datos
            return redirect('index')
    else:
        form = ListingForm()
    return render(request, 'auctions/create_listing.html', {'form': form})


@login_required
def listing(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    highest_bid = listing.bids.order_by('-amount').first()
    if highest_bid and highest_bid.bidder == request.user:
        listing.current_bid_user = True
    else:
        listing.current_bid_user = False
    
    in_watchlist = Watchlist.objects.filter(user=request.user, listing=listing).exists()
        # Comprueba si el modelo Watchlist relaciona usuarios y listings

    if request.method == 'POST':
        bid_amount = float(request.POST.get('bid', 0))  # Obtener 'bid' o 0 si no existe
        starting_bid = listing.starting_bid
        highest_bid = listing.bids.order_by('-amount').first()
        # Verificar si el bid es válido.
        if bid_amount < starting_bid or (highest_bid and bid_amount <= highest_bid.amount):
            # Si el bid no es válido, muestra un mensaje de error.
            messages.error(request, 'Your bid must be at least equal to the starting bid and higher than any other bids.')
        else:
            # Si el bid es válido, proceder a guardarlo.
            new_bid = Bid(listing=listing, bidder=request.user, amount=bid_amount)
            new_bid.save()
            messages.success(request, 'Your bid was successfully placed!')
            return redirect(reverse('listing', kwargs={'listing_id': listing.id}))
        # Nota: Si el bid no es válido, la función continuará para renderizar la página de nuevo con el mensaje de error.

    # Para solicitudes GET o después de manejar un POST con errores, simplemente renderiza el template
    return render(request, 'auctions/listing.html', {'listing': listing, 'in_watchlist': in_watchlist})


@login_required
def add_watchlist(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    watchlist = Watchlist(user=request.user, listing=listing)
    watchlist.save()
    return redirect(reverse('listing', kwargs={'listing_id': listing.id}))


@login_required
def remove_watchlist(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    watchlist = Watchlist.objects.filter(user=request.user, listing=listing)
    watchlist.delete()
    return redirect(reverse('listing', kwargs={'listing_id': listing.id}))
