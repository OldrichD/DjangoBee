from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from myapp.forms import LoginForm, RegisterForm, AddHivesPlace
from django.contrib.auth.decorators import login_required
from myapp.models import Hives, HivesPlaces, Beekeepers
from django.contrib.auth.models import User


def index(request):
    return render(request, 'index.html')


def login_user(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Přihlášení proběhlo úspěšně.')
                return redirect('home')  # Přesměrování na domovskou stránku nebo kamkoliv jinam
            else:
                messages.error(request, 'Neplatné přihlašovací údaje.')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def logout_user(request):
    logout(request)
    messages.success(request, 'Odhlášení proběhlo úspěšně.')
    return redirect('index')


def signup(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=password)
            login(request, user)
            messages.success(request, 'Registrace nového uživatele proběhla úspěšně, nyní jste přihlášen.')
            return redirect('home')  # přesměrování na přihlašovací stránku
    else:
        form = RegisterForm()
    return render(request, 'signup.html', {'form': form})


def login_required_message(request):
    messages.error(request, 'Obsah je dostupný jen přihlášeným uživatelům.')
    return redirect('login_user')


@login_required
def overview(request):

    hives_places_count = HivesPlaces.objects.filter(beekeeper=request.user).count()
    hives_count = Hives.objects.filter(place__beekeeper=request.user).count()

    return render(request, 'overview.html', {'hives_places_count': hives_places_count, 'hives_count': hives_count})


@login_required
def add_hives_place(request):
    if request.method == 'POST':
        form = AddHivesPlace(request.POST)
        if form.is_valid():
            # Získání aktuálně přihlášeného uživatele
            beekeeper_id = Beekeepers.objects.get(user_ptr__username=request.user.username)

            # Uložení nového záznamu do databáze
            hives_place = form.save(commit=False)
            hives_place.beekeeper = beekeeper_id # Přiřazení přihlášeného uživatele
            hives_place.save()
            messages.success(request, 'Nové stanoviště bylo vytvořeno.')
            return redirect('home')  # Přesměrování na domovskou stránku nebo jinam po úspěšném vytvoření
    else:
        form = AddHivesPlace()

    return render(request, 'create_hives_place.html', {'form': form})

