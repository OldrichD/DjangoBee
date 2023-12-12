from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db.models import Q
from django.utils import timezone
from datetime import date
from django.contrib.auth.forms import UserCreationForm
from myapp.models import Beekeepers, HivesPlaces, Hives, Mothers, Visits, Tasks


class LoginForm(forms.Form):
    username = forms.CharField(max_length=65)
    password = forms.CharField(max_length=65, widget=forms.PasswordInput)


class RegisterForm(UserCreationForm):
    beekeeper_id = forms.IntegerField(validators=[MinValueValidator(0)])

    class Meta:
        model = Beekeepers
        fields = ['username', 'email', 'password1', 'password2', 'beekeeper_id']


class AddHivesPlace(forms.ModelForm):
    class Meta:
        model = HivesPlaces
        fields = ['name', 'type', 'location', 'comment']

    def clean_name(self):
        beekeeper = self.cleaned_data.get('beekeeper')
        name = self.cleaned_data.get('name')

        # Kontrola, zda záznam s daným beekeeper_id a place_name již existuje
        if HivesPlaces.objects.filter(beekeeper=beekeeper, name=name, active=True).exists():
            raise forms.ValidationError("Záznam s tímto jménem již existuje pro daného včelaře.")

        return name


class AddHive(forms.ModelForm):

    type = forms.CharField(label='Typ úlové sestavy:')
    comment = forms.CharField(label='Komentář:', required=False)

    class Meta:
        model = Hives
        fields = ['type', 'comment']


class AddMother(forms.ModelForm):
    class Meta:
        model = Mothers
        fields = ['ancestor', 'mark', 'year', 'male_line', 'female_line', 'comment']
        labels = {
            'ancestor': 'Předek:',
            'mark': 'Značka:',
            'year': 'Rok:',
        }
    comment = forms.CharField(widget=forms.Textarea, label="Komentář:", required=False)
    male_line = forms.CharField(initial='volně pářená', label='Trubčí linie:', required=False)
    female_line = forms.CharField(label='Linie matky:', required=False)

    def __init__(self, user, *args, **kwargs):
        super(AddMother, self).__init__(*args, **kwargs)
        # Omezit hodnoty pro 'ancestor' pouze na záznamy z tabulky Mothers, které jsou propojené s přihlášeným uživatelem
        mothers_queryset = Mothers.objects.filter(hive__place__beekeeper__username=user.username)
        self.fields['ancestor'].queryset = mothers_queryset
        self.fields['ancestor'].label_from_instance = lambda obj: obj.display_name()


class AddVisit(forms.ModelForm):

    CONDITION_CHOICES = [
        (None, '-'),
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
    ]

    date = forms.DateField(
        label='Datum prohlídky:',
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=date.today()
    )
    inspection_type = forms.CharField(
        label='Typ prohlídky:',
        required=True
    )
    condition = forms.TypedChoiceField(
        label='Síla včelstva:',
        choices=CONDITION_CHOICES,
        coerce=int,
        empty_value=None,
        required=False
    )
    hive_body_size = forms.IntegerField(
        label='Velikost plodiště:',
        validators=[MinValueValidator(0)],
        required=False
    )
    honey_supers_size = forms.IntegerField(
        label='Velikost medníku:',
        validators=[MinValueValidator(0)],
        required=False
    )
    honey_yield = forms.DecimalField(
        label='Výnos medu (kg):',
        decimal_places=2,
        localize=False,
        required=False,
    )
    medication_application = forms.CharField(
        label='Aplikace léčiva:',
        required=False,
    )
    disease = forms.CharField(
        label='Příznaky onemocnění:',
        required=False
    )
    mite_drop = forms.IntegerField(
        label='Spad roztočů:',
        validators=[MinValueValidator(0)],
        required=False
    )

    performed_tasks = forms.ModelMultipleChoiceField(
        queryset=Tasks.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Provedené úkony:'
    )

    class Meta:
        model = Visits
        fields = ['date', 'inspection_type', 'condition', 'hive_body_size',
                  'honey_supers_size', 'honey_yield', 'medication_application',
                  'disease', 'mite_drop', 'performed_tasks']


class EditVisit(forms.ModelForm):

    CONDITION_CHOICES = [
        (None, '-'),
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
    ]

    date = forms.DateField(
        label='Datum prohlídky:',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    inspection_type = forms.CharField(
        label='Typ prohlídky:',
        required=True
    )
    condition = forms.TypedChoiceField(
        label='Síla včelstva:',
        choices=CONDITION_CHOICES,
        coerce=int,
        empty_value=None,
        required=False
    )
    hive_body_size = forms.IntegerField(
        label='Velikost plodiště:',
        validators=[MinValueValidator(0)],
        required=False
    )
    honey_supers_size = forms.IntegerField(
        label='Velikost medníku:',
        validators=[MinValueValidator(0)],
        required=False
    )
    honey_yield = forms.DecimalField(
        label='Výnos medu (kg):',
        decimal_places=2,
        localize=False,
        required=False,
    )
    medication_application = forms.CharField(
        label='Aplikace léčiva:',
        required=False,
    )
    disease = forms.CharField(
        label='Příznaky onemocnění:',
        required=False
    )
    mite_drop = forms.IntegerField(
        label='Spad roztočů:',
        validators=[MinValueValidator(0)],
        required=False
    )

    performed_tasks = forms.ModelMultipleChoiceField(
        queryset=Tasks.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Provedené úkony:'
    )

    class Meta:
        model = Visits
        fields = ['date', 'inspection_type', 'condition', 'hive_body_size',
                  'honey_supers_size', 'honey_yield', 'medication_application',
                  'disease', 'mite_drop', 'performed_tasks']


class EditHivesPlace(forms.ModelForm):
    class Meta:
        model = HivesPlaces
        fields = ['name', 'type', 'location', 'comment']

    def clean_name(self):
        beekeeper = self.cleaned_data.get('beekeeper')
        name = self.cleaned_data.get('name')

        # Kontrola, zda záznam s daným beekeeper_id a place_name již existuje
        if HivesPlaces.objects.filter(beekeeper=beekeeper, name=name, active=True).exists():
            raise forms.ValidationError("Záznam s tímto jménem již existuje pro daného včelaře.")

        return name


class ChangeHivesPlace(forms.Form):
    old_hives_place = forms.CharField(widget=forms.HiddenInput(), required=False)


    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        hives_place_id = kwargs.pop('hives_place_id', None)
        super(ChangeHivesPlace, self).__init__(*args, **kwargs)

        self.fields['selected_hives'] = forms.ModelMultipleChoiceField(
            queryset=Hives.objects.filter(place__beekeeper=user),
            widget=forms.CheckboxSelectMultiple,
            label='Vyberte včelstva:',
            required=True
        )

        self.fields['new_hives_place'] = forms.ModelChoiceField(
            queryset=HivesPlaces.objects.filter(beekeeper=user, active=True).exclude(id=hives_place_id),
            label='Vyberte nové stanoviště:',
        )


class CustomHiveWidget(forms.Select):
    def format_option(self, obj):
        return self.label_from_instance(obj)


class ChangeMotherHive(forms.Form):
    def __init__(self, *args, user=None, mother_id=None, **kwargs):
        self.mother = kwargs.pop('mother', None)
        self.user = kwargs.pop('user', None)
        super(ChangeMotherHive, self).__init__(*args, **kwargs)

        # Předání parametru 'user' do konstruktoru pole 'new_hive'
        self.fields['new_hive'] = forms.ModelChoiceField(
            queryset=Hives.objects.filter(
                Q(mothers__isnull=True) | Q(mothers__active=False),
                place__beekeeper=user,
                active=True),
            label='Vyberte nové včelstvo:',
            widget=CustomHiveWidget()
        )
        self.fields['new_hive'].label_from_instance = self.label_from_instance

    @staticmethod
    def label_from_instance(obj):
        return f"{obj.place} - č. {obj}"




