from django.db.models import Count, Value
from django.db.models.functions import Coalesce
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from myapp.forms import LoginForm, RegisterForm, AddHivesPlace
from django.contrib.auth.decorators import login_required
from myapp.models import Hives, HivesPlaces, Beekeepers, Visits, Mothers
from django.contrib.auth.models import User


def index(request):
    return render(request, 'index.html')


def login_user(request):
    if request.user.is_authenticated:
        # Uživatel je již přihlášen, takže přesměrujte na stránku overview
        return redirect('overview')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Přihlášení proběhlo úspěšně.')
                return redirect('overview')  # Přesměrování na domovskou stránku nebo kamkoliv jinam
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
            return redirect('overview')  # přesměrování na přihlašovací stránku
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
    hives_places = HivesPlaces.objects.filter(beekeeper=request.user)
    hives_places_dict = (
        HivesPlaces.objects
        .filter(beekeeper=request.user)
        .annotate(hives_count=Coalesce(Count('hives', distinct=True), Value(0)))
        .values('name', 'hives_count')
    )
    hives_places_dict = {item['name']: item['hives_count'] for item in hives_places_dict}

    return render(request, 'overview.html', {
        'hives_places_count': hives_places_count,
        'hives_count': hives_count,
        'hives_places': hives_places,
        'hives_places_dict': hives_places_dict
    })


@login_required
def hives_place(request, hives_place_id=None):
    try:
        user_hives_place = get_object_or_404(HivesPlaces, id=hives_place_id, beekeeper=request.user)
        hives = Hives.objects.filter(place=user_hives_place)

        # Vytvoření slovníku pro předání do šablony
        hives_dict = {}
        mothers_dict = {}
        for hive in hives:
            mother = (
                Mothers.objects
                .filter(hive=hive)
                .first()
            )
            if mother:
                hives_dict[hive.id] = mother.mark
                mothers_dict[hive.id] = mother.id
            else:
                hives_dict[hive.id] = None

        return render(request, 'overview.html', {
            'overview_spec': 'hives',
            'hives': hives,
            'hives_dict': hives_dict,
            'mothers_dict': mothers_dict,
            'hives_place_id': hives_place_id,
        })
    except Http404:
        messages.error(request, "Záznamy o včelstvu pro přihlášeného uživatele nejsou k dispozici.")
        return redirect('overview')


@login_required
def visits(request, hive_id=None):
    return render(request, 'overview.html', {
        'overview_spec': 'visits',
        'hive_id': hive_id,
    })


@login_required
def mothers(request, mother_id=None):
    mother = (
        Mothers.objects
        .filter(id=mother_id)
        .first()
    )
    ancestors = []
    current_ancestor = mother.ancestor
    while current_ancestor:
        ancestors.append(current_ancestor)
        current_ancestor = current_ancestor.ancestor

    descendants = Mothers.objects.filter(ancestor=mother_id)
    sisters = Mothers.objects.filter(ancestor=mother.ancestor).exclude(id=mother.id)

    return render(request, 'overview.html', {
        'overview_spec': 'mothers',
        'mother': mother,
        'ancestors': ancestors,
        'descendants': descendants,
        'sisters': sisters,
    })


@login_required
def add_hives_place(request):
    if request.method == 'POST':
        form = AddHivesPlace(request.POST)
        if form.is_valid():
            # Získání aktuálně přihlášeného uživatele
            beekeeper_id = Beekeepers.objects.get(user_ptr__username=request.user.username)

            # Uložení nového záznamu do databáze
            hives_place = form.save(commit=False)
            hives_place.beekeeper = beekeeper_id  # Přiřazení přihlášeného uživatele
            hives_place.save()
            messages.success(request, 'Nové stanoviště bylo vytvořeno.')
            return redirect('overview')  # Přesměrování na domovskou stránku nebo jinam po úspěšném vytvoření
    else:
        form = AddHivesPlace()

    return render(request, 'create_hives_place.html', {'form': form})
