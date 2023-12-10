from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone
from datetime import date
from django.contrib.auth.forms import UserCreationForm
from myapp.models import Beekeepers, HivesPlaces, Hives, Mothers, Visits, Tasks


class LoginForm(forms.Form):
    username = forms.CharField(max_length=65)
    password = forms.CharField(max_length=65, widget=forms.PasswordInput)


class RegisterForm(UserCreationForm):
    beekeeper_id = forms.IntegerField()

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
    class Meta:
        model = Hives
        fields = ['type', 'size', 'comment']


class AddMother(forms.ModelForm):
    class Meta:
        model = Mothers
        fields = ['ancestor', 'mark', 'year', 'male_line', 'female_line', 'comment']

    def __init__(self, user, *args, **kwargs):
        super(AddMother, self).__init__(*args, **kwargs)
        # Omezit hodnoty pro 'ancestor' pouze na záznamy z tabulky Mothers, které jsou propojené s přihlášeným uživatelem
        mothers_queryset = Mothers.objects.filter(hive__place__beekeeper__username=user.username)
        self.fields['ancestor'].queryset = mothers_queryset


class AddVisit(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), initial=date.today())
    inspection_type = forms.CharField(required=True)

    condition = forms.CharField(required=False)
    hive_body_size = forms.CharField(required=False)
    honey_supers_size = forms.CharField(required=False)
    honey_yield = forms.CharField(required=False)
    medication_application = forms.CharField(required=False)
    disease = forms.CharField(required=False)
    mite_drop = forms.CharField(required=False)

    performed_tasks = forms.ModelMultipleChoiceField(
        queryset=Tasks.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Visits
        fields = ['date', 'inspection_type', 'condition', 'hive_body_size',
                  'honey_supers_size', 'honey_yield', 'medication_application',
                  'disease', 'mite_drop', 'performed_tasks']


class EditVisit(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    inspection_type = forms.CharField(required=True)

    condition = forms.CharField(required=False)
    hive_body_size = forms.CharField(required=False)
    honey_supers_size = forms.CharField(required=False)
    honey_yield = forms.CharField(required=False)
    medication_application = forms.CharField(required=False)
    disease = forms.CharField(required=False)
    mite_drop = forms.CharField(required=False)

    performed_tasks = forms.ModelMultipleChoiceField(
        queryset=Tasks.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
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
            label='Vyberte včelstva',
            required=True
        )

        self.fields['new_hives_place'] = forms.ModelChoiceField(
            queryset=HivesPlaces.objects.filter(beekeeper=user, active=True).exclude(id=hives_place_id),
            label='Vyberte nové stanoviště',
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





