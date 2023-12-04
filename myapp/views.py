from django.db.models import Count, Value, Max
from django.db.models.functions import Coalesce
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from myapp.forms import LoginForm, RegisterForm, AddHivesPlace, AddHive, AddMother, AddVisit
from django.contrib.auth.decorators import login_required
from myapp.models import Hives, HivesPlaces, Beekeepers, Visits, Mothers, Tasks
from django.contrib.auth.models import User


def index(request):
    return render(request, 'index.html')


def login_user(request):
    if request.user.is_authenticated:
        # Uživatel je již přihlášen, takže přesměruje na stránku overview
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

    last_visits = (
        Visits.objects
        .filter(hive__place__beekeeper=request.user)
        .values('hive__place__name')
        .annotate(last_visit=Max('date'))
    )
    last_visits = {item['hive__place__name']: item['last_visit'] for item in last_visits}

    return render(request, 'overview.html', {
            'hives_places_count': hives_places_count,
            'hives_count': hives_count,
            'hives_places': hives_places,
            'hives_places_dict': hives_places_dict,
            'last_visits': last_visits
        })


@login_required
def hives_place(request, hives_place_id=None):
    try:
        user_hives_place = get_object_or_404(HivesPlaces, id=hives_place_id, beekeeper=request.user)
        hives = Hives.objects.filter(place=user_hives_place)
        last_visits = (
            Visits.objects
            .filter(hive__place__beekeeper=request.user, hive__place=hives_place_id)
            .values('hive__id')
            .annotate(last_visit=Max('date'))
        )
        last_visits = {item['hive__id']: item['last_visit'] for item in last_visits}


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
            'last_visits': last_visits
        })
    except Http404:
        messages.error(request, "Záznamy o včelstvu pro přihlášeného uživatele nejsou k dispozici.")
        return redirect('overview')


@login_required
def visits(request, hive_id=None):
    try:
        user_hive = get_object_or_404(Hives, id=hive_id, place__beekeeper=request.user)
        user_visits = Visits.objects.filter(hive=user_hive)
        user_hive.mother = Mothers.objects.filter(hive=user_hive)

        return render(request, 'overview.html', {
            'overview_spec': 'visits',
            'hive_id': hive_id,
            'user_hive': user_hive,
            'user_visits': user_visits
        })
    except Http404:
        messages.error(request, "Záznamy o včelstvu pro přihlášeného uživatele nejsou k dispozici.")
        return redirect('overview')


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
    sisters = Mothers.objects.filter(ancestor=mother.ancestor, ancestor__isnull=False).exclude(id=mother.id)

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


@login_required
def add_hive(request, hives_place_id=None):
    try:
        hives_place = get_object_or_404(HivesPlaces, id=hives_place_id)
    except Http404:
        messages.error(request, "Záznamy o stanovišti pro přihlášeného uživatele nejsou k dispozici.")
        return redirect('overview')

    # Kontrola, zda přihlášený uživatel odpovídá beekeeperovi v HivesPlaces
    if request.user.id != hives_place.beekeeper.id:
        messages.error(request, 'Nemáte oprávnění přidávat včelstvo na toto stanoviště.')
        return redirect('overview')

    if request.method == 'POST':
        form = AddHive(request.POST)
        if form.is_valid():
            hive = form.save(commit=False)
            # Získání maximální hodnoty sloupce 'number'
            max_number = Hives.objects.filter(place_id=hives_place_id).aggregate(Max('number'))['number__max']
            # Zvýšení hodnoty o 1
            hive.number = max_number + 1 if max_number is not None else 1
            hive.place_id = hives_place.id
            hive.save()
            messages.success(request, f'Bylo vytvořeno včelstvo č. {hive.number} '
                                      f'na stanovišti {hives_place.name}')
            return redirect('hives_place', hives_place_id)
    else:
        form = AddHive()

    return render(request, 'create_hive.html', {'form': form})


@login_required
def add_mother(request, hive_id=None):
    try:
        selected_hive = get_object_or_404(Hives, id=hive_id)
    except Http404:
        messages.error(request, "Uživatel může přidávat matky pouze do svých včelstev.")
        return redirect('overview')

    if request.user.id != selected_hive.place.beekeeper.id:
        messages.error(request, 'Nemáte oprávnění přidávat matku do požadovaného včelstva.')
        return redirect('overview')

    if request.method == 'POST':
        form = AddMother(request.user, request.POST)
        if form.is_valid():
            mother = form.save(commit=False)
            mother.hive = selected_hive
            mother.save()
            messages.success(request, f'Matka byla přidána do včelstva {selected_hive.number} '
                                      f'na stanovišti {selected_hive.place.name} .'
                             )
            return redirect('hives_place', selected_hive.place.id)
    else:
        form = AddMother(request.user)

    return render(request, 'create_mother.html', {'form': form})


@login_required
def add_visit(request, hive_id=None):
    try:
        user_hive = get_object_or_404(Hives, id=hive_id, place__beekeeper=request.user)
        user_hive.mother = Mothers.objects.filter(hive=user_hive)

    except Http404:
        messages.error(request, "Záznamy o vybraném včelstvu nejsou k dispozici.")
        return redirect('overview')

    if request.user.id != user_hive.place.beekeeper.id:
        messages.error(request, "Uživatel může zapisovat prohlídky pouze u svých včelstev.")
        return redirect('overview')

    if request.method == 'POST':
        form = AddVisit(request.POST)
        if form.is_valid():
            visit = form.save(commit=False)
            visit.hive_id = user_hive.id
            visit.save()
            visit.performed_tasks.add(*form.cleaned_data['performed_tasks'])
            messages.success(request, f'U včelstva {user_hive.number} '
                                      f'na stanovišti {user_hive.place.name} '
                                      f'byla zapsána prohlídka.')
            return redirect('visits', user_hive.id)
    else:
        form = AddVisit()

    return render(request, 'create_visit.html', {
        'form': form,
        'user_hive': user_hive
    })
